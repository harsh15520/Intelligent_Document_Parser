from __future__ import annotations

import re
from typing import List, Dict, Any

from PIL import Image
import pytesseract


def extract_text_from_image(image: Image.Image) -> str:
    """
    Extract raw text from an image using Tesseract OCR.

    Parameters
    ----------
    image: PIL.Image.Image
        The image object uploaded by the user.
    """
    # Basic configuration for English OCR; can be extended for other languages.
    return pytesseract.image_to_string(image, lang="eng")


def find_dates(text: str) -> List[str]:
    """
    Find date-like patterns in the given text.

    This is intentionally simple for MVP purposes and focuses on
    common formats like DD/MM/YYYY, DD-MM-YYYY, and YYYY-MM-DD.
    """
    date_patterns = [
        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",  # 31/01/2024 or 31-01-2024
        r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",  # 2024-01-31
    ]
    matches: List[str] = []
    for pattern in date_patterns:
        matches.extend(re.findall(pattern, text))
    # Remove duplicates while preserving order
    seen = set()
    unique_matches: List[str] = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            unique_matches.append(m)
    return unique_matches


def find_id_numbers(text: str) -> Dict[str, List[str]]:
    """
    Find ID number patterns such as Indian PAN and Aadhaar-like sequences.

    - PAN: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
    - Aadhaar-like: 4-4-4 digit groups (e.g., 1234 5678 9012 or 1234-5678-9012)
    """
    pan_pattern = r"\b[A-Z]{5}\d{4}[A-Z]\b"
    aadhaar_pattern = r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"

    pans = re.findall(pan_pattern, text)
    aadhaars = re.findall(aadhaar_pattern, text)

    # Normalize Aadhaar numbers by removing spaces/dashes
    normalized_aadhaars = []
    seen_aadhaar = set()
    for a in aadhaars:
        cleaned = re.sub(r"[ -]", "", a)
        if cleaned not in seen_aadhaar:
            seen_aadhaar.add(cleaned)
            normalized_aadhaars.append(cleaned)

    # De-duplicate PANs while preserving order
    seen_pan = set()
    unique_pans: List[str] = []
    for p in pans:
        if p not in seen_pan:
            seen_pan.add(p)
            unique_pans.append(p)

    return {
        "pan_numbers": unique_pans,
        "aadhaar_numbers": normalized_aadhaars,
    }


def process_document_image(image: Image.Image) -> Dict[str, Any]:
    """
    High-level helper that runs OCR and basic pattern extraction.
    """
    text = extract_text_from_image(image)
    dates = find_dates(text)
    id_numbers = find_id_numbers(text)
    return {
        "raw_text": text,
        "dates": dates,
        "id_numbers": id_numbers,
    }


__all__ = [
    "extract_text_from_image",
    "find_dates",
    "find_id_numbers",
    "process_document_image",
]

