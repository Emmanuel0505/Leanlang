"""Tests de /blueprint/{id}/export: PDF (formato principal), markdown y json.
Crea el usuario/proyecto/blueprint directo en la DB (como test_shadow_read.py)
para no depender de un LLM real ni del flujo completo del grafo."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.auth.security import create_access_token
from app.db.models import Blueprint, Project, User
from app.db.session import SessionLocal
from app.main import app

_STATE = {
    "constraints": {"budget_level": "low", "time_horizon": "weeks", "stage": "discovery"},
    "problem": {"statement": "Los padres no encuentran tiempo.", "context": "ctx", "pains": ["sin tiempo"]},
    "customer_segment": {"name": "Padres", "description": "desc"},
    "value_proposition": {"statement": "Kits mensuales", "differentiator": "vs. hacerlo a mano"},
    "hypotheses": [{"id": "h1", "statement": "Creemos que X"}],
    "classifications": [{"hypothesis_id": "h1", "risk_type": "desirability"}],
    "prioritization": [{"hypothesis_id": "h1", "importance": 0.9, "evidence": 0.1, "is_riskiest": True}],
    "research": {"status": "completed", "confidence": "Media", "queries": ["competidores de X"]},
    "recommendations": [{
        "sequence_order": 1, "experiment_name": "Pico de experiencia", "experiment_id": "xp-spike",
        "stage": "discovery", "expected_evidence_strength": 3, "cost": 1, "hypothesis_id": "h1",
        "rationale": "barato y rapido",
    }],
    "test_cards": [{
        "experiment_name": "Pico de experiencia", "experiment_id": "xp-spike", "hypothesis_id": "h1",
        "hypothesis_statement": "Creemos que X", "test_description": "test", "metric": "CTR",
        "success_criteria": ">= 5%", "expected_evidence_strength": 3, "cost": 1,
        "duration_estimate": "1-2 semanas",
    }],
    "critic_review": {"quality_score": 0.8, "passed": True, "summary": "solido", "issues": []},
    "report": {"executive_summary": "resumen"},
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _make_project_and_blueprint(name: str = "Kits de ciencia"):
    with SessionLocal() as db:
        user = User(email=f"export-{uuid.uuid4().hex[:8]}@test.com", hashed_password="x")
        db.add(user)
        db.commit()
        db.refresh(user)
        project = Project(user_id=user.id, name=name, raw_idea="idea de prueba", constraints={})
        db.add(project)
        db.commit()
        db.refresh(project)
        bp = Blueprint(project_id=project.id, thread_id="t1", status="done", state=_STATE)
        db.add(bp)
        db.commit()
        db.refresh(bp)
        token = create_access_token(user.id)
        return project, bp, token


def test_export_default_format_is_pdf(client):
    _, bp, token = _make_project_and_blueprint()
    r = client.get(f"/blueprint/{bp.id}/export", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"
    assert "attachment" in r.headers["content-disposition"]


def test_export_pdf_explicit_includes_real_content(client):
    _, bp, token = _make_project_and_blueprint(name="Mi Proyecto Especial")
    r = client.get(f"/blueprint/{bp.id}/export?format=pdf", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"
    assert len(r.content) > 1000  # no es un PDF vacio: tiene secciones reales
    assert "Mi-Proyecto-Especial" in r.headers["content-disposition"]


def test_export_md_still_available(client):
    _, bp, token = _make_project_and_blueprint()
    r = client.get(f"/blueprint/{bp.id}/export?format=md", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/markdown")
    assert "Pico de experiencia" in r.text  # experiment_name, no el id crudo
    assert "Investigacion" in r.text or "Investigación" in r.text


def test_export_json_still_available(client):
    _, bp, token = _make_project_and_blueprint()
    r = client.get(f"/blueprint/{bp.id}/export?format=json", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"
    assert "xp-spike" in r.text


def test_export_rejects_other_users_blueprint(client):
    _, bp, _ = _make_project_and_blueprint()
    _, _, other_token = _make_project_and_blueprint()
    r = client.get(f"/blueprint/{bp.id}/export", headers={"Authorization": f"Bearer {other_token}"})
    assert r.status_code == 404
