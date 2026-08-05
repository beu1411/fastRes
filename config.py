import json
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))
else:
    BASE_DIR = Path(__file__).parent
    BUNDLE_DIR = BASE_DIR

DATA_DIR = Path(os.getenv("APPDATA", str(BASE_DIR))) / "FastRes"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_FILE = DATA_DIR / "custom_resolutions.json"
CONFIG_FILE = DATA_DIR / "config.json"
ASSETS = BUNDLE_DIR / "assets"
ICON_PATH = ASSETS / "beu.ico"

DEFAULT_CONFIG = {
    "language": "en",
    "theme": "dark",
    "hide_welcome": False,
    "game_path": "",
    "enable_blood": True,
}


def load_config():
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text(encoding="utf-8"))}
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def load_customs():
    if not CUSTOM_FILE.exists():
        return []
    try:
        data = json.loads(CUSTOM_FILE.read_text(encoding="utf-8"))
        return [(int(w), int(h)) for w, h in data]
    except Exception:
        return []


def save_customs(customs):
    CUSTOM_FILE.write_text(json.dumps(customs, indent=2), encoding="utf-8")
