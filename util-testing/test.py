from qdrant_client.http import models
from qdrant_client import QdrantClient
import json
# from utils.doc_search import DocumentSearch
import os
import time
from dotenv import load_dotenv
load_dotenv()
# doc_search = DocumentSearch(url=os.getenv("QDRANT_URL"),
#                             api_key=os.getenv("QDRANT_API"),
#                             collection_name=os.getenv("QDRANT_COLLECTION"))

st = time.time()
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API"),
)
et = time.time()
res = et - st
print("Init time", res)
print(f"Connected to Qdrant : {os.getenv('QDRANT_COLLECTION')}", qdrant_client.count(
    collection_name="my_rec"))
et = time.time()
res = et - st
# time.sleep(3)
print("count time", res)
# doc_search.test()
# result = doc_search.get_search_result(
#     search_query="how to create experiments in vlabs",
#     thresh=0.20,
#     limit=5,
#     page_title_filter="content development platform")
# print(len(result))
# print(json.dumps(result, indent=4))


# doc_search.insert_doc(
#     type="md", url="https://github.com/virtual-labs/vlabs-systems/blob/main/src/systems-engineer-role/servers-compute-resources.md")
