from collections import defaultdict
from typing import Dict, List, Any


class RelationshipGraph:
    def __init__(
        self,
        relationships: List[Dict[str, Any]],
        techniques: List[Dict[str, Any]],
        groups: List[Dict[str, Any]],
        malware: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        mitigations: List[Dict[str, Any]],
    ):
        # ID → name maps
        self.technique_map = {t["stix_id"]: t for t in techniques}
        self.group_map = {g["stix_id"]: g for g in groups}
        self.malware_map = {m["stix_id"]: m for m in malware}
        self.tool_map = {t["stix_id"]: t for t in tools}
        self.mitigation_map = {m["stix_id"]: m for m in mitigations}

        # Graph mappings
        self.technique_to_groups = defaultdict(list)
        self.technique_to_malware = defaultdict(list)
        self.technique_to_tools = defaultdict(list)
        self.technique_to_mitigations = defaultdict(list)

        self.group_to_techniques = defaultdict(list)
        self.malware_to_techniques = defaultdict(list)
        self.tool_to_techniques = defaultdict(list)

        self._build_graph(relationships)

    # =====================================================
    # Build Graph
    # =====================================================

    def _build_graph(self, relationships: List[Dict[str, Any]]) -> None:
        for rel in relationships:
            source = rel.get("source_ref")
            target = rel.get("target_ref")
            rel_type = rel.get("relationship_type")

            if not source or not target:
                continue

            # -------------------------------------------
            # "uses" Relationships
            # -------------------------------------------
            if rel_type == "uses":

                # Group → Technique
                if source in self.group_map and target in self.technique_map:
                    group_name = self.group_map[source]["name"]
                    technique_name = self.technique_map[target]["name"]

                    self.technique_to_groups[target].append(group_name)
                    self.group_to_techniques[source].append(technique_name)

                # Malware → Technique
                elif source in self.malware_map and target in self.technique_map:
                    malware_name = self.malware_map[source]["name"]
                    technique_name = self.technique_map[target]["name"]

                    self.technique_to_malware[target].append(malware_name)
                    self.malware_to_techniques[source].append(technique_name)

                # Tool → Technique
                elif source in self.tool_map and target in self.technique_map:
                    tool_name = self.tool_map[source]["name"]
                    technique_name = self.technique_map[target]["name"]

                    self.technique_to_tools[target].append(tool_name)
                    self.tool_to_techniques[source].append(technique_name)

            # -------------------------------------------
            # "mitigates" Relationships
            # -------------------------------------------
            elif rel_type == "mitigates":
                if source in self.mitigation_map and target in self.technique_map:
                    mitigation_name = self.mitigation_map[source]["name"]
                    self.technique_to_mitigations[target].append(mitigation_name)

    # =====================================================
    # Public Getters
    # =====================================================

    def get_technique_relationships(self, technique_stix_id: str) -> Dict[str, List[str]]:
        return {
            "groups": self.technique_to_groups.get(technique_stix_id, []),
            "malware": self.technique_to_malware.get(technique_stix_id, []),
            "tools": self.technique_to_tools.get(technique_stix_id, []),
            "mitigations": self.technique_to_mitigations.get(technique_stix_id, []),
        }

    def get_group_techniques(self, group_stix_id: str) -> List[str]:
        return self.group_to_techniques.get(group_stix_id, [])

    def get_malware_techniques(self, malware_stix_id: str) -> List[str]:
        return self.malware_to_techniques.get(malware_stix_id, [])

    def get_tool_techniques(self, tool_stix_id: str) -> List[str]:
        return self.tool_to_techniques.get(tool_stix_id, [])

    # =====================================================
    # Merge Relationships into Techniques (for RAG docs)
    # =====================================================

    def enrich_techniques(self) -> List[Dict[str, Any]]:
        enriched = []

        for stix_id, technique in self.technique_map.items():
            relationships = self.get_technique_relationships(stix_id)

            enriched_doc = {
                **technique,
                "related_groups": relationships["groups"],
                "related_malware": relationships["malware"],
                "related_tools": relationships["tools"],
                "related_mitigations": relationships["mitigations"],
            }

            enriched.append(enriched_doc)

        return enriched