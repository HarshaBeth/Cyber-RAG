import json
import faiss
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-large"


class SemanticSearcher:

    def __init__(self, index_path: str, metadata_path: str):
        self.index = faiss.read_index(index_path)

        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)

    # ======================================
    # Embed Query
    # ======================================

    def embed_query(self, query: str):
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query
        )

        return np.array(response.data[0].embedding).astype("float32")

    # ======================================
    # Search
    # ======================================

    def search(self, query: str, top_k: int = 5):
        query_vector = self.embed_query(query)

        query_vector = np.expand_dims(query_vector, axis=0)

        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results