import os
from typing import List, Dict, Any, Tuple
from pptx import Presentation

def extract_pptx_content(file_path: str) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Extracts text, speaker notes, and embedded images from PPTX slides.
    Returns: (total_slides, list_of_slides)
    """
    if not os.path.exists(file_path):
        return 0, []

    prs = Presentation(file_path)
    total_slides = len(prs.slides)
    slides_data = []

    for idx, slide in enumerate(prs.slides):
        slide_number = idx + 1
        slide_texts = []
        image_count = 0

        # Extract text from shapes
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    line = paragraph.text.strip()
                    if line:
                        slide_texts.append(line)
            if shape.has_table:
                for row in shape.table.rows:
                    row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_texts:
                        slide_texts.append(" | ".join(row_texts))
            # Shape image detection
            if shape.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                image_count += 1

        # Extract Speaker Notes
        speaker_notes = ""
        try:
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                speaker_notes = slide.notes_slide.notes_text_frame.text.strip()
        except Exception:
            speaker_notes = ""

        combined_text = "\n".join(slide_texts).strip()

        slides_data.append({
            "page_or_slide_number": slide_number,
            "text": combined_text,
            "character_count": len(combined_text),
            "speaker_notes": speaker_notes if speaker_notes else None,
            "embedded_image_count": image_count
        })

    return total_slides, slides_data
