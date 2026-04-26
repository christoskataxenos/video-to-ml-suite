"""
Pydantic μοντέλα για ρυθμίσεις γονέα και session παιδιού.
Ορίζουν τη δομή των δεδομένων στο API.
"""

from pydantic import BaseModel, Field
from typing import Literal


class ParentSettings(BaseModel):
    """Ρυθμίσεις που ελέγχει ο γονέας/admin."""

    # Όνομα παιδιού — χρησιμοποιείται από τη μασκότ
    child_name: str = Field(default="Explorer", min_length=1, max_length=50)

    # Γλώσσα (Αγγλικά, Ελληνικά, Γερμανικά)
    language: Literal["en", "el", "de"] = "en"

    # Τρόπος annotation: sticker (μικρές ηλικίες) ή catch (μεγαλύτερες)
    annotation_mode: Literal["sticker", "catch"] = "sticker"

    # Στυλ UI: μασκότ, μόνο εικονίδια, ηχητική καθοδήγηση
    ui_style: Literal["mascot", "icon", "audio"] = "mascot"

    # Τρόπος αλληλεπίδρασης μετά το training
    interaction_mode: Literal["logic_blocks", "storyteller"] = "storyteller"


class ChildSession(BaseModel):
    """Δεδομένα τρέχουσας session παιδιού."""

    child_name: str
    language: str
    annotation_mode: str
    ui_style: str
    interaction_mode: str
    total_score: int = 0
    achievements: list[str] = []


class ProgressEntry(BaseModel):
    """Μια εγγραφή προόδου."""

    activity: str
    score: int = 0
