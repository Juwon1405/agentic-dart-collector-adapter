"""Tests for hash_indexer.compute_sha256 / compute_sha256_tree."""
import hashlib
from pathlib import Path

import pytest

from dart_collector_adapter.hash_indexer import compute_sha256, compute_sha256_tree


def test_compute_sha256_matches_hashlib(tmp_path: Path):
    p = tmp_path / "x.bin"
    payload = b"agentic-dart-collector-adapter unit test\n" * 100
    p.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()
    assert compute_sha256(p) == expected


def test_compute_sha256_streams_large_file(tmp_path: Path):
    """Stream a 4 MiB file (larger than 1 MiB buffer) and confirm digest is stable."""
    p = tmp_path / "big.bin"
    data = b"\xab" * (4 * 1024 * 1024 + 17)
    p.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    assert compute_sha256(p) == expected


def test_compute_sha256_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        compute_sha256(tmp_path / "does-not-exist")


def test_compute_sha256_tree_indexes_files(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.txt").write_bytes(b"hello\n")
    (tmp_path / "b.txt").write_bytes(b"world\n")
    index = compute_sha256_tree(tmp_path)
    assert "a/x.txt" in index
    assert "b.txt" in index
    assert index["a/x.txt"] == hashlib.sha256(b"hello\n").hexdigest()
    assert index["b.txt"] == hashlib.sha256(b"world\n").hexdigest()


def test_compute_sha256_tree_rejects_non_directory(tmp_path: Path):
    f = tmp_path / "not-a-dir.txt"
    f.write_text("hi")
    with pytest.raises(NotADirectoryError):
        compute_sha256_tree(f)
