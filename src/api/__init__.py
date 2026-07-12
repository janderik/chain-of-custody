"""Chain of Custody REST API."""

try:
    from flask import Flask, request, jsonify
except ImportError:
    Flask = None

from datetime import datetime, timezone
from src.custody.engine import ChainOfCustody
from src.verification import IntegrityVerifier


def create_app(storage_dir: str = "./custody_data"):
    if Flask is None:
        raise ImportError("Flask required")

    app = Flask(__name__)
    coc = ChainOfCustody(storage_dir=storage_dir)
    verifier = IntegrityVerifier()

    @app.route("/api/v1/custody", methods=["POST"])
    def create_record():
        data = request.get_json()
        record = coc.create_record(
            evidence_id=data.get("evidence_id", ""),
            description=data.get("description", ""),
            handler=data.get("handler", ""),
            file_path=data.get("file_path"),
        )
        return jsonify(record.to_dict()), 201

    @app.route("/api/v1/custody/<evidence_id>", methods=["GET"])
    def get_record(evidence_id):
        chain = coc.get_chain(evidence_id)
        if not chain:
            return jsonify({"error": "Not found"}), 404
        return jsonify(chain)

    @app.route("/api/v1/custody/<evidence_id>/transfer", methods=["POST"])
    def transfer_custody(evidence_id):
        data = request.get_json()
        success = coc.transfer(
            evidence_id=evidence_id,
            from_handler=data.get("from_handler", ""),
            to_handler=data.get("to_handler", ""),
            location=data.get("location", ""),
            notes=data.get("notes", ""),
        )
        if not success:
            return jsonify({"error": "Record not found"}), 404
        return jsonify({"status": "transferred", "evidence_id": evidence_id})

    @app.route("/api/v1/custody/<evidence_id>/verify", methods=["POST"])
    def verify(evidence_id):
        result = coc.verify_integrity(evidence_id)
        if not result:
            return jsonify({"error": "Not found"}), 404
        return jsonify(result)

    @app.route("/api/v1/custody/<evidence_id>/chain", methods=["GET"])
    def get_chain(evidence_id):
        chain = coc.get_chain(evidence_id)
        if not chain:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"chain": chain})

    @app.route("/api/v1/custody/search", methods=["GET"])
    def search():
        query = request.args.get("q", "")
        results = coc.search_records(query)
        return jsonify({"results": results, "total": len(results)})

    @app.route("/api/v1/audit", methods=["GET"])
    def audit():
        report = coc.get_audit_report()
        return jsonify(report)

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()})

    return app
