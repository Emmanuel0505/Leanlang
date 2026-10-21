"""Endpoints de autenticacion: registro y login (JWT)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, verify_password
from app.core.rate_limit import get_login_identity_key, limiter
from app.db.models import User
from app.db.session import get_db
from app.schemas.api import Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _capture_login_identity(
    request: Request, form: OAuth2PasswordRequestForm = Depends()
) -> OAuth2PasswordRequestForm:
    """Guarda el email (normalizado) en `request.state` para que el limite
    por cuenta de `login` (ver `get_login_identity_key`) pueda leerlo.

    FastAPI resuelve esta dependencia como parte de la resolucion de
    dependencias de la request, que siempre corre antes de invocar al
    endpoint -- y por lo tanto antes de que el decorador `@limiter.limit`
    evalue los limites (el decorador envuelve la funcion del endpoint en si,
    que FastAPI llama solo una vez resueltas todas sus dependencias).
    """
    request.state.login_identity = form.username.strip().lower()
    return form


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
# Solo por IP: cada registro es (por definicion) un email nuevo, no hay una
# "cuenta" previa que proteger de fuerza bruta aqui. El riesgo es volumetrico
# (spam de cuentas), no de credenciales -- de ahi un limite mas generoso que
# el de login, pensado para no bloquear una rafaga legitima de registros
# simultaneos desde la misma red (ej. 30 alumnos registrandose en la demo).
@limiter.limit("40/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == data.email))
    if exists:
        raise HTTPException(status_code=400, detail="El email ya esta registrado")
    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
# Dos limites independientes (ver get_login_identity_key para el razonamiento
# completo): uno generoso por IP -- solo frena abuso volumetrico puro, no
# penaliza a usuarios legitimos detras del mismo NAT -- y uno ajustado por
# cuenta, que es la proteccion real contra fuerza bruta de una contrasena.
@limiter.limit("30/minute")
@limiter.limit("5/minute", key_func=get_login_identity_key)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(_capture_login_identity),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contrasena incorrectos")
    return Token(access_token=create_access_token(user.id))
