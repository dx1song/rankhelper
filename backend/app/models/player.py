from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    # SQLModel 0.0.49+ 要求 timezone-aware datetime
    return datetime.now(timezone.utc)


class Player(SQLModel, table=True):
    __tablename__ = "players"

    id: Optional[int] = Field(default=None, primary_key=True)
    riot_id: str = Field(index=True, unique=True)
    region: str = ""
    current_rank: str
    current_rr: int = 0
    peak_rank: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class RankSnapshot(SQLModel, table=True):
    __tablename__ = "rank_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    region: str = ""
    current_rank: str
    current_rr: int = 0
    peak_rank: str
    mmr_history: list = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now)


class RRRecord(SQLModel, table=True):
    __tablename__ = "rr_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    date: str
    rr: int
    delta: int
    map: str
    agent: str
    result: str


class Match(SQLModel, table=True):
    __tablename__ = "matches"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    match_id: str = Field(index=True, unique=True)
    date: str
    map: str
    agent: str
    result: str
    kills: int
    deaths: int
    assists: int
    hs_pct: float
    adr: float
    kast: float
    econ_rating: float
    weapon_breakdown: dict = Field(default_factory=dict, sa_column=Column(JSON))
