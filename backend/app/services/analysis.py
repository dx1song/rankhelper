"""排位表现评价 + 针对性提升方案：编排、解析校验与降级。"""

import json
import logging

from app.schemas.analysis import RadarData
from app.schemas.coach import AimStyleAnalysis, Drill, ImprovementPlan
from app.services.deepseek import DeepSeekClient

logger = logging.getLogger(__name__)

FALLBACK_NOTE = "AI 分析不可用"

# metric_to_track 白名单：命中任一关键词（含组合描述如 "hs_pct + adr"）才算有效
METRIC_WHITELIST = ("hs_pct", "adr", "kast", "econ_rating")

# 具体对象关键词：drill 文本命中任一即视为"含具体弱点断言"，样本不足(<5场)时过滤。
# 启发式 substring 匹配，个别单字词（如"零"）可能误伤通用词，属可接受的近似。
SPECIFIC_TERMS = [
    # agents（英文）
    "brimstone", "viper", "omen", "killjoy", "cypher", "sova", "sage",
    "phoenix", "jett", "raze", "breach", "reyna", "yoru", "astra",
    "kayo", "chamber", "neon", "fade", "harbor", "gekko", "deadlock",
    "iso", "clove", "vyse", "tejo", "waylay",
    # agents（中文）
    "炼狱", "蝰蛇", "幽影", "奇乐", "零", "猎枭", "贤者", "不死鸟",
    "捷风", "雷兹", "叛奇", "芮娜", "夜露", "亚星卓", "尚勃勒",
    "霓虹", "黑梦", "海神", "盖可", "致死锁", "丁香", "维斯",
    # maps
    "ascent", "bind", "haven", "split", "icebox", "breeze", "fracture",
    "pearl", "lotus", "sunset", "abyss",
    "源工重镇", "亚海悬城", "隐世修所", "莲华古城", "冰封遗址",
    "微风岛屿", "裂变峡谷", "珍珠市", "遗落禅寺", "日落之城", "深渊",
    # ranks
    "iron", "bronze", "silver", "gold", "platinum", "diamond",
    "ascendant", "immortal", "radiant",
    "黑铁", "青铜", "白银", "黄金", "铂金", "钻石", "超凡", "神话", "无畏战魂",
]

# primary_style -> 五维雷达数值（后端预计算，前端不硬编码映射）
RADAR_BY_STYLE: dict[str, RadarData] = {
    "tap_headhunter": RadarData(tap=85, spray=30, utility=45, positioning=55, consistency=60),
    "spray_transfer": RadarData(tap=40, spray=85, utility=40, positioning=50, consistency=55),
    "op_holder": RadarData(tap=60, spray=25, utility=35, positioning=80, consistency=65),
    "utility_anchor": RadarData(tap=35, spray=35, utility=85, positioning=60, consistency=55),
    "mixed": RadarData(tap=55, spray=55, utility=55, positioning=55, consistency=55),
}


def radar_for_style(primary_style: str) -> RadarData:
    return RADAR_BY_STYLE.get(primary_style, RADAR_BY_STYLE["mixed"])


def fallback_aim_analysis() -> AimStyleAnalysis:
    """降级结果：解析/校验失败时返回，不向前端抛异常。"""
    return AimStyleAnalysis(
        primary_style="mixed",
        hs_pct_benchmark="",
        strengths=[],
        weaknesses=[],
        confidence_note=FALLBACK_NOTE,
    )


def parse_aim_analysis(raw: str) -> AimStyleAnalysis:
    """json.loads + Pydantic 校验；缺字段或枚举非法一律降级，绝不抛异常。"""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        logger.warning("DeepSeek 返回非 JSON，降级")
        return fallback_aim_analysis()
    try:
        return AimStyleAnalysis.model_validate(data)
    except Exception:
        logger.warning("AimStyleAnalysis 校验失败，降级")
        return fallback_aim_analysis()


def build_user_message(recent_matches: list, rr_history: list) -> str:
    """把 recent_matches 与 rr_history 组装成给 DeepSeek 的 user message。"""
    payload = {"recent_matches": recent_matches, "rr_history": rr_history}
    return json.dumps(payload, ensure_ascii=False)


