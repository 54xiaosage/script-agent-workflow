from __future__ import annotations

from app.llm import complete_json
from app.models import SceneBeatPlan


SYSTEM = """你从刚写完的场次中抽取可写入正史的信息。只记录明确发生的事，不要脑补。
只输出 JSON。"""


def extract_from_scene(scene_id: str, content: str, plan: SceneBeatPlan) -> dict:
    user = f"""场次ID: {scene_id}
规划: {plan.model_dump_json(ensure_ascii=False)}

正文:
{content}

输出 JSON:
{{
  "summary": "不超过120字摘要",
  "title": "短标题",
  "facts": [{{"id": "Fxxx", "text": "", "locked": false, "category": "world|character|object|relationship|knowledge"}}],
  "timeline": [{{"when": "", "event": ""}}],
  "character_states": {{"角色id或名": {{"location": "", "injury": "", "knowledge": "", "emotion": ""}}}},
  "open_threads": ["未完成线索"],
  "chekhov": [{{"item": "", "status": "planted|paid"}}]
}}"""
    return complete_json(SYSTEM, user, temperature=0.1)
