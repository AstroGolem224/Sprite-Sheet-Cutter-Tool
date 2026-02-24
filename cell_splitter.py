"""Split a sprite-sheet image into individual cell images based on detected grid rectangles."""

from __future__ import annotations

from typing import List, Tuple

from PIL import Image

Rect = Tuple[int, int, int, int]  # (x, y, w, h)


def split_cells(img: Image.Image, cells: List[Rect]) -> List[Image.Image]:
    """Crop *img* into sub-images defined by *cells*.

    Each cell ``(x, y, w, h)`` is cropped via PIL's ``crop((left, upper, right, lower))``.
    Returns the list in the same order as *cells* (top-left to bottom-right).
    """
    result: List[Image.Image] = []
    for x, y, w, h in cells:
        box = (x, y, x + w, y + h)
        result.append(img.crop(box).copy())
    return result
