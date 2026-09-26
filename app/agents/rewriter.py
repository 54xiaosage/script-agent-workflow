from __future__ import annotations

from app.context import bible_block, canon_block
from app.llm import complete
from app.models import Canon, Character, GuardIssue, SceneBeatPlan

SYSTEM = """你是改稿编剧。在尽量保留原场节奏与可用对白的前提下，只修复列出的问题。
要求：
- 不引入新的锁定事实冲突
- 不无故更换出场人物
- 人设声口仍须一致
- 仍完成规划中的 goal 与 emotional_turn
只输出修订后的完整场次，不要解释。"""


def rewrite_scene(
    *,
    characters: list[Character],
    canon: Canon,
    plan: SceneBeatPlan,
    draft: str,
    issues: list[GuardIssue],
) -> str:
    issue_text = "\n".join(
        f"- [{i.severity}] ({i.agent}/{i.character_id}) {i.detail} => {i.suggestion}" for i in issues
    )
    user = f"""## 规划
{plan.model_dump_json(indent=2, ensure_ascii=False)}

## 人设
{bible_block(characters)}

## 正史
{canon_block(canon)}

## 必须修复
{issue_text}

## 原稿
{draft}"""
    return complete(SYSTEM, user, temperature=0.4)
