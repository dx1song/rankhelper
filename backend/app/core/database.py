from sqlmodel import SQLModel, create_engine

from app.core.config import settings

# SQLite 需要 check_same_thread=False（FastAPI 多线程访问）
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=_connect_args, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
