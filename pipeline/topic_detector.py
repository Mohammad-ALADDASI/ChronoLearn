"""
topic_detector.py
-------------------
This module handles topic extraction from Arabic/English PDF text.
It uses OpenAI LLM models and produces a clean JSON list of topics.

Pipeline:
1. Clean text using the text normalizer
2. Generate high-level conceptual topics
3. Generate keyphrase-style subtopics (optional)
4. Return both for user selection (1–3 topics)
"""

import json
from typing import List, Dict, Any

from openai import OpenAI
from dotenv import load_dotenv
import os

from pipeline.text_normalizer import prepare_for_topic_detection, clean_text


# ------------------------------------------------------
# Load API key
# ------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY missing in environment.")


client = OpenAI(api_key=OPENAI_API_KEY)


# ------------------------------------------------------
# Core Topic Extraction Prompt
# ------------------------------------------------------
TOPIC_PROMPT = """
أريد منك استخراج المواضيع الرئيسية من النص التالي.

❗ تعليمات ضرورية:
- أعد فقط JSON صالح 100%.
- بدون أي شرح خارجي، بدون نص خارج JSON.
- استخرج بين 4 إلى 8 مواضيع عالية المستوى.
- المواضيع يجب أن تكون عامة، وليست كلمات مفردة فقط.
- أمثلة على ما أريده:
[معركة الكرامة، معاهدة السلام، التراث الثقافي الفلسطيني، النكبة]
النص:
{content}
"""

# ------------------------------------------------------
# Optional Keyphrase Extraction Prompt
# ------------------------------------------------------
KEYPHRASE_PROMPT = """
استخرج أهم المفاهيم والكلمات المفتاحية من النص التالي.

❗ أعد فقط JSON بصيغة قائمة كلمات (Arab/English).

مثال:
["الهجرة", "الأطفال", "الصحة العامة", "social policy", "youth programs"]

النص:
{content}
"""


# ------------------------------------------------------
# Utility: safe JSON parsing
# ------------------------------------------------------
def safe_load_json(response: str) -> Any:
    """
    Attempts to parse JSON regardless of model formatting oddities.
    """
    try:
        return json.loads(response)
    except Exception:
        # Remove Markdown fences if present
        if "```" in response:
            response = response.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(response)
            except:
                pass

    raise ValueError(f"❌ Model returned invalid JSON:\n{response}")


# ------------------------------------------------------
# Extract Main Topics
# ------------------------------------------------------
def extract_main_topics(text: str, max_topics: int = 8) -> List[str]:
    """
    Extracts high-level conceptual topics using OpenAI.
    """

    cleaned = prepare_for_topic_detection(text)

    prompt = TOPIC_PROMPT.format(content=cleaned)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an expert topic extractor."},
            {"role": "user", "content": prompt},
        ]
    )

    raw = response.choices[0].message.content
    topics = safe_load_json(raw)

    # Limit number of topics
    topics = topics[:max_topics]

    return topics


# ------------------------------------------------------
# Optional: Extract keyphrases for UI assistance
# ------------------------------------------------------
def extract_keyphrases(text: str, max_phrases: int = 12) -> List[str]:
    """
    Extracts finer-grained keyphrases from text.
    Useful to support the user in selecting relevant topics.
    """

    cleaned = prepare_for_topic_detection(text)
    prompt = KEYPHRASE_PROMPT.format(content=cleaned)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an expert keyword extractor."},
            {"role": "user", "content": prompt},
        ]
    )

    raw = response.choices[0].message.content
    keyphrases = safe_load_json(raw)

    return keyphrases[:max_phrases]


# ------------------------------------------------------
# Unified topic extraction pipeline
# ------------------------------------------------------
def detect_topics(text: str) -> Dict[str, Any]:
    """
    Main function used by Flask or the pipeline.
    Returns:
    {
       "topics": [...],
       "keywords": [...]   (optional)
    }
    """

    main_topics = extract_main_topics(text)
    keyphrases = extract_keyphrases(text)

    return {
        "topics": main_topics,
        "keywords": keyphrases
    }


# ------------------------------------------------------
# Module Self-Test
# ------------------------------------------------------
if __name__ == "__main__":
    sample = """
    تناول التقرير واقع الأمن المائي في المنطقة،
    وتأثير التغير المناخي على دول الشرق الأوسط،
    إضافة إلى دور المنظمات الدولية في دعم مشاريع التنمية.
    """

    result = detect_topics(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))
