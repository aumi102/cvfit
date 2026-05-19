import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import AnalysisJob, CVFile, JDDoc
from app.schemas.requests import ScoreCreateRequest
from app.schemas.responses import JobCreateResponse, JobStatusResponse, JobResultResponse
from app.services.storage import StorageNotFoundError, get_storage
from app.api.routes.utils import parse_uuid_or_400

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])

@router.post("/create-score", response_model=JobCreateResponse)
def create_score_job(payload: ScoreCreateRequest, db: Session = Depends(get_db)):
    cv_id = parse_uuid_or_400(payload.cv_file_id, "cv_file_id")
    cv = db.get(CVFile, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="cv_file_id not found")

    jd = JDDoc(id=uuid.uuid4(), jd_text=payload.jd_text, role=payload.options.target_role)
    db.add(jd)
    db.flush()

    job = AnalysisJob(
        id=uuid.uuid4(),
        cv_file_id=cv.id,
        jd_id=jd.id,
        status="queued",
        progress=0,
    )
    db.add(job)
    db.commit()

    # enqueue
    from app.workers.tasks import run_job
    run_job.delay(str(job.id))
    return JobCreateResponse(job_id=str(job.id))

@router.get("/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: str, db: Session = Depends(get_db)):
    job_uuid = parse_uuid_or_400(job_id, "job_id")
    job = db.get(AnalysisJob, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobStatusResponse(job_id=job_id, status=job.status, progress=job.progress, error_message=job.error_message)

@router.get("/{job_id}/result", response_model=JobResultResponse)
def job_result(job_id: str, db: Session = Depends(get_db)):
    job_uuid = parse_uuid_or_400(job_id, "job_id")
    job = db.get(AnalysisJob, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != "succeeded" or not job.result_json:
        raise HTTPException(status_code=409, detail=f"job not ready: {job.status}")
    return JobResultResponse(job_id=job_id, result=job.result_json)

@router.get("/{job_id}/report")
def job_report(job_id: str, db: Session = Depends(get_db)):
    job_uuid = parse_uuid_or_400(job_id, "job_id")
    job = db.get(AnalysisJob, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if not job.report_docx_path:
        raise HTTPException(status_code=409, detail="report not ready")
    return {
        "format": "docx",
        "download_url": f"/v1/jobs/{job_id}/report/download",
    }

@router.get("/{job_id}/report/download")
def download_docx(job_id: str, db: Session = Depends(get_db)):
    job_uuid = parse_uuid_or_400(job_id, "job_id")
    job = db.get(AnalysisJob, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != "succeeded" or not job.report_docx_path:
        raise HTTPException(status_code=409, detail="report not ready")

    try:
        content = get_storage().read_bytes(job.report_docx_path)
    except StorageNotFoundError:
        raise HTTPException(status_code=404, detail="report file not found")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="cvfit_report_{job_id}.docx"'},
    )
