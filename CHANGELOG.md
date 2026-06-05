# Changelog

All notable changes to **agentic-dart-collector-adapter** are documented here.
The adapter follows the [Agentic-DART](https://github.com/Juwon1405/agentic-dart)
release line.

## [1.0.0] — 2026-06-05 — First stable release

First stable release, aligned with Agentic-DART v1.0.0. The adapter's core job —
translating Velociraptor offline-collector output into the `evidence_root`
layout that Agentic-DART reads — is complete, hardened, and fully tested.

### Added
- This CHANGELOG.

### Changed
- Roadmap renumbered onto a v1.x line. `v1.0` (current, stable) consolidates the
  former `v0.1` (foundation) and `v0.2` (hardened integrity) milestones; sidecar
  generation, `results/*.json` ingest, and cross-platform artifact parity become
  `v1.1`–`v1.3`. The README roadmap table and the generated
  `docs/img/roadmap.png` were regenerated to match.

### Stable at release
- Velociraptor offline-collector ZIP -> `evidence_root` layout translation.
- `manifest.json` schema `1.1` — input-ZIP `source.sha256` anchor + `skipped`
  audit trail alongside the per-file SHA-256 index.
- Hardened integrity: ZIP-bomb + symlink defenses, single-pass hashing, mtime
  preservation, overwrite-safe writes.
- `install.sh` verifies the downloaded Velociraptor binary against the upstream
  SHA-256 manifest before use.
- 45 tests passing on Linux + macOS x py3.10/11/12. Zero runtime dependencies
  (standard library only).

## [0.2.0] — 2026-05-17 — Hardened integrity + manifest 1.1

- Manifest schema bumped to `1.1` (`source.sha256` input-ZIP anchor, `skipped`
  audit trail).
- ZIP-bomb + symlink defenses, single-pass hashing, mtime preservation,
  overwrite-safe writes.
- Hardened `install.sh` with install-time binary checksum verification.
- Single-source version.

## [0.1.1] — 2026-05-14 — Initial adapter

- Velociraptor offline-collector ZIP -> `evidence_root` with SHA-256 manifest.
- Full test suite passing on Linux + macOS x py3.10/11/12.
