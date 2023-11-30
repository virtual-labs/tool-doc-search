import os
from dotenv import load_dotenv
from utils.doc_search import DocumentSearch
from utils.doc_record import DocumentRecord
load_dotenv()

doc_record = DocumentRecord(url=os.getenv("QDRANT_URL"),
                            api_key=os.getenv(
    "QDRANT_API"),
    collection_name=os.getenv("QDRANT_RECORD_COLLECTION"),
    folder_collection_name=os.getenv("QDRANT_FOLDER_COLLECTION"))

doc_search = DocumentSearch(url=os.getenv("QDRANT_URL"),
                            api_key=os.getenv("QDRANT_API"),
                            collection_name=os.getenv("QDRANT_COLLECTION"),
                            doc_record=doc_record)
