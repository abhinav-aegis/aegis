import asyncio
from backend.common.db.init_db import init_db
from backend.common.db.session import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_init_data() -> None:
    async with SessionLocal() as session:
        logger.info("Creating initial data")
        await init_db(session)


async def main() -> None:
    await create_init_data()


if __name__ == "__main__":
    asyncio.run(main())
