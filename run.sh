#!/usr/bin/env bash
# run.sh -- launches +2 Cipher on Linux desktop.
#
# First run creates a local virtual environment and installs dependencies;
# every run after that just activates the venv and starts the app. Safe to
# double-click from a file manager (see install-desktop.sh / the .desktop
# launcher) as well as to run from a terminal.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up +2 Cipher for the first time (this only happens once)..."
    python3 -m venv "$VENV_DIR"
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
else
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
fi

exec python3 main.py
