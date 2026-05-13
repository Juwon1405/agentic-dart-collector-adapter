"""
manifest.json writer.

The manifest is the chain-of-custody seed for Agentic-DART:
- adapter_version identifies which adapter produced the layout
- file_count / total_bytes catch silent truncation
- sha256_index lets downstream tools verify integrity without re-reading the ZIP
"""
from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from .hash_indexer import compute_sha256_tree

MANIFEST_NAME = "manifest.json"
MANIFEST_VERSION = "1.0"


def write_manifest(
    evidence_root: str | Path,
    *,
    case_id: str,
    source_zip: str,
    files_copied: int,
    bytes_copied: int,
    categories: dict[str, int],
    skipped_count: int,
    include_sha256_index: bool = True,
) -> Path:
    """
    Write manifest.json under evidence_root and return its path.
    """
    root = Path(evidence_root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "case_id": case_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "zip": source_zip,
            "type": "velociraptor_offline_collector",
        },
        "host": {
            "os": platform.system(),
            "release": platform.release(),
            "python": platform.python_version(),
        },
        "adapter": {
            "name": "agentic-dart-collector-adapter",
            "version": "0.1.0",
        },
        "counters": {
            "files_copied": files_copied,
            "bytes_copied": bytes_copied,
            "files_skipped": skipped_count,
        },
        "categories": categories,
    }

    if include_sha256_index:
        manifest["sha256_index"] = {
            k: v for k, v in compute_sha256_tree(root).items()
            if k != MANIFEST_NAME
        }

    target = root / MANIFEST_NAME
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return target
