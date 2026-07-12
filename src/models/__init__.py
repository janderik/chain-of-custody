"""Evidence Data Models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import hashlib
import json


@dataclass
class EvidenceItem:
    """Data model for a digital evidence item."""
    evidence_id: str
    case_id: str
    description: str
    collector: str
    collected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: int = 0
    file_type: str = ""
    state: str = "collected"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "evidence_id": self.evidence_id,
            "case_id": self.case_id,
            "description": self.description,
            "collector": self.collector,
            "collected_at": self.collected_at,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "state": self.state,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EvidenceItem":
        return cls(
            evidence_id=data["evidence_id"],
            case_id=data.get("case_id", ""),
            description=data.get("description", ""),
            collector=data.get("collector", ""),
            collected_at=data.get("collected_at", ""),
            file_path=data.get("file_path"),
            file_hash=data.get("file_hash"),
            file_size=data.get("file_size", 0),
            file_type=data.get("file_type", ""),
            state=data.get("state", "collected"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CustodyEntry:
    """A single entry in the chain of custody."""
    entry_id: str
    timestamp: str
    handler: str
    action: str
    location: str = ""
    notes: str = ""
    hash_value: Optional[str] = None
    previous_hash: Optional[str] = None
    entry_hash: str = ""

    def compute_hash(self) -> str:
        data = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "handler": self.handler,
            "action": self.action,
            "location": self.location,
            "notes": self.notes,
            "previous_hash": self.previous_hash,
        }
        content = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "handler": self.handler,
            "action": self.action,
            "location": self.location,
            "notes": self.notes,
            "hash_value": self.hash_value,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }


@dataclass
class Case:
    """Data model for a forensic case."""
    case_id: str
    title: str
    description: str
    investigator: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    state: str = "open"
    evidence_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "investigator": self.investigator,
            "created_at": self.created_at,
            "state": self.state,
            "evidence_count": len(self.evidence_items),
        }
