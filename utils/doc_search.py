from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from utils.document_parser import get_chunks_batch, get_doc_urls_from_drive
import uuid
from error.CustomException import CustomException
from utils.document_parser import get_formatted_google_url
import re
import json
import datetime
from utils.delete_doc_util import delete_document_chunks


class DocumentSearch:

    def __init__(self, url, api_key, collection_name, doc_record=None) -> None:
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant_client = QdrantClient(
            url=url,
            api_key=api_key,
        )

        self.doc_record = doc_record

        self.collection_name = collection_name

        # self.reset_database()

        print(f"Connected to Qdrant : {collection_name}", self.qdrant_client.count(
            collection_name=collection_name))
        print("Document Search Initialized...")

    def reset_database(self):
        # recreate db
        print("Recreating database")
        self.qdrant_client.recreate_collection(
            collection_name=f"{self.collection_name}",
            vectors_config=models.VectorParams(
                size=self.encoder.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        )
        self.create_index()

    def batched(self, arr, batch_size):
        batches = [arr[i:i + batch_size]
                   for i in range(0, len(arr), batch_size)]
        return batches

    def upsert_batchs(self, ids, payloads, vectors, doc_chunk_idx):
        batch_size = 25
        ids = self.batched(ids, batch_size)
        payloads = self.batched(payloads, batch_size)
        vectors = self.batched(vectors, batch_size)
        batch_num = len(ids)
        current_idx = 0
        completed_chunks = 0
        for i in range(batch_num):
            try:
                print("Upserting batch", i+1)
                # if i == 0:
                #     raise Exception("write operation timed out")
                self.qdrant_client.upsert(
                    collection_name=f"{self.collection_name}",
                    points=models.Batch(
                        ids=ids[i],
                        payloads=payloads[i],
                        vectors=vectors[i]
                    ),
                )
                print("Upserted batch", i+1)
                completed_chunks += len(ids[i])
                while (completed_chunks >= doc_chunk_idx[current_idx].get("r", 1000000000)):
                    current_idx += 1
            except Exception as e:
                print(e)
                return current_idx
        return current_idx

    def insert_doc_batch(self, docs, credentials, user="unknown", operation="insert"):
        try:
            print("Getting document chunks for batch request from user :", user)
            data, base_urls, document_parse_error_url, doc_chunk_idx = get_chunks_batch(
                docs, credentials, user)
            print(len(data))
            print(json.dumps(base_urls, indent=4))
            print(json.dumps(document_parse_error_url, indent=4))
            print(json.dumps(doc_chunk_idx, indent=4))
            # return []
            if len(data):
                print("Deleting docs")
                self.qdrant_client.delete(
                    collection_name=f"{self.collection_name}",
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            should=[
                                models.FieldCondition(
                                    key="base_url",
                                    match=models.MatchValue(value=base_url),
                                ) for base_url in base_urls
                            ]
                        )
                    ),
                )
                print("Deleted docs")
                payloads = []
                vectors = []
                ids = []
                print("Encoding docs")
                for chunk in data:
                    # print(chunk)
                    ids.append(uuid.uuid4().int >> 64)
                    vectors.append(self.encoder.encode(
                        chunk["content"]).tolist())
                    payloads.append(chunk["payload"])
                print("Encoded docs")
                print("Upserting docs")
                upserted_till = self.upsert_batchs(
                    ids, payloads, vectors, doc_chunk_idx)
                print(upserted_till)

                unsuccessful_docs = []
                while upserted_till < len(doc_chunk_idx):
                    unsuccessful_docs.append(
                        doc_chunk_idx[upserted_till].get("url"))
                    upserted_till += 1

                print("Upserted docs")

                records = []
                results = []
                current_time = datetime.datetime.now()
                if len(unsuccessful_docs) and unsuccessful_docs[0] == data[0]["payload"]["base_url"]:
                    pass
                else:
                    results.append({
                        "page_title": data[0]["payload"]["page_title"],
                        "base_url": data[0]["payload"]["base_url"],
                        "sections": 1,
                        "accessibility": data[0]["payload"]["accessibility"]
                    })
                    records.append({
                        "page_title": data[0]["payload"]["page_title"],
                        "base_url": data[0]["payload"]["base_url"],
                        "accessibility": data[0]["payload"]["accessibility"],
                        "type": data[0]["payload"]["type"],
                        "created_by": user,
                        "created_at": current_time,
                        "updated_by": user,
                        "last_updated": current_time
                    })

                for i in range(1, len(data)):
                    if len(unsuccessful_docs) and unsuccessful_docs[0] == data[i]["payload"]["base_url"]:
                        break
                    if data[i]["payload"]["base_url"] == results[-1]["base_url"]:
                        results[-1]["sections"] += 1
                    else:
                        results.append({
                            "page_title": data[i]["payload"]["page_title"],
                            "base_url": data[i]["payload"]["base_url"],
                            "sections": 1,
                            "accessibility": data[i]["payload"]["accessibility"]
                        })
                        records.append({
                            "page_title": data[i]["payload"]["page_title"],
                            "base_url": data[i]["payload"]["base_url"],
                            "accessibility": data[i]["payload"]["accessibility"],
                            "type": data[i]["payload"]["type"],
                            "created_by": user,
                            "created_at": current_time,
                            "updated_by": user,
                            "last_updated": current_time
                        })

                records = list(filter(lambda record: record.get(
                    "type", "dir") != "dir", records))

                self.doc_record.insert_entry(records, operation=operation)
                resultObj = {
                    "message": f"Document{'s' if len(results) > 1 else ''} upserted successfully", "result": results,
                    "unsuccessful_upsertions": unsuccessful_docs,
                    "document_parse_error_url": document_parse_error_url
                }
                print(json.dumps(resultObj, indent=4))

                return resultObj
            else:
                resultObj = {
                    "error": f"", "message": "Document(s) have no headings.",
                    "document_parse_error_url": document_parse_error_url
                }
                return resultObj
        except Exception as e:
            print(e)
            raise e

    def insert_drive_folder(self, folder, credentials, user="unknown", operation="insert"):
        try:
            folderUrl = folder.get("folderURL")

            urls, name, accessibility = get_doc_urls_from_drive(
                folderUrl, credentials)

            if not folder.get("insertFiles", True):
                urls = []

            records = []
            current_time = datetime.datetime.now()
            match = re.search(r'/folders/([a-zA-Z0-9_-]+)', folderUrl)
            if match:
                doc_id = match.group(1)
                folderUrl = get_formatted_google_url(doc_id, "folder")

            name = folder.get("folderName", None) if folder.get(
                "folderName", None) else name

            urls.append({"url": folderUrl,
                         "type": "dir",
                         "accessibility": accessibility,
                         "page_title": name, })

            records.append({
                "folder_name": name,
                "base_url": folderUrl,
                "accessibility": accessibility,
                "created_by": user,
                "created_at": current_time,
                "updated_by": user,
                "last_updated": current_time,
                "files": urls,
                "dir": 1
            })
            print(records)
            self.doc_record.insert_folder_entry(records, operation=operation)
            self.doc_record.insert_entry(records, operation=operation)

            print(json.dumps(urls, indent=4))
            print(len(urls))

            return self.insert_doc_batch(
                docs=urls, credentials=credentials, user=user, operation="insert")
        except Exception as e:
            raise e

    def delete_doc(self, urls, user="unknown"):
        # print("indelete_doc")
        # return jsonify({})
        try:
            print(
                f"Deleting documents {json.dumps(urls, indent=4)} request from user :", user)
            if len(urls):
                delete_document_chunks(urls=urls, qdrant_client=self.qdrant_client, collection_name=self.collection_name,
                                       record_collection_name=self.doc_record.collection_name, models=models)
            else:
                return ("No valid document.")
        except Exception as e:
            raise e

    def get_search_result(self, search_query,
                          limit=10,
                          thresh=0.0,
                          doc_filter="Any",
                          src_filter="Any",
                          acc_filter="Any",
                          page_title_filter=""):
        try:

            if search_query == '' and page_title_filter == '':
                return []
            print("Building filters")
            page_title_filter = page_title_filter.strip()

            must_conditions = []
            if (doc_filter != 'Any'):
                must_conditions.append(models.FieldCondition(
                    key="type",  match=models.MatchValue(value=doc_filter)))

            if (src_filter != 'Any'):
                must_conditions.append(models.FieldCondition(
                    key="src",  match=models.MatchValue(value=src_filter)))

            if (acc_filter != 'Any'):
                must_conditions.append(models.FieldCondition(
                    key="accessibility",  match=models.MatchValue(value=acc_filter)))

            if (page_title_filter != ''):
                must_conditions.append(models.FieldCondition(
                    key="page_title",
                    match=models.MatchText(text=page_title_filter)
                ))

            filter_condition = doc_filter != 'Any' or src_filter != "Any" or acc_filter != "Any" or page_title_filter != ""

            filter = models.Filter(
                must=must_conditions
            ) if filter_condition else None
            print("Filters build")

            hits = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=self.encoder.encode(
                    search_query or page_title_filter).tolist(),
                limit=int(limit),
                query_filter=filter,
                score_threshold=thresh
            )
            print("Got search results", len(hits))
            search_results = []
            for hit in hits:
                parsed_text = hit.payload["text"].split("::")
                if len(parsed_text) > 2:
                    parsed_text = parsed_text[2].strip()
                else:
                    parsed_text = hit.payload["text"]
                search_results.append({
                    "accessibility": hit.payload["accessibility"],
                    "type": hit.payload["type"],
                    "url": hit.payload["url"],
                    "base_url": hit.payload["base_url"],
                    "score": hit.score,
                    "heading": hit.payload["heading"],
                    "document": hit.payload["page_title"],
                    "src": hit.payload["src"],
                    "text": str(parsed_text),
                })
            # print(json.dumps(search_results, indent=4))
            print("Search Results for", page_title_filter,
                  search_query, len(search_results))
            return search_results
        except Exception as e:
            print(e)
            raise CustomException(str(e), 500)

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
        # for doc in docs:
        #     self.insert_doc(type=doc["type"], url=doc["url"])
