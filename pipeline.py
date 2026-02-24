"""Orchestrate the full sprite-extraction pipeline for a single image or folder."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from PIL import Image

from background_remover import remove_background
from cell_splitter import split_cells
from config import Config
from grid_detector import detect_cells
from sprite_cropper import crop_sprite, resize_sprite

log = logging.getLogger(__name__)


def process_image(
    src: Path,
    out_dir: Path,
    cfg: Config,
) -> List[Path]:
    """Run the full pipeline on a single sprite-sheet image.

    Returns a list of paths to the saved individual sprites.
    """
    log.info("processing %s", src.name)
    img = Image.open(src).convert("RGBA")

    cells = detect_cells(img, cfg)
    log.info("  detected %d cell(s)", len(cells))

    cell_images = split_cells(img, cells)

    saved: List[Path] = []
    idx = 0
    for ci, cell_img in enumerate(cell_images):
        cleaned = remove_background(cell_img, cfg)
        cropped = crop_sprite(cleaned, cfg)
        if cropped is None:
            log.debug("  cell %d is empty, skipping", ci)
            continue

        if cfg.output_size > 0:
            final = resize_sprite(cropped, cfg.output_size)
        else:
            final = cropped

        stem = src.stem
        folder = out_dir / stem
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / f"{idx}.png"
        final.save(dest, "PNG")
        log.info("  saved %s (%dx%d)", dest.name, final.width, final.height)
        saved.append(dest)
        idx += 1

    return saved


def process_folder(
    src_dir: Path,
    out_dir: Path,
    cfg: Config,
) -> List[Path]:
    """Process every PNG in *src_dir* (non-recursive) and save results to *out_dir*."""
    all_saved: List[Path] = []
    pngs = sorted(src_dir.glob("*.png"))
    if not pngs:
        log.warning("no PNG files found in %s", src_dir)
        return all_saved

    log.info("found %d PNG file(s) in %s", len(pngs), src_dir)
    for p in pngs:
        saved = process_image(p, out_dir, cfg)
        all_saved.extend(saved)

    log.info("done – %d sprites extracted total", len(all_saved))
    return all_saved
