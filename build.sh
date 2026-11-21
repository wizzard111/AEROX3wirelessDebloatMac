#!/bin/sh
# Creates .venv, installs dependencies, runs the tests and builds "dist/Aerox Lite.app".
set -e
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
    echo "Python 3 was not found. Install it from https://www.python.org/downloads/macos/" >&2
    exit 1
fi
if ! "$PY" -c "import tkinter" 2>/dev/null; then
    echo "Tkinter is missing. With Homebrew: brew install python-tk" >&2
    exit 1
fi
[ -x .venv/bin/python ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements.txt -r requirements-build.txt
.venv/bin/python -X utf8 -m unittest discover -s tests -v
.venv/bin/python -X utf8 -m PyInstaller --clean --noconfirm AeroxLite.spec
echo
echo "Built successfully: dist/Aerox Lite.app"
echo "Move it to /Applications, then allow it under Privacy & Security → Input Monitoring and Accessibility."
