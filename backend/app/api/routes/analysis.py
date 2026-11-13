from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_deepseek_client, get_session
from app.models.player import Match, Player
from app.schemas.analysis import AimAnalysisRequest, AimAnalysisResponse, PlanResponse
from app.services.analysis import AnalysisService, radar_for_style
from app.services.deepseek import DeepSeekClient

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _recent_matches(session: Session, riot_id: str) -> list[dict]:
    """从库读取该玩家已录入的对局，转为 recent_matches dict 列表。"""
    player = session.exec(select(Player).where(Player.riot_id == riot_id)).first()
    if player is None:
        return []
    matches = session.exec(
        select(Match).where(Match.player_id == player.id).order_by(Match.id.desc())
    ).all()
    return [
        {
            "match_id": m.match_id,
            "date": m.date,
            "map": m.map,
            "agent": m.agent,
            "result": m.result,
            "kills": m.kills,
            "deaths": m.deaths,
            "assists": m.assists,
            "hs_pct": m.hs_pct,
            "adr": m.adr,
            "kast": m.kast,
            "econ_rating": m.econ_rating,
            "weapon_breakdown": m.weapon_breakdown,
        }
        for m in matches
    ]


@router.post("/aim", response_model=AimAnalysisResponse)
def analyze_aim(
    payload: AimAnalysisRequest,
    session: Session = Depends(get_session),
    deepseek: DeepSeekClient = Depends(get_deepseek_client),
):
    matches = _recent_matches(session, payload.riot_id)
    if not matches:
        raise HTTPException(status_code=404, detail="未找到该玩家的对局数据，请先录入")
    aim, match_count = AnalysisService(deepseek).analyze_aim(matches)
    return AimAnalysisResponse(
        aim_style_analysis=aim,
        radar=radar_for_style(aim.primary_style),
        match_count=match_count,
    )


@router.post("/plan", response_model=PlanResponse)
def analyze_plan(
    payload: AimAnalysisRequest,
    session: Session = Depends(get_session),
    deepseek: DeepSeekClient = Depends(get_deepseek_client),
):
    matches = _recent_matches(session, payload.riot_id)
    if not matches:
        raise HTTPException(status_code=404, detail="未找到该玩家的对局数据，请先录入")
    plan, fallback = AnalysisService(deepseek).analyze_plan(matches)
    return PlanResponse(improvement_plan=plan, fallback=fallback)
