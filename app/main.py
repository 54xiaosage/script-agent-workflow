from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import STATIC_DIR
from app.llm import LLMError
from app.models import Character, Plot, ProjectMeta
from app import store
from app.workflow import run_next_scene

app = FastAPI(title="剧本智能体工作流", version="0.1.0")
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")


class NewProjectIn(BaseModel):
    title: str
    logline: str = ""
    genre: str = "都市剧"


class GenerateIn(BaseModel):
    extra_instruction: str = ""
    auto_save: bool = True


class CharacterIn(Character):
    pass


class PlotIn(Plot):
    pass


class MetaPatch(BaseModel):
    title: Optional[str] = None
    logline: Optional[str] = None
    genre: Optional[str] = None
    tone: Optional[str] = None
    theme: Optional[str] = None


class ApproveIn(BaseModel):
    status: str = Field(default="approved")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/projects")
def api_projects():
    return [p.model_dump() for p in store.list_projects()]


@app.post("/api/projects")
def api_create_project(body: NewProjectIn):
    return store.create_project(body.title, body.logline, body.genre).model_dump()


@app.get("/api/projects/{slug}")
def api_project(slug: str):
    try:
        return store.dump_project(slug)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(404, str(e)) from e


@app.patch("/api/projects/{slug}/meta")
def api_patch_meta(slug: str, body: MetaPatch):
    meta = store.load_meta(slug)
    data = meta.model_dump()
    for k, v in body.model_dump(exclude_none=True).items():
        data[k] = v
    meta = ProjectMeta.model_validate(data)
    store.save_meta(meta)
    return meta.model_dump()


@app.put("/api/projects/{slug}/characters")
def api_put_characters(slug: str, body: list[CharacterIn]):
    existing = {c.id: c for c in store.load_characters(slug)}
    chars: list[Character] = []
    for item in body:
        data = item.model_dump()
        old = existing.get(data["id"])
        if old:
            if not data.get("capabilities"):
                data["capabilities"] = old.capabilities
            if not data.get("relationships"):
                data["relationships"] = old.relationships
            if not data.get("current_state"):
                data["current_state"] = old.current_state
            new_voice = data.get("voice") or {}
            if not new_voice.get("sample_lines"):
                new_voice["sample_lines"] = old.voice.sample_lines
            if not new_voice.get("vocabulary"):
                new_voice["vocabulary"] = old.voice.vocabulary
            data["voice"] = new_voice
        chars.append(Character.model_validate(data))
    store.save_characters(slug, chars)
    return [c.model_dump() for c in chars]


@app.put("/api/projects/{slug}/plot")
def api_put_plot(slug: str, body: PlotIn):
    plot = Plot.model_validate(body.model_dump())
    store.save_plot(slug, plot)
    return plot.model_dump()


@app.post("/api/projects/{slug}/generate")
def api_generate(slug: str, body: GenerateIn):
    try:
        result = run_next_scene(slug, extra_instruction=body.extra_instruction, auto_save=body.auto_save)
    except LLMError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, "项目不存在") from e
    return result.model_dump()


@app.post("/api/projects/{slug}/scenes/{scene_id}/status")
def api_scene_status(slug: str, scene_id: str, body: ApproveIn):
    scenes = store.list_scenes(slug)
    for s in scenes:
        if s.id == scene_id:
            s.status = body.status
            store.save_scene(slug, s)
            return s.model_dump()
    raise HTTPException(404, "场次不存在")
