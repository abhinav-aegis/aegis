from sqlmodel.ext.asyncio.session import AsyncSession
from backend.proxy.models import LLMStubReplaySequence
from backend.proxy.utils.exceptions import SerializedException, EXCEPTION_CLASS_MAP
from sqlmodel import select
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

STUB_MODEL_NAME = "stub_error_sequence"

async def init_db(db_session: AsyncSession) -> None:
    """
    Initialize the stub_error_sequence LLMStubReplaySequence with all known exceptions.
    """
    logger.info(f"Checking for existing stub sequence: {STUB_MODEL_NAME}")

    existing = await db_session.exec(
        select(LLMStubReplaySequence).where(LLMStubReplaySequence.model == STUB_MODEL_NAME)
    )
    if existing.first():
        logger.info(f"Stub model '{STUB_MODEL_NAME}' already exists. Skipping creation.")
        return

    logger.info("Creating error sequence with known exception types...")

    sequence = []
    for exc_type, _ in EXCEPTION_CLASS_MAP.items():
        exc = SerializedException(
            message=f"This is a test for {exc_type}",
            body=None,
            code="E123",
            param="example_param",
            type=exc_type,
        )
        sequence.append(exc.model_dump())

    stub_sequence = LLMStubReplaySequence(
        id=uuid4(),
        model=STUB_MODEL_NAME,
        responses=sequence,
        is_active=True,
        current_index=0,
    )

    db_session.add(stub_sequence)
    await db_session.commit()
    logger.info(f"Stub model '{STUB_MODEL_NAME}' initialized with {len(sequence)} errors.")
