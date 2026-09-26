from __future__ import annotations

from app.models import Canon, Character, Plot, Scene


def character_card(c: Character) -> str:
    voice = c.voice
    return "\n".join(
        [
            f"ID: {c.id} | 姓名: {c.name} | 年龄: {c.age} | 功能: {c.role}",
            f"身份: {c.identity}",
            f"价值观: {', '.join(c.values)}",
            f"恐惧: {', '.join(c.fears)}",
            f"欲望: {', '.join(c.desires)}",
            f"锁定人设（不可为剧情方便而破坏）: {', '.join(c.locked_traits)}",
            f"能力: {', '.join(c.capabilities)}",
            f"能力边界: {', '.join(c.limits)}",
            f"关系: {c.relationships}",
            f"语域: {voice.register}",
            f"用词: {voice.vocabulary}",
            f"口头禅/语气习惯: {', '.join(voice.verbal_tics)}",
            f"绝不会说: {', '.join(voice.never_says)}",
            f"台词样本: {voice.sample_lines}",
            f"当前状态: {c.current_state}",
        ]
    )


def bible_block(characters: list[Character]) -> str:
    if not characters:
        return "（尚无人设）"
    return "\n\n".join(character_card(c) for c in characters)


def plot_block(plot: Plot) -> str:
    lines = [f"前提: {plot.premise}", f"赌注: {plot.stakes}", f"未收线: {plot.open_threads}"]
    for act in plot.acts:
        lines.append(f"## {act.title} ({act.id})")
        for b in act.beats:
            lines.append(f"- [{b.status}] {b.id} {b.title}: {b.description}")
            if b.planted:
                lines.append(f"  埋线: {b.planted}")
            if b.payoff:
                lines.append(f"  回收: {b.payoff}")
    return "\n".join(lines)


def canon_block(canon: Canon) -> str:
    facts = "\n".join(
        f"- [{'LOCK' if f.locked else 'open'}][{f.category}] {f.id}: {f.text}" for f in canon.facts
    ) or "（暂无事实）"
    timeline = "\n".join(f"- {t.when}: {t.event} ({t.scene_id})" for t in canon.timeline) or "（暂无时间线）"
    chekhov = "\n".join(str(x) for x in canon.chekhov) or "（无）"
    return f"## 正史事实\n{facts}\n\n## 时间线\n{timeline}\n\n## 契诃夫之枪\n{chekhov}"


def recent_scenes_block(scenes: list[Scene], window: int) -> str:
    recent = scenes[-window:]
    if not recent:
        return "（尚无已写场次）"
    parts = []
    for s in recent:
        parts.append(f"### {s.id} {s.title}\n摘要: {s.summary}\n\n{s.content}")
    return "\n\n".join(parts)


def voice_samples(characters: list[Character], scenes: list[Scene], limit_per_char: int = 4) -> str:
    samples: dict[str, list[str]] = {c.name: list(c.voice.sample_lines) for c in characters}
    for scene in scenes:
        for line in scene.content.splitlines():
            for name, bucket in samples.items():
                if line.strip().startswith(f"{name}：") or line.strip().startswith(f"{name}:"):
                    bucket.append(line.strip())
    out = []
    for c in characters:
        lines = samples.get(c.name, [])[-limit_per_char:]
        if lines:
            out.append(f"{c.name} 既有台词:\n" + "\n".join(f"- {x}" for x in lines))
    return "\n\n".join(out) or "（暂无既有台词）"
