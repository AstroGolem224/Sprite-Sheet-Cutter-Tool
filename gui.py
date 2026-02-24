#!/usr/bin/env python3
"""Modern dark-themed GUI for the Sprite Sheet Cutter tool."""

from __future__ import annotations

import logging
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from config import Config
from pipeline import process_folder, process_image

# ---------------------------------------------------------------------------
# Colour palette – matched to the Cursor IDE dark theme
# ---------------------------------------------------------------------------
BG_DARK = "#1e1e1e"
BG_PANEL = "#252526"
BG_INPUT = "#2d2d30"
BORDER = "#3c3c3c"
ACCENT = "#007acc"
ACCENT_HOVER = "#1a8fdb"
TEXT = "#cccccc"
TEXT_DIM = "#858585"
TEXT_SUCCESS = "#4ec9b0"
TEXT_ERROR = "#f14c4c"
LOG_BG = "#1e1e1e"

FONT_UI = "Segoe UI"
FONT_MONO = "Cascadia Code"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ---------------------------------------------------------------------------
# Queue-based log handler  (worker thread -> UI)
# ---------------------------------------------------------------------------
class QueueHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord):
        self.log_queue.put(self.format(record))


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
def _app_dir() -> Path:
    """Return the directory the app is running from (works for .exe and source)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


class SpriteCutterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sprite Sheet Cutter")
        self.geometry("720x820")
        self.minsize(620, 700)
        self.configure(fg_color=BG_DARK)

        self._log_queue: queue.Queue[str] = queue.Queue()
        self._worker: threading.Thread | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        row = 0

        # ── Title bar ────────────────────────────────────────────────
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=row, column=0, padx=24, pady=(24, 2), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        row += 1

        title = ctk.CTkLabel(
            title_frame, text="Sprite Sheet Cutter",
            font=ctk.CTkFont(family=FONT_UI, size=20, weight="bold"),
            text_color=TEXT,
        )
        title.grid(row=0, column=0, sticky="w")

        help_btn = ctk.CTkButton(
            title_frame, text="?", width=32, height=32,
            font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
            fg_color=BG_INPUT, hover_color=BORDER, text_color=TEXT,
            border_width=1, border_color=BORDER, corner_radius=4,
            command=self._open_guide,
        )
        help_btn.grid(row=0, column=1, sticky="e")

        subtitle = ctk.CTkLabel(
            self,
            text="Extract individual sprites from sprite-sheet PNGs",
            font=ctk.CTkFont(family=FONT_UI, size=12),
            text_color=TEXT_DIM,
        )
        subtitle.grid(row=row, column=0, padx=24, pady=(0, 16), sticky="w")
        row += 1

        # ── Folder selectors ─────────────────────────────────────────
        folders_frame = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=6, border_width=1, border_color=BORDER)
        folders_frame.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="ew")
        folders_frame.grid_columnconfigure(1, weight=1)
        row += 1

        self.input_var = ctk.StringVar()
        self.output_var = ctk.StringVar()

        self._folder_row(folders_frame, 0, "Input Folder", self.input_var, self._browse_input)
        self._folder_row(folders_frame, 1, "Output Folder", self.output_var, self._browse_output)

        # ── Settings panel ───────────────────────────────────────────
        settings_frame = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=6, border_width=1, border_color=BORDER)
        settings_frame.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="ew")
        row += 1

        settings_label = ctk.CTkLabel(
            settings_frame, text="Settings",
            font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
            text_color=TEXT_DIM,
        )
        settings_label.grid(row=0, column=0, columnspan=4, padx=16, pady=(12, 4), sticky="w")

        settings_inner = ctk.CTkFrame(settings_frame, fg_color="transparent")
        settings_inner.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 14), sticky="ew")
        for c in range(4):
            settings_inner.grid_columnconfigure(c, weight=1)

        self.size_var = ctk.StringVar(value="512")
        self.padding_var = ctk.StringVar(value="10")
        self.threshold_var = ctk.StringVar(value="230")
        self.tolerance_var = ctk.StringVar(value="25")

        self._setting_field(settings_inner, 0, "Output Size", self.size_var)
        self._setting_field(settings_inner, 1, "Padding", self.padding_var)
        self._setting_field(settings_inner, 2, "White Threshold", self.threshold_var)
        self._setting_field(settings_inner, 3, "Flood Tolerance", self.tolerance_var)

        # ── Execute button ───────────────────────────────────────────
        self.exec_btn = ctk.CTkButton(
            self,
            text="Extract Sprites",
            font=ctk.CTkFont(family=FONT_UI, size=13, weight="bold"),
            height=38,
            corner_radius=4,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#ffffff",
            command=self._on_execute,
        )
        self.exec_btn.grid(row=row, column=0, padx=20, pady=(4, 10), sticky="ew")
        row += 1

        # ── Progress bar ─────────────────────────────────────────────
        self.progress = ctk.CTkProgressBar(
            self, height=4, corner_radius=2,
            fg_color=BG_INPUT, progress_color=ACCENT,
        )
        self.progress.grid(row=row, column=0, padx=20, pady=(0, 6), sticky="ew")
        self.progress.set(0)
        row += 1

        self.status_label = ctk.CTkLabel(
            self, text="Ready", font=ctk.CTkFont(family=FONT_UI, size=11), text_color=TEXT_DIM,
        )
        self.status_label.grid(row=row, column=0, padx=24, pady=(0, 4), sticky="w")
        row += 1

        # ── Log output ───────────────────────────────────────────────
        log_frame = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=6, border_width=1, border_color=BORDER)
        log_frame.grid(row=row, column=0, padx=20, pady=(0, 20), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(row, weight=1)
        row += 1

        log_label = ctk.CTkLabel(
            log_frame, text="Output",
            font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
            text_color=TEXT_DIM,
        )
        log_label.grid(row=0, column=0, padx=14, pady=(10, 0), sticky="w")

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            fg_color=LOG_BG,
            text_color=TEXT_DIM,
            corner_radius=4,
            border_width=0,
            state="disabled",
            wrap="word",
        )
        self.log_text.grid(row=1, column=0, padx=10, pady=(6, 10), sticky="nsew")

    # ------------------------------------------------------------------
    # Reusable widget builders
    # ------------------------------------------------------------------
    def _folder_row(self, parent, row: int, label: str, var: ctk.StringVar, cmd):
        lbl = ctk.CTkLabel(
            parent, text=label,
            font=ctk.CTkFont(family=FONT_UI, size=12), text_color=TEXT_DIM,
        )
        lbl.grid(row=row * 2, column=0, columnspan=3, padx=14, pady=(12 if row == 0 else 2, 0), sticky="w")

        entry = ctk.CTkEntry(
            parent, textvariable=var, height=32,
            font=ctk.CTkFont(family=FONT_UI, size=12),
            fg_color=BG_INPUT, border_color=BORDER, text_color=TEXT,
            corner_radius=4, border_width=1,
        )
        entry.grid(row=row * 2 + 1, column=0, columnspan=2, padx=(14, 6), pady=(2, 12 if row == 1 else 4), sticky="ew")

        btn = ctk.CTkButton(
            parent, text="Browse", width=72, height=32,
            font=ctk.CTkFont(family=FONT_UI, size=11),
            fg_color=BG_INPUT, hover_color=BORDER, text_color=TEXT,
            border_width=1, border_color=BORDER, corner_radius=4,
            command=cmd,
        )
        btn.grid(row=row * 2 + 1, column=2, padx=(0, 14), pady=(2, 12 if row == 1 else 4))

    def _setting_field(self, parent, col: int, label: str, var: ctk.StringVar):
        lbl = ctk.CTkLabel(
            parent, text=label,
            font=ctk.CTkFont(family=FONT_UI, size=11), text_color=TEXT_DIM,
        )
        lbl.grid(row=0, column=col, padx=6, pady=(0, 2))

        entry = ctk.CTkEntry(
            parent, textvariable=var, width=80, height=28,
            font=ctk.CTkFont(family=FONT_MONO, size=12), justify="center",
            fg_color=BG_INPUT, border_color=BORDER, text_color=TEXT,
            corner_radius=4, border_width=1,
        )
        entry.grid(row=1, column=col, padx=6, pady=(0, 4))

    # ------------------------------------------------------------------
    # Help / guide
    # ------------------------------------------------------------------
    def _open_guide(self):
        pdf = _app_dir() / "SpriteSheetCutter_Guide.pdf"
        if pdf.exists():
            os.startfile(str(pdf))
        else:
            self._append_log(f"[WARN]   Guide not found at {pdf}")

    # ------------------------------------------------------------------
    # Folder dialogs
    # ------------------------------------------------------------------
    def _browse_input(self):
        path = filedialog.askdirectory(title="Select input folder")
        if path:
            self.input_var.set(path)
            if not self.output_var.get():
                self.output_var.set(str(Path(path) / "output"))

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_var.set(path)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def _append_log(self, text: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _poll_log(self):
        while True:
            try:
                msg = self._log_queue.get_nowait()
                self._append_log(msg)
            except queue.Empty:
                break
        if self._worker and self._worker.is_alive():
            self.after(80, self._poll_log)

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------
    def _on_execute(self):
        src = self.input_var.get().strip()
        dst = self.output_var.get().strip()

        if not src:
            self._append_log("[ERROR]  Please select an input folder.")
            return
        if not dst:
            self._append_log("[ERROR]  Please select an output folder.")
            return

        src_path = Path(src)
        if not src_path.exists():
            self._append_log(f"[ERROR]  Input path does not exist: {src}")
            return

        self.exec_btn.configure(state="disabled", text="Processing...")
        self.progress.set(0)
        self.status_label.configure(text="Starting...", text_color=TEXT_DIM)

        # Clear log
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        cfg = Config(
            white_threshold=int(self.threshold_var.get()),
            flood_fill_tolerance=int(self.tolerance_var.get()),
            padding=int(self.padding_var.get()),
            output_size=int(self.size_var.get()),
        )

        self._worker = threading.Thread(
            target=self._run_pipeline,
            args=(src_path, Path(dst), cfg),
            daemon=True,
        )
        self._worker.start()
        self.after(80, self._poll_log)

    def _run_pipeline(self, src: Path, dst: Path, cfg: Config):
        handler = QueueHandler(self._log_queue)
        handler.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)

        pil_logger = logging.getLogger("PIL")
        pil_logger.setLevel(logging.WARNING)

        try:
            dst.mkdir(parents=True, exist_ok=True)

            if src.is_file():
                pngs = [src]
            else:
                pngs = sorted(src.glob("*.png"))

            total = len(pngs)
            if total == 0:
                self._log_queue.put("[WARN]   No PNG files found.")
                self._finish(0)
                return

            self._log_queue.put(f"         Found {total} PNG file(s)\n")
            all_saved = 0

            for i, p in enumerate(pngs):
                saved = process_image(p, dst, cfg)
                all_saved += len(saved)
                progress = (i + 1) / total
                self.after(0, self._update_progress, progress, i + 1, total, all_saved)

            self._finish(all_saved)

        except Exception as exc:
            self._log_queue.put(f"[ERROR]  {exc}")
            self._finish(-1)
        finally:
            root_logger.removeHandler(handler)

    def _update_progress(self, frac: float, done: int, total: int, sprites: int):
        self.progress.set(frac)
        self.status_label.configure(
            text=f"Processing {done}/{total} sheets  ·  {sprites} sprites extracted",
            text_color=TEXT_DIM,
        )

    def _finish(self, count: int):
        def _ui():
            self.exec_btn.configure(state="normal", text="Extract Sprites")
            self.progress.set(1 if count >= 0 else 0)
            if count < 0:
                self.status_label.configure(text="Error – check log", text_color=TEXT_ERROR)
            elif count == 0:
                self.status_label.configure(text="No sprites found", text_color=TEXT_DIM)
            else:
                self.status_label.configure(
                    text=f"Done – {count} sprite(s) extracted",
                    text_color=TEXT_SUCCESS,
                )
                self._log_queue.put(f"\n  --- {count} sprite(s) extracted ---")
        self.after(0, _ui)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    app = SpriteCutterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
