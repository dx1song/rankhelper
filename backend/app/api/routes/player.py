import time

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_session
from app.models.player import Match, Player
from app.schemas.player import ManualImportRequest, PlayerRankResponse

router = APIRouter(prefix="/api/player", tags=["player"])


@router.post("/manual", response_model=PlayerRankResponse)
def import_manual(
    payload: ManualImportRequest,
    session: Session = Depends(get_session),
):
    """手动录入国服数据：段位 + 最近 N 场对局（覆盖式写入）。"""
    riot_id = payload.riot_id.strip()
    if "#" not in riot_id:
        raise HTTPException(status_code=422, detail="riot_id 需为 name#tag 格式")

    player = session.exec(select(Player).where(Player.riot_id == riot_id)).first()
    if player is None:
        player = Player(
            riot_id=riot_id,
            region="cn",
            current_rank=payload.current_rank,
            current_rr=payload.current_rr,
            peak_rank=payload.peak_rank,
        )
        session.add(player)
        session.flush()
    else:
        player.region = "cn"
        player.current_rank = payload.current_rank
        player.current_rr = payload.current_rr
        player.peak_rank = payload.peak_rank
        session.add(player)

    # 覆盖式：清空旧对局，重新录入
    old_matches = session.exec(select(Match).where(Match.player_id == player.id)).all()
    for m in old_matches:
        session.delete(m)

    stamp = int(time.time() * 1000)
    for i, mm in enumerate(payload.matches):
        session.add(
            Match(
                player_id=player.id,
                match_id=f"manual-{stamp}-{i}",
                date=mm.date,
                map=mm.map,
                agent=mm.agent,
                result=mm.result,
                kills=mm.kills,
                deaths=mm.deaths,
                assists=mm.assists,
                hs_pct=mm.hs_pct,
                adr=mm.adr,
                kast=0.0,
                econ_rating=0.0,
                weapon_breakdown={},
            )
        )
    session.commit()

    return PlayerRankResponse(
        riot_id=riot_id,
        current_rank=payload.current_rank,
        current_rr=payload.current_rr,
        peak_rank=payload.peak_rank,
        region="cn",
    )
