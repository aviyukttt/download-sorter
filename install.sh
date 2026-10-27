#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/download-sorter"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
AUTOSTART_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
ENABLE_AUTOSTART=0

if [[ "${1:-}" == "--autostart" ]]; then
  ENABLE_AUTOSTART=1
elif [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'USAGE'
Usage: ./install.sh [--autostart]

Installs Download Sorter for the current user and creates an application-menu launcher.
--autostart  Also launch Download Sorter automatically when you log in.
USAGE
  exit 0
elif [[ $# -gt 0 ]]; then
  echo "Unknown option: $1" >&2
  echo "Run ./install.sh --help for usage." >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it with: sudo apt update && sudo apt install python3" >&2
  exit 1
fi

if ! python3 - <<'PY' >/dev/null 2>&1
import tkinter
PY
then
  echo "Tkinter is required. Install it with: sudo apt update && sudo apt install python3-tk" >&2
  exit 1
fi

mkdir -p "$APP_DIR" "$DESKTOP_DIR"
install -Dm755 "$SCRIPT_DIR/app.py" "$APP_DIR/app.py"

# Expand the placeholder only after the path is known; this works from any clone directory.
sed "s|__APP_DIR__|${APP_DIR//|/\\|}|g" "$SCRIPT_DIR/download-sorter.desktop.in" \
  | install -Dm644 /dev/stdin "$DESKTOP_DIR/download-sorter.desktop"

if [[ "$ENABLE_AUTOSTART" -eq 1 ]]; then
  mkdir -p "$AUTOSTART_DIR"
  cp "$DESKTOP_DIR/download-sorter.desktop" "$AUTOSTART_DIR/download-sorter.desktop"
fi

# Refresh the desktop database when available; it is optional on minimal installations.
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi

echo "Download Sorter installed successfully."
echo "Launch it from your application menu, or run: python3 '$APP_DIR/app.py'"
if [[ "$ENABLE_AUTOSTART" -eq 1 ]]; then
  echo "Autostart is enabled for the current user."
else
  echo "To enable autostart later, run: $SCRIPT_DIR/install.sh --autostart"
fi
