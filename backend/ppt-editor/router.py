from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AddSlideRequest(BaseModel):
    filename: str
    title: str
    content: str

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "ppt-editor"}

@router.post("/slide/add")
def add_slide(payload: AddSlideRequest):
    return {
        "status": "success",
        "message": f"Added slide '{payload.title}' to presentation '{payload.filename}' successfully."
    }
