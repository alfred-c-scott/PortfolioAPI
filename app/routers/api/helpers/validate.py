from fastapi import UploadFile
from fastapi import HTTPException
import os


def validate_image(file: UploadFile):

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="file too large (max 5MB)")

    valid_content_types = ["image/jpeg", "image/png"]

    if file.content_type not in valid_content_types:
        raise HTTPException(status_code=400, detail="file must be JPEG or PNG")

    return file
