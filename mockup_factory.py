import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List

from config import MOCKUPS_DIR


ASSETS_BG = Path("assets/mockup_backgrounds")
PHONE_FRAME = ASSETS_BG / "phone_frame.png"


def _imagemagick_available() -> str:
    # returns path to 'magick' or 'convert' if available, else empty
    mag = shutil.which("magick")
    if mag:
        return mag
    conv = shutil.which("convert")
    return conv or ""


def _imagemagick_composite(inner_path: str, frame_path: str, out_path: str) -> bool:
    """Use ImageMagick to composite `inner_path` into `frame_path` centered and write to out_path.

    Returns True on success, False otherwise.
    """
    tool = _imagemagick_available()
    if not tool:
        return False
    # Build a simple composite command that centers inner into frame
    try:
        if os.path.basename(tool).lower() == "magick":
            cmd = [tool, "convert", frame_path, inner_path, "-gravity", "center", "-composite", out_path]
        else:
            cmd = [tool, frame_path, inner_path, "-gravity", "center", "-composite", out_path]
        subprocess.run(cmd, check=True)
        return True
    except Exception:
        return False


def _apply_perspective(im: Image.Image, magnitude: float = 0.12) -> Image.Image:
    # Create a subtle perspective warp to make mockups feel more realistic.
    w, h = im.size
    shift = int(w * magnitude)
    coeffs = _perspective_coeffs(
        (0, 0, w, 0, w, h, 0, h),
        (shift, 0, w - shift, 0, w, h, 0, h)
    )
    return im.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)


def _perspective_coeffs(src, dst):
    # Computes coefficients for PIL perspective transform.
    matrix = []
    for p1, p2 in zip(zip(*[iter(src)]*2), zip(*[iter(dst)]*2)):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = matrix
    B = [c for pair in zip(*[iter(dst)]*2) for c in pair]
    import numpy as np
    res = np.linalg.lstsq(np.array(A, dtype=float), np.array(B, dtype=float), rcond=None)[0]
    return res.tolist()


def ensure_dir():
    os.makedirs(MOCKUPS_DIR, exist_ok=True)


def _drop_shadow(im: Image.Image, offset=(10, 10), background_color=0xFFFFFF, shadow_color=0x444444, border=20, iterations=10):
    # Adapted drop shadow helper
    total_width = im.size[0] + abs(offset[0]) + 2 * border
    total_height = im.size[1] + abs(offset[1]) + 2 * border
    back = Image.new(im.mode, (total_width, total_height), background_color)
    shadow = Image.new("RGBA", im.size, shadow_color)
    shadow_left = border + max(offset[0], 0)
    shadow_top = border + max(offset[1], 0)
    back.paste(shadow, (shadow_left, shadow_top))
    for i in range(iterations):
        back = back.filter(ImageFilter.BLUR)
    image_left = border + max(-offset[0], 0)
    image_top = border + max(-offset[1], 0)
    back.paste(im, (image_left, image_top), im)
    return back


def make_mockups(input_png: str, title: str, niche: str) -> List[str]:
    ensure_dir()
    base = Image.open(input_png).convert("RGBA")
    w, h = base.size
    outputs: List[str] = []

    # Collect background files if provided
    bg_files = []
    if ASSETS_BG.exists() and ASSETS_BG.is_dir():
        for p in ASSETS_BG.iterdir():
            if p.suffix.lower() in (".png", ".jpg", ".jpeg"):
                bg_files.append(p)

    # If we have backgrounds, composite onto them; otherwise produce programmatic variants
    if bg_files:
        # Use up to 8 backgrounds (repeat if fewer)
        for i in range(8):
            bg = Image.open(str(bg_files[i % len(bg_files)])).convert("RGBA")
            # Fit base into center of bg with padding
            bg_w, bg_h = bg.size
            scale = min((bg_w * 0.8) / w, (bg_h * 0.8) / h)
            img = base.resize((int(w * scale), int(h * scale)))
            # create drop shadow and composite
            shadowed = _drop_shadow(img, offset=(12, 12), background_color=0xFFFFFF, shadow_color=(0,0,0,150))
            # center positions
            x = (bg_w - shadowed.size[0]) // 2
            y = (bg_h - shadowed.size[1]) // 2
            composed = bg.copy()
            composed.paste(shadowed, (x, y), shadowed)
            # If a phone frame exists, try ImageMagick first for a nicer composite, otherwise fallback to PIL composite
            if PHONE_FRAME.exists():
                try:
                    # save current composed to a temp file and ask ImageMagick to composite into frame
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t_in:
                        composed.convert("RGBA").save(t_in.name)
                        tmp_input = t_in.name
                    out_tmp = str(Path(tempfile.gettempdir()) / f"mockout-{os.getpid()}-{x}.png")
                    success = _imagemagick_composite(tmp_input, str(PHONE_FRAME), out_tmp)
                    if success and os.path.exists(out_tmp):
                        composed = Image.open(out_tmp).convert("RGBA")
                    else:
                        # fallback: paste frame using PIL
                        frame = Image.open(str(PHONE_FRAME)).convert("RGBA")
                        fw, fh = frame.size
                        scale = min((fw * 0.8) / composed.size[0], (fh * 0.8) / composed.size[1])
                        inner = composed.resize((int(composed.size[0] * scale), int(composed.size[1] * scale)))
                        fx = (fw - inner.size[0]) // 2
                        fy = (fh - inner.size[1]) // 2
                        frame_copy = frame.copy()
                        frame_copy.paste(inner, (fx, fy), inner)
                        cx = (bg_w - fw) // 2
                        cy = (bg_h - fh) // 2
                        bg_with_frame = bg.copy()
                        bg_with_frame.paste(frame_copy, (cx, cy), frame_copy)
                        composed = bg_with_frame
                except Exception:
                    pass
            draw = ImageDraw.Draw(composed)
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except Exception:
                font = ImageFont.load_default()
            draw.text((30, composed.size[1] - 60), title, fill=(0,0,0), font=font)
            outpath = f"{MOCKUPS_DIR}/{niche}-{i}.png"
            composed.convert("RGB").save(outpath, "PNG")
            outputs.append(outpath)
    else:
        for i in range(8):
            canvas = Image.new("RGBA", (w, h), (255, 255, 255, 255))
            img = base.copy()
            scale = 0.95 - i * 0.01
            img = img.resize((int(w * scale), int(h * scale)))
            offset = int((w - img.size[0]) / 2), int((h - img.size[1]) / 2)
            # add shadowed composite
            shadowed = _drop_shadow(img, offset=(8, 8), background_color=0xFFFFFF, shadow_color=(0,0,0,160))
            canvas.paste(shadowed, (offset[0] - 8, offset[1] - 8), shadowed)
            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except Exception:
                font = ImageFont.load_default()
            draw.text((10, h - 40), title, fill=(0,0,0), font=font)
            outpath = f"{MOCKUPS_DIR}/{niche}-{i}.png"
            canvas.convert("RGB").save(outpath, "PNG")
            outputs.append(outpath)

    return outputs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mockup_factory.py path/to/template.png --niche niche --title 'Title'")
        sys.exit(1)
    inp = sys.argv[1]
    niche = "general"
    title = "Template"
    for i, a in enumerate(sys.argv[2:]):
        if a == "--niche" and i+2 <= len(sys.argv):
            niche = sys.argv[2+i]
        if a == "--title" and i+2 <= len(sys.argv):
            title = sys.argv[2+i]
    outs = make_mockups(inp, title, niche)
    print("Created:", outs)
