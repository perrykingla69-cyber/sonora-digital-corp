"""Helpers to bridge the v2 app with the legacy backend modules."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
LEGACY_BACKEND = ROOT / "backend"
if str(LEGACY_BACKEND) not in sys.path:
    sys.path.insert(0, str(LEGACY_BACKEND))
