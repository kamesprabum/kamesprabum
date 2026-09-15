#!/usr/bin/env python3
"""
Generate a Neofetch-style developer information card SVG for kamesprabum.
Width: 490px.
Pairs side-by-side with kamesprabu-ascii.svg (370px) to sum to 860px.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "info-card.svg")

WIDTH = 490
HEIGHT = 440
PAD_X = 22
PAD_Y = 18
TITLEBAR_H = 34

BG = "#0d1117"
BG_CARD = "#161b22"
BORDER = "#30363d"
TEXT_MAIN = "#e6edf3"
TEXT_MUTED = "#7d8590"
COLOR_KEY = "#38bdf8"       # Cyan
COLOR_AI = "#a855f7"        # Purple
COLOR_CLOUD = "#f59e0b"     # Amber
COLOR_DEVOPS = "#10b981"    # Emerald
COLOR_CORE = "#3b82f6"      # Blue


def generate_svg():
    info_rows = [
        ("Host", "cloud-devops-engine", "#7d8590"),
        ("OS", "Linux (Ubuntu / Alpine)", "#e6edf3"),
        ("Direction", "Python + AI + Cloud + DevOps", "#38bdf8"),
        ("Core Stack", "Python, Linux, Git, GitHub, REST APIs", "#34d399"),
        ("Cloud (AWS)", "Architecture, Infrastructure, Deployment", "#fbbf24"),
        ("DevOps / CI-CD", "Docker, Jenkins, GitHub Actions, IaC", "#60a5fa"),
        ("Orchestration", "Kubernetes (Exploring & Building)", "#818cf8"),
        ("AI Focus", "AI Engineering, LLMs, Machine Learning, Agents", "#c084fc"),
        ("Methodology", "CI/CD, Infrastructure as Code, Automation", "#a7f3d0"),
        ("Status", "Actively Building & Scaling Systems", "#4ade80"),
    ]

    lines_svg = []
    start_y = TITLEBAR_H + 34
    line_height = 28

    # User title line
    user_line = (
        f'<g class="line" style="animation-delay: 0.1s;">'
        f'<text x="{PAD_X}" y="{start_y}" class="title-user">kamesprabum</text>'
        f'<text x="{PAD_X + 115}" y="{start_y}" class="title-at">@</text>'
        f'<text x="{PAD_X + 130}" y="{start_y}" class="title-host">gravity-dev</text>'
        f'</g>'
    )
    lines_svg.append(user_line)

    # Separator rule
    sep_y = start_y + 12
    sep_line = (
        f'<g class="line" style="animation-delay: 0.2s;">'
        f'<line x1="{PAD_X}" y1="{sep_y}" x2="{WIDTH - PAD_X}" y2="{sep_y}" stroke="{BORDER}" stroke-dasharray="4,4" />'
        f'</g>'
    )
    lines_svg.append(sep_line)

    curr_y = sep_y + 24
    for idx, (key, val, val_color) in enumerate(info_rows):
        delay = round(0.3 + idx * 0.08, 2)
        escaped_key = html.escape(key)
        escaped_val = html.escape(val)
        row_svg = (
            f'<g class="line" style="animation-delay: {delay}s;">'
            f'<text x="{PAD_X}" y="{curr_y}" class="key-text">{escaped_key}:</text>'
            f'<text x="{PAD_X + 125}" y="{curr_y}" class="val-text" fill="{val_color}">{escaped_val}</text>'
            f'</g>'
        )
        lines_svg.append(row_svg)
        curr_y += line_height

    # Color palette blocks at the bottom
    palette_y = HEIGHT - 24
    palette_colors = ["#1f2937", "#ef4444", "#f97316", "#f59e0b", "#10b981", "#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899", "#f3f4f6"]
    palette_rects = []
    box_w = 20
    box_h = 10
    start_p_x = PAD_X
    for pi, col in enumerate(palette_colors):
        px = start_p_x + pi * (box_w + 6)
        palette_rects.append(f'<rect x="{px}" y="{palette_y}" width="{box_w}" height="{box_h}" rx="2" fill="{col}" />')

    palette_group = (
        f'<g class="line" style="animation-delay: {round(0.3 + len(info_rows) * 0.08, 2)}s;">'
        f'{" ".join(palette_rects)}'
        f'</g>'
    )
    lines_svg.append(palette_group)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
  <defs>
    <style>
      @keyframes slideIn {{
        0% {{
          opacity: 0;
          transform: translateY(8px);
        }}
        100% {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
      .bg {{ fill: {BG}; stroke: {BORDER}; stroke-width: 1px; rx: 8px; }}
      .titlebar {{ fill: {BG_CARD}; }}
      .titlebar-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; fill: {TEXT_MUTED}; font-weight: 500; }}
      .title-user {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 15px; font-weight: 700; fill: #38bdf8; }}
      .title-at {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 15px; fill: {TEXT_MUTED}; }}
      .title-host {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 15px; font-weight: 700; fill: #a855f7; }}
      .key-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; font-weight: 600; fill: {COLOR_KEY}; }}
      .val-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; font-weight: 400; }}
      .line {{
        animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
      }}
    </style>
  </defs>

  <!-- Background -->
  <rect class="bg" width="{WIDTH}" height="{HEIGHT}" />

  <!-- Title bar -->
  <path d="M 0,8 Q 0,0 8,0 L {WIDTH - 8},0 Q {WIDTH},0 {WIDTH},8 L {WIDTH},{TITLEBAR_H} L 0,{TITLEBAR_H} Z" fill="{BG_CARD}" stroke="{BORDER}" stroke-width="1px" />
  <circle cx="{PAD_X}" cy="{TITLEBAR_H // 2}" r="5" fill="#ff5f56" />
  <circle cx="{PAD_X + 14}" cy="{TITLEBAR_H // 2}" r="5" fill="#ffbd2e" />
  <circle cx="{PAD_X + 28}" cy="{TITLEBAR_H // 2}" r="5" fill="#27c93f" />
  <text class="titlebar-text" x="{PAD_X + 44}" y="{TITLEBAR_H // 2 + 4}">neofetch --profile</text>

  <!-- Content Lines -->
  {' '.join(lines_svg)}
</svg>"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT_PATH} successfully.")


def main():
    generate_svg()


if __name__ == "__main__":
    main()
