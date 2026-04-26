"""
Ρυθμίσεις εφαρμογής PolyMind.
Κεντρική διαχείριση παραμέτρων για backend.
"""

from pathlib import Path
from pydantic import BaseModel


# Βασικά paths του project
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "polymind.db"
STRINGS_DIR = BASE_DIR / "strings"

# Υποστηριζόμενες γλώσσες
SUPPORTED_LANGUAGES = ["en", "el", "de"]
DEFAULT_LANGUAGE = "en"


class AppConfig(BaseModel):
    """Κεντρική ρύθμιση εφαρμογής."""

    app_name: str = "PolyMind"
    version: str = "1.0.0"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
