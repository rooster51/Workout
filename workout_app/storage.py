from __future__ import annotations

import json
import hashlib
from pathlib import Path

import streamlit as st

DATA_DIR = Path(".workout_data")

DEFAULT_SETTINGS = {"equipment":["No equipment"],"duration":30,"difficulty":"Beginner","low_impact":False,"favorites":[],"disabled":[]}

def _has_secret(name: str) -> bool:
    try:
        return name in st.secrets
    except Exception:
        return False

def _safe_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:24]

def _firestore():
    if not _has_secret("firebase_service_account"):
        return None
    from google.cloud import firestore
    from google.oauth2 import service_account
    info = dict(st.secrets["firebase_service_account"])
    credentials = service_account.Credentials.from_service_account_info(info)
    return firestore.Client(project=info["project_id"], credentials=credentials)

def cloud_ready() -> bool:
    return _has_secret("firebase_service_account")

def _read(name: str, fallback, user_id: str):
    database = _firestore()
    if database is not None:
        snapshot = database.collection("users").document(user_id).collection("app_data").document(name).get()
        if not snapshot.exists:
            return fallback
        value = snapshot.to_dict().get("value", fallback)
        return value if isinstance(value, type(fallback)) else fallback
    path = DATA_DIR / _safe_user_id(user_id) / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, type(fallback)) else fallback
    except (OSError, ValueError, TypeError):
        return fallback

def _write(name: str, value, user_id: str) -> None:
    database = _firestore()
    if database is not None:
        database.collection("users").document(user_id).collection("app_data").document(name).set({"value": value})
        return
    directory = DATA_DIR / _safe_user_id(user_id)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / name
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(target)

def load_settings(user_id): return {**DEFAULT_SETTINGS, **_read("settings", {}, user_id)}
def save_settings(value, user_id): _write("settings", value, user_id)
def load_history(user_id): return _read("history", [], user_id)
def save_history(value, user_id): _write("history", value, user_id)
def load_programs(user_id): return _read("programs", [], user_id)
def save_programs(value, user_id): _write("programs", value, user_id)
def load_weights(user_id): return _read("weights", [], user_id)
def save_weights(value, user_id): _write("weights", value, user_id)
