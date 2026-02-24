# Sprite Sheet Cutter Tool

**Stand:** 2026-02-24

---

## Uebersicht

| Aspekt | Beschreibung |
|--------|--------------|
| **Pfad** | `tools/sprite_cutter/` |
| **Typ** | Python CLI + GUI Tool |
| **Zweck** | Sprite Sheets automatisch in Einzelsprites zerlegen, weissen Hintergrund transparent machen |
| **Stack** | Python 3.10+, Pillow, NumPy, SciPy, customtkinter |
| **Input** | PNG Sprite Sheets (Gemini-generiert, 1024x1024, 2816x1536, etc.) |
| **Output** | Einzelne PNGs mit transparentem Hintergrund, 512x512 (konfigurierbar) |

---

## Quick Start

```bash
cd tools/sprite_cutter
pip install -r requirements.txt

# GUI starten
python main.py --gui

# Oder CLI
python main.py -i "pfad/zu/sheets" -o "pfad/zu/output"
```

---

## GUI

Das Tool hat eine moderne Dark-Theme-Oberflaeche (Cursor-inspiriert):

- **Input Folder** – Ordner mit Sprite-Sheet PNGs auswaehlen
- **Output Folder** – Zielordner (wird automatisch vorgeschlagen)
- **Settings** – Output Size, Padding, White Threshold, Flood Tolerance
- **Extract Sprites** – Startet die Verarbeitung
- **Progress Bar** – Echtzeit-Fortschritt pro Sheet
- **Live Log** – Zeigt alle Verarbeitungsschritte

Starten: `python main.py --gui` oder `python gui.py`

---

## CLI Optionen

| Flag | Default | Beschreibung |
|------|---------|--------------|
| `--gui` | off | Grafische Oberflaeche starten |
| `-i`, `--input` | — | Pfad zu PNG-Datei oder Ordner |
| `-o`, `--output` | — | Ausgabe-Ordner |
| `--size` | `512` | Zielgroesse in px (`0` = Original-Crop behalten) |
| `--padding` | `10` | Transparenter Rand um den Sprite |
| `--white-threshold` | `230` | RGB-Wert ab dem ein Pixel als weiss/Hintergrund gilt |
| `--flood-tolerance` | `25` | Farbtoleranz fuer Flood-Fill |
| `-v` | off | Debug-Logging |

---

## Pipeline

```
PNG Sprite Sheet
       |
       v
  Grid Detection ──── erkennt 3x3 / 3x2 / 2x2 / 1x1
       |
       v
  Cell Splitting ──── schneidet zwischen Trennlinien (nicht mittendurch)
       |
       v
  Background Removal ─ Edge-Flood-Fill: weiss → transparent
       |
       v
  Tight Crop + Resize ─ BBox + Padding, Letterbox auf Zielgroesse
       |
       v
  Save PNG (transparent)
```

### Grid Detection (2 Strategien)

1. **Separator Lines** – Erkennt dunkle Trennlinien (>95% non-white pro Zeile/Spalte).
   Zellen werden aus den Luecken *zwischen* den Bands geschnitten, sodass keine
   dunklen Separator-Pixel in der Zelle landen.

2. **White Gaps** (Fallback) – Findet breite weisse Baender via Projection-Profile.
   Waehlt die breitesten 1-2 Gaps die eine balancierte Aufteilung ergeben.

### Background Removal

- Edge-Flood-Fill von allen Rand-Pixeln die near-white sind
- Flood-Fill expandiert mit konfigurierbarer Toleranz nach innen
- Weisse Bereiche *innerhalb* von Sprites bleiben erhalten (nicht mit Rand verbunden)

---

## Architektur

```
tools/sprite_cutter/
  main.py               Entry-Point (--gui oder CLI)
  gui.py                Dark-Theme customtkinter GUI
  pipeline.py           Orchestrierung: load → detect → split → clean → save
  grid_detector.py      Grid-Erkennung (Separator Lines + White Gaps)
  cell_splitter.py      Bild in Grid-Zellen aufteilen
  background_remover.py Edge-Flood-Fill (weiss → transparent)
  sprite_cropper.py     Tight-Crop + Aspect-Ratio-Resize
  config.py             Default-Konfiguration (Thresholds, Padding, Groesse)
  requirements.txt      Abhaengigkeiten
  README.md             Englische Dokumentation
```

---

## Output-Struktur

Jedes Quellbild bekommt einen eigenen Subfolder. Sprites sind von links-oben
nach rechts-unten nummeriert:

```
output/
  Gemini_Generated_Image_abc123/
    0.png    (512x512, transparent)
    1.png
    ...
    8.png    (bei 3x3 Grid)
  Gemini_Generated_Image_xyz789/
    0.png
    ...
    3.png    (bei 2x2 Grid)
```

---

## Tuning

| Problem | Loesung |
|---------|---------|
| Zu viel vom Sprite wird transparent | `--white-threshold` senken (z.B. 210) oder `--flood-tolerance` senken (z.B. 15) |
| Weisse Reste am Rand bleiben | `--white-threshold` erhoehen (z.B. 240) oder `--flood-tolerance` erhoehen (z.B. 35) |
| Sprite zu klein im Output | `--size 0` fuer Original-Groesse oder `--size 256` fuer kleinere Ausgabe |
| Grid wird falsch erkannt | Tool faellt automatisch auf Single-Sprite zurueck |

---

## Ergebnisse (aktueller Testlauf)

- **31 Quellbilder** verarbeitet
- **178 Sprites** extrahiert
- **0 Transparenz-Fehler** (alle Sprites haben korrekten transparenten Hintergrund)
- Erkannte Layouts: 12x 3x3, 17x 2x2, 1x 3x2, 1x Single
