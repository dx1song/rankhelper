from typing import Literal

from sqlmodel import SQLModel


class AimStyleAnalysis(SQLModel):
    primary_style: Literal[
        "tap_headhunter", "spray_transfer", "op_holder", "utility_anchor", "mixed"
    ]
    hs_pct_benchmark: str
    strengths: list[str]
    weaknesses: list[str]
    confidence_note: str


class Drill(SQLModel):
    name: str
    description: str
    frequency: str
    metric_to_track: str


class ImprovementPlan(SQLModel):
    weekly_focus: str
    drills: list[Drill]
    next_5_games_goal: str
    warning: str


class CoachOutput(SQLModel):
    aim_style_analysis: AimStyleAnalysis
    improvement_plan: ImprovementPlan
