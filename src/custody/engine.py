"""Chain of Custody Core Engine - Manages evidence custody tracking."""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class CustodyRecord:
    """Represents a chain of custody record for an evidence item."""

    def __init__(self, evidence_id: str, description: str = ""):
        self.evidence_id = evidence_id
        self.description = description
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.entries: List[Dict] = []
        self.current_handler = None
        self.state = "registered"
        self.initial_hash = None
        self.current_hash = None

    def add_entry(self, handler: str, action: str, location: str = "",
                  notes: str = "", hash_value: str = None):
        entry = {
            "entry_id": uuid.uuid4().hex[:12],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "handler": handler,
            "action": action,
            "location": location,
            "notes": notes,
            "hash": hash_value,
            "previous_entry_hash": self._get_last_entry_hash(),
        }
        entry["entry_hash"] = self._compute_entry_hash(entry)
        self.entries.append(entry)

        if hash_value and not self.initial_hash:
            self.initial_hash = hash_value
        if hash_value:
            self.current_hash = hash_value

        self.current_handler = handler

        state_map = {
            "collected": "in_custody",
            "submitted": "in_custody",
            "transferred": "in_transit",
            "received": "in_custody",
            "analyzing": "under_analysis",
            "analyzed": "analyzed",
            "stored": "archived",
            "released": "released",
            "destroyed": "destroyed",
        }
        self.state = state_map.get(action, self.state)

    def verify_integrity(self) -> Dict:
        if not self.current_hash:
            return {"verified": True, "note": "No hash to verify"}

        chain_valid = True
        for i, entry in enumerate(self.entries):
            expected = self._compute_entry_hash(entry, skip_hash=True)
            if entry.get("entry_hash") != expected:
                chain_valid = False
                break

        return {
            "evidence_id": self.evidence_id,
            "chain_valid": chain_valid,
            "entries_count": len(self.entries),
            "current_hash": self.current_hash,
            "initial_hash": self.initial_hash,
            "tampered": not chain_valid,
        }

    def _get_last_entry_hash(self) -> Optional[str]:
        if self.entries:
            return self.entries[-1].get("entry_hash")
        return None

    def _compute_entry_hash(self, entry: Dict, skip_hash: bool = False) -> str:
        data = {
            "entry_id": entry["entry_id"],
            "timestamp": entry["timestamp"],
            "handler": entry["handler"],
            "action": entry["action"],
            "location": entry.get("location", ""),
            "notes": entry.get("notes", ""),
            "previous_entry_hash": entry.get("previous_entry_hash"),
        }
        content = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "evidence_id": self.evidence_id,
            "description": self.description,
            "created_at": self.created_at,
            "state": self.state,
            "current_handler": self.current_handler,
            "initial_hash": self.initial_hash,
            "current_hash": self.current_hash,
            "entries": self.entries,
            "entries_count": len(self.entries),
        }


class ChainOfCustody:
    """Core chain of custody management system."""

    def __init__(self, storage_dir: str = "./custody_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.records: Dict[str, CustodyRecord] = {}
        self._load_existing()

    def create_record(self, evidence_id: str, description: str = "",
                      handler: str = "", file_path: str = None, **kwargs) -> CustodyRecord:
        record = CustodyRecord(evidence_id, description)

        hash_value = None
        if file_path and os.path.exists(file_path):
            hash_value = self._compute_file_hash(file_path)

        record.add_entry(
            handler=handler,
            action="collected",
            notes=f"Evidence registered. {description}",
            hash_value=hash_value,
        )

        self.records[evidence_id] = record
        self._persist_record(record)
        return record

    def transfer(self, evidence_id: str, from_handler: str, to_handler: str,
                 location: str = "", notes: str = "") -> bool:
        record = self.records.get(evidence_id)
        if not record:
            return False

        record.add_entry(
            handler=to_handler,
            action="transferred",
            location=location,
            notes=f"Transferred from {from_handler}. {notes}",
        )
        self._persist_record(record)
        return True

    def receive(self, evidence_id: str, handler: str, notes: str = "") -> bool:
        record = self.records.get(evidence_id)
        if not record:
            return False

        record.add_entry(handler=handler, action="received", notes=notes)
        self._persist_record(record)
        return True

    def analyze(self, evidence_id: str, handler: str, notes: str = "") -> bool:
        record = self.records.get(evidence_id)
        if not record:
            return False

        record.add_entry(handler=handler, action="analyzing", notes=notes)
        self._persist_record(record)
        return True

    def get_chain(self, evidence_id: str) -> Optional[Dict]:
        record = self.records.get(evidence_id)
        return record.to_dict() if record else None

    def verify_integrity(self, evidence_id: str) -> Optional[Dict]:
        record = self.records.get(evidence_id)
        return record.verify_integrity() if record else None

    def search_records(self, query: str) -> List[Dict]:
        results = []
        query_lower = query.lower()
        for record in self.records.values():
            data = json.dumps(record.to_dict(), default=str).lower()
            if query_lower in data:
                results.append(record.to_dict())
        return results

    def get_audit_report(self, evidence_id: str = None) -> Dict:
        records = [self.records[evidence_id].to_dict()] if evidence_id else [
            r.to_dict() for r in self.records.values()
        ]

        return {
            "report_type": "custody_audit",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_records": len(records),
            "records": records,
            "integrity_summary": {
                "total_entries": sum(r.get("entries_count", 0) for r in records),
            },
        }

    def _compute_file_hash(self, filepath: str) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _persist_record(self, record: CustodyRecord):
        filepath = self.storage_dir / f"{record.evidence_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2)

    def _load_existing(self):
        for filepath in self.storage_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                record = CustodyRecord(data["evidence_id"], data.get("description", ""))
                record.created_at = data.get("created_at", record.created_at)
                record.state = data.get("state", "registered")
                record.current_handler = data.get("current_handler")
                record.initial_hash = data.get("initial_hash")
                record.current_hash = data.get("current_hash")
                record.entries = data.get("entries", [])
                self.records[record.evidence_id] = record
            except (json.JSONDecodeError, KeyError):
                continue
