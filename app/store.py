from __future__ import annotations

import json
import re
from pathlib import Path

from app.config import DATA_DIR
from app.models import Canon, Character, Plot, ProjectMeta, Scene


def _slugify(name: str) -> str:
    slug = re.sub(r"[^\w\-]+", "-", name.strip(), flags=re.UNICODE).strip("-").lower()
    return slug or "untitled"


def project_dir(slug: str) -> Path:
    return DATA_DIR / slug


def _read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_projects() -> list[ProjectMeta]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for d in sorted(DATA_DIR.iterdir()):
        meta = d / "project.json"
        if meta.exists():
            items.append(ProjectMeta.model_validate(_read_json(meta, {})))
    return items


def create_project(title: str, logline: str = "", genre: str = "都市剧") -> ProjectMeta:
    slug = _slugify(title)
    base = project_dir(slug)
    n = 1
    while (base / "project.json").exists():
        n += 1
        slug = f"{_slugify(title)}-{n}"
        base = project_dir(slug)
    meta = ProjectMeta(slug=slug, title=title, logline=logline, genre=genre)
    save_meta(meta)
    save_characters(slug, [])
    save_plot(slug, Plot())
    save_canon(slug, Canon())
    (base / "scenes").mkdir(exist_ok=True)
    return meta


def load_meta(slug: str) -> ProjectMeta:
    return ProjectMeta.model_validate(_read_json(project_dir(slug) / "project.json", {}))


def save_meta(meta: ProjectMeta) -> None:
    _write_json(project_dir(meta.slug) / "project.json", meta.model_dump())


def load_characters(slug: str) -> list[Character]:
    raw = _read_json(project_dir(slug) / "characters.json", [])
    return [Character.model_validate(x) for x in raw]


def save_characters(slug: str, characters: list[Character]) -> None:
    _write_json(project_dir(slug) / "characters.json", [c.model_dump() for c in characters])


def upsert_character(slug: str, character: Character) -> list[Character]:
    chars = load_characters(slug)
    by_id = {c.id: c for c in chars}
    by_id[character.id] = character
    out = list(by_id.values())
    save_characters(slug, out)
    return out


def load_plot(slug: str) -> Plot:
    return Plot.model_validate(_read_json(project_dir(slug) / "plot.json", {}))


def save_plot(slug: str, plot: Plot) -> None:
    _write_json(project_dir(slug) / "plot.json", plot.model_dump())


def load_canon(slug: str) -> Canon:
    return Canon.model_validate(_read_json(project_dir(slug) / "canon.json", {}))


def save_canon(slug: str, canon: Canon) -> None:
    _write_json(project_dir(slug) / "canon.json", canon.model_dump())


def list_scenes(slug: str) -> list[Scene]:
    folder = project_dir(slug) / "scenes"
    folder.mkdir(parents=True, exist_ok=True)
    scenes = []
    for p in sorted(folder.glob("*.json")):
        scenes.append(Scene.model_validate(_read_json(p, {})))
    return scenes


def save_scene(slug: str, scene: Scene) -> None:
    folder = project_dir(slug) / "scenes"
    folder.mkdir(parents=True, exist_ok=True)
    _write_json(folder / f"{scene.id}.json", scene.model_dump())


def next_scene_id(slug: str) -> str:
    existing = list_scenes(slug)
    return f"S{len(existing) + 1:03d}"


def dump_project(slug: str) -> dict:
    return {
        "meta": load_meta(slug).model_dump(),
        "characters": [c.model_dump() for c in load_characters(slug)],
        "plot": load_plot(slug).model_dump(),
        "canon": load_canon(slug).model_dump(),
        "scenes": [s.model_dump() for s in list_scenes(slug)],
    }
