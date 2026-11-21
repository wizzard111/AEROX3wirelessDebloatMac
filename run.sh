#!/bin/sh
# Starts Aerox Lite: the built app if present, otherwise from source in .venv.
cd "$(dirname "$0")"
if [ -d "dist/Aerox Lite.app" ]; then
    exec open "dist/Aerox Lite.app" --args "$@"
fi
if [ -x .venv/bin/python ]; then
    exec .venv/bin/python aerox_lite.py "$@"
fi
echo "Run ./build.sh first." >&2
exit 1
