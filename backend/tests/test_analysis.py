"""排位表现评价 + 提升方案模块单元测试：mock DeepSeek 返回，验证解析与降级。"""

import json
from unittest.mock import MagicMock

from app.schemas.coach import AimStyleAnalysis
from app.services.analysis import (
    FALLBACK_NOTE,
    AnalysisService,
    build_user_message,
    parse_aim_analysis,
    parse_improvement_plan,
    radar_for_style,
)

VALID_JSON = (
    '{"primary_style": "tap_headhunter", "hs_pct_benchmark": "25%+", '
    '"strengths": ["预瞄准", "定位快"], "weaknesses": ["压枪不稳"], '
    '"confidence_note": "样本充足"}'
)


# ---------- aim 解析 ----------


def test_parse_valid_json():
    result = parse_aim_analysis(VALID_JSON)
    assert isinstance(result, AimStyleAnalysis)
    assert result.primary_style == "tap_headhunter"
    assert result.strengths == ["预瞄准", "定位快"]


def test_parse_missing_field():
    result = parse_aim_analysis('{"primary_style": "mixed"}')
    assert result.confidence_note == FALLBACK_NOTE
    assert result.primary_style == "mixed"


def test_parse_invalid_enum():
    raw = (
        '{"primary_style": "unknown_style", "hs_pct_benchmark": "x", '
        '"strengths": [], "weaknesses": [], "confidence_note": ""}'
    )
    result = parse_aim_analysis(raw)
    assert result.confidence_note == FALLBACK_NOTE
    assert result.primary_style == "mixed"


def test_parse_invalid_json():
    result = parse_aim_analysis("not a json")
    assert result.confidence_note == FALLBACK_NOTE


def test_parse_empty_string():
    result = parse_aim_analysis("")
    assert result.confidence_note == FALLBACK_NOTE


def test_build_user_message():
    msg = build_user_message(
        [{"match_id": "m1", "kills": 20}],
        [{"date": "x", "rr": 100}],
    )
    assert "recent_matches" in msg
    assert "rr_history" in msg


def test_radar_for_style():
    radar = radar_for_style("tap_headhunter")
    assert radar.tap == 85
    assert radar.spray == 30


def test_radar_for_unknown_style_defaults_mixed():
    radar = radar_for_style("nonexistent")
    assert radar.tap == 55


def test_analyze_aim_with_matches():
    deepseek = MagicMock()
    deepseek.generate_aim_analysis.return_value = VALID_JSON

    service = AnalysisService(deepseek)
    aim, match_count = service.analyze_aim([{"match_id": "m1", "kills": 20}])

    assert aim.primary_style == "tap_headhunter"
    assert match_count == 1
    deepseek.generate_aim_analysis.assert_called_once()


# ---------- plan 解析与硬校验 ----------


def _plan_json(drills: list) -> str:
    return json.dumps(
        {
            "weekly_focus": "提升定位",
            "drills": drills,
            "next_5_games_goal": "稳定",
            "warning": "",
        }
    )


def _drill(name: str, metric: str, description: str = "通用描述") -> dict:
    return {
        "name": name,
        "description": description,
        "frequency": "每天",
        "metric_to_track": metric,
    }


def test_parse_plan_valid():
    raw = _plan_json(
        [
            _drill("每日练枪", "hs_pct"),
            _drill("经济管理", "econ_rating"),
            _drill("走位意识", "kast"),
        ]
    )
    plan, fallback = parse_improvement_plan(raw, match_count=10)
    assert fallback is False
    assert len(plan.drills) == 3


def test_parse_plan_truncate_over_four():
    raw = _plan_json([_drill(f"训练{i}", "hs_pct") for i in range(6)])
    plan, fallback = parse_improvement_plan(raw, match_count=10)
    assert fallback is False
    assert len(plan.drills) == 4


def test_parse_plan_metric_whitelist():
    raw = _plan_json(
        [
            _drill("无效指标", "kd_ratio"),
            _drill("组合指标", "hs_pct + adr"),
            _drill("有效指标", "adr"),
        ]
    )
    plan, fallback = parse_improvement_plan(raw, match_count=10)
    assert fallback is False
    assert [d.name for d in plan.drills] == ["组合指标", "有效指标"]


def test_parse_plan_filter_specific_when_low_matches():
    raw = _plan_json(
        [
            _drill("jett 冲刺时机", "kast", "练习捷风身法"),
            _drill("基础瞄准", "hs_pct"),
            _drill("经济管理", "econ_rating"),
        ]
    )
    plan, fallback = parse_improvement_plan(raw, match_count=3)
    assert fallback is False
    assert [d.name for d in plan.drills] == ["基础瞄准", "经济管理"]


def test_parse_plan_fallback_when_too_few_drills():
    raw = _plan_json([_drill("无效指标", "kd_ratio")])
    plan, fallback = parse_improvement_plan(raw, match_count=10)
    assert fallback is True
    assert len(plan.drills) == 3  # 兜底固定 3 条


def test_parse_plan_invalid_json():
    plan, fallback = parse_improvement_plan("not a json", match_count=10)
    assert fallback is True
    assert len(plan.drills) == 3
