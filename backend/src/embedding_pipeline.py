import json
import os
import numpy as np
import faiss
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI


# ============================================
# Load environment variables
# ============================================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-large"


# ============================================
# Load RAG Documents
# ============================================

def load_documents(path: str):
    with open(path, "r") as f:
        return json.load(f)


# ============================================
# Generate Embeddings
# ============================================

def generate_embedding(text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def generate_all_embeddings(documents):
    embeddings = []
    metadata = []

    for doc in tqdm(documents, desc="Generating embeddings"):
        vector = generate_embedding(doc["content"])
        embeddings.append(vector)
        metadata.append({
            "id": doc["id"],
            "stix_id": doc["stix_id"],
            "metadata": doc["metadata"]
        })

    return np.array(embeddings).astype("float32"), metadata


# ============================================
# Build FAISS Index
# ============================================

def build_faiss_index(embeddings: np.ndarray):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


# ============================================
# Save Index + Metadata
# ============================================

def save_index(index, metadata, index_path, metadata_path):
    faiss.write_index(index, index_path)

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)


# ============================================
# Main Execution
# ============================================

if __name__ == "__main__":
    docs = load_documents("../data/rag_documents.json")

    embeddings, metadata = generate_all_embeddings(docs)

    index = build_faiss_index(embeddings)

    save_index(
        index,
        metadata,
        "../data/faiss_index.bin",
        "../data/faiss_metadata.json"
    )

    print("Embedding pipeline using FAISS complete.")