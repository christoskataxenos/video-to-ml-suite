"""
API endpoints για τον Γονέα/Admin.
Διαχείριση ρυθμίσεων παιδιού (γλώσσα, mode, στυλ UI).
"""

from fastapi import APIRouter
from models.settings import ParentSettings
from core.database import get_db

router = APIRouter(prefix="/api/parent", tags=["Parent"])


@router.get("/settings", response_model=ParentSettings)
async def get_settings() -> ParentSettings:
    """Ανάκτηση τρεχουσών ρυθμίσεων γονέα."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT child_name, language, annotation_mode, ui_style, interaction_mode "
            "FROM settings WHERE id = 1"
        )
        row = await cursor.fetchone()
        if row:
            return ParentSettings(
                child_name=row[0],
                language=row[1],
                annotation_mode=row[2],
                ui_style=row[3],
                interaction_mode=row[4],
            )
        # Επιστροφή defaults αν δεν βρεθεί εγγραφή
        return ParentSettings()
    finally:
        await db.close()


@router.post("/settings", response_model=ParentSettings)
async def save_settings(settings: ParentSettings) -> ParentSettings:
    """Αποθήκευση ρυθμίσεων γονέα στη βάση."""
    db = await get_db()
    try:
        await db.execute(
            """
            UPDATE settings SET
                child_name = ?,
                language = ?,
                annotation_mode = ?,
                ui_style = ?,
                interaction_mode = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
            """,
            (
                settings.child_name,
                settings.language,
                settings.annotation_mode,
                settings.ui_style,
                settings.interaction_mode,
            ),
        )
        await db.commit()
        return settings
    finally:
        await db.close()
