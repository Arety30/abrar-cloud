from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AIEditRequest(BaseModel):
    filename: str
    prompt: str

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "fileeditor-ai"}

@router.post("/suggest")
def suggest_edit(payload: AIEditRequest):
    return {
        "status": "success",
        "filename": payload.filename,
        "suggestions": [
            f"Regarding your prompt '{payload.prompt}': Consider revising paragraph 2 to improve clarity.",
            "Formatting suggestion: Ensure standard Markdown tags are used."
        ]
    }
