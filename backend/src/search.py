import json
import os
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-large"


class SemanticSearcher:

    def __init__(self, index_path: str, metadata_path: str):
        self.index = faiss.read_index(index_path)

        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)

        metadata_dir = Path(metadata_path).resolve().parent
        documents_path = metadata_dir / "rag_documents.json"
        self.documents_by_id = {}

        if documents_path.exists():
            with open(documents_path, "r") as f:
                documents = json.load(f)
            self.documents_by_id = {
                document["id"]: document for document in documents
            }

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
                result = dict(self.metadata[idx])
                document = self.documents_by_id.get(result["id"])

                if document is not None:
                    result["content"] = document.get("content", "")

                results.append(result)

        return results
