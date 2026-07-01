"""Tests unitarios para build_run_config() en app/core/observability.py."""
from __future__ import annotations

import pytest

THREAD_ID = "bp-test-123"
COMMON = dict(user_id="u1", project_id="p1", blueprint_id="bp1")


@pytest.fixture(autouse=True)
def enable_tracing(monkeypatch):
    """Activa tracing en todos los tests de este módulo."""
    import app.core.observability as obs
    monkeypatch.setattr(obs, "tracing_enabled", lambda: True)


def build(**kwargs):
    from app.core.observability import build_run_config
    return build_run_config(THREAD_ID, **{**COMMON, **kwargs})


# --- run_name ---

def test_run_name_full_run():
    cfg = build(phase="full_run")
    assert cfg["run_name"] == "validation_blueprint/full_run"


def test_run_name_resume_human_hypotheses():
    cfg = build(phase="resume:human_hypotheses")
    assert cfg["run_name"] == "validation_blueprint/resume:human_hypotheses"


def test_run_name_resume_human_prioritization():
    cfg = build(phase="resume:human_prioritization")
    assert cfg["run_name"] == "validation_blueprint/resume:human_prioritization"


def test_run_name_resume_human_approval():
    cfg = build(phase="resume:human_approval")
    assert cfg["run_name"] == "validation_blueprint/resume:human_approval"


def test_run_name_fallback_when_phase_none():
    cfg = build(phase=None)
    assert cfg["run_name"] == "validation_blueprint"


def test_run_name_fallback_when_phase_empty_string():
    cfg = build(phase="")
    assert cfg["run_name"] == "validation_blueprint"


def test_run_name_fallback_when_phase_whitespace_only():
    cfg = build(phase="   ")
    assert cfg["run_name"] == "validation_blueprint"


# --- configurable.thread_id ---

def test_thread_id_unchanged_with_phase():
    cfg = build(phase="full_run")
    assert cfg["configurable"]["thread_id"] == THREAD_ID


def test_thread_id_unchanged_without_phase():
    cfg = build(phase=None)
    assert cfg["configurable"]["thread_id"] == THREAD_ID


def test_thread_id_unchanged_on_resume():
    cfg = build(phase="resume:human_hypotheses")
    assert cfg["configurable"]["thread_id"] == THREAD_ID


# --- metadata.phase_name usa phase_clean ---

def test_metadata_phase_name_stripped():
    cfg = build(phase="  full_run  ")
    assert cfg["metadata"]["phase_name"] == "full_run"
    assert cfg["run_name"] == "validation_blueprint/full_run"


def test_metadata_phase_name_absent_when_no_phase():
    cfg = build(phase=None)
    assert "phase_name" not in cfg["metadata"]


def test_metadata_phase_name_absent_when_empty():
    cfg = build(phase="")
    assert "phase_name" not in cfg["metadata"]


# --- metadata: campos obligatorios siempre presentes ---

def test_metadata_core_fields_present():
    cfg = build(phase="full_run")
    meta = cfg["metadata"]
    for key in ("session_id", "user_id", "project_id", "blueprint_id", "environment", "graph_name"):
        assert key in meta, f"falta {key} en metadata"


def test_metadata_session_id_equals_thread_id():
    cfg = build(phase="full_run")
    assert cfg["metadata"]["session_id"] == THREAD_ID


# --- tags ---

def test_tags_include_phase_tag_when_phase_given():
    cfg = build(phase="full_run")
    assert "phase:full_run" in cfg["tags"]


def test_tags_no_phase_tag_when_phase_none():
    cfg = build(phase=None)
    assert not any(t.startswith("phase:") for t in cfg["tags"])


def test_tags_no_phase_tag_when_phase_empty():
    cfg = build(phase="")
    assert not any(t.startswith("phase:") for t in cfg["tags"])


# --- tags: project, blueprint, resume, full_run ---

def test_tags_full_run_flag_present():
    cfg = build(phase="full_run")
    assert "full_run" in cfg["tags"]


def test_tags_full_run_no_resume_flag():
    cfg = build(phase="full_run")
    assert "resume" not in cfg["tags"]


def test_tags_resume_phase_includes_resume_and_phase_tag():
    cfg = build(phase="resume:approval")
    assert "resume" in cfg["tags"]
    assert "phase:resume:approval" in cfg["tags"]


def test_tags_include_project_id():
    cfg = build(phase="full_run")
    assert "project:p1" in cfg["tags"]


def test_tags_include_blueprint_id():
    cfg = build(phase="full_run")
    assert "blueprint:bp1" in cfg["tags"]


def test_tags_no_duplicates():
    cfg = build(phase="full_run")
    assert len(cfg["tags"]) == len(set(cfg["tags"]))


def test_tags_empty_phase_no_phase_resume_full_run_tags():
    cfg = build(phase="")
    tags = cfg["tags"]
    assert not any(t.startswith("phase:") for t in tags)
    assert "resume" not in tags
    assert "full_run" not in tags


# --- metadata: campos LLM ---

def test_metadata_llm_fields_present():
    cfg = build(phase="full_run")
    meta = cfg["metadata"]
    for key in ("llm_provider", "llm_model", "llm_temperature", "llm_version"):
        assert key in meta, f"falta {key} en metadata"


def test_metadata_llm_fields_match_settings():
    from app.core.config import settings
    cfg = build(phase="full_run")
    meta = cfg["metadata"]
    assert meta["llm_provider"] == settings.llm_provider
    assert meta["llm_model"] == settings.llm_model
    assert meta["llm_temperature"] == settings.llm_temperature
    assert meta["llm_version"] == settings.llm_version


# --- tracing desactivado: config mínimo ---

def test_tracing_off_returns_minimal_config(monkeypatch):
    import app.core.observability as obs
    monkeypatch.setattr(obs, "tracing_enabled", lambda: False)
    from app.core.observability import build_run_config
    cfg = build_run_config(THREAD_ID, **COMMON, phase="full_run")
    assert cfg == {"configurable": {"thread_id": THREAD_ID}}
    assert "run_name" not in cfg
    assert "metadata" not in cfg
    assert "tags" not in cfg
