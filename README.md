# agentic-dart-collector-adapter

[![tests](https://github.com/Juwon1405/agentic-dart-collector-adapter/actions/workflows/tests.yml/badge.svg)](https://github.com/Juwon1405/agentic-dart-collector-adapter/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Companion](https://img.shields.io/badge/companion-Agentic--DART-DD2C00?logo=github)](https://github.com/Juwon1405/agentic-dart)

> **A thin Python layer that turns Velociraptor offline-collector output into the `evidence_root` layout expected by [Agentic-DART](https://github.com/Juwon1405/agentic-dart).**
>
> No fork of Velociraptor. No re-implementation of forensic collection. Just the missing piece between *what an industry-standard collector emits* and *what an agentic DFIR analysis engine wants to read*.

---

## Why this exists

[Velociraptor](https://docs.velociraptor.app/) is an excellent open-source IR collector with cross-platform agents (Windows / Linux / macOS) and a huge artifact library (Windows.KapeFiles.Targets, Windows.Forensics.Lnkfiles, MacOS.Forensics.*, Linux.Forensics.*).

[Agentic-DART](https://github.com/Juwon1405/agentic-dart) is an autonomous DFIR analysis engine that consumes a flat, well-named `evidence_root/` directory:

```
evidence_root/
├── manifest.json
├── Prefetch/         SVCHOST.EXE-XYZ.pf, ...
├── Amcache/          Amcache.hve
├── Registry/         SOFTWARE, SYSTEM, SAM, ...
├── EventLogs/        Security.evtx, ...
├── Browser/          History, places.sqlite, ...
├── WebLogs/          access.log, u_ex240509.log, ...
├── AuthLogs/         auth.log, secure
├── Memory/           memory.dmp
├── LNK/              *.lnk
├── JumpLists/        *.automaticDestinations-ms
├── MFT/              $MFT
├── USNJournal/       $UsnJrnl-$J
├── PowerShell/       ConsoleHost_history.txt
└── Other/            (anything unrecognized)
```

Velociraptor's offline-collector ZIPs do **not** look like that. Members are paths like `uploads/auto/C:/Windows/System32/winevt/Logs/Security.evtx`, mixed with `results/*.json` and per-artifact subtrees.

This adapter is the **glue**:

```
Velociraptor offline ZIP  ─▶  dart-collector-adapter  ─▶  evidence_root/
                                                          (Agentic-DART reads this)
```

It is stdlib-only by design (no third-party Python packages), and small enough to audit in one sitting.

---

## Relationship to Agentic-DART

| Concern                  | Where it lives                                  |
|--------------------------|-------------------------------------------------|
| **Collection** on hosts  | Velociraptor agent (binary, runs on the endpoint) |
| **Layout normalization** | **This repo** (runs on the analysis server)     |
| **Analysis & reasoning** | [Agentic-DART](https://github.com/Juwon1405/agentic-dart) (runs on the analysis server) |
| **Chain-of-custody**     | This adapter seeds it (`manifest.json` + SHA-256 index); Agentic-DART continues it (`audit.jsonl`) |

**The adapter is installed once on the analysis server.** It is *not* installed on incident hosts. Each incident host receives a Velociraptor agent binary for its OS/arch.

```
┌───────────────────────┐        ZIP        ┌────────────────────────────────────────┐
│ Incident host         │  ───────────▶     │ Central analysis server (Linux/macOS)  │
│  Velociraptor agent   │  (SCP / SMB)      │  ┌──────────────────────────────────┐  │
│  (Win / Linux / Mac)  │                   │  │ dart-collector-adapter            │  │
└───────────────────────┘                   │  │   ZIP -> evidence_root/           │  │
                                            │  │   + manifest.json + SHA-256 index │  │
                                            │  └──────────────────────────────────┘  │
                                            │           │                              │
                                            │           ▼                              │
                                            │  ┌──────────────────────────────────┐  │
                                            │  │ Agentic-DART                       │  │
                                            │  │   reads evidence_root/             │  │
                                            │  │   produces findings.json + report  │  │
                                            │  └──────────────────────────────────┘  │
                                            └────────────────────────────────────────┘
```

---

## Install

The analysis server runs on Linux or macOS. `install.sh` does two things in one pass:

1. Installs the Python adapter (`dart-collector-adapter`).
2. Downloads Velociraptor agent binaries for every common OS/arch combo into `./bin/velociraptor/`, so responders can ship the right binary to any incident host without leaving the server.

```bash
git clone https://github.com/Juwon1405/agentic-dart-collector-adapter
cd agentic-dart-collector-adapter
./install.sh
```

Pin a specific Velociraptor version:

```bash
VELO_VERSION=0.74.0 ./install.sh
```

Adapter only (skip the binary downloads):

```bash
./install.sh --no-velociraptor
```

Manual install of the adapter (no Velociraptor downloads):

```bash
pip install -e .
```

---

## Usage

### 1. On the incident host — collect

Ship the matching Velociraptor binary to the host:

```bash
# from the analysis server
scp ./bin/velociraptor/velociraptor-windows-amd64 \
    responder@incident-host:C:/temp/velociraptor.exe
```

Run an offline collector on the host (one-time execution, no agent install):

```cmd
:: on Windows incident host
C:\temp\velociraptor.exe -i artifacts collect Windows.KapeFiles.Targets ^
    --output C:\temp\evidence.zip
```

```bash
# on Linux / macOS incident host
./velociraptor -i artifacts collect Linux.Search.FileFinder \
    --output /tmp/evidence.zip
```

Copy `evidence.zip` back to the analysis server.

### 2. On the analysis server — adapt

```bash
dart-collector-adapter \
    --input /tmp/evidence.zip \
    --output /evidence/case-2026-001/ \
    --case-id case-2026-001
```

Output:

```json
{
  "bytes_copied": 12483920,
  "case_id": "case-2026-001",
  "categories": {
    "amcache": 1,
    "browser": 4,
    "eventlog": 7,
    "prefetch": 156,
    "registry": 6
  },
  "files_copied": 174,
  "files_skipped": 0,
  "output_root": "/evidence/case-2026-001"
}
```

### 3. Hand off to Agentic-DART

```bash
python -m dart_agent run \
    --evidence /evidence/case-2026-001/ \
    --playbook senior-analyst-v3.yaml
```

Agentic-DART picks up the `evidence_root` layout, reads `manifest.json` as the chain-of-custody seed, and writes its own `audit.jsonl` to continue the chain.

---

## Programmatic API

```python
from dart_collector_adapter import adapt

result = adapt(
    velociraptor_zip="/tmp/evidence.zip",
    output_evidence_root="/evidence/case-2026-001/",
    case_id="case-2026-001",
)

print(result.files_copied, result.bytes_copied, result.categories)
```

Returns an `AdapterResult` dataclass:

```python
@dataclass
class AdapterResult:
    output_root: Path
    case_id: str
    files_copied: int
    files_skipped: int
    bytes_copied: int
    categories: dict[str, int]
    skipped_paths: list[str]
```

---

## What the adapter actually does

| Step | What                                                                                                  |
|------|-------------------------------------------------------------------------------------------------------|
| 1    | Open the Velociraptor ZIP and iterate every file member.                                              |
| 2    | Classify each member by name (`.pf` → Prefetch, `Amcache.hve` → Amcache, `*.evtx` → EventLogs, ...).  |
| 3    | Validate the basename — reject control bytes, traversal characters, and anything that resolves outside the evidence_root. |
| 4    | Stream-copy into `evidence_root/<Category>/<basename>` (preserves binary content, never modifies).    |
| 5    | After all files copied, walk the output and SHA-256 every file (1 MiB streaming, no full-file load).  |
| 6    | Write `manifest.json` last so a half-finished run never looks successful.                             |

### Refused inputs

The adapter is opinionated about what it *won't* do, to keep its security surface tiny:

- Files larger than 10 GiB are skipped (configurable).
- ZIP members with control characters in the name are skipped.
- ZIP members whose path would resolve outside `evidence_root` are skipped.
- Existing `evidence_root` with a manifest is not overwritten (use `--overwrite`).

Skipped paths are reported in `AdapterResult.skipped_paths`.

---

## Layout / classification reference

See [`src/dart_collector_adapter/layout.py`](src/dart_collector_adapter/layout.py) for the authoritative classifier. High-level mapping:

| Velociraptor member pattern                                | Goes into             |
|------------------------------------------------------------|-----------------------|
| `*.pf`                                                     | `Prefetch/`           |
| `Amcache.hve`                                              | `Amcache/`            |
| `SECURITY`, `SAM`, `SOFTWARE`, `SYSTEM`, `NTUSER.DAT`, `UsrClass.dat` | `Registry/`  |
| `*.evtx`, `*.evt`                                          | `EventLogs/`          |
| Chrome / Edge / Firefox / Safari / Brave / Opera `History`, Cookies, Cache | `Browser/` |
| `places.sqlite`                                            | `Browser/`            |
| `$MFT`                                                     | `MFT/`                |
| `$UsnJrnl`                                                 | `USNJournal/`         |
| `access*.log`, `nginx/*.log`, `u_ex*.log` (IIS)            | `WebLogs/`            |
| `auth.log`, `secure`, `wtmp`, `btmp`                       | `AuthLogs/`           |
| `*.mem`, `*.dmp`, `*.vmem`, `*.raw`                        | `Memory/`             |
| `*.lnk`                                                    | `LNK/`                |
| `*.automaticDestinations-ms`                               | `JumpLists/`          |
| `ConsoleHost_history.txt`                                  | `PowerShell/`         |
| (everything else)                                          | `Other/`              |

---

## manifest.json

Written under `evidence_root/manifest.json`:

```json
{
  "manifest_version": "1.0",
  "case_id": "case-2026-001",
  "generated_at": "2026-05-13T15:00:00+00:00",
  "source": {
    "zip": "/tmp/evidence.zip",
    "type": "velociraptor_offline_collector"
  },
  "host": {
    "os": "Linux",
    "release": "5.15.0-...",
    "python": "3.12.1"
  },
  "adapter": {
    "name": "agentic-dart-collector-adapter",
    "version": "0.1.0"
  },
  "counters": {
    "files_copied": 174,
    "bytes_copied": 12483920,
    "files_skipped": 0
  },
  "categories": {
    "prefetch": 156,
    "amcache": 1,
    "registry": 6,
    "eventlog": 7,
    "browser": 4
  },
  "sha256_index": {
    "Prefetch/SVCHOST.EXE-ABC.pf": "9d7f...",
    "Amcache/Amcache.hve": "3c8e..."
  }
}
```

---

## Why not just fork Velociraptor?

Because forking 100k+ lines of Go to add one Python adapter would be insane.

- Velociraptor releases patches every few weeks. Tracking those in a fork is a full-time job.
- Adapter design = ~500 LOC of Python. Fork design = thousands of LOC of Go you don't own.
- This way, responders use **upstream Velociraptor releases** and pin the version via `VELO_VERSION` in `install.sh`. Security patches arrive on day zero.

---

## Roadmap

- **v0.1** *(current)* — Windows-heavy artifact mapping, stdlib-only adapter, SHA-256 manifest, CI matrix on Linux/macOS × Python 3.10/3.11/3.12.
- **v0.2** — Sidecar generation: invoke `PECmd`, `AmcacheParser`, `EvtxECmd` when present on the analysis server to drop `*.csv` / `*.json` next to binary artifacts. Optional, off by default.
- **v0.3** — Velociraptor `results/*.json` ingestion (the parsed-artifact JSON) merged into the manifest.
- **v0.4** — macOS and Linux artifact coverage parity with Windows.

Roadmap is intentionally short. The adapter should remain a single clear job.

---

## Companion project

➡️ **[Agentic-DART](https://github.com/Juwon1405/agentic-dart)** — the analysis engine that reads what this adapter produces.

---

## License

Apache-2.0. See [LICENSE](LICENSE).

## Author

**YuShin (優心 / Bang Juwon)** — DFIR practitioner, Tokyo.

> *"One small adapter. One large saved hour per incident."*
