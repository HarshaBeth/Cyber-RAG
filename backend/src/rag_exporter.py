import json
from typing import List, Dict, Any


class RAGDocumentExporter:
    def __init__(self, enriched_techniques: List[Dict[str, Any]]):
        self.enriched_techniques = enriched_techniques

    # =====================================================
    # Build Single RAG Document
    # =====================================================

    def build_document(self, technique: Dict[str, Any]) -> Dict[str, Any]:
        content = self._build_content_string(technique)

        return {
            "id": technique.get("technique_id"),
            "stix_id": technique.get("stix_id"),
            "content": content,
            "metadata": {
                "technique_id": technique.get("technique_id"),
                "name": technique.get("name"),
                "tactics": technique.get("tactics", []),
                "platforms": technique.get("platforms", []),
                "is_subtechnique": technique.get("is_subtechnique", False),
            }
        }

    # =====================================================
    # Format Content for LLM
    # =====================================================

    def _build_content_string(self, technique: Dict[str, Any]) -> str:
        sections = []

        sections.append(f"Technique ID: {technique.get('technique_id')}")
        sections.append(f"Name: {technique.get('name')}")
        sections.append(f"Tactics: {', '.join(technique.get('tactics', []))}")
        sections.append(f"Platforms: {', '.join(technique.get('platforms', []))}")
        sections.append("")
        sections.append("Description:")
        sections.append(technique.get("description", ""))

        # Relationships
        sections.append("")
        sections.append("Related Threat Groups:")
        sections.append(", ".join(technique.get("related_groups", [])) or "None")

        sections.append("")
        sections.append("Related Malware:")
        sections.append(", ".join(technique.get("related_malware", [])) or "None")

        sections.append("")
        sections.append("Related Tools:")
        sections.append(", ".join(technique.get("related_tools", [])) or "None")

        sections.append("")
        sections.append("Mitigations:")
        sections.append(", ".join(technique.get("related_mitigations", [])) or "None")

        return "\n".join(sections)

    # =====================================================
    # Build All Documents
    # =====================================================

    def build_all_documents(self) -> List[Dict[str, Any]]:
        return [
            self.build_document(technique)
            for technique in self.enriched_techniques
        ]

    # =====================================================
    # Export to JSON
    # =====================================================

    def export(self, output_path: str) -> None:
        documents = self.build_all_documents()

        with open(output_path, "w") as f:
            json.dump(documents, f, indent=2)

        print(f"Exported {len(documents)} RAG documents to {output_path}")