"""
Βάση δεδομένων SQLite για αποθήκευση ρυθμίσεων και προόδου.
Χρησιμοποιεί aiosqlite για async λειτουργίες.
"""

import aiosqlite
from pathlib import Path
from core.config import DB_PATH


async def init_db() -> None:
    """Αρχικοποίηση βάσης δεδομένων — δημιουργία πινάκων αν δεν υπάρχουν."""

    # Δημιουργία φακέλου data αν δεν υπάρχει
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(str(DB_PATH)) as db:
        # Πίνακας ρυθμίσεων γονέα/admin
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                child_name TEXT DEFAULT 'Explorer',
                language TEXT DEFAULT 'en',
                annotation_mode TEXT DEFAULT 'sticker',
                ui_style TEXT DEFAULT 'mascot',
                interaction_mode TEXT DEFAULT 'storyteller',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Πίνακας προόδου παιδιού
        await db.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Πίνακας επιτευγμάτων (badges)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                badge_name TEXT NOT NULL UNIQUE,
                description TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Εισαγωγή προεπιλεγμένων ρυθμίσεων αν δεν υπάρχουν
        existing = await db.execute("SELECT COUNT(*) FROM settings")
        count = await existing.fetchone()
        if count and count[0] == 0:
            await db.execute(
                "INSERT INTO settings (child_name, language) VALUES (?, ?)",
                ("Explorer", "en")
            )

        await db.commit()


async def get_db() -> aiosqlite.Connection:
    """Επιστρέφει σύνδεση στη βάση δεδομένων."""
    return await aiosqlite.connect(str(DB_PATH))
