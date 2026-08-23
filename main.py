"""
main.py

Root-level entry point. This file exists specifically so Buildozer /
python-for-android (which by default looks for main.py at the project
root) has a stable, version-independent place to start the app, instead of
relying on buildozer.spec's newer `entrypoint` key.

For normal development, either this file or `python3 -m app.main` both
work identically -- they end up running the exact same app.main.main().
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import main

if __name__ == "__main__":
    main()
