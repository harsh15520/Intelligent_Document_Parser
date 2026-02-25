from __future__ import annotations

from typing import Dict, Any

from langchain_core.runnables import RunnableLambda


def _extract_name_from_text(text: str) -> str | None:
    """
    Very lightweight heuristic to find a name in free-form text.

    For the MVP we look for lines that start with 'Name:' or 'Account Holder:'
    and return the remainder of the line, stripped.
    """
    if not text:
        return None

    lowered = text.lower()
    for line in lowered.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("name:"):
            # Original case is not preserved here, but for comparison
            # we only need a normalized value.
            return line_stripped.replace("name:", "", 1).strip()
        if line_stripped.startswith("account holder:"):
            return line_stripped.replace("account holder:", "", 1).strip()

    return None


def _mock_validation_logic(inputs: Dict[str, str]) -> Dict[str, Any]:
    """
    Core "reasoning" logic that we wrap in a LangChain RunnableLambda.

    It compares names between document text and bank statement text and
    emits simple fraud markers.
    """
    document_text = inputs.get("document_text", "") or ""
    bank_statement_text = inputs.get("bank_statement_text", "") or ""

    doc_name = _extract_name_from_text(document_text)
    bank_name = _extract_name_from_text(bank_statement_text)

    fraud_markers = []

    if not document_text.strip():
        fraud_markers.append(
            {
                "code": "EMPTY_DOCUMENT_TEXT",
                "severity": "high",
                "description": "No text could be extracted from the document.",
            }
        )

    if not bank_statement_text.strip():
        fraud_markers.append(
            {
                "code": "EMPTY_BANK_STATEMENT",
                "severity": "medium",
                "description": "No bank statement text was provided.",
            }
        )

    if doc_name and bank_name:
        if doc_name != bank_name:
            fraud_markers.append(
                {
                    "code": "NAME_MISMATCH",
                    "severity": "high",
                    "description": (
                        "Name on document does not match name in bank statement."
                    ),
                    "details": {
                        "document_name": doc_name,
                        "bank_statement_name": bank_name,
                    },
                }
            )
    elif doc_name and not bank_name:
        fraud_markers.append(
            {
                "code": "MISSING_BANK_NAME",
                "severity": "low",
                "description": "Could not find a clear name in the bank statement.",
                "details": {"document_name": doc_name},
            }
        )
    elif bank_name and not doc_name:
        fraud_markers.append(
            {
                "code": "MISSING_DOCUMENT_NAME",
                "severity": "low",
                "description": "Could not find a clear name in the document text.",
                "details": {"bank_statement_name": bank_name},
            }
        )

    summary = "No obvious fraud markers detected."
    if fraud_markers:
        summary = f"{len(fraud_markers)} potential fraud marker(s) detected."

    return {
        "summary": summary,
        "fraud_markers": fraud_markers,
        "meta": {
            "doc_name_detected": doc_name,
            "bank_name_detected": bank_name,
        },
    }


def build_mock_validation_chain() -> RunnableLambda:
    """
    Build a dummy LangChain Runnable that wraps our local validation logic.

    This satisfies the requirement of using LangChain, but does not call
    any external LLM APIs (no cost).
    """
    return RunnableLambda(_mock_validation_logic)


def validate_document_with_bank_statement(
    document_text: str, bank_statement_text: str
) -> Dict[str, Any]:
    """
    Public service function that uses the mock chain to validate inputs.
    """
    chain = build_mock_validation_chain()
    result: Dict[str, Any] = chain.invoke(
        {
            "document_text": document_text,
            "bank_statement_text": bank_statement_text,
        }
    )
    return result


__all__ = ["build_mock_validation_chain", "validate_document_with_bank_statement"]

