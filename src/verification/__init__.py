"""Integrity Verification Module."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional


class IntegrityVerifier:
    """Verifies the integrity of custody chains and evidence hashes."""

    def verify_entry_chain(self, entries: List[Dict]) -> Dict:
        """Verify the hash chain of custody entries."""
        valid = True
        errors = []

        for i, entry in enumerate(entries):
            expected_prev = entries[i - 1].get("entry_hash") if i > 0 else None
            actual_prev = entry.get("previous_hash")

            if expected_prev != actual_prev:
                valid = False
                errors.append({
                    "entry_index": i,
                    "entry_id": entry.get("entry_id"),
                    "error": "Chain link broken",
                    "expected_previous_hash": expected_prev,
                    "actual_previous_hash": actual_prev,
                })

        return {
            "chain_valid": valid,
            "entries_verified": len(entries),
            "errors": errors,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

    def verify_evidence_hash(self, file_path: str, expected_hash: str) -> Dict:
        """Verify a file's hash matches the expected value."""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            current_hash = sha256.hexdigest()
            verified = current_hash == expected_hash

            return {
                "verified": verified,
                "expected_hash": expected_hash,
                "current_hash": current_hash,
                "file_path": file_path,
                "verified_at": datetime.now(timezone.utc).isoformat(),
            }
        except FileNotFoundError:
            return {
                "verified": False,
                "error": "File not found",
                "file_path": file_path,
            }

    def generate_integrity_report(self, custody_records: List[Dict]) -> Dict:
        """Generate an integrity report for multiple custody records."""
        results = []
        all_valid = True

        for record in custody_records:
            chain_result = self.verify_entry_chain(record.get("entries", []))
            if not chain_result["chain_valid"]:
                all_valid = False

            results.append({
                "evidence_id": record.get("evidence_id"),
                "chain_valid": chain_result["chain_valid"],
                "entries_verified": chain_result["entries_verified"],
                "errors": chain_result["errors"],
            })

        return {
            "report_type": "integrity_report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_valid": all_valid,
            "records_checked": len(results),
            "results": results,
        }
