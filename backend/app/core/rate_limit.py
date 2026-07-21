"""Rate limiter (slowapi) para endpoints sensibles a fuerza bruta (auth).

Almacenamiento en memoria por proceso: correcto para una sola instancia (plan
free de Render, ver render.yaml). Si en el futuro se escala a 2+ instancias
horizontalmente, cada una llevaria su propio contador -- para un limite global
real haria falta un backend compartido (ej. Redis, via `storage_uri`).
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
