# Chain of Custody

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![API](https://img.shields.io/badge/API-REST-blue)]()

A digital evidence chain of custody tracking system for maintaining integrity and accountability throughout the evidence lifecycle.

## Architecture

```
chain-of-custody/
├── src/
│   ├── custody/         # Core custody engine
│   ├── models/          # Evidence data models
│   ├── verification/    # Integrity verification
│   └── api/             # REST API
├── tests/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── setup.py
```

## Features

- **Chain of Custody Tracking**: Complete audit trail from collection to disposition
- **Digital Signatures**: Cryptographic signing of custody transfers
- **Integrity Verification**: SHA-256 hash chain for tamper detection
- **Multi-Stakeholder Support**: Track handlers, analysts, and custodians
- **Evidence States**: Full lifecycle state machine
- **REST API**: Programmatic access to custody records
- **Audit Reports**: Generate compliance audit reports
- **Immutable Ledger**: Append-only custody records

## Chain of Custody Concepts

### What is Chain of Custody?

Chain of custody is the chronological documentation of the seizure, custody, control, transfer, analysis, and disposition of evidence. It ensures that evidence is what it claims to be and has not been altered.

### Legal Requirements

1. **Documentation**: Every transfer must be documented
2. **Identification**: Evidence must be uniquely identified
3. **Integrity**: Evidence must be verified as unaltered
4. **Accountability**: Every handler must be identified
5. **Continuity**: Gaps in custody can invalidate evidence

### Evidence Lifecycle

```
Collection → Submission → Analysis → Storage → Presentation → Disposition
    |            |           |          |            |              |
    v            v           v          v            v              v
  [Handler]  [Custodian] [Analyst] [Storage]    [Court]      [Destroyed]
  [Hash]     [Hash]      [Hash]    [Hash]      [Hash]       [Certified]
```

### Integrity Verification

- **Initial Hash**: SHA-256 computed at collection
- **Transfer Hash**: Re-verified at each transfer point
- **Periodic Verification**: Scheduled integrity checks
- **Alert on Tamper**: Any hash mismatch triggers immediate alert

## Installation

```bash
git clone https://github.com/janderik/chain-of-custody.git
cd chain-of-custody
pip install -r requirements.txt
pip install -e .
```

## Usage

### REST API

```bash
# Create custody record
curl -X POST http://localhost:5000/api/v1/custody \
  -H "Content-Type: application/json" \
  -d '{"evidence_id":"EV-001","handler":"John Doe","action":"collected"}'

# Transfer custody
curl -X POST http://localhost:5000/api/v1/custody/EV-001/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_handler":"John Doe","to_handler":"Jane Smith","notes":"Lab transfer"}'

# Verify integrity
curl -X POST http://localhost:5000/api/v1/custody/EV-001/verify

# Get full chain
curl http://localhost:5000/api/v1/custody/EV-001/chain
```

### Python API

```python
from src.custody.engine import ChainOfCustody

coc = ChainOfCustody()
coc.create_record(evidence_id="EV-001", handler="John Doe")
coc.transfer(evidence_id="EV-001", from_handler="John Doe", to_handler="Jane Smith")
coc.verify_integrity(evidence_id="EV-001")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.
