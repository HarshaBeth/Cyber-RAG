# from src.extractor import MitreExtractor
# from src.graph_builder import RelationshipGraph
# from src.rag_exporter import RAGDocumentExporter

# extractor = MitreExtractor("data/enterprise-attack.json")

# techniques = [extractor.clean_technique(t) for t in extractor.get_techniques()]
# groups = [extractor.clean_group(g) for g in extractor.get_groups()]
# malware = [extractor.clean_malware(m) for m in extractor.get_malware()]
# tools = [extractor.clean_tool(t) for t in extractor.get_tools()]
# mitigations = [extractor.clean_mitigation(m) for m in extractor.get_mitigations()]
# relationships = extractor.get_relationships()

# graph = RelationshipGraph(
#     relationships,
#     techniques,
#     groups,
#     malware,
#     tools,
#     mitigations
# )

# enriched = graph.enrich_techniques()

# exporter = RAGDocumentExporter(enriched)
# exporter.export("data/rag_documents.json")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  
from src.rag_pipeline import RAGPipeline

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGPipeline(
    index_path="data/faiss_index.bin",
    metadata_path="data/faiss_metadata.json"
)  

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/query", response_model=QueryResponse)
def query_rag(req: QueryRequest):
    question = req.question
    answer = rag.generate_answer(question)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)