#!/usr/bin/env python3
"""Entry-point for the Sprite Sheet Cutter tool (CLI + GUI).

Launch the graphical interface::

    python main.py --gui

CLI usage examples::

    python main.py --input ./sprites --output ./output
    python main.py --input sheet.png --output ./output --size 256 --padding 5
    python main.py --input ./sprites --output ./output --size 0
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from config import Config
from pipeline import process_folder, process_image


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Extract individual sprites from sprite-sheet PNGs, "
        "remove white background, and save as transparent PNGs.",
    )
    p.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical interface instead of the CLI.",
    )
    p.add_argument(
        "-i", "--input",
        type=Path,
        help="Path to a single PNG file or a folder of PNGs.",
    )
    p.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory for extracted sprites.",
    )
    p.add_argument(
        "--size",
        type=int,
        default=512,
        help="Target square size in pixels (0 = keep original crop size). Default: 512.",
    )
    p.add_argument(
        "--padding",
        type=int,
        default=10,
        help="Transparent padding around the cropped sprite. Default: 10.",
    )
    p.add_argument(
        "--white-threshold",
        type=int,
        default=230,
        dest="white_threshold",
        help="RGB value above which a pixel is treated as white/background. Default: 230.",
    )
    p.add_argument(
        "--flood-tolerance",
        type=int,
        default=25,
        dest="flood_tolerance",
        help="Colour tolerance for flood-fill expansion. Default: 25.",
    )
    p.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug-level logging.",
    )
    return p


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.gui or (_is_frozen() and not args.input):
        from gui import main as gui_main
        gui_main()
        return 0

    if not args.input or not args.output:
        print("error: --input and --output are required in CLI mode (or use --gui)")
        return 1

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)-7s %(message)s",
    )

    cfg = Config(
        white_threshold=args.white_threshold,
        flood_fill_tolerance=args.flood_tolerance,
        padding=args.padding,
        output_size=args.size,
    )

    src: Path = args.input.resolve()
    out: Path = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    if src.is_file():
        saved = process_image(src, out, cfg)
    elif src.is_dir():
        saved = process_folder(src, out, cfg)
    else:
        logging.error("input path does not exist: %s", src)
        return 1

    print(f"\n--- {len(saved)} sprite(s) extracted to {out} ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
