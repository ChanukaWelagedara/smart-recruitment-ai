import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file safely.
    Returns None if the PDF cannot be read.
    """
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        if not text.strip():
            print(f"Warning: No text found in {pdf_path}")
            return None
        return text
    except Exception as e:
        print(f"Warning: Could not read {pdf_path}: {e}")
        return None


# import fitz  # PyMuPDF

# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     return "\n".join(page.get_text() for page in doc)
