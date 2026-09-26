from __future__ import annotations

from app.context import bible_block, voice_samples
from app.llm import complete_json
from app.models import Character, GuardIssue, GuardReport, Scene

SYSTEM = """你是人设守卫编辑。只检查角色是否 OOC，不评价文采。
重点：
- 锁定人设是否被破坏
- 价值观/恐惧/欲望是否被无铺垫翻转
- 能力边界是否被突破
- 声口是否偏离（礼貌程度、句长、口头禅、绝不会说的话）
- 关系态度是否跳变
对每位出场角色给出判断。blocker 表示必须改写。
只输出 JSON。"""


def check_persona(characters: list[Character], scenes: list[Scene], draft: str) -> GuardReport:
    user = f"""## 人设
{bible_block(characters)}

## 既有声口
{voice_samples(characters, scenes)}

## 待审场次
{draft}

输出 JSON:
{{
  "passed": true,
  "score": 0-100,
  "notes": "",
  "issues": [
    {{
      "agent": "persona",
      "severity": "blocker|major|minor",
      "character_id": "",
      "detail": "",
      "suggestion": ""
    }}
  ]
}}
若无人设问题，issues 为空且 passed=true。"""
    data = complete_json(SYSTEM, user, temperature=0.1)
    issues = [GuardIssue.model_validate(i) for i in data.get("issues") or []]
    passed = bool(data.get("passed", False)) and not any(i.severity == "blocker" for i in issues)
    return GuardReport(
        passed=passed,
        score=float(data.get("score") or 0),
        issues=issues,
        notes=str(data.get("notes") or ""),
    )
