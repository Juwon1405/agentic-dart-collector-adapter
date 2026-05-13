"""
agentic-dart-collector-adapter
==============================

Convert Velociraptor IR collector output into the evidence_root layout
expected by Agentic-DART (https://github.com/Juwon1405/agentic-dart).

Public surface
--------------
- adapt(velociraptor_zip, output_evidence_root, case_id=None)
- write_manifest(evidence_root, case_id=None)
- compute_sha256(path)

Stdlib-only by design.
"""
from .adapter import adapt
from .manifest import write_manifest
from .hash_indexer import compute_sha256

__version__ = "0.1.0"
__all__ = ["adapt", "write_manifest", "compute_sha256", "__version__"]
