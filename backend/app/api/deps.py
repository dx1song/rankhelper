from collections.abc import Generator

from sqlmodel import Session

from app.core.database import engine
from app.services.deepseek import DeepSeekClient


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_deepseek_client() -> DeepSeekClient:
    return DeepSeekClient()
