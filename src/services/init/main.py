"""Init service for database initialization and setup."""

import asyncio
import sys
from loguru import logger
from services.router.app.database import Database
from services.router.app.config import Settings


async def main():
    """Run initialization tasks."""
    logger.info("Starting initialization service...")
    
    try:
        settings = Settings()
        db = Database(settings.database_url)
        await db.connect()
        logger.info("Database connection established")
        
        # TODO
        
        logger.info("Initialization completed successfully")
        await db.close()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

