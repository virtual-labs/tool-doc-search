from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from utils.document_parser import get_chunks
import uuid


class DocumentSearch:

    def __init__(self, url, api_key, collection_name) -> None:
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant_client = QdrantClient(
            url=url,
            api_key=api_key,
        )
        self.collection_name = collection_name

        # print(self.qdrant_client.count(collection_name=collection_name))

    def insert_doc(self, type, url):
        if type == "md" or type == "gdoc":
            doc = {
                "url": url,
                "type": type
            }
            data = get_chunks(doc)
            if len(data):
                self.qdrant_client.delete(
                    collection_name=f"{self.collection_name}",
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="page_title",
                                    match=models.MatchValue(
                                        value=data[0]["payload"]["page_title"]),
                                ),
                            ],
                        )
                    ),
                )
                payloads = []
                vectors = []
                ids = []
                for chunk in data:
                    ids.append(uuid.uuid4().int >> 64)
                    vectors.append(self.encoder.encode(
                        chunk["content"]).tolist())
                    payloads.append(chunk["payload"])
                self.qdrant_client.upsert(
                    collection_name=f"{self.collection_name}",
                    points=models.Batch(
                        ids=ids,
                        payloads=payloads,
                        vectors=vectors
                    ),
                )
        else:
            raise Exception("Invalid document type")

    def get_search_result(self, search_query,
                          limit=10,
                          thresh=0.2,
                          doc_filter="Any",
                          page_title_filter=""):

        if search_query == '':
            return
        if not (doc_filter == "md" or doc_filter == "gdoc" or doc_filter == "Any"):
            return
        page_title_filter = page_title_filter.strip()

        must_conditions = []
        if (doc_filter != 'Any'):
            must_conditions.append(models.FieldCondition(
                key="type",  match=models.MatchValue(value=doc_filter)))
        if (page_title_filter != ''):
            must_conditions.append(models.FieldCondition(
                key="page_title",
                match=models.MatchText(text="content development platform")
            ))

        filter = models.Filter(
            must=must_conditions
        ) if doc_filter != 'Any' or page_title_filter != "" else None

        hits = self.qdrant_client.search(
            collection_name="my_doc",
            query_vector=self.encoder.encode(
                search_query).tolist(),
            limit=int(limit),
            query_filter=filter,
            score_threshold=thresh
        )
        search_results = []
        for hit in hits:
            search_results.append({
                "type": hit.payload["type"],
                "url": hit.payload["url"],
                "score": hit.score,
                "heading": hit.payload["heading"],
                "document": hit.payload["page_title"],
                "text": hit.payload["text"].split("::")[2].strip(),
            })
        return search_results

    # initializing functions

    def create_index(self):
        self.qdrant_client.create_payload_index(
            collection_name=f"{self.collection_name}",
            field_name="type",
            field_schema=models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                min_token_len=2,
                max_token_len=15,
                lowercase=True,
            )
        )
        self.qdrant_client.create_payload_index(
            collection_name=f"{self.collection_name}",
            field_name="page_title",
            field_schema=models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                min_token_len=2,
                max_token_len=15,
                lowercase=True,
            )
        )

    def insert_test_data(self):
        docs = [
            {
                "url": "https://docs.google.com/document/d/1SxTsELQQafYLNXU7q4dcgR-1K0XbX29i",
                "type": "gdoc"
            },
            {
                "url": "https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/developer-doc.md",
                "type": "md"
            },
            {
                "url": "https://docs.google.com/document/d/1SxTsELQQafYLNXU7q4dcgR-1K0XbX29i",
                "type": "gdoc"
            },
            {
                "url": "https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/user-doc.md",
                "type": "md"
            },
            {
                "url": "https://github.com/virtual-labs/app-vlabs-pwa/blob/main/docs/tech_guide.md",
                "type": "md"
            },
            {
                "url": "https://github.com/virtual-labs/app-vlabs-pwa/blob/main/docs/user_manual.md",
                "type": "md"
            },
            {
                "url": "https://docs.google.com/document/d/1lGm88N-Z6fQM6v04k9NZTd-STZ0XYV6YRwIYT1JiSP8/",
                "type": "gdoc"
            }
        ]
        for doc in docs:
            self.insert_doc(type=doc["type"], url=doc["url"])
