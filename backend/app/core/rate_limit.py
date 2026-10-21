"""Rate limiter (slowapi) para endpoints sensibles a fuerza bruta (auth).

Almacenamiento en memoria por proceso: correcto para una sola instancia (plan
free de Render, ver render.yaml). Si en el futuro se escala a 2+ instancias
horizontalmente, cada una llevaria su propio contador -- para un limite global
real haria falta un backend compartido (ej. Redis, via `storage_uri`).
"""
from __future__ import annotations

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_real_client_ip(request: Request) -> str:
    """`request.client.host` es el hop TCP inmediato -- detras de cualquier
    proxy/edge (Render/Cloudflare, Railway, etc.) no es la IP real del cliente
    y varia entre requests (verificado: el limite nunca se acumulaba de forma
    confiable en prod).

    OJO: `X-Forwarded-For` NO es una alternativa segura -- es un header que
    el propio cliente puede mandar directamente (verificado con
    `curl -H "X-Forwarded-For: ..."`), y sin saber cuantos proxies confiables
    hay por delante no se puede distinguir el valor real del inventado por un
    atacante para saltarse el limite (hallazgo real de una revision de
    seguridad sobre un intento anterior de este fix).

    Dos headers si son confiables, cada uno fijado por el borde de su propia
    plataforma de despliegue (no por el cliente, no reenviable a traves del
    edge publico):
      - `CF-Connecting-IP`: Render enruta todo el trafico via Cloudflare
        (confirmado por `Server: cloudflare` / `CF-RAY` en las respuestas).
      - `X-Real-IP`: Railway sobrescribe este header en su edge publico con
        la IP real del cliente -- un caller no puede falsificarlo mandando
        una copia propia a traves del edge publico (confirmado con el staff
        de Railway, ver station.railway.com). OJO: esto aplica solo al
        trafico que entra por el dominio publico; en *.railway.internal
        (servicio a servicio) el header no se sanitiza.

    Se prueba primero CF-Connecting-IP (mas especifico/antiguo en este
    proyecto) y despues X-Real-IP, para que el mismo codigo funcione sin
    cambios sin importar en cual de las dos plataformas corra. Si ninguno
    esta presente (dev local sin proxy delante), se cae a
    `request.client.host` (el peer TCP directo, nunca un header manipulable)
    en vez de a X-Forwarded-For.
    """
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    railway_ip = request.headers.get("x-real-ip")
    if railway_ip:
        return railway_ip.strip()
    return get_remote_address(request)


def get_login_identity_key(request: Request) -> str:
    """Clave por cuenta (email normalizado) para el limite de fuerza bruta de
    login -- independiente de la IP de origen.

    Un limite solo por IP (ver `get_real_client_ip`) castiga a cualquier grupo
    de usuarios legitimos detras del mismo NAT (aula, oficina, red de un
    evento): comparten un unico balde, asi que el intento N+1 de CUALQUIERA de
    ellos devuelve 429, sin importar que sean cuentas distintas (hallazgo real:
    30 alumnos en la misma red agotaban el limite de 5/min en el 6to login,
    sin importar quien lo hiciera).

    El valor real de proteccion contra fuerza bruta es "cuantos intentos puede
    hacer alguien contra UNA cuenta", no "cuantos intentos salen de una IP" --
    eso es lo que este key_func mide. Se combina en las rutas con un limite
    por IP bastante mas generoso (`get_real_client_ip`), que sigue frenando
    abuso puramente volumetrico (ej. un bot probando miles de emails al azar
    desde una sola maquina) sin penalizar a usuarios legitimos compartiendo
    red.

    El email se lee de `request.state.login_identity`, fijado por una
    dependencia de FastAPI (`_capture_login_identity` en auth.py) que corre
    como parte de la resolucion de dependencias de la request -- siempre
    antes de que slowapi evalue los limites de la ruta, sin importar el orden
    de los parametros en la firma del endpoint. Si por algun motivo no esta
    disponible (nunca deberia pasar en el endpoint real), cae al limite por
    IP para no dejar la ruta sin proteccion.
    """
    identity = getattr(request.state, "login_identity", None)
    if identity:
        return f"login:{identity}"
    return get_real_client_ip(request)


limiter = Limiter(key_func=get_real_client_ip)
