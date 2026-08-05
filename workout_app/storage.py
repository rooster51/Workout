from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(".workout_data")

DEFAULT_SETTINGS = {"equipment":["No equipment"],"duration":30,"difficulty":"Beginner","low_impact":False,"favorites":[],"disabled":[]}

def _read(name: str, fallback):
    path = DATA_DIR / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, type(fallback)) else fallback
    except (OSError, ValueError, TypeError):
        return fallback

def _write(name: str, value) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    target = DATA_DIR / name
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(target)

def load_settings(): return {**DEFAULT_SETTINGS, **_read("settings.json", {})}
def save_settings(value): _write("settings.json", value)
def load_history(): return _read("history.json", [])
def save_history(value): _write("history.json", value)
def load_programs(): return _read("programs.json", [])
def save_programs(value): _write("programs.json", value)
