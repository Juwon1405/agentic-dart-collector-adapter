#!/usr/bin/env python3
"""
_gen_diagrams.py — GitHub Pages light-theme diagrams.

Two outputs:
  docs/img/arch.png      end-to-end flow with Falcon/Velociraptor dual channel
  docs/img/roadmap.png   phase roadmap including v0.2 Falcon adapter

Design:
  - white background (#ffffff) — GitHub Pages canvas
  - subtle gray fill (#f6f8fa)
  - GitHub border default (#d0d7de)
  - generous internal padding; text never touches borders
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)

# GitHub Primer palette
BG          = "#ffffff"
SURFACE     = "#f6f8fa"
SURFACE_2   = "#ffffff"
BORDER      = "#d0d7de"
BORDER_MUTED= "#eaeef2"
TEXT_PRI    = "#1f2328"
TEXT_SEC    = "#656d76"
BLUE        = "#0969da"
BLUE_BG     = "#ddf4ff"
GREEN       = "#1a7f37"
GREEN_BG    = "#dafbe1"
PURPLE      = "#8250df"
PURPLE_BG   = "#fbefff"
ORANGE      = "#bc4c00"
ORANGE_BG   = "#fff1e5"

FIG_DPI = 130


def rounded_box(ax, x, y, w, h, *, fill=SURFACE, edge=BORDER, lw=1.0, radius=0.4):
    rect = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=lw, edgecolor=edge, facecolor=fill)
    ax.add_patch(rect)


def arrow(ax, x1, y1, x2, y2, *, color=TEXT_SEC, lw=1.2, label=None, label_offset=(0, 0.7)):
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=4, shrinkB=4))
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=10, color=color, style="italic")


# ════════════════════════════════════════════════════════════════════════════
# ARCH — end-to-end flow with dual-channel collection
# ════════════════════════════════════════════════════════════════════════════
def gen_arch():
    W, H = 1800, 1100
    fig, ax = plt.subplots(figsize=(W/FIG_DPI, H/FIG_DPI), facecolor=BG, dpi=FIG_DPI)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 180); ax.set_ylim(0, 110)
    ax.axis("off")

    # Title
    ax.text(90, 104, "agentic-dart-collector-adapter",
        ha="center", va="center", fontsize=24, color=TEXT_PRI, fontweight="bold")
    ax.text(90, 99.5, "end-to-end flow  ·  dual collection channels  ·  single analysis contract",
        ha="center", va="center", fontsize=13, color=TEXT_SEC, style="italic")
    ax.plot([10, 170], [95, 95], color=BORDER_MUTED, linewidth=0.8)

    # Column headers
    col_y = 90
    col1_x, col2_x, col3_x = 12, 70, 130
    col_w = 38
    section_w = 56

    ax.text(col1_x + col_w/2, col_y, "1.  Collection channels",
        ha="center", va="center", fontsize=15, color=BLUE, fontweight="bold")
    ax.text(col1_x + col_w/2, col_y - 3, "on the incident host",
        ha="center", va="center", fontsize=10, color=TEXT_SEC, style="italic")

    ax.text(col2_x + section_w/2, col_y, "2.  Adapter (this repo)",
        ha="center", va="center", fontsize=15, color=PURPLE, fontweight="bold")
    ax.text(col2_x + section_w/2, col_y - 3, "on the analysis server  ·  stdlib-only Python",
        ha="center", va="center", fontsize=10, color=TEXT_SEC, style="italic")

    ax.text(col3_x + col_w/2, col_y, "3.  Analysis engine",
        ha="center", va="center", fontsize=15, color=GREEN, fontweight="bold")
    ax.text(col3_x + col_w/2, col_y - 3, "Agentic-DART  ·  same server or remote",
        ha="center", va="center", fontsize=10, color=TEXT_SEC, style="italic")

    # ─── Column 1: Three collection sources ──────────────────────────────────
    src_h = 13

    # 1a. Falcon (commercial)
    src1_y = 73
    rounded_box(ax, col1_x, src1_y, col_w, src_h, fill=BLUE_BG, edge=BLUE, lw=1.2, radius=0.5)
    ax.text(col1_x + col_w/2, src1_y + src_h - 2.5, "Falcon Forensics",
        ha="center", va="center", fontsize=12, color=BLUE, fontweight="bold")
    ax.text(col1_x + col_w/2, src1_y + src_h - 5, "commercial  ·  Ad-hoc",
        ha="center", va="center", fontsize=9, color=BLUE, style="italic")
    ax.text(col1_x + col_w/2, src1_y + 5.5, "agent push from console",
        ha="center", va="center", fontsize=9.5, color=TEXT_PRI)
    ax.text(col1_x + col_w/2, src1_y + 3, "Tanium  ·  Live Response",
        ha="center", va="center", fontsize=9, color=TEXT_SEC, style="italic")
    ax.text(col1_x + col_w/2, src1_y + 0.8, "the 80% case",
        ha="center", va="center", fontsize=9, color=TEXT_SEC)

    # 1b. Velociraptor
    src2_y = 51
    rounded_box(ax, col1_x, src2_y, col_w, src_h, fill=ORANGE_BG, edge=ORANGE, lw=1.2, radius=0.5)
    ax.text(col1_x + col_w/2, src2_y + src_h - 2.5, "Velociraptor",
        ha="center", va="center", fontsize=12, color=ORANGE, fontweight="bold")
    ax.text(col1_x + col_w/2, src2_y + src_h - 5, "open-source  ·  offline-collector",
        ha="center", va="center", fontsize=9, color=ORANGE, style="italic")
    ax.text(col1_x + col_w/2, src2_y + 5.5, "single binary  ·  zero install",
        ha="center", va="center", fontsize=9.5, color=TEXT_PRI)
    ax.text(col1_x + col_w/2, src2_y + 3, "Win  ·  Linux  ·  macOS",
        ha="center", va="center", fontsize=9, color=TEXT_SEC, style="italic")
    ax.text(col1_x + col_w/2, src2_y + 0.8, "the other 20%",
        ha="center", va="center", fontsize=9, color=TEXT_SEC)

    # 1c. Raw image
    src3_y = 29
    rounded_box(ax, col1_x, src3_y, col_w, src_h, fill=SURFACE, edge=BORDER, lw=1.0, radius=0.5)
    ax.text(col1_x + col_w/2, src3_y + src_h - 2.5, "Raw disk image",
        ha="center", va="center", fontsize=12, color=TEXT_PRI, fontweight="bold")
    ax.text(col1_x + col_w/2, src3_y + src_h - 5, "DD  ·  E01  ·  AFF  ·  VMDK",
        ha="center", va="center", fontsize=9, color=TEXT_SEC, style="italic")
    ax.text(col1_x + col_w/2, src3_y + 5.5, "no host, just an image",
        ha="center", va="center", fontsize=9.5, color=TEXT_PRI)
    ax.text(col1_x + col_w/2, src3_y + 3, "seized  ·  handed over",
        ha="center", va="center", fontsize=9, color=TEXT_SEC, style="italic")
    ax.text(col1_x + col_w/2, src3_y + 0.8, "the legacy case",
        ha="center", va="center", fontsize=9, color=TEXT_SEC)

    # ─── Column 2: Adapter ───────────────────────────────────────────────────
    adapt_x, adapt_y, adapt_w, adapt_h = col2_x, 51, section_w, 35
    rounded_box(ax, adapt_x, adapt_y, adapt_w, adapt_h, fill=PURPLE_BG, edge=PURPLE, lw=1.5, radius=0.7)
    ax.text(adapt_x + adapt_w/2, adapt_y + adapt_h - 4, "dart-collector-adapter",
        ha="center", va="center", fontsize=14, color=PURPLE, fontweight="bold",
        family="DejaVu Sans Mono")
    ax.text(adapt_x + adapt_w/2, adapt_y + adapt_h - 7, "stdlib-only Python  ·  MIT  ·  full test suite green",
        ha="center", va="center", fontsize=10, color=PURPLE, style="italic")

    funcs = [
        ("classify artifacts", "Prefetch · Amcache · Registry · EventLogs · ..."),
        ("safe-path stream copy", "evidence_root sandbox  ·  no escapes"),
        ("SHA-256 each file", "chain-of-custody seed"),
        ("write manifest.json", "case_id  ·  source  ·  adapter version"),
    ]
    func_y0 = adapt_y + adapt_h - 12
    for i, (name, sub) in enumerate(funcs):
        y = func_y0 - i * 5.5
        ax.text(adapt_x + 4, y, "•", ha="left", va="center", fontsize=14, color=PURPLE, fontweight="bold")
        ax.text(adapt_x + 6.5, y, name, ha="left", va="center", fontsize=11, color=TEXT_PRI, fontweight="bold")
        ax.text(adapt_x + 6.5, y - 2.2, sub, ha="left", va="center", fontsize=9, color=TEXT_SEC, style="italic")

    # evidence_root
    out_x, out_y, out_w, out_h = col2_x, 26, section_w, 20
    rounded_box(ax, out_x, out_y, out_w, out_h, fill=GREEN_BG, edge=GREEN, lw=1.2, radius=0.5)
    ax.text(out_x + out_w/2, out_y + out_h - 3, "evidence_root/",
        ha="center", va="center", fontsize=13, color=GREEN, fontweight="bold",
        family="DejaVu Sans Mono")
    ax.text(out_x + out_w/2, out_y + out_h - 5.5, "well-named, flat, ready for analysis",
        ha="center", va="center", fontsize=9.5, color=GREEN, style="italic")

    cells = [["Prefetch", "Amcache"], ["Registry", "EventLogs"], ["Browser", "WebLogs"], ["MFT", "Other"]]
    cw = out_w / 4
    cell_y = out_y + 4
    for i, col in enumerate(cells):
        cx = out_x + i * cw + cw/2
        for j, item in enumerate(col):
            ax.text(cx, cell_y + 4 - j * 2.5, item,
                ha="center", va="center", fontsize=10, color=TEXT_PRI,
                family="DejaVu Sans Mono")

    # ─── Column 3: Agentic-DART ──────────────────────────────────────────────
    da_y, da_h = 63, 23
    rounded_box(ax, col3_x, da_y, col_w, da_h, fill=GREEN_BG, edge=GREEN, lw=1.2, radius=0.5)
    ax.text(col3_x + col_w/2, da_y + da_h - 3, "dart_agent",
        ha="center", va="center", fontsize=13, color=GREEN, fontweight="bold",
        family="DejaVu Sans Mono")
    ax.text(col3_x + col_w/2, da_y + da_h - 5.5, "autonomous DFIR engine",
        ha="center", va="center", fontsize=9.5, color=GREEN, style="italic")
    for i, item in enumerate(["reads evidence_root", "runs 10-phase playbook",
                              "70 typed read-only MCP tools", "extends SHA-256 audit chain"]):
        ax.text(col3_x + col_w/2, da_y + 11 - i*2.5, item,
            ha="center", va="center", fontsize=10, color=TEXT_PRI)

    # findings
    fj_y, fj_h = 34, 23
    rounded_box(ax, col3_x, fj_y, col_w, fj_h, fill=SURFACE, edge=BORDER, lw=1.0, radius=0.5)
    ax.text(col3_x + col_w/2, fj_y + fj_h - 3, "findings.json",
        ha="center", va="center", fontsize=13, color=TEXT_PRI, fontweight="bold",
        family="DejaVu Sans Mono")
    ax.text(col3_x + col_w/2, fj_y + fj_h - 5.5, "+ audit.jsonl  +  report.md",
        ha="center", va="center", fontsize=9.5, color=TEXT_SEC, style="italic")
    for i, item in enumerate(["typed findings", "tamper-evident chain",
                              "from manifest seed", "judge-readable report"]):
        ax.text(col3_x + col_w/2, fj_y + 11 - i*2.5, item,
            ha="center", va="center", fontsize=10, color=TEXT_PRI)

    # Arrows col 1 → col 2
    arrow(ax, col1_x + col_w + 0.5, src1_y + src_h/2,
              adapt_x - 0.5, adapt_y + adapt_h - 5,
          color=BLUE, lw=1.5, label="JSON / CSV", label_offset=(0, 1.5))
    arrow(ax, col1_x + col_w + 0.5, src2_y + src_h/2,
              adapt_x - 0.5, adapt_y + adapt_h/2,
          color=ORANGE, lw=1.5, label="offline ZIP", label_offset=(0, 1.5))
    arrow(ax, col1_x + col_w + 0.5, src3_y + src_h/2,
              adapt_x - 0.5, adapt_y + 5,
          color=TEXT_SEC, lw=1.2, label="image mount", label_offset=(0, 1.5))

    # adapter → evidence_root
    arrow(ax, out_x + out_w/2, adapt_y - 0.5,
              out_x + out_w/2, out_y + out_h + 0.5,
          color=PURPLE, lw=1.5)

    # evidence_root → dart_agent (대각선 위로, 라벨은 화살표 위쪽에 띄움)
    arrow(ax, out_x + out_w + 0.5, out_y + out_h/2,
              col3_x - 0.5, da_y + da_h/2,
          color=GREEN, lw=1.5)
    # 'read' 라벨 — 화살표 중점 위로 명확히 띄우기 (findings 박스와 안 겹치게)
    mid_x = (out_x + out_w + col3_x) / 2
    mid_y = (out_y + out_h/2 + da_y + da_h/2) / 2
    ax.text(mid_x, mid_y + 2.2, "read",
        ha="center", va="center", fontsize=10, color=GREEN, style="italic",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=BG, edgecolor="none"))

    # dart_agent → findings
    arrow(ax, col3_x + col_w/2, da_y - 0.5,
              col3_x + col_w/2, fj_y + fj_h + 0.5,
          color=GREEN, lw=1.5)

    # Footer
    ax.plot([10, 170], [16, 16], color=BORDER_MUTED, linewidth=0.8)
    ax.text(90, 13, "Two collection channels  ·  one normalised contract  ·  one analysis engine",
        ha="center", va="center", fontsize=12, color=TEXT_PRI, style="italic")
    ax.text(90, 9, "The analysis engine does not care which collector produced the data.",
        ha="center", va="center", fontsize=11, color=TEXT_SEC, style="italic")
    ax.text(90, 5,
        "no incident-host install (Velociraptor binary)  ·  stdlib-only Python adapter  ·  MIT",
        ha="center", va="center", fontsize=9, color=TEXT_SEC)

    out_path = OUT / "arch.png"
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=BG, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"  ok  {out_path.name}  ({out_path.stat().st_size // 1024} kB)")


# ════════════════════════════════════════════════════════════════════════════
# ROADMAP — phases with v0.2 Falcon adapter
# ════════════════════════════════════════════════════════════════════════════
def gen_roadmap():
    W, H = 1800, 760
    fig, ax = plt.subplots(figsize=(W/FIG_DPI, H/FIG_DPI), facecolor=BG, dpi=FIG_DPI)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 180); ax.set_ylim(0, 76)
    ax.axis("off")

    # Title
    ax.text(90, 71, "agentic-dart-collector-adapter",
        ha="center", va="center", fontsize=22, color=TEXT_PRI, fontweight="bold")
    ax.text(90, 67, "phase roadmap  ·  intentionally narrow scope",
        ha="center", va="center", fontsize=12, color=TEXT_SEC, style="italic")
    ax.plot([10, 170], [63.5, 63.5], color=BORDER_MUTED, linewidth=0.8)

    phases = [
        {"version": "v0.1", "stage": "current",
         "tag_fill": GREEN_BG, "tag_edge": GREEN, "tag_color": GREEN,
         "title": "Velociraptor ZIP", "subtitle": "→ evidence_root",
         "body": ["single offline-collector ZIP in",
                  "evidence_root/ + manifest.json out",
                  "SHA-256 chain-of-custody seed",
                  "full test suite green  ·  CI green"],
         "footer": "shipped 2026-05"},
        {"version": "v0.2", "stage": "next",
         "tag_fill": BLUE_BG, "tag_edge": BLUE, "tag_color": BLUE,
         "title": "Falcon Forensics input", "subtitle": "+ Tanium parity",
         "body": ["second input format module",
                  "CrowdStrike Falcon ad-hoc export",
                  "JSON / CSV → evidence_root",
                  "unifies commercial + OSS streams"],
         "footer": "post-SANS  ·  FY26"},
        {"version": "v0.3", "stage": "later",
         "tag_fill": PURPLE_BG, "tag_edge": PURPLE, "tag_color": PURPLE,
         "title": "Sidecar generation", "subtitle": "EZTools auto-invoke",
         "body": ["PECmd  ·  AmcacheParser",
                  "EvtxECmd  ·  RECmd",
                  "called when binary present locally",
                  "parsed JSON merged into manifest"],
         "footer": "after Phase 2 stable"},
        {"version": "v0.4", "stage": "later",
         "tag_fill": ORANGE_BG, "tag_edge": ORANGE, "tag_color": ORANGE,
         "title": "Cross-platform parity", "subtitle": "macOS + Linux artefacts",
         "body": ["Unified log  ·  KnowledgeC  ·  FSEvents",
                  "auditd  ·  journald  ·  launchd",
                  "match Windows classification depth",
                  "no separate code paths"],
         "footer": "long-tail enhancement"},
    ]

    col_w = 40
    gap = 2
    total_w = len(phases) * col_w + (len(phases) - 1) * gap
    start_x = (180 - total_w) / 2

    for i, p in enumerate(phases):
        x = start_x + i * (col_w + gap)

        # Tag box
        tag_h = 7
        tag_y = 51
        rounded_box(ax, x, tag_y, col_w, tag_h, fill=p["tag_fill"], edge=p["tag_edge"], lw=1.2, radius=0.4)
        ax.text(x + col_w/2, tag_y + tag_h - 2, f"{p['version']}",
            ha="center", va="center", fontsize=15, color=p["tag_color"], fontweight="bold",
            family="DejaVu Sans Mono")
        ax.text(x + col_w/2, tag_y + 2, p["stage"],
            ha="center", va="center", fontsize=10, color=p["tag_color"], style="italic")

        # Body box
        body_y = 16
        body_h = 32
        rounded_box(ax, x, body_y, col_w, body_h, fill=SURFACE_2, edge=BORDER, lw=1.0, radius=0.4)

        ax.text(x + col_w/2, body_y + body_h - 4, p["title"],
            ha="center", va="center", fontsize=12, color=TEXT_PRI, fontweight="bold")
        ax.text(x + col_w/2, body_y + body_h - 7, p["subtitle"],
            ha="center", va="center", fontsize=10, color=p["tag_color"], style="italic")

        # Hairline
        ax.plot([x + 4, x + col_w - 4], [body_y + body_h - 9.5, body_y + body_h - 9.5],
            color=BORDER_MUTED, linewidth=0.6)

        # Bullets
        for j, item in enumerate(p["body"]):
            ax.text(x + col_w/2, body_y + body_h - 12 - j*3, item,
                ha="center", va="center", fontsize=9.5, color=TEXT_SEC)

        # Footer label
        ax.text(x + col_w/2, body_y + 1.8, p["footer"],
            ha="center", va="center", fontsize=8.5, color=p["tag_color"], style="italic")

        if i < len(phases) - 1:
            arrow(ax,
                x + col_w + 0.3, tag_y + tag_h/2,
                x + col_w + gap - 0.3, tag_y + tag_h/2,
                color=TEXT_SEC, lw=1.2)

    # Footer
    ax.plot([10, 170], [11, 11], color=BORDER_MUTED, linewidth=0.8)
    ax.text(90, 8,
        "Intentionally narrow scope  ·  one clear job per phase  ·  no scope creep",
        ha="center", va="center", fontsize=11, color=TEXT_PRI, style="italic")
    ax.text(90, 4,
        "Two collection channels (commercial agent + OSS offline collector) feed one normalised evidence_root contract.",
        ha="center", va="center", fontsize=9.5, color=TEXT_SEC, style="italic")

    out_path = OUT / "roadmap.png"
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=BG, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"  ok  {out_path.name}  ({out_path.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    print("[generating light-theme GitHub Pages style diagrams]\n")
    gen_arch()
    gen_roadmap()
    print(f"\ndone -> {OUT}")
