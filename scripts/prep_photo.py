#!/usr/bin/env python3
"""
Prepare a portrait photo for clean ASCII conversion:
  1. Remove background (rembg) so the subject is cleanly isolated
  2. Boost LOCAL contrast (OpenCV CLAHE) so facial features, highlights, and shadows emerge clearly
  3. Composite the subject onto pure white so background pixels map to empty space (blank glyphs in ASCII ramp)

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Usage:
    python scripts/prep_photo.py [source-photo.jpg] [source-prepped.png]
"""
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INP = os.path.join(HERE, "..", "source-photo.jpg")
DEFAULT_OUT = os.path.join(HERE, "..", "source-prepped.png")


def prep_image(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input photo '{input_path}' not found.", file=sys.stderr)
        print("Please place your portrait photo in the root folder as 'source-photo.jpg' or provide its path.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading input photo: {input_path}")
    raw_img = Image.open(input_path)

    # 1. Remove background using rembg
    try:
        from rembg import remove
        print("Removing background with rembg...")
        cutout = remove(raw_img)
    except Exception as e:
        print(f"Warning: rembg failed or not installed ({e}). Proceeding with direct image RGBA conversion.", file=sys.stderr)
        cutout = raw_img.convert("RGBA")

    # 2. Composite over solid white background
    print("Compositing subject onto white background...")
    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("L")  # Convert to grayscale

    # 3. Apply CLAHE local contrast with OpenCV
    try:
        import cv2
        print("Applying OpenCV CLAHE (Contrast-Limited Adaptive Histogram Equalization)...")
        gray_np = np.array(composited)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced_np = clahe.apply(gray_np)
        final_img = Image.fromarray(enhanced_np)
    except Exception as e:
        print(f"Warning: OpenCV CLAHE step skipped ({e}). Using standard contrast enhancement.")
        from PIL import ImageEnhance
        final_img = ImageEnhance.Contrast(composited).enhance(1.4)

    final_img.save(output_path, "PNG")
    print(f"Prepped image saved successfully to: {output_path}")


def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INP
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    prep_image(inp, out)


if __name__ == "__main__":
    main()
