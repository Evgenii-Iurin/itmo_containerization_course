from functools import lru_cache
from typing import Annotated
from fastapi import Request, HTTPException, Depends
from services.router.app.services.llm_service import BaseLLM
from services.router.app.config import Settings
from services.router.app.database import Database

@lru_cache
def get_settings() -> Settings:
    """Dependency function to get application settings.
    
    Uses lru_cache to ensure Settings is only instantiated once,
    which is important for Pydantic BaseSettings to properly load
    environment variables.
    
    Returns:
        Settings instance (singleton)
    """
    return Settings()

def get_model(request: Request):
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized.")
    return model

def get_db(request: Request) -> Database | None:
    """Get database instance from app state."""
    return getattr(request.app.state, "db", None)

LLMModelDI = Annotated[BaseLLM, Depends(get_model)] # dependency injection
SettingsDI = Annotated[Settings, Depends(get_settings)]
DatabaseDI = Annotated[Database | None, Depends(get_db)]