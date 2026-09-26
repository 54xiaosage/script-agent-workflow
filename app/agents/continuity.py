from __future__ import annotations

from app.context import canon_block, plot_block, recent_scenes_block
from app.llm import complete_json
from app.models import Canon, GuardIssue, GuardReport, Plot, Scene, SceneBeatPlan

SYSTEM = """你是剧情贯通编辑。检查待审场次是否与正史、时间线、近场和本场规划矛盾。
检查清单：
1. 时间/地点是否能从上一场合理到达
2. 角色是否使用了不该知道的信息
3. 已死/不在场人物是否错误出现
4. 物品归属、伤势、职业身份是否跳变
5. 是否丢掉当前节拍、或提前回收未种植的枪
6. 是否与锁定事实冲突
只输出 JSON。blocker 必须改写。"""


def check_continuity(
    *,
    plot: Plot,
    canon: Canon,
    scenes: list[Scene],
    plan: SceneBeatPlan,
    draft: str,
    window: int = 4,
) -> GuardReport:
    user = f"""## 大纲
{plot_block(plot)}

## 正史
{canon_block(canon)}

## 近场
{recent_scenes_block(scenes, window)}

## 本场规划
{plan.model_dump_json(indent=2, ensure_ascii=False)}

## 待审场次
{draft}

输出 JSON:
{{
  "passed": true,
  "score": 0-100,
  "notes": "",
  "issues": [
    {{
      "agent": "continuity",
      "severity": "blocker|major|minor",
      "character_id": "",
      "detail": "",
      "suggestion": ""
    }}
  ]
}}"""
    data = complete_json(SYSTEM, user, temperature=0.1)
    issues = [GuardIssue.model_validate(i) for i in data.get("issues") or []]
    passed = bool(data.get("passed", False)) and not any(i.severity == "blocker" for i in issues)
    return GuardReport(
        passed=passed,
        score=float(data.get("score") or 0),
        issues=issues,
        notes=str(data.get("notes") or ""),
    )
