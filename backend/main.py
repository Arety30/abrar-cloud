import importlib
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("abrar_cloud_backend")

app = FastAPI(
    title="AbrarCloud API Server",
    description="Unified API backend for file parsers, editors, and agent workflows",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of modules corresponding to directories inside ~/AbrarCloud/backend/
MODULES = [
    "login",
    "signup",
    "reset-password",
    "email-verify",
    "cloud",
    "file-parser",
    "fileeditor-ai",
    "audio-gen",
    "audio-parser",
    "image-creator",
    "image-editor",
    "image-parser",
    "pdf-editor",
    "ppt-editor",
    "spreadsheet-editor",
    "database-editor",
    "dod-editor"
]

# Dynamically import and register routers
for module_name in MODULES:
    try:
        module_path = f"backend.{module_name}.router"
        try:
            router_module = importlib.import_module(module_path)
        except ImportError:
            # Fallback to main.py if router.py doesn't exist
            module_path = f"backend.{module_name}.main"
            router_module = importlib.import_module(module_path)
            
        if hasattr(router_module, "router"):
            app.include_router(router_module.router, prefix=f"/{module_name}", tags=[module_name])
            logger.info(f"Successfully loaded and registered router: {module_path}")
        else:
            logger.warning(f"Module {module_path} loaded but has no 'router' attribute.")
    except Exception as e:
        logger.error(f"Failed to load router for module '{module_name}': {str(e)}")

# Import and register root integration router
try:
    from backend.router import router as integration_router
    app.include_router(integration_router, prefix="/backend/router", tags=["Integration"])
    logger.info("Successfully loaded and registered root integration router.")
except Exception as e:
    logger.error(f"Failed to load root integration router: {str(e)}")

@app.get("/", tags=["Root"])
def get_root_status():
    """Welcome and health status endpoint."""
    return {
        "project": "AbrarCloud API Server",
        "status": "healthy",
        "registered_modules": MODULES,
        "message": "Welcome to AbrarCloud high-fidelity backend services."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
