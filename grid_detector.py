"""Detect grid layout (3x3, 2x2, or single) in a sprite-sheet image.

Two strategies are tried in order:
1. Filled-row/col detection: rows/columns where almost every pixel is
   non-white indicate separator lines drawn into the image.
2. White-gap projection profiles: large empty bands between sprites
   (no explicit separator lines).
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from PIL import Image

from config import Config

Rect = Tuple[int, int, int, int]  # (x, y, w, h)

MAX_SEPARATOR_THICKNESS = 20


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_cells(img: Image.Image, cfg: Config | None = None) -> List[Rect]:
    """Return a list of ``(x, y, w, h)`` cell rectangles found in *img*.

    Falls back from separator-line detection to white-gap detection
    automatically. If neither finds a grid the whole image is returned
    as a single cell.
    """
    cfg = cfg or Config()
    arr = np.array(img.convert("RGB"))

    cells = _detect_separator_lines(arr, cfg)
    if cells is not None:
        return cells

    cells = _detect_white_gaps(arr, cfg)
    if cells is not None:
        return cells

    h, w = arr.shape[:2]
    return [(0, 0, w, h)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_bands(mask: np.ndarray) -> List[Tuple[int, int]]:
    """Return ``(start, end)`` ranges of consecutive True values in *mask*."""
    bands: List[Tuple[int, int]] = []
    in_band = False
    start = 0
    for i, v in enumerate(mask):
        if v and not in_band:
            start = i
            in_band = True
        elif not v and in_band:
            bands.append((start, i))
            in_band = False
    if in_band:
        bands.append((start, len(mask)))
    return bands


def _bands_to_splits(bands: List[Tuple[int, int]], total: int) -> List[int] | None:
    """Convert separator bands into split positions.

    Returns ``None`` if the bands don't form a plausible grid (0, 1, or >4
    interior separators would be unusual).
    """
    if not bands:
        return None

    # Midpoints of each band become the split positions
    mids = [(s + e) // 2 for s, e in bands]

    # Always include 0 and total as outer boundaries
    splits = []
    if mids[0] > total * 0.05:
        splits.append(0)
    splits.extend(mids)
    if mids[-1] < total * 0.95:
        splits.append(total)

    # Need at least 3 splits (start, mid, end) for a 2-cell row
    return splits if len(splits) >= 3 else None


def _build_cells(h_splits: List[int], v_splits: List[int]) -> List[Rect]:
    cells: List[Rect] = []
    for ri in range(len(h_splits) - 1):
        for ci in range(len(v_splits) - 1):
            y0, y1 = h_splits[ri], h_splits[ri + 1]
            x0, x1 = v_splits[ci], v_splits[ci + 1]
            if (x1 - x0) > 10 and (y1 - y0) > 10:
                cells.append((x0, y0, x1 - x0, y1 - y0))
    return cells


# ---------------------------------------------------------------------------
# Strategy 1 – separator lines (rows/cols that are almost entirely non-white)
# ---------------------------------------------------------------------------

def _detect_separator_lines(arr: np.ndarray, cfg: Config) -> List[Rect] | None:
    h, w, _ = arr.shape
    brightness = arr.mean(axis=2)  # (h, w)

    row_filled = (brightness < cfg.white_threshold).mean(axis=1)
    col_filled = (brightness < cfg.white_threshold).mean(axis=0)

    filled_row_mask = row_filled > 0.95
    filled_col_mask = col_filled > 0.95

    h_bands_raw = _find_bands(filled_row_mask)
    v_bands_raw = _find_bands(filled_col_mask)

    h_bands = [(s, e) for s, e in h_bands_raw if (e - s) <= MAX_SEPARATOR_THICKNESS]
    v_bands = [(s, e) for s, e in v_bands_raw if (e - s) <= MAX_SEPARATOR_THICKNESS]

    if not h_bands and not v_bands:
        return None

    h_intervals = _bands_to_gap_intervals(h_bands, h)
    v_intervals = _bands_to_gap_intervals(v_bands, w)

    if h_intervals is None:
        h_intervals = [(0, h)]
    if v_intervals is None:
        v_intervals = [(0, w)]

    cells: List[Rect] = []
    for y0, y1 in h_intervals:
        for x0, x1 in v_intervals:
            if (x1 - x0) > 10 and (y1 - y0) > 10:
                cells.append((x0, y0, x1 - x0, y1 - y0))

    return cells if len(cells) > 1 else None


def _bands_to_gap_intervals(
    bands: List[Tuple[int, int]], total: int,
) -> List[Tuple[int, int]] | None:
    """Convert separator bands into cell intervals that sit *between* bands.

    Each interval runs from the end of one band to the start of the next,
    completely excluding any dark separator pixels from the cells.
    """
    if not bands:
        return None

    intervals: List[Tuple[int, int]] = []

    # Leading interval (before the first band, if it doesn't start at 0)
    if bands[0][0] > 10:
        intervals.append((0, bands[0][0]))

    # Gaps between consecutive bands
    for i in range(len(bands) - 1):
        y0 = bands[i][1]       # end of current band
        y1 = bands[i + 1][0]   # start of next band
        if y1 - y0 > 10:
            intervals.append((y0, y1))

    # Trailing interval (after the last band, if it doesn't reach total)
    if bands[-1][1] < total - 10:
        intervals.append((bands[-1][1], total))

    return intervals if intervals else None


# ---------------------------------------------------------------------------
# Strategy 2 – white-gap projection profiles
# ---------------------------------------------------------------------------

def _detect_white_gaps(arr: np.ndarray, cfg: Config) -> List[Rect] | None:
    h, w, _ = arr.shape
    brightness = arr.mean(axis=2)
    is_content = brightness < cfg.white_threshold

    row_content = is_content.mean(axis=1)
    col_content = is_content.mean(axis=0)

    content_threshold = 0.02

    h_gaps = _find_gap_bands(row_content, content_threshold, cfg.gap_min_width, h)
    v_gaps = _find_gap_bands(col_content, content_threshold, cfg.gap_min_width, w)

    if not h_gaps and not v_gaps:
        return None

    h_selected = _select_best_gaps(h_gaps, h)
    v_selected = _select_best_gaps(v_gaps, w)

    if h_selected is None and v_selected is None:
        return None

    h_splits = _gaps_to_splits(h_selected, h)
    v_splits = _gaps_to_splits(v_selected, w)

    cells = _build_cells(h_splits, v_splits)
    return cells if len(cells) > 1 else None


def _gaps_to_splits(gaps: List[Tuple[int, int]] | None, total: int) -> List[int]:
    if not gaps:
        return [0, total]
    return [0] + [(s + e) // 2 for s, e in gaps] + [total]


def _select_best_gaps(
    gaps: List[Tuple[int, int]], total: int
) -> List[Tuple[int, int]] | None:
    """Pick the widest 1 or 2 gaps that produce a balanced split.

    Tries 2 gaps first (3-region split), then 1 (2-region split).
    Wider gaps are preferred.
    """
    if not gaps:
        return None

    sorted_gaps = sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)

    for n in (2, 1):
        if len(sorted_gaps) < n:
            continue
        candidate = sorted(sorted_gaps[:n], key=lambda g: g[0])
        splits = _gaps_to_splits(candidate, total)
        if _splits_are_balanced(splits, total):
            return candidate

    return None


def _splits_are_balanced(splits: List[int], total: int, min_ratio: float = 0.25) -> bool:
    """Check that every interval between consecutive splits is at least *min_ratio* of *total*."""
    for i in range(len(splits) - 1):
        span = splits[i + 1] - splits[i]
        if span < total * min_ratio:
            return False
    return True


def _find_gap_bands(
    profile: np.ndarray,
    content_threshold: float,
    min_width: int,
    total: int,
) -> List[Tuple[int, int]]:
    """Find contiguous stretches in *profile* below *content_threshold*.

    Gaps at the very edges (within 5% of total) are excluded.
    """
    is_gap = profile < content_threshold
    bands = _find_bands(is_gap)
    margin = int(total * 0.05)
    return [
        (s, e) for s, e in bands
        if (e - s) >= min_width and s > margin and e < total - margin
    ]
