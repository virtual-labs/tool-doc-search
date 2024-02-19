from vertexai.language_models import TextEmbeddingModel
import vertexai
import os
import pathlib
from google.oauth2 import service_account


class Encoder:
    def __init__(self):
        SERVICE_ACCOUNT_FILE = os.path.join(
            pathlib.Path(__file__).parent, "../secrets/service-account-secret.json")
        SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        vertexai.init(project=os.getenv("GCP_PROJECT_ID"),
                      credentials=credentials, location="us-central1",)

        self.embedding_model = TextEmbeddingModel.from_pretrained(
            "textembedding-gecko@001")

        print("Initialized Vertex AI")

        # self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_size(self):
        # return self.model.get_sentence_embedding_dimension()
        return 768

    def encode(self, text_list):
        # embeddings = self.model.encode(
        #     text).tolist()
        embeddings = [
            embedding.values for embedding in self.embedding_model.get_embeddings(text_list)]
        return embeddings
