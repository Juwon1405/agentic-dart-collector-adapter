"""
SHA-256 file hashing helpers.

Used both to:
- pre-compute file hashes for downstream Agentic-DART audit chain entries, and
- support manifest.json integrity verification.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

_BUF_SIZE = 1024 * 1024  # 1 MiB


def compute_sha256(path: str | Path) -> str:
    """
    Compute the SHA-256 of the file at `path` and return the lowercase hex digest.
    Streams the file in 1 MiB chunks (no full-file load).
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"file not found: {p}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            chunk = f.read(_BUF_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def compute_sha256_tree(root: str | Path) -> dict[str, str]:
    """
    Recursively SHA-256 every regular file under `root`.
    Returns { relative_path_str: hex_digest }.
    """
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"not a directory: {root_path}")

    out: dict[str, str] = {}
    for p in sorted(root_path.rglob("*")):
        if p.is_file():
            try:
                rel = p.relative_to(root_path).as_posix()
            except ValueError:
                continue
            out[rel] = compute_sha256(p)
    return out
