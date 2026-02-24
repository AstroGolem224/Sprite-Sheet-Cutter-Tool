# Sprite Sheet Cutter

Python tool (GUI + CLI) that extracts individual sprites from Gemini-generated
sprite sheets, removes the white background (makes it transparent), and saves
each sprite as an individual PNG.

## Features

- **Dark-themed GUI** – modern Cursor-style interface with folder selectors,
  settings panel, live log output, and progress bar.
- **Auto grid detection** – recognises 3x3, 3x2, 2x2, and single-sprite
  layouts, both with dark separator lines and white-gap spacing.
- **Edge flood-fill background removal** – turns the white background
  transparent while preserving white areas *inside* sprites (e.g. ice horns,
  pearl horns, white fur).
- **Tight crop + resize** – crops to the sprite bounding box with configurable
  padding, then resizes to a uniform square (default 512x512) with preserved
  aspect ratio.

## Requirements

```
Python >= 3.10
Pillow >= 10.0
numpy  >= 1.24
scipy  >= 1.11
customtkinter >= 5.2   (for the GUI)
```

Install:

```bash
pip install -r requirements.txt
```

## Usage

### GUI (recommended)

```bash
python main.py --gui
```

Or launch the GUI directly:

```bash
python gui.py
```

### CLI – process a folder of sprite sheets

```bash
python main.py \
  --input  "path/to/sprite_sheets/" \
  --output "path/to/output/"
```

### CLI – process a single file

```bash
python main.py \
  --input  "sheet.png" \
  --output "output/"
```

### Options

| Flag                  | Default | Description                                          |
|-----------------------|---------|------------------------------------------------------|
| `--gui`               | off     | Launch the graphical interface                       |
| `-i`, `--input`       | —       | Path to a PNG file or folder of PNGs                 |
| `-o`, `--output`      | —       | Output directory for extracted sprites               |
| `--size`              | `512`   | Target square size in px (`0` = keep original size)  |
| `--padding`           | `10`    | Transparent padding around cropped sprite            |
| `--white-threshold`   | `230`   | RGB value above which a pixel counts as white/bg     |
| `--flood-tolerance`   | `25`    | Colour tolerance for flood-fill expansion            |
| `-v`, `--verbose`     | off     | Show debug-level logging                             |

### Output structure

Each source image gets its own subfolder. Sprites are numbered left-to-right,
top-to-bottom:

```
output/
  Gemini_Generated_Image_abc123/
    0.png
    1.png
    ...
    8.png
  single_sprite/
    0.png
```

## Architecture

```
main.py               Entry point (--gui for UI, otherwise CLI)
gui.py                Dark-themed customtkinter GUI
pipeline.py           Orchestrates load → detect → split → clean → save
grid_detector.py      Grid detection (separator lines + white-gap profiles)
cell_splitter.py      Crops image into individual grid cells
background_remover.py Edge-seeded flood-fill for white → transparent
sprite_cropper.py     Tight-crop + aspect-preserving resize
config.py             Default thresholds and settings
```

## Tuning tips

- If too much of a light-coloured sprite gets removed, **lower**
  `--white-threshold` (e.g. `210`) or `--flood-tolerance` (e.g. `15`).
- If background remnants remain around edges, **raise** `--white-threshold`
  (e.g. `240`) or `--flood-tolerance` (e.g. `35`).
- For sprite sheets with unusual grid layouts, the tool falls back gracefully
  to treating the whole image as a single sprite.
