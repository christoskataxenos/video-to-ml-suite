"""
API endpoints για το παιδί.
Επιστρέφει δεδομένα session, πρόοδο και επιτεύγματα.
"""

from fastapi import APIRouter
from models.settings import ChildSession
from core.database import get_db

router = APIRouter(prefix="/api/child", tags=["Child"])


@router.get("/home", response_model=ChildSession)
async def get_child_home() -> ChildSession:
    """Ανάκτηση τρέχουσας session παιδιού με ρυθμίσεις + πρόοδο."""
    db = await get_db()
    try:
        # Ρυθμίσεις από τον γονέα
        cursor = await db.execute(
            "SELECT child_name, language, annotation_mode, ui_style, interaction_mode "
            "FROM settings WHERE id = 1"
        )
        settings_row = await cursor.fetchone()

        # Συνολικό score
        score_cursor = await db.execute(
            "SELECT COALESCE(SUM(score), 0) FROM progress"
        )
        score_row = await score_cursor.fetchone()
        total_score = score_row[0] if score_row else 0

        # Επιτεύγματα (badges)
        achievements_cursor = await db.execute(
            "SELECT badge_name FROM achievements"
        )
        achievement_rows = await achievements_cursor.fetchall()
        badges = [row[0] for row in achievement_rows]

        if settings_row:
            return ChildSession(
                child_name=settings_row[0],
                language=settings_row[1],
                annotation_mode=settings_row[2],
                ui_style=settings_row[3],
                interaction_mode=settings_row[4],
                total_score=total_score,
                achievements=badges,
            )

        # Defaults αν δεν βρεθούν ρυθμίσεις
        return ChildSession(
            child_name="Explorer",
            language="en",
            annotation_mode="sticker",
            ui_style="mascot",
            interaction_mode="storyteller",
            total_score=0,
            achievements=[],
        )
    finally:
        await db.close()
