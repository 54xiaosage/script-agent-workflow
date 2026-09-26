from __future__ import annotations

from app.agents.continuity import check_continuity
from app.agents.extractor import extract_from_scene
from app.agents.persona_guard import check_persona
from app.agents.planner import plan_scene
from app.agents.rewriter import rewrite_scene
from app.agents.writer import write_scene
from app.config import MAX_REWRITE_ROUNDS, RECENT_SCENE_WINDOW
from app.models import (
    Canon,
    Character,
    Fact,
    GuardIssue,
    Plot,
    Scene,
    TimelineEvent,
    WorkflowResult,
)
from app import store


def _merge_extraction(
    slug: str,
    characters: list[Character],
    plot: Plot,
    canon: Canon,
    scene_id: str,
    extracted: dict,
) -> tuple[list[Character], Plot, Canon]:
    existing_ids = {f.id for f in canon.facts}
    for i, raw in enumerate(extracted.get("facts") or [], start=1):
        fid = str(raw.get("id") or f"{scene_id}-F{i}")
        if fid in existing_ids:
            fid = f"{scene_id}-F{i}"
        canon.facts.append(
            Fact(
                id=fid,
                text=str(raw.get("text") or ""),
                locked=bool(raw.get("locked")),
                source_scene=scene_id,
                category=str(raw.get("category") or "world"),
            )
        )
        existing_ids.add(fid)
    for t in extracted.get("timeline") or []:
        canon.timeline.append(
            TimelineEvent(when=str(t.get("when") or ""), event=str(t.get("event") or ""), scene_id=scene_id)
        )
    for item in extracted.get("chekhov") or []:
        if isinstance(item, dict):
            canon.chekhov.append({k: str(v) for k, v in item.items()})
    threads = [str(x) for x in (extracted.get("open_threads") or []) if str(x).strip()]
    if threads:
        merged = list(dict.fromkeys(plot.open_threads + threads))
        plot.open_threads = merged
    states = extracted.get("character_states") or {}
    name_to_char = {c.name: c for c in characters}
    id_to_char = {c.id: c for c in characters}
    for key, st in states.items():
        ch = id_to_char.get(key) or name_to_char.get(key)
        if not ch or not isinstance(st, dict):
            continue
        for k, v in st.items():
            if v:
                ch.current_state[str(k)] = str(v)
    for act in plot.acts:
        for beat in act.beats:
            if beat.status == "in_progress":
                continue
    return characters, plot, canon


def _mark_beat(plot: Plot, beat_id: str) -> Plot:
    found = False
    for act in plot.acts:
        for beat in act.beats:
            if beat.id == beat_id:
                beat.status = "in_progress"
                found = True
            elif beat.status == "in_progress" and beat.id != beat_id:
                beat.status = "done"
    if not found:
        for act in plot.acts:
            for beat in act.beats:
                if beat.status == "pending":
                    beat.status = "in_progress"
                    break
            else:
                continue
            break
    return plot


def run_next_scene(slug: str, extra_instruction: str = "", auto_save: bool = True) -> WorkflowResult:
    meta = store.load_meta(slug)
    characters = store.load_characters(slug)
    plot = store.load_plot(slug)
    canon = store.load_canon(slug)
    scenes = store.list_scenes(slug)

    plan = plan_scene(
        logline=meta.logline or meta.title,
        characters=characters,
        plot=plot,
        canon=canon,
        scenes=scenes,
        extra_instruction=extra_instruction,
        window=RECENT_SCENE_WINDOW,
    )
    draft = write_scene(
        characters=characters,
        canon=canon,
        scenes=scenes,
        plan=plan,
        window=RECENT_SCENE_WINDOW,
    )

    persona = check_persona(characters, scenes, draft)
    continuity = check_continuity(
        plot=plot, canon=canon, scenes=scenes, plan=plan, draft=draft, window=RECENT_SCENE_WINDOW
    )
    rounds = 0
    while rounds < MAX_REWRITE_ROUNDS and (not persona.passed or not continuity.passed):
        issues: list[GuardIssue] = list(persona.issues) + list(continuity.issues)
        blockers = [i for i in issues if i.severity in {"blocker", "major"}] or issues
        draft = rewrite_scene(
            characters=characters, canon=canon, plan=plan, draft=draft, issues=blockers
        )
        persona = check_persona(characters, scenes, draft)
        continuity = check_continuity(
            plot=plot, canon=canon, scenes=scenes, plan=plan, draft=draft, window=RECENT_SCENE_WINDOW
        )
        rounds += 1

    scene_id = store.next_scene_id(slug)
    extracted = extract_from_scene(scene_id, draft, plan)
    scene = Scene(
        id=scene_id,
        title=str(extracted.get("title") or plan.goal[:20] or scene_id),
        plan=plan,
        content=draft,
        summary=str(extracted.get("summary") or ""),
        status="approved" if persona.passed and continuity.passed else "draft",
    )

    if auto_save:
        store.save_scene(slug, scene)
        characters, plot, canon = _merge_extraction(slug, characters, plot, canon, scene_id, extracted)
        plot = _mark_beat(plot, plan.beat_id)
        store.save_characters(slug, characters)
        store.save_plot(slug, plot)
        store.save_canon(slug, canon)

    return WorkflowResult(
        scene=scene,
        plan=plan,
        persona=persona,
        continuity=continuity,
        rewrite_rounds=rounds,
        extracted=extracted,
        auto_saved=auto_save,
    )
