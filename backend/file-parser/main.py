import os
import shutil
from typing import Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

# Imports for LangChain document loaders
try:
    from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
    LANGCHAIN_LOADERS_AVAILABLE = True
except ImportError:
    LANGCHAIN_LOADERS_AVAILABLE = False

# Fallback direct libraries
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Setup routes
router = APIRouter()
app = FastAPI(title="File Parser Service")

USER_FILES_DIR = Path("~/AbrarCloud/userfiles")
USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

class WorkspaceParseRequest(BaseModel):
    filename: str

def parse_txt(filepath: Path) -> str:
    """Parse text file using LangChain TextLoader or standard open."""
    if LANGCHAIN_LOADERS_AVAILABLE:
        try:
            loader = TextLoader(str(filepath), encoding="utf-8")
            docs = loader.load()
            return "\n".join([doc.page_content for doc in docs])
        except Exception:
            pass
    # Fallback
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_pdf(filepath: Path) -> str:
    """Parse PDF file using LangChain PyPDFLoader or fallback pypdf."""
    if LANGCHAIN_LOADERS_AVAILABLE:
        try:
            loader = PyPDFLoader(str(filepath))
            docs = loader.load()
            return "\n".join([doc.page_content for doc in docs])
        except Exception:
            pass
            
    if PYPDF_AVAILABLE:
        try:
            reader = pypdf.PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")
            
    raise HTTPException(status_code=500, detail="No PDF parsing libraries available (LangChain PyPDFLoader or PyPDF).")

def parse_docx(filepath: Path) -> str:
    """Parse DOCX file using LangChain Docx2txtLoader or fallback python-docx."""
    if LANGCHAIN_LOADERS_AVAILABLE:
        try:
            loader = Docx2txtLoader(str(filepath))
            docs = loader.load()
            return "\n".join([doc.page_content for doc in docs])
        except Exception:
            pass
            
    if DOCX_AVAILABLE:
        try:
            doc = docx.Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading DOCX: {str(e)}")
            
    raise HTTPException(status_code=500, detail="No DOCX parsing libraries available (LangChain Docx2txtLoader or python-docx).")

def process_file_parsing(filepath: Path) -> Dict[str, Any]:
    """Determine file extension and apply appropriate parser."""
    ext = filepath.suffix.lower()
    
    if ext in [".txt", ".md", ".json", ".csv"]:
        content = parse_txt(filepath)
    elif ext == ".pdf":
        content = parse_pdf(filepath)
    elif ext in [".docx", ".doc"]:
        content = parse_docx(filepath)
    else:
        # Generic read
        content = parse_txt(filepath)
        
    return {
        "filename": filepath.name,
        "extension": ext,
        "content_length": len(content),
        "content": content
    }

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "file-parser"}

@router.post("/parse/workspace")
def parse_workspace_file(payload: WorkspaceParseRequest):
    """Parse a file that exists in the user's workspace directory."""
    filepath = USER_FILES_DIR / payload.filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{payload.filename}' not found in user workspace."
        )
    try:
        return process_file_parsing(filepath)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse file: {str(e)}"
        )

@router.post("/parse/upload")
async def parse_uploaded_file(file: UploadFile = File(...)):
    """Accept an uploaded file, save it temporarily, and parse its contents."""
    temp_path = USER_FILES_DIR / f"temp_{file.filename}"
    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = process_file_parsing(temp_path)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parsing error: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path.exists():
            os.remove(temp_path)

app.include_router(router)
