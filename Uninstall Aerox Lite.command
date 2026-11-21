#!/bin/bash
# Removes Aerox Lite: the app, its login item and its macOS permissions.
# Then asks whether to keep the settings and this folder, or remove everything
# (including the installer and this uninstaller).
APP="/Applications/Aerox Lite.app"
AGENT="$HOME/Library/LaunchAgents/io.github.aeroxlite.plist"
SETTINGS="$HOME/Library/Application Support/AeroxLite"
BUNDLE_ID="io.github.aeroxlite"
DIR="$(cd "$(dirname "$0")" && pwd)"

# Only a folder that is clearly the Aerox Lite download may be deleted as a whole.
is_package() {
    [ -f "$DIR/Install Aerox Lite.command" ] && { [ -d "$DIR/src" ] || [ -d "$DIR/app" ] || [ -d "$DIR/packaging" ]; } \
        && [ -w "$DIR" ] && [ "$DIR" != "$HOME" ] && [ "$DIR" != "/" ]
}

echo "================================================"
echo "  Aerox Lite uninstaller"
echo "================================================"
echo "What should be removed?"
echo "  1) Only the app            (your settings and this folder stay)"
if is_package; then
    echo "  2) Everything              (the app, its settings and this folder:"
    echo "                              $DIR"
    echo "                              including the installer and this uninstaller)"
else
    echo "  2) The app and its settings"
fi
read -r -p "Choose [1/2]: " choice
echo

osascript -e 'quit app "Aerox Lite"' 2>/dev/null
sleep 1
if [ -d "$APP" ]; then
    rm -rf "$APP" 2>/dev/null || sudo rm -rf "$APP"
    echo "Removed $APP"
fi
if [ -f "$AGENT" ]; then
    launchctl bootout "gui/$(id -u)/$BUNDLE_ID" 2>/dev/null
    rm -f "$AGENT"; echo "Login item removed."
fi
tccutil reset ListenEvent "$BUNDLE_ID" >/dev/null 2>&1 && echo "Input Monitoring permission reset."
tccutil reset Accessibility "$BUNDLE_ID" >/dev/null 2>&1 && echo "Accessibility permission reset."

if [ "$choice" = "2" ]; then
    [ -d "$SETTINGS" ] && rm -rf "$SETTINGS" && echo "Settings removed."
    if is_package; then
        cd "$HOME" || exit 1
        rm -rf "$DIR" && echo "Removed the folder $DIR"
    fi
else
    [ -d "$SETTINGS" ] && echo "Settings kept in $SETTINGS"
fi
echo "Done."
read -r -n 1 -p "Press any key to close this window." _; echo
