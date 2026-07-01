"""Endpoints de proyectos (CRUD por usuario) y catalogo de experimentos."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.catalog.service import load_catalog
from app.db.models import Project, User
from app.db.session import get_db
from app.schemas.api import ProjectCreate, ProjectOut

router = APIRouter(tags=["projects"])


@router.get("/experiments")
def list_experiments():
    """Catalogo publico de los 44 experimentos (para la UI de referencia)."""
    return [e.model_dump(mode="json") for e in load_catalog()]


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = Project(
        user_id=user.id,
        name=data.name,
        raw_idea=data.raw_idea,
        constraints=data.constraints.model_dump(mode="json"),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Project).where(Project.user_id == user.id)).all()
    return list(rows)


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    project = db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    project = db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.delete(project)
    db.commit()
