"""End-to-end adapter tests using a synthetic Velociraptor-shaped ZIP."""
import json
import zipfile
from pathlib import Path

import pytest

from dart_collector_adapter import adapt
from dart_collector_adapter.adapter import _safe_target_path


@pytest.fixture()
def velo_zip(tmp_path: Path) -> Path:
    """Build a tiny ZIP that mimics a Velociraptor offline-collector output."""
    z = tmp_path / "case_synthetic.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("uploads/auto/C:/Windows/Prefetch/SVCHOST.EXE-ABC.pf", b"PF\x00\x00fake")
        zf.writestr("uploads/auto/C:/Windows/AppCompat/Programs/Amcache.hve", b"AMCACHE")
        zf.writestr("uploads/auto/C:/Windows/System32/config/SECURITY", b"REGF" + b"\x00" * 12)
        zf.writestr("uploads/auto/C:/Windows/System32/winevt/Logs/Security.evtx", b"ElfFile\x00")
        zf.writestr("uploads/auto/var/log/auth.log", b"auth\n")
        zf.writestr("uploads/auto/var/log/nginx/access_2024.log", b"200 GET /\n")
        zf.writestr("uploads/auto/random/unknown.bin", b"???")
    return z


def test_adapt_produces_expected_layout(velo_zip: Path, tmp_path: Path):
    out = tmp_path / "evidence_root"
    result = adapt(velo_zip, out, case_id="case-test")

    assert result.files_copied == 7
    assert result.files_skipped == 0
    assert (out / "manifest.json").is_file()

    # Each artifact landed in the correct subdir
    assert (out / "Prefetch" / "SVCHOST.EXE-ABC.pf").is_file()
    assert (out / "Amcache" / "Amcache.hve").is_file()
    assert (out / "Registry" / "SECURITY").is_file()
    assert (out / "EventLogs" / "Security.evtx").is_file()
    assert (out / "AuthLogs" / "auth.log").is_file()
    assert (out / "WebLogs" / "access_2024.log").is_file()
    assert (out / "Other" / "unknown.bin").is_file()


def test_manifest_has_required_fields(velo_zip: Path, tmp_path: Path):
    out = tmp_path / "evidence_root"
    adapt(velo_zip, out, case_id="case-manifest")
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))

    for k in ("manifest_version", "case_id", "generated_at",
              "source", "host", "adapter", "counters",
              "categories", "sha256_index"):
        assert k in manifest, f"missing manifest field: {k}"

    assert manifest["case_id"] == "case-manifest"
    assert manifest["counters"]["files_copied"] == 7
    assert manifest["categories"]["prefetch"] == 1
    assert manifest["categories"]["amcache"] == 1
    # SHA-256 index covers every output file
    assert "Prefetch/SVCHOST.EXE-ABC.pf" in manifest["sha256_index"]


def test_adapt_refuses_overwrite_by_default(velo_zip: Path, tmp_path: Path):
    out = tmp_path / "evidence_root"
    adapt(velo_zip, out, case_id="case-1")
    with pytest.raises(FileExistsError):
        adapt(velo_zip, out, case_id="case-2")


def test_adapt_overwrites_when_requested(velo_zip: Path, tmp_path: Path):
    out = tmp_path / "evidence_root"
    adapt(velo_zip, out, case_id="case-1")
    # No exception when overwrite=True
    result = adapt(velo_zip, out, case_id="case-2", overwrite=True)
    assert result.case_id == "case-2"


def test_adapt_missing_zip_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        adapt(tmp_path / "nope.zip", tmp_path / "out")


def test_safe_target_path_rejects_traversal(tmp_path: Path):
    # The adapter's _safe_target_path is the single line of defence against
    # malicious ZIP member names. Test it directly.
    assert _safe_target_path(tmp_path, "../../etc/passwd") is None
    assert _safe_target_path(tmp_path, "") is None
    assert _safe_target_path(tmp_path, ".") is None
    assert _safe_target_path(tmp_path, "..") is None


def test_unsafe_names_skipped(tmp_path: Path):
    z = tmp_path / "bad.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("ok.txt", b"fine")
        zf.writestr("bad\x01name.txt", b"control-byte")
    out = tmp_path / "out"
    result = adapt(z, out, case_id="case-unsafe")
    assert result.files_copied == 1
    assert result.files_skipped == 1
    assert any("unsafe characters" in s for s in result.skipped_paths)
