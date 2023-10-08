from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from utils.document_parser import get_chunks, get_chunks_batch
import uuid
from error.CustomException import CustomException
from flask import jsonify
import json


class DocumentRecord:

    def __init__(self, url, api_key, collection_name) -> None:
        self.qdrant_client = QdrantClient(
            url=url,
            api_key=api_key,
        )

        self.collection_name = collection_name

        # self.create_index()

        print("Connected to Qdrant : ", self.qdrant_client.count(
            collection_name=collection_name))
        print("Document Record Initialized...")

    def insert_entry(self, docs):
        try:
            if len(docs):
                self.qdrant_client.delete(
                    collection_name=f"{self.collection_name}",
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            should=[
                                models.FieldCondition(
                                    key="base_url",
                                    match=models.MatchValue(
                                        value=doc["base_url"]),
                                ) for doc in docs
                            ]
                        )
                    ),
                )
                print("records got", json.dumps(docs, indent=4))
                print("Deleted records")
                payloads = []
                vectors = []
                ids = []
                for chunk in docs:
                    ids.append(uuid.uuid4().int >> 64)
                    vectors.append([0.0])
                    payloads.append(chunk)
                self.qdrant_client.upsert(
                    collection_name=f"{self.collection_name}",
                    points=models.Batch(
                        ids=ids,
                        payloads=payloads,
                        vectors=vectors
                    ),
                )
                print(json.dumps(payloads, indent=4))
                print("Inserted record")
                return "success"
            else:
                raise Exception("No valid document.")
        except Exception as e:
            raise e

    def test(self):
        self.insert_entry([
            {
                "base_url": "url1",
                "page_title": "document 1",
                "inserted_by": "user1",
                "type": "md"
            },
            {
                "base_url": "url2",
                "page_title": "document 2",
                "inserted_by": "user2",
                "type": "gdoc"
            },
        ])

    def get_docs(self, search_query):
        # make logic for search query
        try:
            search_query = "" if search_query == None else search_query
            filter = models.Filter(
                must=[models.FieldCondition(
                    key="page_title",
                    match=models.MatchText(text=search_query.strip())
                )]
            ) if search_query.strip() else None

            print(filter)

            hits = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=[0],
                with_vectors=True,
                with_payload=True,
                # score_threshold=10,
                limit=10 if search_query.strip() else 500,
                query_filter=filter
            )
            search_results = []
            for hit in hits:
                search_results.append({
                    "accessibility": hit.payload["accessibility"],
                    "type": hit.payload["type"],
                    "base_url": hit.payload["base_url"],
                    "page_title": hit.payload["page_title"],
                    "inserted_by": hit.payload["inserted_by"],
                })
            return search_results
        except Exception as e:
            raise CustomException(str(e), 500)

    def reset_database(self):
        # recreate db
        print("Recreating record database")
        self.qdrant_client.recreate_collection(
            collection_name=f"{self.collection_name}",
            vectors_config=models.VectorParams(
                size=1,
                distance=models.Distance.DOT
            )
        )
        self.create_index()

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
            field_name="base_url",
            field_schema=models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                min_token_len=2,
                max_token_len=80,
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
