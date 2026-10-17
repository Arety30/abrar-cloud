import os
from pathlib import Path
from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.utils.agent import OpenManusAgent, read_user_file, write_user_file, list_user_files

router = APIRouter()
app = FastAPI(title="Document Editor Service")

USER_FILES_DIR = Path("~/AbrarCloud/userfiles")
USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

class EditRequest(BaseModel):
    filename: str
    instruction: str
    create_if_missing: bool = True

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "dod-editor"}

@router.post("/edit")
def edit_document(payload: EditRequest):
    """
    Apply natural language edits to a document in the workspace
    using the OpenManus Agent.
    """
    filepath = USER_FILES_DIR / payload.filename
    
    # Check existence
    if not filepath.exists():
        if payload.create_if_missing:
            # Create a base file
            write_user_file(payload.filename, f"Document: {payload.filename}\n")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{payload.filename}' not found in workspace."
            )
            
    # Load original content
    original_content = read_user_file(payload.filename)
    
    # Initialize the OpenManus Document Editor Agent
    system_prompt = (
        "You are the AbrarCloud Document Editor Agent (powered by OpenManus).\n"
        "Your task is to modify documents based on the user's instructions.\n"
        "When writing back files, keep existing styles and only alter what was requested.\n"
        "You have direct workspace tools (read_file_tool, write_file_tool, list_files_tool) available."
    )
    agent = OpenManusAgent(system_prompt=system_prompt)
    
    # Construct task query
    query = (
        f"Read file '{payload.filename}', apply the following instruction: '{payload.instruction}'.\n"
        f"Original content was:\n---\n{original_content}\n---\n"
        f"Make sure to update '{payload.filename}' with the modifications."
    )
    
    # Run Agent
    agent_result = agent.execute(query)
    
    # Reload file to capture the updates made by the agent
    updated_content = read_user_file(payload.filename)
    
    return {
        "status": "success",
        "filename": payload.filename,
        "original_content": original_content,
        "updated_content": updated_content,
        "agent_response": agent_result["output"],
        "agent_type": agent_result["agent"]
    }

app.include_router(router)
