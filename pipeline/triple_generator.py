"""
triple_generator.py (Improved Version)
---------------------------------------
Generates ontology-aligned triples using:
- Event / Cultural T-Box constraints
- Allowed predicates ONLY
- Event-based segmentation for long narratives
- Strong grounding enforcement
- Verb-predicate filtering

This prevents noisy triples, ensures structure, and improves KG quality.
"""

import os
import re
from typing import List, Dict, Any

from openai import OpenAI
from .text_normalizer import clean_text
from tbox_loader import load_tbox_template


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------------------------------------
# 1. Allowed predicates per theme (canonical)
# ------------------------------------------------------
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


def get_allowed_predicates(theme: str) -> Dict[str, str]:
    if theme == "event":
        return EVENT_PREDICATES
    if theme == "cultural":
        return CULTURAL_PREDICATES
    return {}  # "other" theme requires user-defined T-Box


# ------------------------------------------------------
# 2. Automatic event segmentation
# ------------------------------------------------------
def segment_into_events(text: str) -> List[str]:
    """
    Splits large historical narrative into event-based chunks.
    Uses common Arabic event markers.
    """
    markers = [
        "معركة", "أحداث", "حرب", "اشتباك", "صراع", "وقعت",
        "اندلعت", "حدثت", "اجتياح", "عملية", "اغتيال"
    ]

    segments = []
    current = []

    for line in text.split("\n"):
        if any(m in line for m in markers):
            if current:
                segments.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        segments.append("\n".join(current))

    return [seg.strip() for seg in segments if seg.strip()]


# ------------------------------------------------------
# 3. Prompt template for LLM generation
# ------------------------------------------------------
def build_generation_prompt(text_segment: str, topics: List[str], theme: str, tbox_template: str) -> str:
    allowed_preds = get_allowed_predicates(theme)

    allowed_predicate_list = "\n".join([
        f"- {iri} (Arabic: {ar})"
        for iri, ar in allowed_preds.items()
    ])

    return f"""
مهمتك استخراج ثلاثيات معرفية (S-P-O) من النص التالي، ولكن ضمن شروط صارمة:

🔥 هام جداً:
❗ استخدم فقط العلاقات الموجودة في الـ T-Box التالي، ولا تنتج أية علاقات أخرى:

{tbox_template}

العلاقات المسموح بها:
{allowed_predicate_list}

المواضيع المختارة:
{topics}

النص:
{text_segment}

قواعد الاستخراج:
1. يجب أن ترتبط كل ثلاثية بحدث واضح (HistoricalEvent).
2. لا تستخرج علاقات لغوية مثل: "زادت في تحديها" أو "عملت على شل".
3. يجب أن يكون كل S-P-O موجوداً صراحة في النص.
4. يجب أن تكون P من القائمة أعلاه فقط.
5. لا تكرر المعلومات أو الأحداث.
6. ركّز على البنية الحدثية: من شارك؟ أين؟ متى؟ ما النتيجة؟

أعد النتيجة بصيغة JSON:
[
  {{"subject": "...", "predicate": "...", "object": "...", "span": "..."}}
]
"""


# ------------------------------------------------------
# 4. Generate triples for a text segment
# ------------------------------------------------------
def generate_triples_for_segment(
    text_segment: str,
    topics: List[str],
    theme: str,
    tbox_template: str
) -> List[Dict[str, Any]]:

    prompt = build_generation_prompt(text_segment, topics, theme, tbox_template)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    import json
    try:
        triples = json.loads(response.choices[0].message.content)
        return triples
    except Exception:
        return []


# ------------------------------------------------------
# 5. Main function: generate triples for whole text
# ------------------------------------------------------
def generate_triples(
    text: str,
    topics: List[str],
    theme: str,
    user_tbox: str = None
) -> Dict[str, Any]:

    text = clean_text(text)

    # Load ontology template
    tbox_template, tbox_class = load_tbox_template(theme, user_tbox)

    # Segment text into event chunks
    segments = segment_into_events(text)

    all_triples = []

    for seg in segments:
        triples = generate_triples_for_segment(seg, topics, theme, tbox_template)
        all_triples.extend(triples)

    # Filter P to allowed predicates only
    allowed = get_allowed_predicates(theme)
    clean_triples = [
        t for t in all_triples
        if t.get("predicate") in allowed
    ]

    return {
        "theme": theme,
        "tbox": tbox_class,
        "segments": segments,
        "triples": clean_triples
    }
