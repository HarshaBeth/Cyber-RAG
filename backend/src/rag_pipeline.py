import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from src.search import SemanticSearcher


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class RAGPipeline:

    def __init__(self, index_path, metadata_path, generation_model: str = "gpt-4o-mini"):
        self.searcher = SemanticSearcher(index_path, metadata_path)
        self.generation_model = generation_model

    # =====================================
    # Build Context from Retrieved Docs
    # =====================================

    def retrieve_documents(self, query: str, top_k: int = 5):
        return self.searcher.search(query, top_k=top_k)

    def build_context(self, docs):
        context_chunks = []

        for doc in docs:
            if doc.get("content"):
                context_chunks.append(doc["content"])
                continue

            context_chunks.append(
                "\n".join(
                    [
                        f"Technique ID: {doc['id']}",
                        f"Name: {doc['metadata']['name']}",
                        f"Tactics: {', '.join(doc['metadata']['tactics'])}",
                        f"Platforms: {', '.join(doc['metadata']['platforms'])}",
                    ]
                )
            )

        return "\n\n---\n\n".join(context_chunks)

    def build_prompt(self, query: str, context: str):
        return f"""
You are a cybersecurity expert using the MITRE ATT&CK framework.

Use the following ATT&CK knowledge to answer the user's question.

Context:
{context}

Question:
{query}

Provide a clear and concise explanation.

You are not allowed to answer with information that is not present in the context. If you don't know the answer, say you don't know.

You can only answer questions related to MITRE ATT&CK information provided in the context.
"""

    def complete_prompt(self, prompt: str):
        response = client.chat.completions.create(
            model=self.generation_model,
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    # =====================================
    # Generate Answer
    # =====================================

    def generate_answer(self, query: str, top_k: int = 5):
        retrieved_docs = self.retrieve_documents(query, top_k=top_k)
        context = self.build_context(retrieved_docs)
        prompt = self.build_prompt(query, context)
        return self.complete_prompt(prompt)

    def generate_answer_with_context(self, query: str, top_k: int = 5):
        retrieved_docs = self.retrieve_documents(query, top_k=top_k)
        context = self.build_context(retrieved_docs)
        prompt = self.build_prompt(query, context)
        answer = self.complete_prompt(prompt)

        return {
            "answer": answer,
            "context": context,
            "retrieved_docs": retrieved_docs,
        }
