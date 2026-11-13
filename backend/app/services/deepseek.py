"""DeepSeek AI 客户端（OpenAI 兼容接口）。"""

from openai import OpenAI

from app.core.config import settings

COACH_EVAL_PROMPT = """你是无畏契约表现分析师。只收到结构化对局数据，看不到画面。
任务：输出对玩家瞄准风格的评估。

原则：
1. 不得仅凭全局 hs_pct 下结论。先看 weapon_breakdown 与 agent：狙击占比高时低 hs_pct 不算缺陷；烟位/哨位玩家 hs_pct 22–27% 且 kast 高时，应明确说"这是健康数据，无需为数字改变击杀方式"。
2. 只有 Vandal/Phantom 为主、hs_pct 持续低于同段位中位数、且 adr 无补偿性偏高时，才把"准星放置"列为可改进项。
3. 对局少于 8 场时降低断言强度，用"目前数据不足以判断……"。
4. strengths / weaknesses 每条必须引用输入中的具体指标。

只返回一个 json 对象，不要 Markdown 代码块，不要 json 之外任何文字：
{"primary_style":"tap_headhunter|spray_transfer|op_holder|utility_anchor|mixed","hs_pct_benchmark":"中文描述，结合武器与角色解释","strengths":["..."],"weaknesses":["..."],"confidence_note":"说明基于多少场及主要局限"}"""

COACH_PLAN_PROMPT = """你是无畏契约上分教练。输入是玩家的瞄准评估结果与对局摘要。
任务：给出本周可执行的训练方案。

原则：
1. 区分可训练项（瞄准、准星放置、经济决策，可短期见效）与长周期项（角色熟练度、地图理解），后者不放进 drills。
2. weekly_focus 只允许一个核心方向。
3. drills 给 2–4 项，metric_to_track 只能是 hs_pct / adr / kast / econ_rating 之一。
4. 数据不足时宁可不写，不要编造。
5. warning 必须是针对该玩家的真实风险，例如"不要为练爆头在残局放弃稳杀"。

只返回一个 json 对象，不要 Markdown 代码块，不要 json 之外任何文字：
{"weekly_focus":"...","drills":[{"name":"...","description":"...","frequency":"...","metric_to_track":"..."}],"next_5_games_goal":"...","warning":"..."}"""


class DeepSeekClient:
    def __init__(self) -> None:
        self.client = OpenAI(
            base_url=settings.deepseek_base_url,
            api_key=settings.deepseek_api_key,
        )
        self.model = settings.deepseek_model

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """统一走 chat.completions，返回原始 JSON 字符串（不做解析）。"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content or ""

    def generate_aim_analysis(self, user_message: str) -> str:
        return self._chat(COACH_EVAL_PROMPT, user_message)

    def generate_improvement_plan(self, user_message: str) -> str:
        return self._chat(COACH_PLAN_PROMPT, user_message)
