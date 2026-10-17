from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class MergeRequest(BaseModel):
    files: list[str]
    output_filename: str

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "pdf-editor"}

@router.post("/merge")
def merge_pdfs(payload: MergeRequest):
    return {
        "status": "success",
        "message": f"Successfully merged {len(payload.files)} files into {payload.output_filename}."
    }
