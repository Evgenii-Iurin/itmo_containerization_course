"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from loguru import logger


class Database:
    """Database connection manager using SQLAlchemy."""
    
    def __init__(self, database_url: str):
        # Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        self.database_url = database_url
        self.engine = None
        self.async_session_maker: async_sessionmaker[AsyncSession] | None = None
    
    async def connect(self) -> None:
        """Create SQLAlchemy async engine and session maker."""
        try:
            self.engine = create_async_engine(
                self.database_url,
                pool_size=10,
                max_overflow=20,
                echo=False
            )
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("SQLAlchemy database engine created successfully")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    
    async def close(self) -> None:
        """Close database engine."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database engine closed")
    
    def get_session(self):
        """Get async database session context manager."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call connect() first.")
        
        return self.async_session_maker()



