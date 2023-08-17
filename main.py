from document_parser import get_chunks_from_github
from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer


encoder = SentenceTransformer('all-MiniLM-L6-v2')
url = "https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/user-doc.md"
data = get_chunks_from_github(url)
