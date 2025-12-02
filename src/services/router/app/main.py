"""Main FastAPI application for Router service."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from loguru import logger

from services.router.app.dependencies import get_settings
from services.router.app.models import ChatRequest, ChatResponse, HealthResponse
from services.router.app.services.llm_service import OpenAPILLM
from services.router.app.routers import router
from services.router.app.database import Database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    settings = get_settings()
    
    # Initialize database
    try:
        db = Database(settings.database_url)
        await db.connect()
        app.state.db = db
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize database: {e}. Database features will be unavailable.")
        app.state.db = None
    
    # Initialize LLM
    try:
        model_provider = settings.model_provider

        if model_provider == "openai":
            llm_client = OpenAPILLM(
                model=settings.model.model,
                api_key=settings.model.openai_api_key,
                temperature=settings.model.temperature,
                max_tokens=settings.model.max_tokens,
                timeout=settings.llm_model_timeout
            )
            
        elif model_provider == "gigachat":
            logger.debug("Gigachat is unavailable. Please, implement interface in the `llm_service`.")
            raise ValueError("Model is unavailable. Please, choose another model.")

        else:
            logger.debug(f"Unknown model: {model_provider}.")
            raise ValueError("Model is unavailable. Please, choose another model.")

        app.state.model = llm_client
        logger.info("LLM model initialized successfully")

    except Exception as e:
        logger.warning(f"Failed to initialize model: {e}. LLM capabilities will be unavailable.")
        app.state.model = None

    yield

    logger.info("Shutting down Router service...")
    closing_tasks = []

    # Close database
    db = getattr(app.state, "db", None)
    if db:
        closing_tasks.append(db.close())
    
    # Close LLM
    llm = getattr(app.state, "model", None)
    if llm:
        closing_tasks.append(llm.close())
    
    if closing_tasks:
        results = await asyncio.gather(*closing_tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error during shutdown: {result}")


app = FastAPI(
    title="Router Service",
    description="API Gateway and router for CBQ Smart Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
