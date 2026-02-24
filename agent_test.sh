#!/usr/bin/env bash
set -euo pipefail

detect_python_bin() {
  if command -v python > /dev/null 2>&1; then
    echo "python"
  elif command -v python3 > /dev/null 2>&1; then
    echo "python3"
  else
    echo ""
  fi
}

run_automated_tests() {
  local repo_root
  local py_bin
  repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$repo_root"

  py_bin="$(detect_python_bin)"
  if [ -z "$py_bin" ]; then
    echo "[agent-test] no python interpreter found (python/python3)"
    return 127
  fi

  echo "[agent-test] running compile checks"
  "$py_bin" -m compileall .

  echo "[agent-test] checking CLI contract"
  "$py_bin" main.py --help > /dev/null

  if [ -d "tests" ]; then
    echo "[agent-test] tests/ found, running pytest"
    if "$py_bin" - <<'PY'
import importlib.util
import sys

sys.exit(0 if importlib.util.find_spec("pytest") else 1)
PY
    then
      "$py_bin" -m pytest -q
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
