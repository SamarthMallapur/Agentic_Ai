import fitz  # PyMuPDF
import os

def parse_resume(file_path: str) -> str:
    """Extracts text from a PDF resume."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")
        
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        
    return text.strip()
