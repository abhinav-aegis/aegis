from sqlmodel import Session, create_engine
from redis import Redis
from backend.common.config import settings
from typing import Generator

# Set up PostgreSQL database engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=False)

# Set up Redis connection for caching
redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting a new database session.
    """
    with Session(engine) as session:
        yield session
