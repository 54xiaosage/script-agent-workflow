from __future__ import annotations

from app.context import bible_block, canon_block, plot_block, recent_scenes_block
from app.llm import complete_json
from app.models import Canon, Character, Plot, Scene, SceneBeatPlan


SYSTEM = """你是剧集主创（Showrunner）手下的场次规划师。
任务：根据大纲、正史和已写场次，规划【下一场】，保证剧情向前推进且不跳轴。
规则：
1. 优先推进 status=in_progress 的节拍；若无，则取第一个 pending 节拍。
2. 本场必须制造具体冲突，并让至少一个角色的欲望/恐惧起作用。
3. 不得安排角色做超出能力边界、或违反锁定人设的事。
4. must_not 要列出会破坏连贯性的事项（死人复活、未获知识、地点瞬移等）。
只输出 JSON。"""


def plan_scene(
    *,
    logline: str,
    characters: list[Character],
    plot: Plot,
    canon: Canon,
    scenes: list[Scene],
    extra_instruction: str = "",
    window: int = 4,
) -> SceneBeatPlan:
    user = f"""剧作一句话: {logline}

## 人设
{bible_block(characters)}

## 大纲
{plot_block(plot)}

## 正史
{canon_block(canon)}

## 近场
{recent_scenes_block(scenes, window)}

额外指令: {extra_instruction or "无"}

请输出 JSON:
{{
  "beat_id": "",
  "goal": "本场外在目标",
  "conflict": "阻力/对手/两难",
  "characters": ["角色id"],
  "location": "",
  "time": "相对上一场的时间",
  "must_include": ["必须发生的事"],
  "must_not": ["禁止发生的事"],
  "emotional_turn": "情绪如何转向"
}}"""
    data = complete_json(SYSTEM, user, temperature=0.3)
    ids = {c.id for c in characters}
    names = {c.name: c.id for c in characters}
    raw_chars = data.get("characters") or []
    mapped = []
    for item in raw_chars:
        if item in ids:
            mapped.append(item)
        elif item in names:
            mapped.append(names[item])
    data["characters"] = mapped or [c.id for c in characters[:2]]
    return SceneBeatPlan.model_validate(data)
