#!/usr/bin/env python3
"""
Generate architecture PNG for agentic-dart-collector-adapter README.

Two diagrams:
- arch.png       : end-to-end flow (incident host -> adapter -> agentic-dart)
- roadmap.png    : v0.1 / v0.2 / v0.3 / v0.4 phases
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

# Atlassian-friendly palette
BG     = "#FFFFFF"
TEXT   = "#172B4D"
ACCENT = "#0052CC"
MINT   = "#00875A"
RED    = "#DE350B"
AMBER  = "#FF8B00"
PURPLE = "#5243AA"
GRAY   = "#5E6C84"
LIGHT  = "#F4F5F7"
WHITE  = "#FFFFFF"

OUT = Path(__file__).parent.parent / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)


def _box(ax, x, y, w, h, color, *, title, lines, font=10.5):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.3,rounding_size=0.8",
                          linewidth=1.8, edgecolor=color,
                          facecolor=LIGHT)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 2.0, title,
            ha="center", va="top", fontsize=11.5, fontweight="bold",
            color=color)
    for i, line in enumerate(lines):
        ax.text(x + w/2, y + h - 5.6 - i*2.4, line,
                ha="center", va="top", fontsize=font, color=TEXT)


def _arrow(ax, x1, y1, x2, y2, color=GRAY, label=None, label_y_off=1.2):
    arr = FancyArrowPatch((x1, y1), (x2, y2),
                          arrowstyle='-|>', mutation_scale=22,
                          linewidth=2.0, color=color)
    ax.add_patch(arr)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + label_y_off, label,
                ha='center', fontsize=9.5, color=color, style='italic',
                fontweight='bold')


# ────────────────────────────────────────────────────────────────
# arch.png — end-to-end flow
# ────────────────────────────────────────────────────────────────
def diagram_arch():
    fig, ax = plt.subplots(figsize=(15, 8), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    ax.text(50, 57.5,
            "agentic-dart-collector-adapter  ·  end-to-end flow",
            ha="center", fontsize=15, fontweight="bold", color=TEXT)
    ax.text(50, 54.5,
            "incident host  →  this adapter (analysis server)  →  Agentic-DART",
            ha="center", fontsize=10.5, color=GRAY, style="italic")

    # ── Left zone: incident host ────────────────────────────────
    zone1 = FancyBboxPatch((2, 8), 23, 40,
                           boxstyle="round,pad=0.4,rounding_size=1.0",
                           linewidth=2.0, edgecolor=RED,
                           facecolor="#FDF6F5")
    ax.add_patch(zone1)
    ax.text(13.5, 45.5, "1. Incident host",
            ha="center", fontsize=12, fontweight="bold", color=RED)
    ax.text(13.5, 42.7, "(short-lived, no install)",
            ha="center", fontsize=9, color=GRAY, style="italic")

    _box(ax, 4, 28, 19, 11, RED,
         title="Velociraptor agent",
         lines=["OS-matched binary",
                "Win / Linux / macOS",
                "1× execution",
                "no agent install"],
         font=9.5)

    _box(ax, 4, 12, 19, 11, AMBER,
         title="evidence.zip",
         lines=["Velociraptor",
                "offline-collector",
                "output format"],
         font=9.5)

    _arrow(ax, 13.5, 28, 13.5, 23, color=GRAY, label_y_off=0)

    # ── Middle zone: analysis server (this adapter) ──────────────
    zone2 = FancyBboxPatch((28, 8), 44, 40,
                           boxstyle="round,pad=0.4,rounding_size=1.0",
                           linewidth=2.5, edgecolor=ACCENT,
                           facecolor="#F0F5FB")
    ax.add_patch(zone2)
    ax.text(50, 45.5, "2. Analysis server",
            ha="center", fontsize=12, fontweight="bold", color=ACCENT)
    ax.text(50, 42.7, "(Linux / macOS, install once)",
            ha="center", fontsize=9, color=GRAY, style="italic")

    _box(ax, 30, 28, 18, 11, ACCENT,
         title="dart-collector-adapter",
         lines=["classify artifacts",
                "stream-copy + safe paths",
                "SHA-256 each file",
                "write manifest.json"],
         font=9.5)

    _box(ax, 52, 28, 18, 11, MINT,
         title="evidence_root/",
         lines=["Prefetch/   Amcache/",
                "Registry/   EventLogs/",
                "Browser/    WebLogs/",
                "MFT/  LNK/  Other/"],
         font=9.5)

    _arrow(ax, 48, 33.5, 52, 33.5, color=ACCENT, label="layout", label_y_off=2.2)

    _box(ax, 30, 12, 40, 11, PURPLE,
         title="manifest.json  +  SHA-256 index",
         lines=["chain-of-custody seed",
                "case_id  ·  source  ·  adapter version  ·  category counts",
                "(consumed by Agentic-DART's audit chain as entry 0)"],
         font=9.5)

    _arrow(ax, 39, 28, 39, 23, color=PURPLE, label_y_off=0)
    _arrow(ax, 61, 28, 61, 23, color=PURPLE, label_y_off=0)

    _arrow(ax, 25, 33.5, 30, 33.5, color=RED, label="SCP / SMB / USB", label_y_off=2.2)

    # ── Right zone: Agentic-DART ────────────────────────────────
    zone3 = FancyBboxPatch((75, 8), 23, 40,
                           boxstyle="round,pad=0.4,rounding_size=1.0",
                           linewidth=2.0, edgecolor=MINT,
                           facecolor="#F0F8F5")
    ax.add_patch(zone3)
    ax.text(86.5, 45.5, "3. Agentic-DART",
            ha="center", fontsize=12, fontweight="bold", color=MINT)
    ax.text(86.5, 42.7, "(same analysis server)",
            ha="center", fontsize=9, color=GRAY, style="italic")

    _box(ax, 77, 28, 19, 11, MINT,
         title="dart_agent",
         lines=["reads evidence_root",
                "runs playbook v3",
                "67 read-only MCP tools",
                "SHA-256 audit chain"],
         font=9.5)

    _box(ax, 77, 12, 19, 11, ACCENT,
         title="findings.json",
         lines=["report.md",
                "audit.jsonl",
                "(extends chain-of-",
                "custody from seed)"],
         font=9.5)

    _arrow(ax, 86.5, 28, 86.5, 23, color=MINT, label_y_off=0)
    _arrow(ax, 72, 33.5, 77, 33.5, color=MINT, label="read", label_y_off=2.2)

    # ── Footer ──────────────────────────────────────────────────
    ax.text(50, 4.5,
            "the adapter installs ONCE on the analysis server  ·  "
            "Velociraptor binaries shipped to each incident host on demand",
            ha="center", fontsize=10, color=GRAY, style="italic")
    ax.text(50, 1.8,
            "no incident-host install · stdlib-only Python · 27/27 tests · Apache-2.0",
            ha="center", fontsize=9, color=GRAY)

    plt.tight_layout()
    out = OUT / "arch.png"
    plt.savefig(out, dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  ok  {out.name}")


# ────────────────────────────────────────────────────────────────
# roadmap.png — phase plan
# ────────────────────────────────────────────────────────────────
def diagram_roadmap():
    fig, ax = plt.subplots(figsize=(14, 4), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 30)
    ax.axis('off')

    ax.text(50, 27,
            "agentic-dart-collector-adapter  ·  phase roadmap",
            ha="center", fontsize=14, fontweight="bold", color=TEXT)

    phases = [
        ("v0.1", "current",
         ["Velociraptor ZIP -> evidence_root", "SHA-256 manifest", "27/27 tests", "CI Linux+macOS x py3.10/11/12"],
         ACCENT, True),
        ("v0.2", "next",
         ["sidecar generation", "PECmd / AmcacheParser /", "EvtxECmd auto-invoke", "(when available locally)"],
         AMBER, False),
        ("v0.3", "later",
         ["Velociraptor results/*.json", "parsed-artifact JSON merged", "into manifest"],
         PURPLE, False),
        ("v0.4", "later",
         ["macOS + Linux artifact", "coverage parity with Windows"],
         GRAY, False),
    ]

    x_start = 4
    box_w = 22
    gap = 2

    for i, (ver, status, lines, color, is_current) in enumerate(phases):
        x = x_start + i * (box_w + gap)
        # Title bar
        title_bar = FancyBboxPatch((x, 17), box_w, 5,
                                   boxstyle="round,pad=0.1,rounding_size=0.4",
                                   linewidth=0, facecolor=color)
        ax.add_patch(title_bar)
        ax.text(x + box_w/2, 19.5, f"{ver}  ·  {status}",
                ha="center", va="center", fontsize=11, fontweight="bold",
                color="white")
        # Body
        body = FancyBboxPatch((x, 4), box_w, 12.5,
                              boxstyle="round,pad=0.2,rounding_size=0.6",
                              linewidth=1.5, edgecolor=color,
                              facecolor=LIGHT if not is_current else "#FFF8E7")
        ax.add_patch(body)
        for j, line in enumerate(lines):
            ax.text(x + box_w/2, 13.5 - j*2.2, line,
                    ha="center", fontsize=9, color=TEXT)
        # Arrow between phases
        if i < len(phases) - 1:
            arr_x1 = x + box_w + 0.3
            arr_x2 = x + box_w + gap - 0.3
            _arrow(ax, arr_x1, 19.5, arr_x2, 19.5, color=GRAY)

    ax.text(50, 1,
            "adapter is intentionally narrow — one clear job, plus thin parser sidecar invocation later",
            ha="center", fontsize=9, color=GRAY, style="italic")

    plt.tight_layout()
    out = OUT / "roadmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  ok  {out.name}")


if __name__ == "__main__":
    print("[generating adapter diagrams]")
    diagram_arch()
    diagram_roadmap()
    print(f"\ndone -> {OUT}")
