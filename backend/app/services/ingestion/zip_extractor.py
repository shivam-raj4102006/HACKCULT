import os
import zipfile
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.services.ingestion.validator import ALLOWED_EXTENSIONS, sanitize_filename

def safe_extract_zip(zip_path: str, extract_dir: str) -> List[Dict[str, Any]]:
    """
    Safely unpacks a ZIP archive while protecting against ZipSlip path traversal.
    Returns list of extracted valid files.
    """
    extracted_records = []
    abs_extract_dir = os.path.abspath(extract_dir)
    os.makedirs(abs_extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as archive:
        for member in archive.infolist():
            # Skip directories
            if member.is_dir():
                continue

            # ZipSlip security check
            target_path = os.path.abspath(os.path.join(abs_extract_dir, member.filename))
            if not target_path.startswith(abs_extract_dir):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Security violation: Archive member '{member.filename}' attempts path traversal."
                )

            # Check extension
            _, ext = os.path.splitext(member.filename.lower())
            if ext not in ALLOWED_EXTENSIONS or ext == ".zip":
                continue

            # Ensure parent directories exist
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            with archive.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())

            extracted_records.append({
                "original_filename": os.path.basename(member.filename),
                "storage_path": target_path,
                "file_size": member.file_size,
                "extension": ext
            })

    return extracted_records
