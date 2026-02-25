from __future__ import annotations

from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from document_processor import process_document_image
from llm_validator import validate_document_with_bank_statement


PROJECT_ROOT = Path(__file__).parent
MOCK_DATA_DIR = PROJECT_ROOT / "mock_data"
DEFAULT_BANK_STATEMENT_PATH = MOCK_DATA_DIR / "sample_bank_statement.txt"


def load_default_bank_statement() -> str:
    try:
        return DEFAULT_BANK_STATEMENT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def main() -> None:
    st.set_page_config(
        page_title="Intelligent Document Parser & Validator",
        layout="wide",
    )

    st.title("Intelligent Document Parser & Validator")
    st.caption(
        "MVP demo: upload an ID document image, provide a bank statement, and "
        "run basic OCR + mock LLM validation to flag potential fraud markers."
    )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("1. Upload Document Image")
        uploaded_file = st.file_uploader(
            "Upload a mock PAN/Aadhaar or similar ID image",
            type=["png", "jpg", "jpeg"],
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded document", use_column_width=True)

    with col_right:
        st.subheader("2. Paste / Edit Bank Statement Text")
        default_text = load_default_bank_statement()
        bank_statement_text = st.text_area(
            "Mock bank statement",
            value=default_text,
            height=300,
            help=(
                "For this MVP, include a line like 'Name: John Doe' or "
                "'Account Holder: John Doe' so the validator can compare names."
            ),
        )

    st.markdown("---")
    run_button = st.button("Run Extraction & Validation", type="primary", use_container_width=True)

    if run_button:
        if not uploaded_file:
            st.error("Please upload a document image first.")
            return

        with st.spinner("Running OCR and validation..."):
            # Convert uploaded file into a PIL image
            bytes_data = uploaded_file.read()
            image = Image.open(BytesIO(bytes_data)).convert("RGB")

            # Service layer: OCR + regex extraction
            doc_result = process_document_image(image)

            # Service layer: mock LLM-style validation
            validation_result = validate_document_with_bank_statement(
                document_text=doc_result.get("raw_text", ""),
                bank_statement_text=bank_statement_text,
            )

        st.success("Extraction and validation complete.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Extracted Document Details")
            with st.expander("Raw OCR Text", expanded=False):
                st.text_area(
                    "OCR Text",
                    value=doc_result.get("raw_text", ""),
                    height=250,
                )

            st.markdown("**Detected Dates**")
            dates = doc_result.get("dates", [])
            if dates:
                st.write(dates)
            else:
                st.write("_No date-like patterns detected._")

            st.markdown("**Detected ID Numbers**")
            id_numbers = doc_result.get("id_numbers", {})
            st.json(id_numbers)

        with col2:
            st.subheader("Validation Result (Mock LLM Chain)")
            st.markdown(
                "This output is produced by a **dummy LangChain Runnable** that "
                "simulates LLM-style reasoning without calling any external APIs."
            )
            st.json(validation_result)


if __name__ == "__main__":
    main()

