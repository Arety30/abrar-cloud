from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "cloud-manager"}

@router.get("/files")
def list_files():
    return {
        "status": "success",
        "files": [
            {"name": "demo_document.txt", "size": "15 KB", "type": "text/plain"},
            {"name": "presentation.pptx", "size": "1.2 MB", "type": "application/vnd.ms-powerpoint"}
        ]
    }
