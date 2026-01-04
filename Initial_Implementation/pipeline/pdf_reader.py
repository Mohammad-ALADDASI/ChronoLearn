"""
pdf_reader.py
----------------
This module handles:
1. Reading Arabic + English text from PDF files
2. Normalizing & cleaning Arabic text
3. Preparing text for topic/theme/triple extraction

It replaces older PDF/text code and will be integrated into the new semantic pipeline.
"""

import os
import re
import PyPDF2
import unicodedata


# ------------------------------------------------------
# Arabic Text Normalization
# ------------------------------------------------------
def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text without damaging English content.
    Performs:
    - Unicode NFC normalization
    - Removing Tatweel
    - Normalizing various forms of Alef/Hamza
    - Standardizing Ya and Ta Marbuta
    """

    if not isinstance(text, str):
        return text

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    arabic_pattern = re.compile(r"[\u0600-\u06FF]")

    # If no Arabic exists → return as-is
    if not arabic_pattern.search(text):
        return text

    # Remove Tatweel
    text = text.replace("ـ", "")

    # Normalize Alef variants
    alef_variants = {
        "إ": "ا",
        "أ": "ا",
        "آ": "ا",
        "ٱ": "ا",
    }
    for k, v in alef_variants.items():
        text = text.replace(k, v)

    # Normalize Yeh
    text = text.replace("ى", "ي")

    # Normalize Ta Marbuta
    text = text.replace("ة", "ه")

    # Remove diacritics
    diacritics = re.compile(
        r"[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED]"
    )
    text = re.sub(diacritics, "", text)

    return text


# ------------------------------------------------------
# Extract text from PDF using PyPDF2
# ------------------------------------------------------
def extract_pdf_text(pdf_path: str) -> str:
    """
    Extracts clean Arabic (and English) text from a PDF.
    This function is safe for text-based PDFs (not scanned).
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text = ""

    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    extracted = normalize_arabic(extracted)
                    text += extracted + "\n"

    except Exception as e:
        raise RuntimeError(f"Failed to extract PDF text: {e}")

    return text.strip()


# ------------------------------------------------------
# Utility: clean large text blocks
# ------------------------------------------------------
def clean_text_block(text: str) -> str:
    """
    Additional cleaning:
    - Remove duplicate spaces
    - Remove weird control characters
    - Normalize punctuation
    """

    if not text:
        return ""

    text = text.replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


# ------------------------------------------------------
# Main processing function (for pipeline + scripts)
# ------------------------------------------------------
def process_pdf(pdf_path: str) -> str:
    """
    Reads the PDF, extracts raw text, normalizes it,
    and returns final clean text ready for topic/theme extraction.
    """

    raw = extract_pdf_text(pdf_path)
    cleaned = clean_text_block(raw)

    return cleaned
