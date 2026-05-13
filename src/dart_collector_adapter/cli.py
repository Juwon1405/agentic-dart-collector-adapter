"""
Command-line entrypoint:

    dart-collector-adapter --input collector.zip --output /evidence/case-XYZ/

Designed to be small and to exit non-zero on any error so that pipelines
can chain it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .adapter import adapt


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dart-collector-adapter",
        description=(
            "Convert a Velociraptor offline-collector ZIP into the Agentic-DART "
            "evidence_root layout (writes manifest.json with SHA-256 index)."
        ),
    )
    p.add_argument("--input", "-i", required=True,
                   help="Path to the Velociraptor offline-collector ZIP.")
    p.add_argument("--output", "-o", required=True,
                   help="Target evidence_root directory (created if missing).")
    p.add_argument("--case-id", default=None,
                   help="Case identifier written into manifest.json. "
                        "Defaults to the ZIP basename.")
    p.add_argument("--overwrite", action="store_true",
                   help="Replace an existing manifest.json instead of failing.")
    p.add_argument("--no-hash-index", action="store_true",
                   help="Skip the sha256_index field in manifest.json (faster, less safe).")
    p.add_argument("--quiet", "-q", action="store_true",
                   help="Suppress progress output.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = adapt(
            velociraptor_zip=args.input,
            output_evidence_root=args.output,
            case_id=args.case_id,
            overwrite=args.overwrite,
        )
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except FileExistsError as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        summary = {
            "output_root": str(result.output_root),
            "case_id": result.case_id,
            "files_copied": result.files_copied,
            "files_skipped": result.files_skipped,
            "bytes_copied": result.bytes_copied,
            "categories": result.categories,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        if result.skipped_paths:
            print(f"\n[note] {len(result.skipped_paths)} entries skipped",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
