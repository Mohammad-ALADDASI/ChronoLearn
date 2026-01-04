"""
tbox_loader.py
--------------------
Utility for loading ontology T-Box templates used by both:
- triple_generator.py
- triple_validator.py

Provides:
- Loading T-Box TTL templates
- Returning allowed predicates per theme
- Returning the ontology class (e.g., dbo:Event)
"""

import os
import json


ONTOLOGY_DIR = "ontology"


# ------------------------------------------------------------------
# 1. Allowed predicates per theme
# ------------------------------------------------------------------
EVENT_PREDICATES = {
    "occurredIn": "وقع في",
    "occurredOn": "وقع بتاريخ",
    "hasParticipant": "شارك فيه",
    "hasOutcome": "نتج عنه",
    "relatedToEvent": "مرتبط ب",
    "precededBy": "سبق",
    "followedBy": "تلاه"
}

CULTURAL_PREDICATES = {
    "originatedIn": "نشأت في",
    "practicedBy": "تمارس من قبل",
    "belongsToCulture": "ينتمي إلى ثقافة",
    "relatedTradition": "مرتبط بتقليد",
    "hasSymbolism": "له دلالة"
}


# ------------------------------------------------------------------
# 2. Predicate Lookup
# ------------------------------------------------------------------
def load_allowed_predicates(theme: str):
    """
    Returns allowed predicates for the given theme.
    Used by triple_generator and triple_validator.
    """
    if theme == "event":
        return EVENT_PREDICATES
    if theme == "cultural":
        return CULTURAL_PREDICATES
    return {}  # user will provide their own T-Box for "other" theme


# ------------------------------------------------------------------
# 3. Load T-Box TTL from file
# ------------------------------------------------------------------
def load_tbox_file(filename: str) -> str:
    """
    Reads the TTL file under ontology/.
    If missing, returns a warning placeholder.
    """
    path = os.path.join(ONTOLOGY_DIR, filename)
    if not os.path.exists(path):
        return f"# WARNING: Missing T-Box file: {filename}"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------------
# 4. Main function to retrieve T-Box template + class
# ------------------------------------------------------------------
def load_tbox_template(theme: str, user_tbox: str = None):
    """
    Returns:
    - T-Box TTL template as a string
    - Ontology class associated with the theme

    If theme == "other" → user_tbox must be provided.
    """

    # EVENT THEME
    if theme == "event":
        template = load_tbox_file("event.tbox.ttl")
        return template, "dbo:Event"

    # CULTURAL THEME
    if theme == "cultural":
        template = load_tbox_file("cultural.tbox.ttl")
        return template, "dbo:CulturalHeritageObject"

    # USER-DEFINED THEME
    if theme == "other":
        if not user_tbox:
            raise ValueError("User must provide a T-Box class when theme='other'.")
        template = load_tbox_file("custom.tbox.ttl")
        return template, user_tbox

    raise ValueError(f"Unknown theme: {theme}")
