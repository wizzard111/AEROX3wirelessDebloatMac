#!/bin/sh
# Developer run: the built app if present, otherwise from source in .venv.
cd "$(dirname "$0")/../.."   # repository root
if [ -d "build/dist/Aerox Lite.app" ]; then
    exec open "build/dist/Aerox Lite.app" --args "$@"
fi
if [ -x .venv/bin/python ]; then
    exec .venv/bin/python src/aerox_lite.py "$@"
fi
echo "Run packaging/macos/build.sh first (or Install Aerox Lite.command)." >&2
exit 1
