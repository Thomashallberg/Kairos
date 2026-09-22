import os
from pathlib import Path

# Application
APP_NAME = "Kairos"
APP_VERSION = "0.1.0"

# Database
LOCAL_APP_DATA = Path(
    os.environ.get("LOCALAPPDATA", Path.home())
)

APP_DATA_DIR = LOCAL_APP_DATA / APP_NAME
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_NAME = "kairos.db"
DATABASE_PATH = APP_DATA_DIR / DATABASE_NAME

# Activity Tracking
TRACKING_INTERVAL_SECONDS = 2

# AI
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:4b"