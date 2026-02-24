"""Tight-crop a sprite to its visible content and optionally resize to a uniform square."""

from __future__ import annotations

import numpy as np
from PIL import Image

from config import Config


def crop_sprite(img: Image.Image, cfg: Config | None = None) -> Image.Image | None:
    """Crop *img* to the bounding box of non-transparent pixels.

    Returns ``None`` if the image contains fewer visible pixels than
    ``cfg.min_sprite_pixels`` (i.e. the cell is effectively empty).
    """
    cfg = cfg or Config()
    rgba = img.convert("RGBA")
    alpha = np.array(rgba)[:, :, 3]

    if int(np.count_nonzero(alpha)) < cfg.min_sprite_pixels:
        return None

    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    y_min, y_max = int(np.argmax(rows)), int(len(rows) - 1 - np.argmax(rows[::-1]))
    x_min, x_max = int(np.argmax(cols)), int(len(cols) - 1 - np.argmax(cols[::-1]))

    # Apply padding (clamped to image bounds)
    h, w = alpha.shape
    pad = cfg.padding
    y_min = max(0, y_min - pad)
    y_max = min(h - 1, y_max + pad)
    x_min = max(0, x_min - pad)
    x_max = min(w - 1, x_max + pad)

    cropped = rgba.crop((x_min, y_min, x_max + 1, y_max + 1))
    return cropped


def resize_sprite(img: Image.Image, size: int) -> Image.Image:
    """Resize *img* into a ``size x size`` square, preserving aspect ratio.

    The sprite is centred on a transparent canvas; empty space stays transparent.
    """
    cw, ch = img.size
    scale = min(size / cw, size / ch)
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset_x = (size - new_w) // 2
    offset_y = (size - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y))
    return canvas
