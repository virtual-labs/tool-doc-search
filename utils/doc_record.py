from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import uuid
from error.CustomException import CustomException
from flask import jsonify
import json
import random


class DocumentRecord:

    def __init__(self, url, api_key, collection_name, folder_collection_name) -> None:
        self.qdrant_client = QdrantClient(
            url=url,
            api_key=api_key,
        )

        self.collection_name = collection_name
        self.folder_collection_name = folder_collection_name

        # self.reset_database()

        print(f"Connected to Qdrant : {collection_name}", self.qdrant_client.count(
            collection_name=collection_name))
        print("Document Record Initialized...")

        print(f"Connected to Qdrant : {folder_collection_name}", self.qdrant_client.count(
            collection_name=folder_collection_name))
        print("Folder Record Initialized...")

    def insert_entry(self, docs, operation="insert"):
        print("Upserting entries in Record DB")
        try:
            if len(docs):
                filter = models.Filter(
                    should=[
                        models.FieldCondition(
                            key="base_url",
                            match=models.MatchValue(
                                value=doc["base_url"]),
                        ) for doc in docs
                    ]
                )

                print(operation)
                if operation == "update":
                    hits = self.qdrant_client.search(
                        collection_name=self.collection_name,
                        query_vector=[0.5, 0.5, 0.5, 0.5],
                        with_vectors=False,
                        with_payload=["created_by", "created_at", "base_url"],
                        score_threshold=0.0,
                        query_filter=filter
                    )
                    search_results = []
                    for hit in hits:
                        search_results.append({
                            "created_by": hit.payload["created_by"],
                            "created_at": hit.payload["created_at"],
                            "base_url": hit.payload["base_url"]
                        })
                    for doc in docs:
                        for result in search_results:
                            if doc["base_url"] == result["base_url"]:
                                doc["created_by"] = result["created_by"]
                                doc["created_at"] = result["created_at"]
                                break

                returnval = self.qdrant_client.delete(
                    collection_name=f"{self.collection_name}",
                    points_selector=models.FilterSelector(
                        filter=filter,
                    ))
                print(returnval)
                print("Records")
                print(json.dumps(
                    [doc["base_url"] for doc in docs], indent=4))
                print("Deleted records")
                payloads = []
                vectors = []
                ids = []
                for chunk in docs:
                    ids.append(uuid.uuid4().int >> 64)
                    vectors.append(
                        [random.random() for i in range(4)])
                    payloads.append(chunk)
                self.qdrant_client.upsert(
                    collection_name=f"{self.collection_name}",
                    points=models.Batch(
                        ids=ids,
                        payloads=payloads,
                        vectors=vectors
                    ),
                )
                print("Inserted new record")
                return "success"
            else:
                raise Exception("No valid document.")
        except Exception as e:
            print(e)
            raise e

    def insert_folder_entry(self, docs, operation="insert"):
        print("Upserting entries in Folder DB")
        try:
            if len(docs):
                filter = models.Filter(
                    should=[
                        models.FieldCondition(
                            key="base_url",
                            match=models.MatchValue(
                                value=doc["base_url"]),
                        ) for doc in docs
                    ]
                )

                print(operation)
                if operation == "update":
                    hits = self.qdrant_client.search(
                        collection_name=self.folder_collection_name,
                        query_vector=[0.5, 0.5, 0.5, 0.5],
                        with_vectors=False,
                        with_payload=["created_by", "created_at", "base_url"],
                        score_threshold=0.0,
                        query_filter=filter
                    )
                    search_results = []
                    for hit in hits:
                        search_results.append({
                            "created_by": hit.payload["created_by"],
                            "created_at": hit.payload["created_at"],
                            "base_url": hit.payload["base_url"]
                        })
                    for doc in docs:
                        for result in search_results:
                            if doc["base_url"] == result["base_url"]:
                                doc["created_by"] = result["created_by"]
                                doc["created_at"] = result["created_at"]
                                break

                returnval = self.qdrant_client.delete(
                    collection_name=f"{self.folder_collection_name}",
                    points_selector=models.FilterSelector(
                        filter=filter,
                    ))
                print(returnval)
                print("Records")
                print(json.dumps(
                    [doc["base_url"] for doc in docs], indent=4))
                print("Deleted folder records")
                payloads = []
                vectors = []
                ids = []
                for chunk in docs:
                    ids.append(uuid.uuid4().int >> 64)
                    vectors.append(
                        [random.random() for i in range(4)])
                    payloads.append(chunk)
                self.qdrant_client.upsert(
                    collection_name=f"{self.folder_collection_name}",
                    points=models.Batch(
                        ids=ids,
                        payloads=payloads,
                        vectors=vectors
                    ),
                )
                print("Inserted new folder record")
                return "success"
            else:
                raise Exception("No valid document.")
        except Exception as e:
            print(e)
            raise e

    def delete_entry(self, docs):
        print("Deleting entries in Record DB")
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
                                        value=doc),
                                ) for doc in docs
                            ]
                        )
                    ),
                )
                print("Records")
                print(json.dumps(
                    docs, indent=4))
                print("Deleted records")
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

    def get_docs(self, search_query, page):
        print("Searching Record DB for search_query=",
              search_query, "page=", page)

        page_size = 10

        try:
            page = int(page)
            search_query = "" if search_query == None else search_query
            filter = models.Filter(
                should=[models.FieldCondition(
                    key="page_title",
                    match=models.MatchText(text=search_query.strip())
                ), models.FieldCondition(
                    key="folder_name",
                    match=models.MatchText(text=search_query.strip())
                )]
            ) if search_query.strip() else None
            # print(3, (page-1)*3)

            hits = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=[0.5, 0.5, 0.5, 0.5],
                with_vectors=True,
                with_payload=True,
                limit=page_size,
                offset=(page-1)*page_size,
                score_threshold=0.0,
                query_filter=filter
            )
            search_results = []
            for hit in hits:
                search_results.append({
                    "accessibility": hit.payload["accessibility"],
                    "type": hit.payload.get("type", "dir"),
                    "base_url": hit.payload["base_url"],
                    "page_title": hit.payload.get("page_title", hit.payload.get("folder_name", "unknown")),
                    "updated_by": hit.payload["updated_by"],
                    "last_updated": hit.payload["last_updated"],
                    "dir": hit.payload.get("dir", 0),
                })
            print(f"Returning results for {search_query} : ", len(
                search_results))
            if page == 1:
                count = self.qdrant_client.count(
                    collection_name=self.collection_name,
                    count_filter=models.Filter(
                        must=[models.FieldCondition(
                            key="page_title",
                            match=models.MatchText(text=search_query.strip())
                        )]
                    ) if search_query.strip() != "" else None,
                    exact=True,)
                print(count)
                return {"search_results": search_results, "count": int(str(count).split("=")[1]), "page_size": page_size}

            return {"search_results": search_results}
        except Exception as e:
            raise CustomException(str(e), 500)

    def reset_database(self):
        # recreate db
        print("Recreating record database")
        self.qdrant_client.recreate_collection(
            collection_name=f"{self.collection_name}",
            vectors_config=models.VectorParams(
                size=4,
                distance=models.Distance.COSINE
            )
        )

        self.qdrant_client.recreate_collection(
            collection_name=f"{self.folder_collection_name}",
            vectors_config=models.VectorParams(
                size=4,
                distance=models.Distance.COSINE
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
        self.qdrant_client.create_payload_index(
            collection_name=f"{self.collection_name}",
            field_name="folder_name",
            field_schema=models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                min_token_len=2,
                max_token_len=15,
                lowercase=True,
            )
        )
