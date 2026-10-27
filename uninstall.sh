#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/download-sorter"
DESKTOP_FILE="${XDG_DATA_HOME:-$HOME/.local/share}/applications/download-sorter.desktop"
AUTOSTART_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/autostart/download-sorter.desktop"

rm -rf "$APP_DIR"
rm -f "$DESKTOP_FILE" "$AUTOSTART_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${XDG_DATA_HOME:-$HOME/.local/share}/applications" >/dev/null 2>&1 || true
fi

echo "Download Sorter was uninstalled. Your organized files and settings were left untouched."
