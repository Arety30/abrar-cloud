import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App base directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    USER_FILES_DIR: Path = BASE_DIR / "userfiles"
    TASKS_DIR: Path = BASE_DIR / "tasks"
    
    # Security / Auth Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "abrar_cloud_secret_key_super_secure_123456789")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day
    
    # AI API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # App Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Ensure directories exist
settings = Settings()
settings.USER_FILES_DIR.mkdir(parents=True, exist_ok=True)
settings.TASKS_DIR.mkdir(parents=True, exist_ok=True)
