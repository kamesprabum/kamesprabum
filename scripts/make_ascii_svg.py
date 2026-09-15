#!/usr/bin/env python3
"""
Convert a prepped portrait image (source-prepped.png) into a self-typing monochrome ASCII-art SVG.
Width: 370px, Height: 440px.
Pairs side-by-side with info-card.svg (490px) to sum to 860px.
"""
import html
import os
import sys
from PIL import Image, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "kamesprabu-ascii.svg")

COLS = 58
ROWS = 36
CELL_W = 5.8
CELL_H = 9.8

RAMP = " .`:-=+*cs#%@"  # Bright (sparse) -> Dark (dense). Leading space ensures background is blank.

PAD_X = 16
PAD_Y = 14
TITLEBAR_H = 34
STATUS_H = 26

CANVAS_W = 370
CANVAS_H = 440

BG = "#0d1117"
BG_CARD = "#161b22"
BORDER = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#e6edf3"         # Monochrome terminal font color
ACCENT_GREEN = "#39d353"

GAMMA = 1.15
WHITE_FLOOR = 0.82

ROW_DUR = 0.08
STAGGER = 0.065


def get_ascii_rows():
    if os.path.exists(SRC):
        print(f"Reading prepped image: {SRC}")
        im = Image.open(SRC).convert("L")
        im = ImageEnhance.Brightness(im).enhance(1.0)
        im = ImageEnhance.Contrast(im).enhance(1.1)
        im = im.resize((COLS, ROWS), Image.Resampling.LANCZOS)
        px = im.load()

        rows = []
        ramp_len = len(RAMP)
        for y in range(ROWS):
            chars = []
            for x in range(COLS):
                lum = px[x, y] / 255.0
                lum = pow(lum, GAMMA)
                if lum >= WHITE_FLOOR:
                    chars.append(" ")
                    continue
                idx = int((1.0 - lum) * (ramp_len - 1))
                idx = max(0, min(ramp_len - 1, idx))
                chars.append(RAMP[idx])
            rows.append("".join(chars))
        return rows
    else:
        print(f"Source prepped image '{SRC}' not found. Using default terminal developer avatar pattern.")
        # Elegant fallback developer avatar pattern until photo is generated
        pattern = [
            "                                                          ",
            "                  .::::::::::::::::::.                    ",
            "               .::::::::::::::::::::::::.                 ",
            "             .::::::::::::::::::::::::::::.               ",
            "            ::::::::::::::::::::::::::::::::              ",
            "           ::::::::::::::::::::::::::::::::::             ",
            "          ::::::::::::::::::::::::::::::::::::            ",
            "          ::::::::::::::::::::::::::::::::::::            ",
            "          ::::::::::::::::::::::::::::::::::::            ",
            "          .::::::::::::::::::::::::::::::::::.            ",
            "           ::::::::::::::::::::::::::::::::::             ",
            "            .::::::::::::::::::::::::::::::.              ",
            "              .::::::::::::::::::::::::::.                ",
            "                 .::::::::::::::::::::.                   ",
            "                     .::::::::::::.                       ",
            "             ..::::::::::::::::::::::::::..               ",
            "         .::::::::::::::::::::::::::::::::::::.           ",
            "       .::::::::::::::::::::::::::::::::::::::::.         ",
            "      ::::::::::::::::::::::::::::::::::::::::::::        ",
            "     ::::::::::::::::::::::::::::::::::::::::::::::       ",
            "    ::::::::::::::::::::::::::::::::::::::::::::::::      ",
            "    ::::::::::::::::::::::::::::::::::::::::::::::::      ",
            "   ::::::::::::::::::::::::::::::::::::::::::::::::::     ",
            "   ::::::::::::::::::::::::::::::::::::::::::::::::::     ",
            "   ::::::::::::::::::::::::::::::::::::::::::::::::::     ",
            "   ::::::::::::::::::::::::::::::::::::::::::::::::::     ",
            "   ::::::::::::::::::::::::::::::::::::::::::::::::::     ",
            "   ::::::::::::::::::::::::::::::::::::::::::::::::::     ",
            "   ::::::::::::::::::::::::::::::::::::::::::::::::::     ",
            "    ::::::::::::::::::::::::::::::::::::::::::::::::      ",
            "    ::::::::::::::::::::::::::::::::::::::::::::::::      ",
            "     ::::::::::::::::::::::::::::::::::::::::::::::       ",
            "      ::::::::::::::::::::::::::::::::::::::::::::        ",
            "       ::::::::::::::::::::::::::::::::::::::::::         ",
            "        .::::::::::::::::::::::::::::::::::::::.          ",
            "                                                          ",
        ]
        # Pad or trim to COLS x ROWS
        res = []
        for r in pattern[:ROWS]:
            r_str = (r + " " * COLS)[:COLS]
            res.append(r_str)
        while len(res) < ROWS:
            res.append(" " * COLS)
        return res


