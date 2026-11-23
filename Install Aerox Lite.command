#!/bin/bash
# Aerox Lite installer for macOS (Intel and Apple Silicon).
# Double-click this file: Terminal opens and shows every step. It finds or installs Python,
# builds the app for this Mac, opens a window to drag it into Applications, then launches it.
# The app itself asks macOS for the Input Monitoring / Accessibility permissions on first launch.

cd "$(dirname "$0")" || exit 1
LOG="$PWD/install.log"
exec > >(tee "$LOG") 2>&1

bold() { printf "\n\033[1m==> %s\033[0m\n" "$*"; }
fail() {
    printf "\n\033[31mInstallation failed: %s\033[0m\nFull log: %s\n" "$*" "$LOG"
    read -r -n 1 -p "Press any key to close this window." _; echo; exit 1
}
ask() {  # ask "Question" -> 0 for yes (default), 1 for no
    local a; read -r -p "$1 [Y/n] " a; [[ -z "$a" || "$a" =~ ^[Yy] ]]
}

echo "================================================"
echo "  Aerox Lite installer"
echo "  macOS $(sw_vers -productVersion), $(uname -m)"
echo "================================================"

# ---------------------------------------------------------------- 1. SteelSeries GG
if pgrep -qif "SteelSeries ?GG|SteelSeriesEngine"; then
    bold "SteelSeries GG is running"
    echo "It overwrites the mouse settings and lighting while it runs."
    if ask "Quit SteelSeries GG now?"; then
        osascript -e 'quit app "SteelSeries GG"' 2>/dev/null || pkill -if "SteelSeries ?GG"
        echo "Done. Also remove it from System Settings > General > Login Items if it starts by itself."
    fi
fi

# ---------------------------------------------------------------- 2. Python 3.10-3.14 with Tk
bold "Looking for Python 3.10 - 3.14 with Tk"
check_py() {
    "$1" - 2>/dev/null <<'EOF'
import sys, tkinter
ok = (3, 10) <= sys.version_info[:2] <= (3, 14) and tkinter.TkVersion >= 8.6
print("%d.%d.%d" % sys.version_info[:3]) if ok else sys.exit(1)
EOF
}
PY=""
for c in /Library/Frameworks/Python.framework/Versions/3.1{4,3,2,1,0}/bin/python3 \
         python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
    p=$(command -v "$c" 2>/dev/null) || continue
    if v=$(check_py "$p"); then PY="$p"; echo "Found Python $v: $p"; break; fi
done

if [ -z "$PY" ]; then
    echo "No suitable Python found. The official installer from python.org (about 70 MB) is needed once."
    ask "Download and install it now? (your Mac password will be requested)" || fail "Python is required."
    bold "Finding the latest Python 3.14 release"
    VERSIONS=$(curl -fsSL https://www.python.org/ftp/python/ | grep -oE 'href="3\.14\.[0-9]+/"' \
               | grep -oE '3\.14\.[0-9]+' | sort -t. -k3 -n -r)
    PKG=""
    for v in $VERSIONS; do
        url="https://www.python.org/ftp/python/$v/python-$v-macos11.pkg"
        if curl -fsIL "$url" >/dev/null 2>&1; then PKG="$url"; PYV="$v"; break; fi
    done
    [ -n "$PKG" ] || fail "could not find the Python installer. Install it from https://www.python.org/downloads/macos/ and run this again."
    TMPD=$(mktemp -d)
    bold "Downloading Python $PYV"
    curl -fL --progress-bar -o "$TMPD/python.pkg" "$PKG" || fail "download failed"
    bold "Installing Python $PYV"
    sudo installer -pkg "$TMPD/python.pkg" -target / || fail "the Python installer failed"
    rm -rf "$TMPD"
    CERT="/Applications/Python 3.14/Install Certificates.command"
    [ -f "$CERT" ] && { bold "Installing certificates for Python"; sh "$CERT" || true; }
    PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
    v=$(check_py "$PY") || fail "Python was installed but does not work. See $LOG"
    echo "Python $v is ready."
fi

# ---------------------------------------------------------------- 3. build
bold "Building Aerox Lite for this Mac (takes a few minutes the first time)"
if [ -x .venv/bin/python ] && [ "$(.venv/bin/python -c 'import sys;print(sys.version)')" != "$("$PY" -c 'import sys;print(sys.version)')" ]; then
    echo "Removing an old build environment made with another Python."
    rm -rf .venv
fi
chmod +x packaging/macos/*.sh 2>/dev/null
rm -rf build
PYTHON="$PY" packaging/macos/build.sh || fail "the build did not succeed (see the messages above)"

# A lasting local signature, so macOS keeps the app's permissions after updates (the Mac password is
# asked once), and "Update Aerox Lite" in Applications for later updates.
bash "Update Aerox Lite.command" --setup --sign "build/dist/Aerox Lite.app"

bold "Creating the installer window"
packaging/macos/make-dmg.sh "build/AeroxLite.dmg" || fail "could not create the disk image"

# ---------------------------------------------------------------- 4. drag to Applications
TARGET="/Applications/Aerox Lite.app"
osascript -e 'quit app "Aerox Lite"' 2>/dev/null
STAMP=$(date +%s)
open "build/AeroxLite.dmg"
bold "Drag \"Aerox Lite\" onto \"Applications\" in the window that just opened"
echo "(If macOS asks whether to replace an older version, choose Replace.)"
echo "Waiting for the app to appear in Applications…"
moved=""
for _ in $(seq 1 600); do
    if [ -d "$TARGET" ] && [ "$(stat -f %c "$TARGET" 2>/dev/null || echo 0)" -ge "$STAMP" ]; then moved=1; break; fi
    sleep 1
done
if [ -z "$moved" ]; then
    echo "Not moved yet. You can still drag it later; then open Aerox Lite from Applications."
    read -r -n 1 -p "Press any key to close this window." _; echo; exit 0
fi
sleep 3   # let Finder finish copying
hdiutil detach "/Volumes/Aerox Lite" -quiet 2>/dev/null || true

# ---------------------------------------------------------------- 5. first launch + permissions
bold "Starting Aerox Lite"
open "$TARGET"
cat <<'EOF'

Aerox Lite is installed and running.

macOS will now show permission requests from Aerox Lite:
  * "Keystroke Receiving" / Input Monitoring -> click "Open System Settings" and switch Aerox Lite ON
  * Accessibility                            -> click "Open System Settings" and switch Aerox Lite ON
Then quit Aerox Lite (Cmd+Q) and open it again from Applications.
These are needed only for macros, multi-click and smart lighting; mouse settings work without them.

Remember to click "SAVE TO MOUSE" after changing settings.
EOF
read -r -n 1 -p "Press any key to close this window." _; echo
