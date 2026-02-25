# Intelligent Document Parser & Validator (MVP)

An MVP Streamlit app that:

- **Parses uploaded ID document images** (e.g., mock PAN / Aadhaar) using **Tesseract OCR**.
- **Extracts key patterns** such as **dates** and **ID numbers** via RegEx.
- **Validates** the extracted text against a **mock bank statement** using a **dummy LangChain chain** that simulates LLM-style fraud checks (no external API calls).

---

## Tech Stack

- **Python 3.9+** (recommended)
- **Streamlit** for the web UI
- **pytesseract** + **Tesseract OCR** for text extraction
- **Pillow (PIL)** for image handling
- **LangChain (langchain-community, langchain-core)** for a mock validation chain
- **python-dotenv** (included for future configuration needs)

---

## Project Structure

- `app.py`  
  Streamlit frontend that:
  - Accepts an uploaded document image.
  - Accepts/prefills a mock bank statement text area.
  - Calls the service layers for OCR and validation.
  - Displays extracted data and fraud markers in a clean layout.

- `document_processor.py`  
  Service layer for **OCR and regex-based extraction**:
  - `extract_text_from_image(image)` – runs Tesseract OCR.
  - `find_dates(text)` – finds common date formats.
  - `find_id_numbers(text)` – finds PAN-like and Aadhaar-like patterns.
  - `process_document_image(image)` – high-level helper returning raw text, dates, and IDs.

- `llm_validator.py`  
  Service layer that uses a **mock LangChain `RunnableLambda`**:
  - Wraps `_mock_validation_logic` in a LangChain chain.
  - Compares names between the document text and the bank statement.
  - Returns a **JSON-like dict** with `summary`, `fraud_markers`, and `meta`.

- `mock_data/sample_bank_statement.txt`  
  Example bank statement used to prefill the text area in the UI.

- `requirements.txt`  
  Python dependencies for the project.

---

## Installation

From the project root:

```bash
cd c:\Users\apoor\intelligent_document_parser
pip install -r requirements.txt
```

### Install Tesseract OCR (Required for pytesseract)

1. Download Tesseract for Windows (e.g. from `https://github.com/UB-Mannheim/tesseract/wiki`).
2. Install it, and ensure the installation path (e.g. `C:\Program Files\Tesseract-OCR`) is added to your **system PATH**.
3. Optionally verify from a terminal:

```bash
tesseract --version
```

If `pytesseract` cannot find the binary, you may need to configure `pytesseract.pytesseract.tesseract_cmd` manually in `document_processor.py`.

---

## Running the App

From the project root:

```bash
streamlit run app.py
```

Streamlit will open a browser tab (or give you a local URL).

---

## Using the MVP

1. **Upload a document image**
   - Use a mock PAN / Aadhaar / ID image (`.png`, `.jpg`, or `.jpeg`).
   - Ideally, include a line such as `Name: John Doe` or `Account Holder: John Doe` in the image text so the OCR can pick it up.

2. **Review / edit mock bank statement**
   - The text area is prefilled from `mock_data/sample_bank_statement.txt`.
   - You can edit it directly (e.g., change `Account Holder: John Doe` to another name).

3. **Click “Run Extraction & Validation”**
   - The app:
     - Runs OCR on the uploaded image.
     - Extracts dates and ID numbers.
     - Passes the extracted document text and bank statement text to the mock LangChain validator.
   - The right panel shows:
     - **Extracted OCR text** (in an expandable section).
     - **Detected dates** and **ID numbers**.
     - **Validation result JSON**, including potential fraud markers like:
       - `NAME_MISMATCH`
       - `MISSING_BANK_NAME`
       - `MISSING_DOCUMENT_NAME`
       - `EMPTY_DOCUMENT_TEXT` / `EMPTY_BANK_STATEMENT`

---

## Notes & Limitations (MVP)

- The LangChain integration is **mocked** using `RunnableLambda`; **no real LLM API** is called.
- Fraud detection is **heuristic and simplified** (mostly name comparison).
- OCR quality depends heavily on image quality and Tesseract configuration.
- Regex patterns for dates and ID numbers are simplified and can be extended for production use.

This structure is intentionally minimal and opinionated to serve as a foundation you can extend with real LLMs, richer validation rules, database integration, and authentication.
