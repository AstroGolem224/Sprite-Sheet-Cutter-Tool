# AGENTS.md

Guide for humans and coding agents working in this repository.

## 1) Project snapshot

- **Name:** Sprite Sheet Cutter
- **Stack:** Python 3.10+, Pillow, NumPy, SciPy, customtkinter
- **Main entrypoint:** `main.py`
- **Modes:**
  - GUI: `python main.py --gui` (or `python gui.py`)
  - CLI: `python main.py -i "<input>" -o "<output>"`

## 2) Repository map

- `main.py` - CLI/GUI entrypoint
- `gui.py` - customtkinter UI
- `pipeline.py` - orchestration (load -> detect -> split -> clean -> save)
- `grid_detector.py` - grid detection
- `cell_splitter.py` - splitting grid cells
- `background_remover.py` - edge flood-fill white -> transparent
- `sprite_cropper.py` - tight crop + resize
- `config.py` - default settings
- `build_guide.py` - build helper content
- `agent_test.sh` - standard automated test runner for agents
- `docs/SPRITE_CUTTER_TOOL.md` - detailed German documentation

## 3) Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) Run commands

```bash
# GUI
python main.py --gui

# CLI (folder)
python main.py -i "path/to/sheets" -o "path/to/output"

# CLI (single file)
python main.py -i "sheet.png" -o "output"
```

## 5) Change workflow (expected)

1. Understand target behavior before editing.
2. Keep changes focused and minimal.
3. Update docs when behavior, flags, defaults, or output format change.
4. Run lightweight validation before handing off.
5. Write clear commit messages (imperative mood).

## 6) Validation checklist

Primary automated check entrypoint (agents should use this first):

```bash
bash ./agent_test.sh
```

Equivalent manual checks (fallback):

```bash
python -m compileall .
python main.py --help
```

If GUI code changed, also launch once:

```bash
python main.py --gui
```

If image pipeline changed, perform one real sample run with `-i/-o` and verify:

- sprites are extracted in correct order (left->right, top->bottom)
- background is transparent at sprite borders
- output dimensions match configured `--size` (unless `--size 0`)

## 7) Coding rules

- Prefer small, testable functions.
- Keep module responsibilities separated (detector/splitter/remover/cropper).
- Avoid hardcoding paths; keep IO configurable via CLI/options.
- Preserve existing behavior unless the task explicitly requires a change.
- Use logging for operational insight; avoid noisy prints in library-style code.

## 8) Documentation rules

- Keep `README.md` user-facing and concise.
- Keep deeper implementation and workflow notes in `docs/*.md`.
- Whenever commands or defaults change, update docs in the same PR/commit set.

## 9) Notes for future agents

- There is currently no dedicated automated test suite in this repo.
- Prefer adding narrow tests when introducing non-trivial logic changes.
- If adding dependencies, use the latest stable release and document why.

## 10) Agent function: run_automated_tests

Use this standard behavior:

1. Run compile/syntax validation.
2. Run CLI contract check (`main.py --help`).
3. If `tests/` exists, run `pytest -q`; fail clearly if `pytest` is missing.
4. Print a short PASS/FAIL summary for handoff.
5. If runtime deps are missing, fail with install hint (`pip install -r requirements.txt`).

Implementation:

```bash
bash ./agent_test.sh
```

`agent_test.sh` auto-detects `python` or `python3`.
