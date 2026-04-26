"""
API endpoints για διεθνοποίηση (i18n).
Επιστρέφει UI strings στην επιλεγμένη γλώσσα.
"""

import json
from fastapi import APIRouter, HTTPException
from core.config import STRINGS_DIR, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/api/language", tags=["Language"])


@router.get("/{lang}")
async def get_strings(lang: str) -> dict:
    """Επιστρέφει όλα τα UI strings για τη ζητούμενη γλώσσα."""

    # Έλεγχος αν η γλώσσα υποστηρίζεται
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: '{lang}'. Supported: {SUPPORTED_LANGUAGES}",
        )

    # Φόρτωση αρχείου μεταφράσεων
    strings_file = STRINGS_DIR / f"{lang}.json"
    if not strings_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Strings file not found for language: '{lang}'",
        )

    with open(strings_file, "r", encoding="utf-8") as f:
        strings = json.load(f)

    return strings


@router.get("/")
async def list_languages() -> dict:
    """Επιστρέφει τη λίστα υποστηριζόμενων γλωσσών."""
    return {
        "supported": SUPPORTED_LANGUAGES,
        "labels": {
            "en": "English",
            "el": "Ελληνικά",
            "de": "Deutsch",
        },
    }
