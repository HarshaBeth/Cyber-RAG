import os
from dotenv import load_dotenv
from openai import OpenAI
from src.search import SemanticSearcher


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class RAGPipeline:

    def __init__(self, index_path, metadata_path):
        self.searcher = SemanticSearcher(index_path, metadata_path)

    # =====================================
    # Build Context from Retrieved Docs
    # =====================================

    def build_context(self, docs):
        context = ""

        for doc in docs:
            context += f"""
                        Technique ID: {doc["id"]}
                        Name: {doc["metadata"]["name"]}
                        Tactics: {doc["metadata"]["tactics"]}
                        Platforms: {doc["metadata"]["platforms"]}

                        """
        return context

    # =====================================
    # Generate Answer
    # =====================================

    def generate_answer(self, query: str):

        retrieved_docs = self.searcher.search(query, top_k=5)

        context = self.build_context(retrieved_docs)

        prompt = f"""
You are a cybersecurity expert using the MITRE ATT&CK framework.

Use the following ATT&CK knowledge to answer the user's question.

Context:
{context}

Question:
{query}

Provide a clear and concise explanation.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content