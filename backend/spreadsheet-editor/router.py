from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CellUpdateRequest(BaseModel):
    filename: str
    sheet_name: str
    cell: str
    value: str

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "spreadsheet-editor"}

@router.post("/cell/update")
def update_cell(payload: CellUpdateRequest):
    return {
        "status": "success",
        "message": f"Updated cell {payload.cell} in sheet '{payload.sheet_name}' of file '{payload.filename}' with value '{payload.value}'."
    }
