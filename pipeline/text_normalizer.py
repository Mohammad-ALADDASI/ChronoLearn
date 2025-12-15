"""
text_normalizer.py
-------------------
General-purpose text normalization and preprocessing utilities used across
the entire semantic KG pipeline.

This module:
- Provides Arabic + English normalization
- Cleans extracted text
- Splits text into semantic chunks for LLM processing
- Offers utility functions for topic/theme/triple modules
"""

import re
import unicodedata
from typing import List


# ------------------------------------------------------
# Arabic Normalization (importable by other modules)
# ------------------------------------------------------
def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text while leaving English intact.
    - Removes Tatweel
    - Normalizes Alef/Hamza forms
    - Normalizes Ya / Ta Marbuta
    - Removes diacritics
    - Applies NFC Unicode normalization
    """

    if not isinstance(text, str):
        return text

    text = unicodedata.normalize("NFC", text)

    arabic_pattern = re.compile(r"[\u0600-\u06FF]")
    if not arabic_pattern.search(text):
        return text  # no Arabic → skip

    # Remove Tatweel
    text = text.replace("ـ", "")

    # Normalize Alef/Hamza
    alef_map = {
        "إ": "ا",
        "أ": "ا",
        "آ": "ا",
        "ٱ": "ا",
    }
    for k, v in alef_map.items():
        text = text.replace(k, v)

    # Normalize Yeh and Alif Maqsura (ى → ي)
    text = text.replace("ى", "ي")

    # Ta Marbuta → ه
    text = text.replace("ة", "ه")

    # Remove Arabic diacritics (Harakat)
    diacritics = re.compile(
        r"[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED]"
    )
    text = re.sub(diacritics, "", text)

    return text


# ------------------------------------------------------
# English Normalization (light)
# ------------------------------------------------------
def normalize_english(text: str) -> str:
    """
    Perform light cleanup for English text.
    Does NOT change meaning or punctuation.
    - Removes control characters
    - Normalizes whitespace
    """
    if not isinstance(text, str):
        return text

    # Remove control chars
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ------------------------------------------------------
# Combined Cleaner
# ------------------------------------------------------
def clean_text(text: str) -> str:
    """
    Cleans both Arabic and English without altering semantics.
    """

    if not text:
        return ""

    # Arabic first
    text = normalize_arabic(text)

    # Then English cleanup
    text = normalize_english(text)

    # Remove repeating punctuation
    text = re.sub(r"([.!?؟])\1+", r"\1", text)

    # Normalize spacing before punctuation
    text = re.sub(r"\s+([.,!?:؟])", r"\1", text)

    return text.strip()


# ------------------------------------------------------
# Sentence Splitting
# ------------------------------------------------------
def split_sentences(text: str) -> List[str]:
    """
    Splits Arabic/English text into sentences.
    Handles:
    - Arabic punctuation: ؟ ، ؛
    - English punctuation: . ! ?
    """

    if not text:
        return []

    # Replace odd line breaks
    text = re.sub(r"\n+", " ", text)

    # Regex split on punctuation
    sentences = re.split(r"(?<=[.!?؟])\s+", text)

    return [clean_text(s) for s in sentences if s.strip()]


# ------------------------------------------------------
# Chunking for LLM (1200–1500 chars per block)
# ------------------------------------------------------
def chunk_text(text: str, max_length: int = 1500) -> List[str]:
    """
    Splits large texts into manageable chunks for LLM processing.
    Ensures chunks break at sentence boundaries when possible.
    """

    sentences = split_sentences(text)
    chunks = []

    current = ""
    for sentence in sentences:
        # If adding sentence exceeds max_length → finalize chunk
        if len(current) + len(sentence) + 1 > max_length:
            if current:
                chunks.append(current.strip())
                current = ""

        current += sentence + " "

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ------------------------------------------------------
# Keyword Cleaning for Topics/Themes
# ------------------------------------------------------
def prepare_for_topic_detection(text: str) -> str:
    """
    Slightly simplify text for topic/theme extraction.
    Removes:
    - Excess whitespace
    - URLs
    - Emails
    """

    text = clean_text(text)

    # Remove URLs
    text = re.sub(r"http[s]?://\S+", "", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", "", text)

    return text.strip()


# ------------------------------------------------------
# Module Test
# ------------------------------------------------------
if __name__ == "__main__":
    test = "هَذَا نَصّ مُخْتَبَر!   Testing 123... هل هذا يعمل؟ نعم   "
    print("Original:", test)
    print("Cleaned:", clean_text(test))
    print("Sentences:", split_sentences(test))
    print("Chunks:", chunk_text(test, max_length=20))
