from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
import aiofiles

from ..config import settings
from pathlib import Path

import hashlib
from datetime import datetime
import uuid


async def save_file_to_storage(file: UploadFile, project_id: int) -> dict:
    dir_project = Path(settings.storage_path) / str(project_id)
    if not dir_project.exists():
        dir_project.mkdir(parents=True, exist_ok=True)

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo no tiene un nombre válido."
        )

    uuid_file = uuid.uuid4()
    stored_name = str(uuid_file) + Path(file.filename).suffix
    path = dir_project / stored_name

    sha256 = hashlib.sha256()
    size_bytes = 0

    #stream to disk in chunks
    try:
        async with aiofiles.open(path, "wb") as out:
            while chunk := await file.read(1024 * 1024):  # 1 MB
                await out.write(chunk)
                sha256.update(chunk)
                size_bytes += len(chunk)
            file_hash = sha256.hexdigest()
    except Exception as e:
        if path.exists():
            path.unlink()  # Delete the file if an error occurs
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar el archivo {file.filename}: {str(e)}"
        )

    return {
        "original_name": file.filename,
        "stored_name": stored_name,
        "storage_path": str(path),
        "content_type": file.content_type,
        "size_bytes": size_bytes,
        "sha256": file_hash,
    }

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1_000_000), b""):
            h.update(chunk)
    return h.hexdigest()

def get_file_path(project_id: int, filename: str):
    return Path.joinpath(settings.storage_path, str(project_id), filename)



