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

from src.rag_pipeline import RAGPipeline

rag = RAGPipeline(
    "data/faiss_index.bin",
    "data/faiss_metadata.json"
)

question = "How do attackers dump Windows credentials?"

answer = rag.generate_answer(question)

print("\nAnswer:\n")
print(answer)