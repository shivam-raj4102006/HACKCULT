import os
import hashlib
import re
from typing import Tuple
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".zip": "application/zip",
}

def sanitize_filename(filename: str) -> str:
    # Strip any directory path components
    basename = os.path.basename(filename)
    # Remove potentially dangerous characters, keep alphanumerics, dots, hyphens, underscores
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', basename)
    return clean_name or "uploaded_archive"

def compute_sha256(content: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()

def validate_upload(file: UploadFile, content: bytes) -> Tuple[str, str]:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty"
        )

    clean_filename = sanitize_filename(file.filename)
    _, ext = os.path.splitext(clean_filename.lower())

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed types: {list(ALLOWED_EXTENSIONS.keys())}"
        )

    file_size = len(content)
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {file_size} bytes exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes"
        )

    mime_type = file.content_type or ALLOWED_EXTENSIONS.get(ext, "application/octet-stream")
    return clean_filename, mime_type
