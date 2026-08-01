from pathlib import Path

# Application
APP_NAME = "Kairos"
APP_VERSION = "0.1.0"

# Database
DATABASE_NAME = "kairos.db"
DATABASE_PATH = Path(DATABASE_NAME)

# Activity Tracking
TRACKING_INTERVAL_SECONDS = 2

# AI
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:4b"