import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CVFile
from app.services.storage import UploadValidationError, save_upload
from app.schemas.responses import UploadResponse

router = APIRouter(prefix="/v1/cv", tags=["cv"])
SUPPORTED_CV_EXTENSIONS = {".pdf", ".docx"}

@router.post("/upload", response_model=UploadResponse)
def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_CV_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only pdf/docx supported")

    try:
        path, digest, mime = save_upload(file)
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    row = CVFile(
        id=uuid.uuid4(),
        original_filename=file.filename,
        mime_type=mime,
        storage_path=path,
        sha256=digest,
    )
    db.add(row)
    db.commit()
    return UploadResponse(cv_file_id=str(row.id))
