from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ProjectMeta(BaseModel):
    slug: str
    title: str
    logline: str = ""
    genre: str = "都市剧"
    tone: str = "克制、写实"
    theme: str = ""


class VoiceProfile(BaseModel):
    register: str = ""
    vocabulary: str = ""
    verbal_tics: list[str] = Field(default_factory=list)
    never_says: list[str] = Field(default_factory=list)
    sample_lines: list[str] = Field(default_factory=list)


class Character(BaseModel):
    id: str
    name: str
    age: str = ""
    role: str = ""
    identity: str = ""
    values: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    desires: list[str] = Field(default_factory=list)
    locked_traits: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    limits: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)
    voice: VoiceProfile = Field(default_factory=VoiceProfile)
    current_state: dict[str, str] = Field(default_factory=dict)


class Beat(BaseModel):
    id: str
    title: str
    description: str
    status: str = "pending"  # pending | in_progress | done
    planted: list[str] = Field(default_factory=list)
    payoff: list[str] = Field(default_factory=list)


class Act(BaseModel):
    id: str
    title: str
    beats: list[Beat] = Field(default_factory=list)


class Plot(BaseModel):
    premise: str = ""
    stakes: str = ""
    acts: list[Act] = Field(default_factory=list)
    open_threads: list[str] = Field(default_factory=list)


class Fact(BaseModel):
    id: str
    text: str
    locked: bool = False
    source_scene: str = ""
    category: str = "world"  # world | character | object | relationship | knowledge


class TimelineEvent(BaseModel):
    when: str
    event: str
    scene_id: str = ""


class Canon(BaseModel):
    facts: list[Fact] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    chekhov: list[dict[str, str]] = Field(default_factory=list)


class SceneBeatPlan(BaseModel):
    beat_id: str = ""
    goal: str
    conflict: str
    characters: list[str] = Field(default_factory=list)
    location: str = ""
    time: str = ""
    must_include: list[str] = Field(default_factory=list)
    must_not: list[str] = Field(default_factory=list)
    emotional_turn: str = ""


class Scene(BaseModel):
    id: str
    title: str
    plan: Optional[SceneBeatPlan] = None
    content: str
    summary: str = ""
    status: str = "draft"  # draft | approved | rejected


class GuardIssue(BaseModel):
    agent: str
    severity: str  # blocker | major | minor
    character_id: str = ""
    detail: str
    suggestion: str = ""


class GuardReport(BaseModel):
    passed: bool
    score: float = 0.0
    issues: list[GuardIssue] = Field(default_factory=list)
    notes: str = ""


class WorkflowResult(BaseModel):
    scene: Scene
    plan: SceneBeatPlan
    persona: GuardReport
    continuity: GuardReport
    rewrite_rounds: int = 0
    extracted: dict[str, Any] = Field(default_factory=dict)
    auto_saved: bool = False
