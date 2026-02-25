from __future__ import annotations

import re
from typing import List, Dict, Any

from PIL import Image
import pytesseract


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


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

    Focuses on common formats like DD/MM/YYYY, DD-MM-YYYY, and YYYY-MM-DD,
    and also prefers dates preceded by typical labels like DOB / Date of Birth.
    """
    if not text:
        return []

    date_patterns = [
        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",  # 31/01/2024 or 31-01-2024
        r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",  # 2024-01-31
    ]

    matches: List[str] = []
    for pattern in date_patterns:
        matches.extend(re.findall(pattern, text))

    return _dedupe_preserve_order(matches)


def find_id_numbers(text: str) -> Dict[str, List[str]]:
    """
    Find ID number patterns such as Indian PAN and Aadhaar-like sequences.

    - PAN: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
    - Aadhaar-like: 4-4-4 digit groups (e.g., 1234 5678 9012 or 1234-5678-9012)
    """
    if not text:
        return {"pan_numbers": [], "aadhaar_numbers": []}

    # Case-insensitive PAN detection, normalize to upper-case.
    pan_pattern = re.compile(r"\b([A-Z]{5}\d{4}[A-Z])\b", re.IGNORECASE)
    aadhaar_pattern = re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b")

    pans = [m.group(1).upper() for m in pan_pattern.finditer(text)]
    aadhaars_raw = [m.group(0) for m in aadhaar_pattern.finditer(text)]

    # Normalize Aadhaar numbers by removing spaces/dashes and requiring 12 digits.
    normalized_aadhaars: List[str] = []
    for a in aadhaars_raw:
        cleaned = re.sub(r"[ -]", "", a)
        if len(cleaned) == 12:
            normalized_aadhaars.append(cleaned)

    return {
        "pan_numbers": _dedupe_preserve_order(pans),
        "aadhaar_numbers": _dedupe_preserve_order(normalized_aadhaars),
    }


def find_name_candidates(text: str) -> List[str]:
    """
    Extract likely name fields from Aadhaar / PAN / ITR style text.

    Looks for lines starting with common labels such as:
    - Name:
    - Applicant Name:
    - Account Holder:
    - Father Name:
    """
    if not text:
        return []

    label_pattern = re.compile(
        r"^(name|applicant name|account holder|father name)\s*[:\-]\s*(.+)$",
        re.IGNORECASE,
    )

    candidates: List[str] = []
    for line in text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        m = label_pattern.match(line_stripped)
        if m:
            value = m.group(2).strip()
            if value:
                candidates.append(value)

    return _dedupe_preserve_order(candidates)


def find_dob_candidates(text: str) -> List[str]:
    """
    Extract likely date-of-birth fields using labels plus date patterns.
    """
    if not text:
        return []

    # Look for patterns like "DOB: 01/01/1990" or "Date of Birth - 1990-01-01"
    dob_pattern = re.compile(
        r"(dob|d\.o\.b\.|date of birth)\s*[:\-]\s*(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})",
        re.IGNORECASE,
    )

    candidates: List[str] = []
    for match in dob_pattern.finditer(text):
        candidates.append(match.group(2))

    # Fall back to generic dates if nothing labeled was found.
    if not candidates:
        candidates = find_dates(text)

    return _dedupe_preserve_order(candidates)


def infer_document_type(text: str, id_numbers: Dict[str, List[str]]) -> str:
    """
    Coarse classification of the document type based on content and patterns.
    """
    if not text:
        return "unknown"

    lowered = text.lower()
    has_pan = bool(id_numbers.get("pan_numbers"))
    has_aadhaar = bool(id_numbers.get("aadhaar_numbers"))

    if "income tax return" in lowered or "itr acknowledgment" in lowered:
        return "itr"

    if "permanent account number" in lowered or "income tax department" in lowered:
        if has_pan:
            return "pan"

    if "aadhaar" in lowered or "uidai" in lowered:
        if has_aadhaar:
            return "aadhaar"

    if has_pan and not has_aadhaar:
        return "pan"
    if has_aadhaar and not has_pan:
        return "aadhaar"

    return "unknown"


def process_document_image(image: Image.Image) -> Dict[str, Any]:
    """
    High-level helper that runs OCR and structured pattern extraction.

    Returns a rich payload suitable for downstream validation:
    - raw_text
    - dates (all date-like strings)
    - id_numbers (PAN / Aadhaar)
    - names (likely name fields)
    - dob_candidates (likely date-of-birth values)
    - document_type (aadhaar / pan / itr / unknown)
    """
    text = extract_text_from_image(image)
    dates = find_dates(text)
    id_numbers = find_id_numbers(text)
    names = find_name_candidates(text)
    dob_candidates = find_dob_candidates(text)
    document_type = infer_document_type(text, id_numbers)

    return {
        "raw_text": text,
        "dates": dates,
        "id_numbers": id_numbers,
        "names": names,
        "dob_candidates": dob_candidates,
        "document_type": document_type,
    }


__all__ = [
    "extract_text_from_image",
    "find_dates",
    "find_id_numbers",
    "find_name_candidates",
    "find_dob_candidates",
    "infer_document_type",
    "process_document_image",
]

