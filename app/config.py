from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "projects"
STATIC_DIR = ROOT / "static"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_REWRITE_ROUNDS = int(os.getenv("MAX_REWRITE_ROUNDS", "2"))
RECENT_SCENE_WINDOW = 4
