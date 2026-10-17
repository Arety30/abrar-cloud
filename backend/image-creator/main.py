import os
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel
from PIL import Image, ImageDraw

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from backend.config import settings

router = APIRouter()
app = FastAPI(title="Image Creator Service")

USER_FILES_DIR = Path("~/AbrarCloud/userfiles")
USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

class GenerateImageRequest(BaseModel):
    prompt: str
    width: int = 512
    height: int = 512
    filename: str = "generated_image.png"

def generate_local_placeholder(prompt: str, width: int, height: int, filepath: Path):
    """Generate a placeholder image with background color hashed from the prompt."""
    # Create background color from prompt hash
    hash_object = hashlib.md5(prompt.encode("utf-8"))
    hex_digest = hash_object.hexdigest()
    
    # Extract RGB values from hash
    r = int(hex_digest[0:2], 16) % 200 + 30  # Avoid too bright/dark
    g = int(hex_digest[2:4], 16) % 200 + 30
    b = int(hex_digest[4:6], 16) % 200 + 30
    bg_color = (r, g, b)
    
    # Create image
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw simple visual borders
    draw.rectangle([10, 10, width - 10, height - 10], outline=(255, 255, 255), width=2)
    
    # Draw prompt text (simple wrap/crop)
    text = f"Prompt: {prompt}"
    max_len = 45
    lines = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    
    y_offset = height // 3
    for line in lines[:5]:  # max 5 lines
        draw.text((30, y_offset), line, fill=(255, 255, 255))
        y_offset += 25
        
    draw.text((30, height - 40), "[AbrarCloud AI Local Creator]", fill=(200, 200, 200))
    
    img.save(filepath, format="PNG")

def generate_dalle_image(prompt: str, width: int, height: int, filepath: Path) -> bool:
    """Generate image via OpenAI DALL-E and save to path."""
    if not (OPENAI_AVAILABLE and settings.OPENAI_API_KEY):
        return False
        
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.images.generate(
            model="dall-e-2",  # More cost-efficient / matches older size constraints
            prompt=prompt,
            n=1,
            size=f"{width}x{height}"
        )
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        filepath.write_bytes(img_data)
        return True
    except Exception as e:
        # Fallback to local instead of failing
        return False

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "image-creator"}

@router.post("/generate")
def generate_image(payload: GenerateImageRequest):
    """Generate image based on the prompt. Saves image file to user workspace."""
    filepath = USER_FILES_DIR / payload.filename
    
    # Attempt DALL-E, fallback to local placeholder
    success = generate_dalle_image(payload.prompt, payload.width, payload.height, filepath)
    
    generator_source = "DALL-E API"
    if not success:
        generate_local_placeholder(payload.prompt, payload.width, payload.height, filepath)
        generator_source = "Local Placeholder Generator (Pillow)"
        
    return {
        "status": "success",
        "prompt": payload.prompt,
        "width": payload.width,
        "height": payload.height,
        "filename": payload.filename,
        "filepath": str(filepath),
        "generator": generator_source
    }

app.include_router(router)