def fallback_plan() -> ImprovementPlan:
    """兜底方案：固定 3 条通用基础 drill（不含具体弱点断言）。"""
    return ImprovementPlan(
        weekly_focus="基础巩固",
        drills=[
            Drill(
                name="瞄准基础训练",
                description="每日固定练枪，保持准星稳定与定位手感。",
                frequency="每天 30 分钟",
                metric_to_track="hs_pct",
            ),
            Drill(
                name="经济与起枪节奏",
                description="关注经济管理与起枪时机，避免无谓对枪。",
                frequency="每局执行",
                metric_to_track="econ_rating",
            ),
            Drill(
                name="小地图与走位意识",
                description="养成看小地图与信息收集习惯，减少无信息前压。",
                frequency="每局执行",
                metric_to_track="kast",
            ),
        ],
        next_5_games_goal="稳定发挥，避免连败掉分",
        warning="当前为规则兜底方案，AI 分析暂不可用。",
    )


def _metric_in_whitelist(metric: str) -> bool:
    return any(w in metric for w in METRIC_WHITELIST)


def _is_generic(drill: Drill) -> bool:
    text = f"{drill.name} {drill.description}".lower()
    return not any(term in text for term in SPECIFIC_TERMS)


def parse_improvement_plan(raw: str, match_count: int) -> tuple[ImprovementPlan, bool]:
    """解析 + 硬校验；失败或有效 drill 不足则返回兜底方案（fallback=True）。

    硬校验规则（不只靠 prompt）：
    1. metric_to_track 必须命中白名单，否则丢弃该 drill。
    2. 对局数 < 5 时只保留通用基础项，过滤含具体弱点断言的条目。
    3. drills 数量 2-4，超出截断；过滤后 < 2 条则降级兜底。
    """
    try:
        data = json.loads(raw)
        plan = ImprovementPlan.model_validate(data)
    except Exception:
        logger.warning("ImprovementPlan 解析/校验失败，降级兜底")
        return fallback_plan(), True

    drills = list(plan.drills or [])
    drills = [d for d in drills if _metric_in_whitelist(d.metric_to_track)]
    if match_count < 5:
        drills = [d for d in drills if _is_generic(d)]
    drills = drills[:4]

    if len(drills) < 2:
        logger.warning("有效 drill 不足 2 条，降级兜底")
        return fallback_plan(), True

    return plan.model_copy(update={"drills": drills}), False


def build_plan_message(aim: AimStyleAnalysis, recent_matches: list) -> str:
    """aim 分析结果 + recent_matches 摘要，组装成 plan 的 user message。"""
    summary = [
        {
            "agent": m.get("agent", ""),
            "result": m.get("result", ""),
            "kills": m.get("kills", 0),
            "deaths": m.get("deaths", 0),
            "assists": m.get("assists", 0),
            "hs_pct": m.get("hs_pct", 0.0),
            "adr": m.get("adr", 0.0),
        }
        for m in recent_matches
    ]
    payload = {
        "aim_style_analysis": aim.model_dump(),
        "recent_matches_summary": summary,
    }
    return json.dumps(payload, ensure_ascii=False)


class AnalysisService:
    """AI 分析编排：接收已读好的 recent_matches（dict 列表），调 DeepSeek 并校验。"""

    def __init__(self, deepseek: DeepSeekClient) -> None:
        self.deepseek = deepseek

    def _aim_from_data(self, recent_matches: list) -> AimStyleAnalysis:
        raw = self.deepseek.generate_aim_analysis(build_user_message(recent_matches, []))
        return parse_aim_analysis(raw)

    def analyze_aim(self, recent_matches: list) -> tuple[AimStyleAnalysis, int]:
        """返回 (aim 分析, 对局数)。"""
        aim = self._aim_from_data(recent_matches)
        return aim, len(recent_matches)

    def analyze_plan(self, recent_matches: list) -> tuple[ImprovementPlan, bool]:
        """先 aim 后 plan，分两次调用 DeepSeek，避免单次输出过长被截断。"""
        aim = self._aim_from_data(recent_matches)
        raw = self.deepseek.generate_improvement_plan(build_plan_message(aim, recent_matches))
        return parse_improvement_plan(raw, match_count=len(recent_matches))
