# agentic-dart-collector-adapter

[![tests](https://github.com/Juwon1405/agentic-dart-collector-adapter/actions/workflows/tests.yml/badge.svg)](https://github.com/Juwon1405/agentic-dart-collector-adapter/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Phase](https://img.shields.io/badge/phase-1.3%20%C2%B7%20Agentic--DART%20roadmap-FF8B00)](https://github.com/Juwon1405/agentic-dart#phase-1-rollout-roadmap)
[![Companion](https://img.shields.io/badge/companion-Agentic--DART-DD2C00?logo=github)](https://github.com/Juwon1405/agentic-dart)

> **A thin Python layer that turns Velociraptor offline-collector output into the `evidence_root` layout expected by [Agentic-DART](https://github.com/Juwon1405/agentic-dart).**
>
> No fork of Velociraptor. No re-implementation of forensic collection. Just the missing piece between *what an industry-standard collector emits* and *what an agentic DFIR analysis engine wants to read*.

---

## Architecture

![architecture](docs/img/arch.png)

The adapter installs **once** on the analysis server. It is **not** installed on incident hosts. Each incident host receives a Velociraptor agent binary for its OS / arch (Windows / Linux / macOS), runs it once to produce `evidence.zip`, and ships the ZIP back. The adapter then performs the layout translation that Agentic-DART expects.

---

## Position in the Agentic-DART roadmap

This repository is **Phase 1.3** of the [Agentic-DART rollout roadmap](https://github.com/Juwon1405/agentic-dart#phase-1-rollout-roadmap) — the *collector adapter* deliverable. It exists so the upstream collection layer (Velociraptor) and the upstream analysis engine (Agentic-DART) can stay independent of each other.

| Concern                  | Where it lives                                                                                                       |
|--------------------------|----------------------------------------------------------------------------------------------------------------------|
| **Collection** on hosts  | [Velociraptor](https://docs.velociraptor.app/) agent (binary, runs on the endpoint)                                  |
| **Layout normalization** | **This repo** *(Phase 1.3, current)*                                                                                 |
| **Analysis & reasoning** | [Agentic-DART](https://github.com/Juwon1405/agentic-dart) (runs on the same analysis server)                         |
| **Chain-of-custody**     | This adapter seeds it (`manifest.json` + SHA-256 index); Agentic-DART continues it as `audit.jsonl` entry 1 onwards. |

---

## Why this exists

[Velociraptor](https://docs.velociraptor.app/) is an excellent open-source IR collector with cross-platform agents (Windows / Linux / macOS) and a huge artifact library (`Windows.KapeFiles.Targets`, `Windows.Forensics.Lnkfiles`, `MacOS.Forensics.*`, `Linux.Forensics.*`).

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

## Install

The analysis server runs on Linux or macOS. `install.sh` does two things in one pass:

1. Installs the Python adapter (`dart-collector-adapter`).
2. Downloads Velociraptor agent binaries for every common OS / arch combo into `./bin/velociraptor/`, so responders can ship the right binary to any incident host without leaving the server.

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

## `manifest.json`

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

## Phase roadmap

![roadmap](docs/img/roadmap.png)

| Phase     | Status   | Scope                                                                                            |
|-----------|----------|--------------------------------------------------------------------------------------------------|
| **v0.1**  | current  | Velociraptor ZIP → evidence_root with SHA-256 manifest. 27/27 tests on Linux+macOS × py3.10/11/12. |
| **v0.2**  | next     | Sidecar generation — auto-invoke `PECmd`, `AmcacheParser`, `EvtxECmd` when present locally.       |
| **v0.3**  | later    | Ingest Velociraptor `results/*.json` (parsed-artifact JSON) and merge into the manifest.          |
| **v0.4**  | later    | macOS + Linux artifact coverage parity with Windows.                                              |

The adapter is intentionally narrow. It will not grow into a "platform."

---

## Companion

**[agentic-dart](https://github.com/Juwon1405/agentic-dart)** — the analysis engine this adapter feeds.

---

## License

MIT. See [LICENSE](LICENSE).

## Author

**YuShin** (優心 / Bang Juwon) — DFIR practitioner, Tokyo.

> *"One small adapter. One large saved hour per incident."*
