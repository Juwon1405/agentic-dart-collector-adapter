#!/usr/bin/env bash
# ===========================================================================
# install.sh
#
# Installs the dart-collector-adapter Python package on the analysis server
# AND downloads Velociraptor agent binaries for every common (OS, arch) combo
# into ./bin/velociraptor/ so that responders can ship the right binary
# to each incident host without leaving the analysis server.
#
# This script is intended to run on the analysis server (Linux or macOS).
# It does NOT install anything on incident hosts.
#
# Usage:
#   ./install.sh                 # full setup
#   VELO_VERSION=0.74.0 ./install.sh   # pin a specific Velociraptor version
#   ./install.sh --no-velociraptor     # adapter only (skip binaries)
# ===========================================================================
set -euo pipefail

# Default version; override via env var to bump.
VELO_VERSION="${VELO_VERSION:-0.73.4}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${SCRIPT_DIR}/bin/velociraptor"
SKIP_VELO=0
if [[ "${1:-}" == "--no-velociraptor" ]]; then
    SKIP_VELO=1
fi

# Velociraptor release matrix that responders typically need.
# Format: "os-arch:release-asset-suffix"
VELO_TARGETS=(
    "windows-amd64:windows-amd64.exe"
    "windows-arm64:windows-arm64.exe"
    "linux-amd64:linux-amd64"
    "linux-arm64:linux-arm64"
    "darwin-amd64:darwin-amd64"
    "darwin-arm64:darwin-arm64"
)

# ---------------------------------------------------------------------------
# Step 1 — adapter (Python, OS-agnostic)
# ---------------------------------------------------------------------------
echo "==> Step 1/2: installing dart-collector-adapter (Python)"
PYTHON_BIN="$(command -v python3 || command -v python || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
    echo "error: python3 not found on PATH" >&2
    exit 1
fi
"${PYTHON_BIN}" -m pip install --upgrade --user -e "${SCRIPT_DIR}" >/dev/null
echo "    adapter installed: $(command -v dart-collector-adapter 2>/dev/null || echo '(use python -m dart_collector_adapter.cli)')"

# ---------------------------------------------------------------------------
# Step 2 — Velociraptor binaries for every (OS, arch) combo
# ---------------------------------------------------------------------------
if [[ "${SKIP_VELO}" -eq 1 ]]; then
    echo "==> Step 2/2: skipped (--no-velociraptor)"
    exit 0
fi

echo "==> Step 2/2: downloading Velociraptor v${VELO_VERSION} binaries"
mkdir -p "${BIN_DIR}"

for target in "${VELO_TARGETS[@]}"; do
    os_arch="${target%%:*}"
    suffix="${target##*:}"
    url="https://github.com/Velocidex/velociraptor/releases/download/v${VELO_VERSION}/velociraptor-v${VELO_VERSION}-${suffix}"
    dst="${BIN_DIR}/velociraptor-${os_arch}"

    if [[ -f "${dst}" ]]; then
        echo "    [skip] ${os_arch}  (already present)"
        continue
    fi

    if command -v curl >/dev/null 2>&1; then
        echo "    [fetch] ${os_arch}"
        if ! curl -fSL -o "${dst}" "${url}"; then
            echo "    [warn] failed to download ${os_arch}, continuing"
            rm -f "${dst}"
            continue
        fi
    elif command -v wget >/dev/null 2>&1; then
        echo "    [fetch] ${os_arch}"
        if ! wget -O "${dst}" "${url}"; then
            echo "    [warn] failed to download ${os_arch}, continuing"
            rm -f "${dst}"
            continue
        fi
    else
        echo "error: neither curl nor wget is available" >&2
        exit 1
    fi
    chmod +x "${dst}" 2>/dev/null || true
done

echo ""
echo "Done."
echo "  Adapter:               dart-collector-adapter --help"
echo "  Velociraptor binaries: ${BIN_DIR}"
echo ""
echo "Ship the matching binary to each incident host. For example:"
echo "  scp ${BIN_DIR}/velociraptor-windows-amd64  responder@incident-host:C:/temp/"
