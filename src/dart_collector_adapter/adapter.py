"""
Main adapter — turns a Velociraptor offline-collector ZIP into the
evidence_root layout used by Agentic-DART.

Velociraptor offline collector outputs (typical layout):
    archive.zip
    +-- results/
    |   +-- Windows.KapeFiles.Targets/All file metadata.json
    |   +-- Windows.KapeFiles.Targets/All file metadata.zip
    |   +-- Windows.Forensics.Lnkfiles/All file metadata.json
    |   +-- ...
    +-- uploads/
    |   +-- auto/C:/Windows/Prefetch/SVCHOST.EXE-...pf
    |   +-- auto/C:/Windows/AppCompat/Programs/Amcache.hve
    |   +-- ...

Target evidence_root layout (what Agentic-DART expects):
    evidence_root/
    +-- manifest.json
    +-- Prefetch/
    |   +-- SVCHOST.EXE-XYZ.pf
    +-- Amcache/
    |   +-- Amcache.hve
    +-- EventLogs/
    |   +-- Security.evtx
    +-- Registry/
    |   +-- SOFTWARE
    |   +-- SYSTEM
    +-- WebLogs/
    |   +-- access.log
    +-- Browser/
    +-- ...
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .hash_indexer import compute_sha256
from .manifest import write_manifest
from .layout import EVIDENCE_LAYOUT, classify_artifact

# Files larger than this are treated as suspicious / skipped by default.
DEFAULT_MAX_BYTES = 10 * 1024 * 1024 * 1024  # 10 GiB

# Safe filename regex (no traversal characters).
import re
_UNSAFE_NAME_RE = re.compile(r"[\x00-\x1f\x7f]")


@dataclass
class AdapterResult:
    """What adapt() returns."""
    output_root: Path
    case_id: str
    files_copied: int = 0
    files_skipped: int = 0
    bytes_copied: int = 0
    categories: dict[str, int] = field(default_factory=dict)
    skipped_paths: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def adapt(
    velociraptor_zip: str | Path,
    output_evidence_root: str | Path,
    *,
    case_id: str | None = None,
    max_bytes_per_file: int = DEFAULT_MAX_BYTES,
    overwrite: bool = False,
) -> AdapterResult:
    """
    Extract Velociraptor offline-collector ZIP into Agentic-DART
    evidence_root layout.

    Parameters
    ----------
    velociraptor_zip : path to the Velociraptor collector ZIP.
    output_evidence_root : target directory. Created if it does not exist.
    case_id : optional case identifier written into manifest.json. Defaults
        to the ZIP basename.
    max_bytes_per_file : safety guard. Files larger than this are skipped.
    overwrite : if False and output already contains a non-empty manifest,
        raises FileExistsError.

    Returns
    -------
    AdapterResult with counters and a list of skipped paths.

    Raises
    ------
    FileNotFoundError : ZIP does not exist.
    zipfile.BadZipFile : ZIP is malformed.
    FileExistsError : evidence_root has a manifest and overwrite=False.
    """
    src = Path(velociraptor_zip).resolve()
    if not src.is_file():
        raise FileNotFoundError(f"ZIP not found: {src}")

    dst = Path(output_evidence_root).resolve()
    dst.mkdir(parents=True, exist_ok=True)

    if not overwrite and (dst / "manifest.json").exists():
        raise FileExistsError(
            f"manifest.json already exists in {dst}; pass overwrite=True to replace"
        )

    cid = case_id or src.stem
    result = AdapterResult(output_root=dst, case_id=cid)

    for layout_dir in EVIDENCE_LAYOUT.values():
        (dst / layout_dir).mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(src, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            if info.file_size > max_bytes_per_file:
                result.files_skipped += 1
                result.skipped_paths.append(f"{info.filename}  (too large: {info.file_size} bytes)")
                continue
            if _UNSAFE_NAME_RE.search(info.filename):
                result.files_skipped += 1
                result.skipped_paths.append(f"{info.filename}  (unsafe characters)")
                continue

            target = _safe_target_path(dst, info.filename)
            if target is None:
                result.files_skipped += 1
                result.skipped_paths.append(f"{info.filename}  (would escape evidence_root)")
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as fsrc, open(target, "wb") as fdst:
                while True:
                    chunk = fsrc.read(1024 * 1024)
                    if not chunk:
                        break
                    fdst.write(chunk)

            result.files_copied += 1
            result.bytes_copied += info.file_size
            category = classify_artifact(info.filename)
            result.categories[category] = result.categories.get(category, 0) + 1

    # Manifest written last so that incomplete runs do not look successful.
    write_manifest(
        evidence_root=dst,
        case_id=cid,
        source_zip=str(src),
        files_copied=result.files_copied,
        bytes_copied=result.bytes_copied,
        categories=result.categories,
        skipped_count=result.files_skipped,
    )

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_target_path(evidence_root: Path, member_name: str) -> Path | None:
    """
    Map a Velociraptor ZIP member name to a path under evidence_root using
    the layout categories, refusing anything that looks like a traversal
    or path-injection attempt.

    Defenses, in order:
    1. Refuse empty / dot-only names.
    2. Refuse absolute paths (Posix `/` and Windows `\\` or drive-letter prefix).
       Velociraptor uses absolute-looking paths inside its ZIP, but we always
       reduce them to their basename — except a leading "/" without any other
       segment is just garbage.
    3. Refuse if any path segment is "..".
    4. After category lookup + basename extraction, the result must resolve
       inside evidence_root.
    """
    if not member_name or member_name in (".", ".."):
        return None

    # Reject if any segment is .. (path traversal).
    norm = member_name.replace("\\", "/")
    segments = [s for s in norm.split("/") if s]
    if any(s == ".." for s in segments):
        return None
    if not segments:
        return None

    base_name = segments[-1]
    if not base_name or base_name in (".", ".."):
        return None

    category = classify_artifact(member_name)
    layout_dir = EVIDENCE_LAYOUT[category]

    candidate = (evidence_root / layout_dir / base_name).resolve()
    try:
        candidate.relative_to(evidence_root.resolve())
    except ValueError:
        return None
    return candidate
