import json
from typing import List, Dict, Any, Optional
from stix2 import MemoryStore, Filter


class MitreExtractor:
    def __init__(self, file_path: str):
        with open(file_path, "r") as f:
            stix_data = json.load(f)

        self.store = MemoryStore(stix_data=stix_data["objects"])

    # =====================================================
    # Core STIX Queries
    # =====================================================

    def get_techniques(self) -> List[Dict[str, Any]]:
        return self.store.query([
            Filter("type", "=", "attack-pattern")
        ])

    def get_groups(self) -> List[Dict[str, Any]]:
        return self.store.query([
            Filter("type", "=", "intrusion-set")
        ])

    def get_malware(self) -> List[Dict[str, Any]]:
        return self.store.query([
            Filter("type", "=", "malware")
        ])

    def get_tools(self) -> List[Dict[str, Any]]:
        return self.store.query([
            Filter("type", "=", "tool")
        ])

    def get_mitigations(self) -> List[Dict[str, Any]]:
        return self.store.query([
            Filter("type", "=", "course-of-action")
        ])

    def get_relationships(self) -> List[Dict[str, Any]]:
        return self.store.query([
            Filter("type", "=", "relationship")
        ])

    # =====================================================
    # Extraction Helpers
    # =====================================================

    def extract_external_id(self, obj: Dict[str, Any]) -> Optional[str]:
        if "external_references" in obj:
            for ref in obj["external_references"]:
                if ref.get("source_name") == "mitre-attack":
                    return ref.get("external_id")
        return None

    def extract_tactics(self, technique: Dict[str, Any]) -> List[str]:
        return [
            phase["phase_name"]
            for phase in technique.get("kill_chain_phases", [])
        ]

    def extract_platforms(self, technique: Dict[str, Any]) -> List[str]:
        return technique.get("x_mitre_platforms", [])

    def extract_data_sources(self, technique: Dict[str, Any]) -> List[str]:
        return technique.get("x_mitre_data_sources", [])

    # =====================================================
    # Cleaning / Structuring
    # =====================================================

    def clean_technique(self, technique: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "stix_id": technique.get("id"),
            "technique_id": self.extract_external_id(technique),
            "name": technique.get("name"),
            "description": technique.get("description"),
            "tactics": self.extract_tactics(technique),
            "platforms": self.extract_platforms(technique),
            "data_sources": self.extract_data_sources(technique),
            "is_subtechnique": technique.get("x_mitre_is_subtechnique", False),
        }

    def clean_group(self, group: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "stix_id": group.get("id"),
            "group_id": self.extract_external_id(group),
            "name": group.get("name"),
            "description": group.get("description"),
            "aliases": group.get("aliases", []),
        }

    def clean_malware(self, malware: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "stix_id": malware.get("id"),
            "malware_id": self.extract_external_id(malware),
            "name": malware.get("name"),
            "description": malware.get("description"),
            "platforms": malware.get("x_mitre_platforms", []),
        }

    def clean_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "stix_id": tool.get("id"),
            "tool_id": self.extract_external_id(tool),
            "name": tool.get("name"),
            "description": tool.get("description"),
            "platforms": tool.get("x_mitre_platforms", []),
        }

    def clean_mitigation(self, mitigation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "stix_id": mitigation.get("id"),
            "mitigation_id": self.extract_external_id(mitigation),
            "name": mitigation.get("name"),
            "description": mitigation.get("description"),
        }

    # =====================================================
    # Bulk Export Methods
    # =====================================================

    def export_cleaned_techniques(self, output_path: str) -> None:
        techniques = self.get_techniques()
        cleaned = [self.clean_technique(t) for t in techniques]

        with open(output_path, "w") as f:
            json.dump(cleaned, f, indent=2)

        print(f"Saved {len(cleaned)} techniques to {output_path}")

    def export_cleaned_groups(self, output_path: str) -> None:
        groups = self.get_groups()
        cleaned = [self.clean_group(g) for g in groups]

        with open(output_path, "w") as f:
            json.dump(cleaned, f, indent=2)

        print(f"Saved {len(cleaned)} groups to {output_path}")

    def export_cleaned_malware(self, output_path: str) -> None:
        malware = self.get_malware()
        cleaned = [self.clean_malware(m) for m in malware]

        with open(output_path, "w") as f:
            json.dump(cleaned, f, indent=2)

        print(f"Saved {len(cleaned)} malware entries to {output_path}")

    def export_cleaned_tools(self, output_path: str) -> None:
        tools = self.get_tools()
        cleaned = [self.clean_tool(t) for t in tools]

        with open(output_path, "w") as f:
            json.dump(cleaned, f, indent=2)

        print(f"Saved {len(cleaned)} tools to {output_path}")

    def export_cleaned_mitigations(self, output_path: str) -> None:
        mitigations = self.get_mitigations()
        cleaned = [self.clean_mitigation(m) for m in mitigations]

        with open(output_path, "w") as f:
            json.dump(cleaned, f, indent=2)

        print(f"Saved {len(cleaned)} mitigations to {output_path}")

    # =====================================================
    # Utility
    # =====================================================

    def get_object_by_stix_id(self, stix_id: str) -> Optional[Dict[str, Any]]:
        results = self.store.query([
            Filter("id", "=", stix_id)
        ])
        return results[0] if results else None