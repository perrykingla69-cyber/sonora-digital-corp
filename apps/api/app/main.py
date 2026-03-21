"""Compat entrypoint for the v2 monorepo layout.

This file intentionally re-exports the current FastAPI application from the
legacy backend package so we can migrate incrementally without breaking the
running system.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
LEGACY_BACKEND = ROOT / "backend"
if str(LEGACY_BACKEND) not in sys.path:
    sys.path.insert(0, str(LEGACY_BACKEND))

from main import app  # noqa: E402
