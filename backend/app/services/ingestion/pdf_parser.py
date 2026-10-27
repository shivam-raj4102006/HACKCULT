import os
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

def extract_pdf_content(file_path: str) -> Tuple[int, List[Dict[str, Any]], bool]:
    """
    Extracts text from PDF page by page.
    Returns: (total_pages, list_of_pages, is_scanned_flag)
    """
    if not os.path.exists(file_path):
        return 0, [], False

    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    pages_data = []
    total_characters = 0

    for idx, page in enumerate(reader.pages):
        page_number = idx + 1
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        
        clean_text = text.strip()
        total_characters += len(clean_text)
        pages_data.append({
            "page_or_slide_number": page_number,
            "text": clean_text,
            "character_count": len(clean_text),
            "speaker_notes": None
        })

    # If the document has pages but virtually zero text extracted, it is likely scanned
    is_scanned = total_pages > 0 and (total_characters / max(total_pages, 1)) < 20
    return total_pages, pages_data, is_scanned
