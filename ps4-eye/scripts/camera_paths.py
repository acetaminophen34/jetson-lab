"""Shared camera data paths; no device access (Python 3.6+)."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = Path((os.environ.get("PS4_EYE_DATA") or str(REPO / "work" / "ps4-eye"))).expanduser().resolve()
CALIB_DIR = DATA / "calibration"
MODEL_DIR = DATA / "models"
CALIBRATION = CALIB_DIR / "stereo_calibration.npz"
PROTO = MODEL_DIR / "deploy.prototxt"
MODEL = MODEL_DIR / "res10.caffemodel"
