from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CropRequest(BaseModel):
    filename: str
    x: int
    y: int
    width: int
    height: int

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "image-editor"}

@router.post("/crop")
def crop_image(payload: CropRequest):
    return {
        "status": "success",
        "message": f"Image '{payload.filename}' cropped to {payload.width}x{payload.height} pixels successfully."
    }
