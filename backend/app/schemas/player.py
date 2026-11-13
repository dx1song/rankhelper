from typing import Optional

from sqlmodel import SQLModel


class RRHistoryEntry(SQLModel):
    date: str
    rr: int
    delta: int
    map: str
    agent: Optional[str] = None
    result: Optional[str] = None
    refunded_rr: Optional[int] = None
    was_derank_protected: Optional[bool] = None


class RecentMatch(SQLModel):
    match_id: str
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
    weapon_breakdown: dict[str, float]


class PlayerRawData(SQLModel):
    riot_id: str
    current_rank: str
    peak_rank: str
    rr_history: list[RRHistoryEntry]
    recent_matches: list[RecentMatch]


# ---- 手动录入（国服）----


class ManualMatch(SQLModel):
    """手动录入的单场对局（核心指标）。"""

    date: str
    map: str
    agent: str
    result: str
    kills: int
    deaths: int
    assists: int
    hs_pct: float
    adr: float


class ManualImportRequest(SQLModel):
    """手动录入请求：段位 + 最近 N 场对局。"""

    riot_id: str
    current_rank: str
    current_rr: int
    peak_rank: str
    matches: list[ManualMatch]


class SyncRequest(SQLModel):
    riot_id: str


class PlayerRankResponse(SQLModel):
    riot_id: str
    current_rank: str
    current_rr: int
    peak_rank: str
    region: str
    cached: bool = False
    stale: bool = False
