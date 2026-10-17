import os
import base64
import shutil
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from PIL import Image
from PIL.ExifTags import TAGS

# Langchain imports (wrapped for safety)
try:
    from langchain_core.messages import HumanMessage
    from langchain_openai import ChatOpenAI
    LANGCHAIN_VISION_AVAILABLE = True
except ImportError:
    LANGCHAIN_VISION_AVAILABLE = False

from backend.config import settings

router = APIRouter()
app = FastAPI(title="Image Parser Service")

USER_FILES_DIR = Path("~/AbrarCloud/userfiles")
USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

class WorkspaceImageRequest(BaseModel):
    filename: str

def extract_image_metadata(filepath: Path) -> Dict[str, Any]:
    """Use Pillow to extract basic properties and EXIF metadata from the image."""
    try:
        with Image.open(filepath) as img:
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
            }
            # Attempt to read EXIF
            exif_data = {}
            if hasattr(img, "_getexif") and img._getexif() is not None:
                for tag, value in img._getexif().items():
                    decoded_tag = TAGS.get(tag, tag)
                    # Convert bytes to string representation to avoid serialization errors
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="ignore")
                        except Exception:
                            value = str(value)
                    exif_data[str(decoded_tag)] = str(value)
            
            metadata["exif"] = exif_data
            return metadata
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unable to process image metadata: {str(e)}"
        )

def get_image_description(filepath: Path) -> str:
    """Describe image using LangChain Vision message or return fallback description."""
    if LANGCHAIN_VISION_AVAILABLE and settings.OPENAI_API_KEY:
        try:
            # Read image bytes and encode to base64
            with open(filepath, "rb") as image_file:
                image_bytes = image_file.read()
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                max_tokens=300,
                api_key=settings.OPENAI_API_KEY
            )
            
            # Formulate user visual prompt message
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Describe this image in detail and extract any text you see (OCR)."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            )
            response = llm.invoke([message])
            return response.content
        except Exception as e:
            return f"[AI Description Error: {str(e)}]. Fallback description: Image contains visual content."
            
    # Mock/Rule-based descriptive fallback
    try:
        with Image.open(filepath) as img:
            return f"Mock visual analysis: Image size is {img.width}x{img.height} pixels in {img.format} format, color mode {img.mode}. " \
                   f"Note: OpenAI API key not configured for live vision analysis."
    except Exception:
        return "Image file format loaded. Vision analysis skipped."

def process_image(filepath: Path) -> Dict[str, Any]:
    """Main function to parse image metadata and description."""
    metadata = extract_image_metadata(filepath)
    description = get_image_description(filepath)
    return {
        "filename": filepath.name,
        "metadata": metadata,
        "description": description
    }

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "image-parser"}

@router.post("/parse/workspace")
def parse_workspace_image(payload: WorkspaceImageRequest):
    """Parse image metadata and description from the user's workspace directory."""
    filepath = USER_FILES_DIR / payload.filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image file '{payload.filename}' not found in user workspace."
        )
    return process_image(filepath)

@router.post("/parse/upload")
async def parse_uploaded_image(file: UploadFile = File(...)):
    """Upload an image file and parse its metadata and description."""
    temp_path = USER_FILES_DIR / f"temp_{file.filename}"
    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = process_image(temp_path)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image parsing error: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path.exists():
            os.remove(temp_path)

app.include_router(router)
