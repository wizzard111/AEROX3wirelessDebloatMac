#!/bin/sh
# Creates .venv, installs dependencies, runs the tests and builds "build/dist/Aerox Lite.app".
set -e
cd "$(dirname "$0")/../.."   # repository root
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
.venv/bin/python -m pip install -q -r packaging/requirements.txt -r packaging/requirements-build.txt
.venv/bin/python -X utf8 -m unittest discover -s tests -v
.venv/bin/python -X utf8 -m PyInstaller --clean --noconfirm --log-level WARN --distpath build/dist --workpath build/work packaging/macos/AeroxLite.spec
"build/dist/Aerox Lite.app/Contents/MacOS/Aerox Lite" --self-test || { echo "The built app failed its self-test." >&2; exit 1; }
echo
echo "Built successfully: build/dist/Aerox Lite.app"
echo "Move it to /Applications, then allow it under Privacy & Security → Input Monitoring and Accessibility."
