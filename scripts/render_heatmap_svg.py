#!/usr/bin/env python3
"""
Render data/contributions.json into an animated, dark terminal GitHub contribution heatmap SVG.
Outputs: contrib-heatmap.svg (width 860px).
"""
import datetime
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# Terminal & Heatmap Color Palette
PALETTE = [
    "#161b22",  # 0: Empty
    "#0e4429",  # 1: Low
    "#006d32",  # 2: Medium-low
    "#26a641",  # 3: Medium
    "#39d353",  # 4: High
    "#5bf58d",  # 5: Peak / Neon
]

CELL_SIZE = 11
GAP = 3
STEP = CELL_SIZE + GAP
PAD_X = 24
PAD_Y = 20
LEFT_LABEL_W = 28
TOP_LABEL_H = 20
TITLEBAR_H = 34
STATS_H = 48

CANVAS_W = 860
BG = "#0d1117"
BG_CARD = "#161b22"
BORDER_COLOR = "#30363d"
TEXT_PRIMARY = "#e6edf3"
TEXT_MUTED = "#7d8590"
ACCENT_GREEN = "#39d353"
ACCENT_CYAN = "#38bdf8"
ACCENT_GOLD = "#fbbf24"


def level_for(count):
    if count <= 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 10:
        return 3
    if count <= 20:
        return 4
    return 5


def build_grid(days):
    if not days:
        # Dummy 53 weeks fallback
        return [[(None, 0, 0) for _ in range(7)] for _ in range(53)]

    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # Sunday = 0, Monday = 1, etc.
    
    grid = []
    col = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    
    # Cap or pad to at most 53 columns
    if len(grid) > 53:
        grid = grid[-53:]
    return grid


