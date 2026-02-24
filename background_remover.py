"""Remove white background from a sprite image using edge-seeded flood fill.

The algorithm seeds from every border pixel that looks near-white, then
flood-fills inward through connected near-white pixels.  All reached pixels
get their alpha set to 0.  White areas *inside* a sprite (not connected to
the border) are preserved.
"""

from __future__ import annotations

from collections import deque

import numpy as np
from PIL import Image

from config import Config


def remove_background(img: Image.Image, cfg: Config | None = None) -> Image.Image:
    """Return a copy of *img* with the white background made transparent."""
    cfg = cfg or Config()
    rgba = img.convert("RGBA")
    arr = np.array(rgba)

    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    bg_mask = np.zeros((h, w), dtype=bool)

    threshold = cfg.white_threshold
    tolerance = cfg.flood_fill_tolerance

    def _is_near_white(r: int, g: int, b: int) -> bool:
        return r >= threshold and g >= threshold and b >= threshold

    def _within_tolerance(r: int, g: int, b: int) -> bool:
        return r >= (threshold - tolerance) and g >= (threshold - tolerance) and b >= (threshold - tolerance)

    # Collect seed pixels from all four borders
    seeds: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            r, g, b = int(arr[y, x, 0]), int(arr[y, x, 1]), int(arr[y, x, 2])
            if _is_near_white(r, g, b):
                seeds.append((x, y))
    for y in range(1, h - 1):
        for x in (0, w - 1):
            r, g, b = int(arr[y, x, 0]), int(arr[y, x, 1]), int(arr[y, x, 2])
            if _is_near_white(r, g, b):
                seeds.append((x, y))

    # BFS flood fill
    for sx, sy in seeds:
        if visited[sy, sx]:
            continue
        visited[sy, sx] = True
        r, g, b = int(arr[sy, sx, 0]), int(arr[sy, sx, 1]), int(arr[sy, sx, 2])
        if not _is_near_white(r, g, b):
            continue
        bg_mask[sy, sx] = True

    queue: deque[tuple[int, int]] = deque()
    for x, y in seeds:
        if bg_mask[y, x]:
            queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx]:
                visited[ny, nx] = True
                r, g, b = int(arr[ny, nx, 0]), int(arr[ny, nx, 1]), int(arr[ny, nx, 2])
                if _within_tolerance(r, g, b):
                    bg_mask[ny, nx] = True
                    queue.append((nx, ny))

    arr[bg_mask, 3] = 0
    return Image.fromarray(arr, "RGBA")
