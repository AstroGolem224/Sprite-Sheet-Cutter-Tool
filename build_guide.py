#!/usr/bin/env python3
"""Generate the Sprite Sheet Cutter user-guide PDF."""

from __future__ import annotations

import sys
from pathlib import Path

from fpdf import FPDF

ACCENT = (0, 122, 204)
DARK = (30, 30, 30)
PANEL = (37, 37, 38)
TEXT_COL = (204, 204, 204)
DIM = (133, 133, 133)
WHITE = (255, 255, 255)
SUCCESS = (78, 201, 176)

HERE = Path(__file__).resolve().parent
DIAGRAM = HERE / "SpriteSheetCutter_Architecture.png"


class GuidePDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*DARK)
        self.rect(0, 0, self.w, 14, style="F")
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*DIM)
        self.set_xy(10, 4)
        self.cell(0, 6, "Sprite Sheet Cutter  -  User Guide", align="L")
        self.set_xy(10, 4)
        self.cell(0, 6, f"Page {self.page_no()}", align="R")
        self.ln(14)

    def footer(self):
        pass

    def section_title(self, num: str, title: str):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*ACCENT)
        self.cell(0, 10, f"{num}  {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def sub_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def mono(self, text: str):
        self.set_font("Courier", "", 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 5, text, fill=True)
        self.ln(3)

    def bullet(self, text: str, bold_prefix: str = ""):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        x0 = self.get_x()
        self.cell(6, 5.5, "-")
        if bold_prefix:
            self.set_font("Helvetica", "B", 10)
            self.write(5.5, bold_prefix + " ")
            self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def table_row(self, cols: list[str], widths: list[float], bold: bool = False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 9)
        self.set_text_color(50, 50, 50)
        h = 7
        for c, w in zip(cols, widths):
            self.cell(w, h, c, border=1)
        self.ln(h)


def build_pdf(out: Path | None = None) -> Path:
    out = out or HERE / "SpriteSheetCutter_Guide.pdf"
    pdf = GuidePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_left_margin(18)
    pdf.set_right_margin(18)

    # ── Cover ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*DARK)
    pdf.rect(0, 0, 210, 297, style="F")

    pdf.set_y(70)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 16, "Sprite Sheet Cutter", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*DIM)
    pdf.cell(0, 10, "User Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.8)
    cx = 105
    pdf.line(cx - 40, pdf.get_y(), cx + 40, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*TEXT_COL)
    pdf.cell(0, 7, "Extract individual sprites from sprite-sheet PNGs", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "with automatic grid detection & background removal", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DIM)
    pdf.cell(0, 7, "v1.0  |  February 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Table of Contents ────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    toc = [
        ("1", "Quick Start"),
        ("2", "Graphical Interface (GUI)"),
        ("3", "Settings Reference"),
        ("4", "Command Line Interface (CLI)"),
        ("5", "Architecture Overview"),
        ("6", "Processing Pipeline"),
        ("7", "Grid Detection Strategies"),
        ("8", "Background Removal"),
        ("9", "Output Structure"),
        ("10", "Tuning Tips"),
        ("11", "Building the Executable"),
        ("12", "Troubleshooting"),
    ]
    for num, title in toc:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(10, 7, num + ".")
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    # ── 1. Quick Start ───────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("1", "Quick Start")

    pdf.sub_title("Option A: Standalone Executable (recommended)")
    pdf.body(
        "Double-click SpriteSheetCutter.exe. No Python installation needed. "
        "The GUI launches automatically."
    )

    pdf.sub_title("Option B: Run from Source")
    pdf.body("Make sure Python 3.10+ is installed, then:")
    pdf.mono("pip install -r requirements.txt\npython main.py --gui")

    pdf.sub_title("Basic Workflow")
    pdf.bullet("Click Browse next to Input Folder and select the folder containing your sprite-sheet PNGs.", "1.")
    pdf.bullet("Click Browse next to Output Folder to choose where extracted sprites should be saved.", "2.")
    pdf.bullet("Adjust settings if needed (defaults work well for most sheets).", "3.")
    pdf.bullet("Click Extract Sprites and watch the progress bar and log output.", "4.")
    pdf.bullet("Find your individual transparent PNGs in the output folder, organized into subfolders.", "5.")

    # ── 2. GUI ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("2", "Graphical Interface (GUI)")

    pdf.body(
        "The GUI uses a dark theme inspired by the Cursor IDE. "
        "It is built with customtkinter and provides a clean, modern look."
    )

    pdf.sub_title("Title Bar")
    pdf.body("Shows the application name. The  ?  button in the top-right corner opens this user guide PDF.")

    pdf.sub_title("Folder Selectors")
    pdf.body(
        "Two rows with text fields and Browse buttons. The Input Folder is where your "
        "sprite-sheet PNG files are located. The Output Folder is where extracted sprites will be saved. "
        "If you leave the output field empty and pick an input folder, it defaults to an 'output' "
        "subfolder inside the input folder."
    )

    pdf.sub_title("Settings Panel")
    pdf.body(
        "Four numeric fields for fine-tuning the extraction. See Section 3 for details on each setting."
    )

    pdf.sub_title("Extract Sprites Button")
    pdf.body(
        "Starts the processing pipeline. The button is disabled while processing is in progress. "
        "A progress bar and status label below the button show real-time progress."
    )

    pdf.sub_title("Output Log")
    pdf.body(
        "A scrollable text area that shows live logging output from the pipeline: "
        "which files are being processed, how many cells were detected, and which sprites were saved."
    )

    # ── 3. Settings ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("3", "Settings Reference")

    w = [42, 20, 112]
    pdf.table_row(["Setting", "Default", "Description"], w, bold=True)
    pdf.table_row(["Output Size", "512", "Target square size in pixels. Sprites are resized (aspect-ratio preserved) onto a transparent canvas of this size. Set to 0 to keep original crop size."], w)
    pdf.table_row(["Padding", "10", "Pixels of transparent padding added around the cropped sprite before resizing."], w)
    pdf.table_row(["White Threshold", "230", "RGB value (0-255) above which a pixel is considered white/background. Lower = stricter (less removed). Higher = more aggressive."], w)
    pdf.table_row(["Flood Tolerance", "25", "Color tolerance for the flood-fill expansion. Controls how far from pure white the algorithm will still consider a pixel as background."], w)

    pdf.ln(4)
    pdf.body(
        "These settings map directly to the Config dataclass in config.py and can also be "
        "set via CLI flags (--size, --padding, --white-threshold, --flood-tolerance)."
    )

    # ── 4. CLI ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("4", "Command Line Interface (CLI)")

    pdf.body("The tool can also be used entirely from the command line without the GUI:")

    pdf.sub_title("Process a folder")
    pdf.mono('python main.py --input "path/to/sprites/" --output "path/to/output/"')

    pdf.sub_title("Process a single file")
    pdf.mono('python main.py --input "sheet.png" --output "output/"')

    pdf.sub_title("All CLI flags")
    w2 = [42, 20, 112]
    pdf.table_row(["Flag", "Default", "Description"], w2, bold=True)
    pdf.table_row(["--gui", "off", "Launch the graphical interface instead of CLI mode."], w2)
    pdf.table_row(["-i, --input", "--", "Path to a single PNG file or a folder of PNGs."], w2)
    pdf.table_row(["-o, --output", "--", "Output directory for extracted sprites."], w2)
    pdf.table_row(["--size", "512", "Target square size in pixels (0 = keep original)."], w2)
    pdf.table_row(["--padding", "10", "Transparent padding around cropped sprite."], w2)
    pdf.table_row(["--white-threshold", "230", "RGB value above which a pixel counts as white."], w2)
    pdf.table_row(["--flood-tolerance", "25", "Color tolerance for flood-fill expansion."], w2)
    pdf.table_row(["-v, --verbose", "off", "Enable debug-level logging."], w2)

    # ── 5. Architecture ──────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("5", "Architecture Overview")

    pdf.body(
        "The tool follows a modular pipeline architecture. Each processing stage is "
        "implemented in its own Python module, making it easy to test, debug, and extend."
    )

    if DIAGRAM.exists():
        iw = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.image(str(DIAGRAM), x=pdf.l_margin, w=iw)
        pdf.ln(6)

    pdf.sub_title("Module Summary")
    w3 = [46, 128]
    pdf.table_row(["Module", "Responsibility"], w3, bold=True)
    pdf.table_row(["main.py", "Entry point: parses CLI args, dispatches to GUI or CLI pipeline."], w3)
    pdf.table_row(["gui.py", "customtkinter GUI with dark Cursor-style theme."], w3)
    pdf.table_row(["pipeline.py", "Orchestrates the full extraction workflow for images/folders."], w3)
    pdf.table_row(["grid_detector.py", "Detects grid layout using two detection strategies + fallback."], w3)
    pdf.table_row(["cell_splitter.py", "Crops an image into sub-images based on detected grid cells."], w3)
    pdf.table_row(["background_remover.py", "Edge-seeded BFS flood fill to make white backgrounds transparent."], w3)
    pdf.table_row(["sprite_cropper.py", "Tight-crop to content bounding box + aspect-preserving resize."], w3)
    pdf.table_row(["config.py", "Shared Config dataclass with default thresholds and settings."], w3)

    # ── 6. Pipeline ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("6", "Processing Pipeline")

    pdf.body("For each input PNG, the pipeline runs these stages sequentially:")
    pdf.ln(2)

    steps = [
        ("Load", "Open the PNG file and convert to RGBA mode using Pillow."),
        ("Detect Grid", "Analyze the image to find the grid layout (3x3, 2x2, or single). Returns a list of (x, y, w, h) rectangles."),
        ("Split Cells", "Crop the original image into individual cell images based on detected rectangles."),
        ("Remove Background", "For each cell, run edge-seeded flood fill to make the white background transparent. White areas inside the sprite (not connected to borders) are preserved."),
        ("Crop & Resize", "Tight-crop each sprite to its non-transparent bounding box with configurable padding, then resize to a uniform square canvas with preserved aspect ratio."),
        ("Save", "Write each sprite as an individual transparent PNG into a subfolder named after the source file."),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        pdf.bullet(desc, f"{title}:")

    pdf.ln(2)
    pdf.sub_title("Data flow between stages")
    pdf.mono(
        "Image.Image  -->  List[Rect]  -->  List[Image]  -->  Image.Image  -->  PNG file\n"
        " (load)        (detect_cells)   (split_cells)    (remove_bg,       (save)\n"
        "                                                  crop, resize)"
    )

    # ── 7. Grid Detection ────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("7", "Grid Detection Strategies")

    pdf.body("The grid detector tries two strategies in order, falling back to treating the whole image as a single sprite if neither succeeds.")

    pdf.sub_title("Strategy 1: Dark Separator Lines")
    pdf.body(
        "Many sprite sheets (especially 3x3 grids) have thin dark lines separating each cell. "
        "The detector calculates per-row and per-column brightness profiles. Rows/columns where "
        "more than 95% of pixels are non-white (below the white threshold) are flagged as separator "
        "bands. Bands thicker than 20px are rejected (likely part of a sprite, not a separator)."
    )
    pdf.body(
        "Cell boundaries are defined as the gaps between consecutive separator bands, ensuring "
        "that no dark separator pixels end up inside the extracted cells. This is critical for "
        "the background removal stage to work correctly."
    )

    pdf.sub_title("Strategy 2: White-Gap Projection Profiles")
    pdf.body(
        "For sheets without explicit separator lines (e.g. 2x2 layouts), the detector analyzes "
        "content density along each axis. It computes the fraction of non-white pixels per row "
        "and per column, then looks for wide bands (>= gap_min_width pixels) where content density "
        "drops below 2%."
    )
    pdf.body(
        "The widest 1-2 gaps are selected, and a balance check ensures the resulting segments "
        "are roughly even (each at least 25% of the total dimension). This prevents false splits "
        "caused by narrow white gaps within a single sprite (e.g. between a pair of legs)."
    )

    pdf.sub_title("Fallback: Single Cell")
    pdf.body(
        "If neither strategy finds a multi-cell grid, the entire image is treated as a single "
        "sprite cell."
    )

    # ── 8. Background Removal ────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("8", "Background Removal")

    pdf.body(
        "The background remover uses an edge-seeded BFS (breadth-first search) flood fill "
        "algorithm. This approach was chosen specifically to preserve white features inside "
        "sprites (e.g. ice horns, pearl textures, white fur) while removing only the outer "
        "white background."
    )

    pdf.sub_title("Algorithm Steps")
    pdf.bullet("Scan all four borders of the cell image for pixels whose RGB values are all above the white threshold.", "Seed:")
    pdf.bullet("From each seed pixel, expand outward using BFS. A neighbor pixel is included if all its RGB channels are within (white_threshold - flood_tolerance).", "Expand:")
    pdf.bullet("All pixels reached by the flood fill get their alpha channel set to 0 (fully transparent).", "Mask:")
    pdf.bullet("Any white region not connected to the border is left untouched.", "Preserve:")

    pdf.ln(2)
    pdf.body(
        "The tolerance parameter controls how aggressively the fill expands. A higher value "
        "removes more off-white pixels (useful for JPEG-like artifacts), while a lower value "
        "is more conservative and preserves light-colored sprite edges."
    )

    # ── 9. Output ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("9", "Output Structure")

    pdf.body("Each source image gets its own subfolder. Sprites are numbered left-to-right, top-to-bottom:")

    pdf.mono(
        "output/\n"
        "  Gemini_Generated_Image_abc123/\n"
        "    0.png\n"
        "    1.png\n"
        "    ...\n"
        "    8.png\n"
        "  single_sprite/\n"
        "    0.png"
    )

    pdf.body(
        "Each output PNG is a transparent-background sprite at the configured output size "
        "(default 512x512), centered on a transparent canvas with preserved aspect ratio."
    )

    # ── 10. Tuning Tips ──────────────────────────────────────────────
    pdf.section_title("10", "Tuning Tips")

    pdf.sub_title("Too much of a light-colored sprite gets removed")
    pdf.bullet("Lower White Threshold (e.g. 210).", "")
    pdf.bullet("Lower Flood Tolerance (e.g. 15).", "")

    pdf.sub_title("Background remnants remain around edges")
    pdf.bullet("Raise White Threshold (e.g. 240).", "")
    pdf.bullet("Raise Flood Tolerance (e.g. 35).", "")

    pdf.sub_title("Unusual grid layouts")
    pdf.body(
        "The tool falls back gracefully to treating the whole image as a single sprite. "
        "For non-standard grids, you may get better results processing individual cells manually."
    )

    pdf.sub_title("Very large sprite sheets")
    pdf.body(
        "Processing time scales with pixel count. For very large images (>4000px), "
        "expect a few seconds per sheet. The GUI shows real-time progress."
    )

    # ── 11. Building the Executable ──────────────────────────────────
    pdf.add_page()
    pdf.section_title("11", "Building the Executable")

    pdf.body("To rebuild the standalone Windows .exe from source:")

    pdf.mono(
        "pip install pyinstaller\n"
        "python -m PyInstaller --noconfirm --onefile --windowed \\\n"
        "  --name SpriteSheetCutter \\\n"
        "  --collect-data customtkinter \\\n"
        "  --hidden-import PIL --hidden-import numpy \\\n"
        "  --hidden-import scipy --hidden-import scipy.ndimage \\\n"
        "  main.py"
    )

    pdf.body(
        "The result lands in dist/SpriteSheetCutter.exe (~56 MB). The exe bundles Python, "
        "all dependencies, and the customtkinter theme data. First launch may take a few "
        "seconds as the onefile archive unpacks to a temp directory."
    )

    # ── 12. Troubleshooting ──────────────────────────────────────────
    pdf.section_title("12", "Troubleshooting")

    pdf.sub_title("Exe won't start / shows no window")
    pdf.body(
        "The onefile exe needs a few seconds on first launch to unpack. Wait 5-10 seconds. "
        "If it still doesn't appear, try running it from a terminal to see error output."
    )

    pdf.sub_title("'No PNG files found'")
    pdf.body(
        "Make sure the input folder directly contains .png files (the tool does not search "
        "subfolders recursively)."
    )

    pdf.sub_title("Sprites still have white background")
    pdf.body(
        "This can happen if the cell borders contain dark separator pixels instead of white. "
        "The v1.0 fix ensures separator-line cells are bounded by the gaps between dark bands. "
        "If you still see this, try raising the Flood Tolerance."
    )

    pdf.sub_title("Grid detected incorrectly (too many / too few cells)")
    pdf.body(
        "The grid detector is tuned for common Gemini-generated sprite sheet layouts. "
        "For unusual layouts, you can process images individually or pre-crop them manually."
    )

    # ── Write ────────────────────────────────────────────────────────
    pdf.output(str(out))
    return out


if __name__ == "__main__":
    dest = build_pdf()
    print(f"PDF written to {dest}")