def generate_svg():
    rows = get_ascii_rows()
    text_elements = []
    
    start_y = TITLEBAR_H + PAD_Y + 12
    total_dur = len(rows) * STAGGER + ROW_DUR

    for idx, row_str in enumerate(rows):
        y_pos = start_y + idx * CELL_H
        escaped_str = html.escape(row_str).replace(" ", "&#160;")
        delay = round(idx * STAGGER, 3)
        
        # Each row wipes in from left to right
        text_elements.append(
            f'<g class="row" style="animation-delay: {delay}s;">'
            f'<text x="{PAD_X}" y="{y_pos:.1f}" class="ascii-font">{escaped_str}</text>'
            f'</g>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="{CANVAS_W}" height="{CANVAS_H}">
  <defs>
    <style>
      @keyframes wipeIn {{
        0% {{
          clip-path: inset(0 100% 0 0);
          opacity: 0.1;
        }}
        1% {{
          opacity: 1;
        }}
        100% {{
          clip-path: inset(0 0 0 0);
          opacity: 1;
        }}
      }}
      .bg {{ fill: {BG}; stroke: {BORDER}; stroke-width: 1px; rx: 8px; }}
      .titlebar {{ fill: {BG_CARD}; }}
      .titlebar-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; fill: {TITLE_TEXT}; font-weight: 500; }}
      .ascii-font {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        font-size: 8.6px;
        fill: {INK};
        white-space: pre;
        letter-spacing: 0.2px;
      }}
      .row {{
        animation: wipeIn {ROW_DUR}s ease-out forwards;
        clip-path: inset(0 100% 0 0);
      }}
      .status-text {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        font-size: 11px;
        fill: {TITLE_TEXT};
      }}
      .status-active {{
        fill: {ACCENT_GREEN};
        font-weight: 600;
      }}
    </style>
  </defs>

  <!-- Background -->
  <rect class="bg" width="{CANVAS_W}" height="{CANVAS_H}" />

  <!-- Title bar -->
  <path d="M 0,8 Q 0,0 8,0 L {CANVAS_W - 8},0 Q {CANVAS_W},0 {CANVAS_W},8 L {CANVAS_W},{TITLEBAR_H} L 0,{TITLEBAR_H} Z" fill="{BG_CARD}" stroke="{BORDER}" stroke-width="1px" />
  <circle cx="{PAD_X}" cy="{TITLEBAR_H // 2}" r="5" fill="#ff5f56" />
  <circle cx="{PAD_X + 14}" cy="{TITLEBAR_H // 2}" r="5" fill="#ffbd2e" />
  <circle cx="{PAD_X + 28}" cy="{TITLEBAR_H // 2}" r="5" fill="#27c93f" />
  <text class="titlebar-text" x="{PAD_X + 44}" y="{TITLEBAR_H // 2 + 4}">portrait.ascii</text>

  <!-- ASCII Art Rows -->
  <g>
    {' '.join(text_elements)}
  </g>

  <!-- Footer Status Bar -->
  <g>
    <line x1="{PAD_X}" y1="{CANVAS_H - STATUS_H}" x2="{CANVAS_W - PAD_X}" y2="{CANVAS_H - STATUS_H}" stroke="{BORDER}" />
    <text x="{PAD_X}" y="{CANVAS_H - 10}" class="status-text">[MODE: <tspan class="status-active">ONLINE</tspan>] 58x36 ASCII</text>
    <text x="{CANVAS_W - PAD_X - 60}" y="{CANVAS_H - 10}" class="status-text">100%</text>
  </g>
</svg>"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT_PATH} successfully.")


def main():
    generate_svg()


if __name__ == "__main__":
    main()
