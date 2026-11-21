#!/bin/sh
# Packs "dist/Aerox Lite.app" into a disk image with an Applications shortcut (drag-to-install window).
# usage: ./make-dmg.sh [output.dmg]
set -e
cd "$(dirname "$0")/../.."   # repository root
APP="build/dist/Aerox Lite.app"
OUT="${1:-build/AeroxLite.dmg}"
if [ ! -d "$APP" ]; then
    echo "$APP not found. Build it first: packaging/macos/build.sh" >&2
    exit 1
fi
# Ad-hoc signature: required on Apple Silicon; macOS ties the granted permissions to it.
codesign --force --deep --sign - "$APP"
STAGE=$(mktemp -d)
ditto "$APP" "$STAGE/Aerox Lite.app"
ln -s /Applications "$STAGE/Applications"
cp HOW-TO-INSTALL.txt "Uninstall Aerox Lite.command" "$STAGE/"
rm -f "$OUT"
hdiutil create -volname "Aerox Lite" -srcfolder "$STAGE" -fs HFS+ -format UDZO -ov "$OUT" >/dev/null
rm -rf "$STAGE"
echo "Disk image: $OUT"
