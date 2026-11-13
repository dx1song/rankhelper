from sqlmodel import SQLModel

from app.schemas.coach import AimStyleAnalysis, ImprovementPlan


class AimAnalysisRequest(SQLModel):
    riot_id: str


class RadarData(SQLModel):
    tap: int
    spray: int
    utility: int
    positioning: int
    consistency: int


class AimAnalysisResponse(SQLModel):
    aim_style_analysis: AimStyleAnalysis
    radar: RadarData
    match_count: int


class PlanResponse(SQLModel):
    improvement_plan: ImprovementPlan
    fallback: bool = False
