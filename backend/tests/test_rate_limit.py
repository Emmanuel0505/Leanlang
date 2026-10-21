"""Tests de `get_real_client_ip`: identificar al cliente real detras del edge
de cada plataforma de despliegue sin poder ser falsificado por el propio
cliente (ver app/core/rate_limit.py para el razonamiento completo)."""
from __future__ import annotations

from starlette.requests import Request

from app.core.rate_limit import get_real_client_ip


def _request(headers: dict[str, str], client_host: str = "10.0.0.1") -> Request:
    """Arma un Request de Starlette minimo, sin pasar por un servidor real."""
    encoded_headers = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    scope = {
        "type": "http",
        "headers": encoded_headers,
        "client": (client_host, 12345),
    }
    return Request(scope)


def test_prefers_cf_connecting_ip_when_present():
    req = _request({"cf-connecting-ip": "203.0.113.7", "x-real-ip": "198.51.100.9"})
    assert get_real_client_ip(req) == "203.0.113.7"


def test_falls_back_to_x_real_ip_for_railway():
    req = _request({"x-real-ip": "198.51.100.9"})
    assert get_real_client_ip(req) == "198.51.100.9"


def test_ignores_spoofable_x_forwarded_for():
    """X-Forwarded-For lo puede mandar el propio cliente (ver docstring de
    get_real_client_ip) -- nunca debe usarse como fuente de la IP real."""
    req = _request({"x-forwarded-for": "1.2.3.4"}, client_host="10.0.0.1")
    assert get_real_client_ip(req) == "10.0.0.1"


def test_falls_back_to_tcp_peer_without_any_proxy_header():
    req = _request({}, client_host="10.0.0.1")
    assert get_real_client_ip(req) == "10.0.0.1"


def test_strips_whitespace_from_header_value():
    req = _request({"x-real-ip": "  198.51.100.9  "})
    assert get_real_client_ip(req) == "198.51.100.9"
