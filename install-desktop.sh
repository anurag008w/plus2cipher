#!/usr/bin/env bash
# install-desktop.sh -- registers +2 Cipher as a normal desktop application
# (appears in your application menu, launches with a double-click, no
# terminal window). Safe to re-run.

set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"

DEST="$APPS_DIR/plus2cipher.desktop"

sed \
    -e "s|__RUN_SCRIPT_PATH__|$PROJECT_DIR/run.sh|g" \
    -e "s|__ICON_PATH__|$PROJECT_DIR/assets/icons/icon_512.png|g" \
    "$PROJECT_DIR/plus2cipher.desktop" > "$DEST"

chmod +x "$DEST"
chmod +x "$PROJECT_DIR/run.sh"

# Refresh the desktop database if the tool is available (not on every distro).
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

echo "+2 Cipher installed. It should now appear in your application menu."
echo "Launcher written to: $DEST"