def render(data):
    days = data.get("days", [])
    grid = build_grid(days)
    n_cols = len(grid)
    
    art_w = n_cols * STEP
    art_h = 7 * STEP
    
    # Calculate month labels
    month_labels = []
    seen_months = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None or cell[0] is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    total = data.get("total", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    username = data.get("username", "kamesprabum")
    
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + STATS_H + PAD_Y * 2
    
    # Generate SVG Cells with CSS animations
    rects_svg = []
    for ci, column in enumerate(grid):
        for ri, cell in enumerate(column):
            if cell is None or cell[0] is None:
                continue
            date_str, count, lvl = cell
            x = PAD_X + LEFT_LABEL_W + ci * STEP
            y = TITLEBAR_H + TOP_LABEL_H + ri * STEP
            color = PALETTE[lvl]
            delay = round(ci * 0.016 + ri * 0.032, 3)
            
            rects_svg.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'rx="2.5" fill="{color}" style="animation-delay:{delay}s">'
                f'<title>{date_str}: {count} contribution{"s" if count != 1 else ""}</title>'
                f'</rect>'
            )

    # Month Labels SVG
    months_svg = []
    for ci, name in month_labels:
        x = PAD_X + LEFT_LABEL_W + ci * STEP
        y = TITLEBAR_H + TOP_LABEL_H - 7
        months_svg.append(f'<text class="lbl" x="{x}" y="{y}">{name}</text>')

    # Weekday Labels SVG
    day_labels_svg = [
        f'<text class="lbl" x="{PAD_X + 2}" y="{TITLEBAR_H + TOP_LABEL_H + 1 * STEP + 9}">Mon</text>',
        f'<text class="lbl" x="{PAD_X + 2}" y="{TITLEBAR_H + TOP_LABEL_H + 3 * STEP + 9}">Wed</text>',
        f'<text class="lbl" x="{PAD_X + 2}" y="{TITLEBAR_H + TOP_LABEL_H + 5 * STEP + 9}">Fri</text>',
    ]

    # Legend SVG
    legend_x = CANVAS_W - PAD_X - (len(PALETTE) * 14 + 75)
    legend_y = canvas_h - PAD_Y - 14
    legend_svg = [f'<text class="lbl" x="{legend_x}" y="{legend_y + 9}">Less</text>']
    for idx, c in enumerate(PALETTE):
        bx = legend_x + 32 + idx * 14
        legend_svg.append(f'<rect x="{bx}" y="{legend_y}" width="10" height="10" rx="2" fill="{c}" />')
    legend_svg.append(f'<text class="lbl" x="{legend_x + 32 + len(PALETTE) * 14 + 6}" y="{legend_y + 9}">More</text>')

    stats_y = canvas_h - PAD_Y - 14
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {canvas_h}" width="{CANVAS_W}" height="{canvas_h}">
  <defs>
    <style>
      @keyframes popIn {{
        0% {{ opacity: 0; transform: scale(0.65); }}
        70% {{ opacity: 1; transform: scale(1.08); }}
        100% {{ opacity: 1; transform: scale(1); }}
      }}
      @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
      }}
      .bg {{ fill: {BG}; stroke: {BORDER_COLOR}; stroke-width: 1px; rx: 8px; }}
      .titlebar {{ fill: {BG_CARD}; rx: 8px; }}
      .title-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; fill: {TEXT_MUTED}; font-weight: 500; }}
      .lbl {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 10px; fill: {TEXT_MUTED}; }}
      .stat-val {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 13px; font-weight: 700; fill: {ACCENT_GREEN}; }}
      .stat-lbl {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; fill: {TEXT_MUTED}; }}
      .c {{
        transform-origin: center;
        animation: popIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
      }}
      .fade {{ animation: fadeIn 0.8s ease forwards; }}
    </style>
  </defs>

  <!-- Background Canvas -->
  <rect class="bg" width="{CANVAS_W}" height="{canvas_h}" />

  <!-- Terminal Window Bar -->
  <path d="M 0,8 Q 0,0 8,0 L {CANVAS_W - 8},0 Q {CANVAS_W},0 {CANVAS_W},8 L {CANVAS_W},{TITLEBAR_H} L 0,{TITLEBAR_H} Z" fill="{BG_CARD}" stroke="{BORDER_COLOR}" stroke-width="1px" />
  <circle cx="{PAD_X}" cy="{TITLEBAR_H // 2}" r="5" fill="#ff5f56" />
  <circle cx="{PAD_X + 14}" cy="{TITLEBAR_H // 2}" r="5" fill="#ffbd2e" />
  <circle cx="{PAD_X + 28}" cy="{TITLEBAR_H // 2}" r="5" fill="#27c93f" />
  <text class="title-text" x="{PAD_X + 44}" y="{TITLEBAR_H // 2 + 4}">{html.escape(username)}@github: ~ $ ./contributions.sh --year</text>

  <!-- Month & Day Labels -->
  <g class="fade">
    {' '.join(months_svg)}
    {' '.join(day_labels_svg)}
  </g>

  <!-- Heatmap Cells -->
  <g>
    {' '.join(rects_svg)}
  </g>

  <!-- Stats & Legend Footer -->
  <g class="fade">
    <text class="stat-lbl" x="{PAD_X}" y="{stats_y + 9}">Contributions (Past Year): <tspan class="stat-val">{total:,}</tspan></text>
    <text class="stat-lbl" x="{PAD_X + 230}" y="{stats_y + 9}">Current Streak: <tspan class="stat-val" fill="{ACCENT_CYAN}">{current_streak} days</tspan></text>
    <text class="stat-lbl" x="{PAD_X + 420}" y="{stats_y + 9}">Longest Streak: <tspan class="stat-val" fill="{ACCENT_GOLD}">{longest_streak} days</tspan></text>
    {' '.join(legend_svg)}
  </g>
</svg>"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT_PATH} successfully.")


def main():
    if not os.path.exists(IN_PATH):
        print(f"Contribution data {IN_PATH} not found. Generating default mock/live fetch...", file=sys.stderr)
        data = {"username": "kamesprabum", "total": 0, "current_streak": 0, "longest_streak": 0, "days": []}
    else:
        with open(IN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    render(data)


if __name__ == "__main__":
    main()
