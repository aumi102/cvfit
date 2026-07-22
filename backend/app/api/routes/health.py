from fastapi import APIRouter

from app.core.build_metadata import safe_build_metadata


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", **safe_build_metadata("backend")}
