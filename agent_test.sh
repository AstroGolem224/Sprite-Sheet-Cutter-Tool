#!/usr/bin/env bash
set -euo pipefail

run_automated_tests() {
  local repo_root
  repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$repo_root"

  echo "[agent-test] running compile checks"
  python -m compileall .

  echo "[agent-test] checking CLI contract"
  python main.py --help > /dev/null

  if [ -d "tests" ]; then
    echo "[agent-test] tests/ found, running pytest"
    if python - <<'PY'
import importlib.util
import sys

sys.exit(0 if importlib.util.find_spec("pytest") else 1)
PY
    then
      python -m pytest -q
    else
      echo "[agent-test] pytest not installed, but tests/ exists"
      echo "[agent-test] install with: pip install pytest"
      return 2
    fi
  else
    echo "[agent-test] no tests/ directory yet, pytest step skipped"
  fi

  echo "[agent-test] PASS"
}

run_automated_tests "$@"
