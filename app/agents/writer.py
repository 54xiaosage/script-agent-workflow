from __future__ import annotations

from app.context import bible_block, canon_block, recent_scenes_block, voice_samples
from app.llm import complete
from app.models import Canon, Character, Scene, SceneBeatPlan

SYSTEM = """你是影视编剧。只写这一场剧本，不要写大纲评论。
格式要求：
1. 先写场景头：【场次】地点 / 日或夜 / 内或外
2. 动作用现在时中文叙述，简洁可视化。
3. 对白格式：角色名：台词。必要时用（括号）写潜台词或动作。
4. 角色说话必须符合人设与既有台词样本：用词、句长、是否绕弯、是否客气。
5. 不得让角色突然全知、突然改性格、突然拥有未建立的技能。
6. 本场必须完成规划中的 goal 与 emotional_turn，并遵守 must_not。
7. 不要写下一场，不要写作者注释。"""


def write_scene(
    *,
    characters: list[Character],
    canon: Canon,
    scenes: list[Scene],
    plan: SceneBeatPlan,
    window: int = 4,
) -> str:
    user = f"""## 本场规划
{plan.model_dump_json(indent=2, ensure_ascii=False)}

## 人设圣经
{bible_block(characters)}

## 正史（不可违背锁定事实）
{canon_block(canon)}

## 既有声口
{voice_samples(characters, scenes)}

## 近场（保持语气与信息连续）
{recent_scenes_block(scenes, window)}

请写出完整一场。"""
    return complete(SYSTEM, user, temperature=0.7)
