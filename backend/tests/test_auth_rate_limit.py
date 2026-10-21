"""Tests del rate limit de /auth/login: el limite por cuenta protege contra
fuerza bruta sin bloquear a usuarios legitimos que comparten IP (ver
app/core/rate_limit.py:get_login_identity_key para el razonamiento completo
-- hallazgo real: 30 alumnos en la misma red agotaban el limite de 5/min en
el 6to login de CUALQUIERA de ellos, sin importar la cuenta)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_exhausting_one_account_does_not_block_a_different_account_same_ip():
    with TestClient(app) as client:
        victim = {"username": "rl-victim@example.com", "password": "wrong-password"}

        # 5 intentos fallidos sobre la MISMA cuenta: todavia dentro del limite
        # por cuenta (5/minuto), asi que cada uno devuelve 401 (credenciales
        # invalidas -- la cuenta ni siquiera existe), no 429.
        for _ in range(5):
            r = client.post("/auth/login", data=victim)
            assert r.status_code == 401, r.text

        # 6to intento sobre la MISMA cuenta: el limite por cuenta lo bloquea.
        r = client.post("/auth/login", data=victim)
        assert r.status_code == 429, r.text

        # Una cuenta DISTINTA, mismo IP (TestClient usa siempre el mismo peer):
        # el bloqueo de arriba fue por cuenta, no por IP, asi que esta sigue
        # funcionando -- es exactamente el escenario de 30 usuarios en la
        # misma red que motivo este fix.
        other = {"username": "rl-bystander@example.com", "password": "wrong-password"}
        r = client.post("/auth/login", data=other)
        assert r.status_code == 401, r.text


def test_register_allows_a_burst_from_the_same_ip():
    """Rafaga de registros legitimos desde la misma red (ej. una demo con
    varios alumnos registrandose a la vez) no debe toparse con el limite de
    IP de /auth/register (40/minuto) con solo un puñado de registros."""
    with TestClient(app) as client:
        for i in range(8):
            r = client.post(
                "/auth/register",
                json={"email": f"rl-burst-{i}@example.com", "password": "password123"},
            )
            assert r.status_code == 201, r.text
