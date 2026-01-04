"""
theme_detector.py
-------------------
This module determines the semantic *theme* of a text segment.

Themes:
- "event"      → time-bound actions, incidents, wars, conferences, etc.
- "cultural"   → arts, heritage, identity, customs, language, social norms
- "other"      → anything that does not explicitly fit the above two

Pipeline:
1. Clean + normalize text
2. Apply lightweight rule-based hints
3. Ask OpenAI to classify into one of the themes
4. Allow user override if "other"

The returned theme will later determine which T-Box class
(event ontology, cultural ontology, or user-defined class)
should be applied in triple generation.
"""

import json
import os
from typing import Dict, Any

from openai import OpenAI
from dotenv import load_dotenv

from .text_normalizer import clean_text, prepare_for_topic_detection


# ------------------------------------------------------
# Load API key
# ------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY missing in environment.")

client = OpenAI(api_key=OPENAI_API_KEY)


# ------------------------------------------------------
# Lightweight Rule-Based Detector (pre-filter)
# ------------------------------------------------------
def rule_based_theme(text: str) -> str | None:
    """
    Detect obvious cases to help the LLM.
    Returns:
        "event", "cultural", or None (means let LLM decide).
    """

    t = text.lower()

    # Event triggers
    event_keywords = [
        "event", "war", "conference", "summit", "attack", "explosion",
        "crisis", "meeting", "agreement", "protest", "incident",
        "حدث", "اجتماع", "مؤتمر", "قمه", "ازمه", "انفجار", "هجوم", "صدام", "عمليه", "اتفاق"
    ]

    # Cultural triggers
    cultural_keywords = [
        "culture", "heritage", "identity", "tradition", "language",
        "art", "music", "folklore", "customs",
        "ثقافه", "تراث", "هويه", "عادات", "تقاليد", "لغه", "ادب", "فن", "موسيقى"
    ]

    if any(k in t for k in event_keywords):
        return "event"

    if any(k in t for k in cultural_keywords):
        return "cultural"

    return None  # uncertain → let LLM handle it


# ------------------------------------------------------
# LLM Prompt for Theme Classification
# ------------------------------------------------------
THEME_PROMPT = """
أريد منك تصنيف النص التالي ضمن أحد الأنواع التالية فقط:

1. "event"      → إذا كان النص يتحدث عن حدث، واقعه، لقاء، مؤتمر، صراع، انفجار، كارثه، اجتماع... إلخ.
2. "cultural"   → إذا كان النص يتحدث عن ثقافه، تراث، هويه، عادات، لغه، فن، أعراف اجتماعيه... إلخ.
3. "other"      → إذا لم يكن النص ينتمي إلى الفئتين السابقتين.

❗ تعليمات:
- أعد فقط JSON بهذا الشكل: {"theme": "event"} أو {"theme": "cultural"} أو {"theme": "other"}
- بدون أي شرح خارجي.
- ركّز على المعنى العام وليس الكلمات المفردة فقط.

النص:
{content}
"""


# ------------------------------------------------------
# Utility: Safe JSON Loader
# ------------------------------------------------------
def safe_load_json(response: str) -> Dict[str, Any]:
    """
    Attempts to decode model response as JSON.
    """
    try:
        return json.loads(response)
    except:
        # Remove markdown formatting if present
        if "```" in response:
            txt = response.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(txt)
            except:
                pass

    raise ValueError(f"❌ Invalid JSON returned by model:\n{response}")


# ------------------------------------------------------
# LLM-Based Theme Detection
# ------------------------------------------------------
def llm_theme_detector(text: str) -> str:
    """
    Uses OpenAI to classify the theme when rule-based detection
    is uncertain.
    """

    cleaned = prepare_for_topic_detection(text)
    prompt = THEME_PROMPT.format(content=cleaned)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an expert classifier for semantic themes."},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content
    data = safe_load_json(raw)

    theme = data.get("theme")
    if theme not in ["event", "cultural", "other"]:
        raise ValueError(f"❌ Invalid theme returned: {theme}")

    return theme


# ------------------------------------------------------
# Unified Theme Detector (pipeline entry point)
# ------------------------------------------------------
def detect_theme(text: str) -> Dict[str, Any]:
    """
    Main entry point for the pipeline or Flask API.
    Returns:
    {
        "theme": "event" | "cultural" | "other",
        "source": "rule_based" | "llm"
    }
    """

    clean = clean_text(text)

    # Step 1: Rule-based quick check
    rule_theme = rule_based_theme(clean)
    if rule_theme:
        return {"theme": rule_theme, "source": "rule_based"}

    # Step 2: Fall back to LLM classification
    llm_theme = llm_theme_detector(clean)
    return {"theme": llm_theme, "source": "llm"}


# ------------------------------------------------------
# Module Test
# ------------------------------------------------------
if __name__ == "__main__":
    sample_event = "انعقد المؤتمر الدولي للمناخ بحضور ممثلين من 40 دولة."
    sample_cultural = "تناولت الندوة موضوع الهويه العربيه وتاريخ التراث الشعبي."
    sample_other = "يشرح النص بعض المفاهيم الاقتصاديه في منطقه الشرق الاوسط."

    print("Event Test:", detect_theme(sample_event))
    print("Cultural Test:", detect_theme(sample_cultural))
    print("Other Test:", detect_theme(sample_other))
