"""Export del Blueprint a PDF (principal), Markdown o JSON."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.api.pdf_export import build_blueprint_pdf
from app.auth.security import get_current_user
from app.db.models import Blueprint, Project, User
from app.db.session import get_db

router = APIRouter(tags=["export"])


def _to_markdown(bp: dict) -> str:
    lines: list[str] = ["# Validation Blueprint\n"]

    problem = bp.get("problem") or {}
    segment = bp.get("customer_segment") or {}
    vp = bp.get("value_proposition") or {}
    if problem or segment or vp:
        lines.append("## Lienzo\n")
        if problem.get("statement"):
            lines.append(f"- **Problema:** {problem['statement']}")
        if segment.get("name"):
            lines.append(f"- **Segmento:** {segment['name']} — {segment.get('description', '')}")
        if vp.get("statement"):
            lines.append(f"- **Propuesta de valor:** {vp['statement']}")
        lines.append("")

    bm = bp.get("business_model") or {}
    if any(bm.get(k) for k in ("revenue_streams", "channels", "key_activities")):
        lines.append("## Modelo de negocio (BMC)\n")
        for k, label in [("channels", "Canales"), ("customer_relationships", "Relación"), ("revenue_streams", "Ingresos"),
                         ("key_resources", "Recursos"), ("key_activities", "Actividades"), ("key_partners", "Socios"), ("cost_structure", "Costos")]:
            if bm.get(k):
                lines.append(f"- **{label}:** {', '.join(bm[k])}")
        lines.append("")

    hyps = {h["id"]: h for h in bp.get("hypotheses", [])}
    cls = {c["hypothesis_id"]: c for c in bp.get("classifications", [])}
    prio = {p["hypothesis_id"]: p for p in bp.get("prioritization", [])}

    lines.append("## Hipotesis y priorizacion\n")
    lines.append("| ID | Hipotesis | Riesgo | Importancia | Evidencia | Riesgosa |")
    lines.append("|----|-----------|--------|-------------|-----------|----------|")
    for hid, h in hyps.items():
        c = cls.get(hid, {})
        p = prio.get(hid, {})
        lines.append(
            f"| {hid} | {h['statement']} | {c.get('risk_type','-')} | "
            f"{p.get('importance','-')} | {p.get('evidence','-')} | "
            f"{'SI' if p.get('is_riskiest') else ''} |"
        )

    research = bp.get("research") or {}
    if research and research.get("status") not in (None, "failed", "empty"):
        lines.append("\n## Investigacion (evidencia externa)\n")
        if research.get("confidence"):
            lines.append(f"- **Confianza:** {research['confidence']}")
        if research.get("market_summary"):
            lines.append(f"- **Resumen de mercado:** {research['market_summary']}")
        if research.get("queries"):
            lines.append(f"- **Consultas realizadas:** {', '.join(research['queries'])}")
        if research.get("competitors"):
            lines.append("- **Competidores:** " + "; ".join(
                f"{c.get('name', '')} — {c.get('description', '')}".strip(" —") for c in research["competitors"]
            ))

    lines.append("\n## Experimentos disenados\n")
    for r in sorted(bp.get("recommendations", []), key=lambda x: x.get("sequence_order", 99)):
        lines.append(
            f"- **{r['sequence_order']}. {r['experiment_name']}** "
            f"({r['stage']}, evidencia {r['expected_evidence_strength']}/5, costo {r['cost']}/5) "
            f"-> hipotesis {r['hypothesis_id']}\n  {r['rationale']}"
        )
        if r.get("design_detail"):
            lines.append(f"  - _Diseno:_ {r['design_detail']}")

    lines.append("\n## Test Cards\n")
    for tc in bp.get("test_cards", []):
        lines.append(
            f"### {tc['experiment_id']} (hipotesis {tc['hypothesis_id']})\n"
            f"- **Creemos que:** {tc['hypothesis_statement']}\n"
            f"- **Para verificarlo:** {tc['test_description']}\n"
            f"- **Y mediremos:** {tc['metric']}\n"
            f"- **Acertamos si:** {tc['success_criteria']}\n"
            f"- Evidencia esperada: {tc['expected_evidence_strength']}/5 | "
            f"Costo: {tc['cost']}/5 | Duracion: {tc['duration_estimate']}\n"
        )

    plan = bp.get("plan_estimate") or {}
    if plan:
        lines.append("\n## Plan estimado\n")
        lines.append(
            f"- Experimentos: {plan.get('experiment_count', '-')} | "
            f"Costo total: {plan.get('total_cost_points', '-')} | "
            f"Esfuerzo total: {plan.get('total_effort_points', '-')} | "
            f"Costo max.: {plan.get('max_cost', '-')}"
        )
        if plan.get("required_capabilities"):
            lines.append(f"- **Capacidades requeridas:** {', '.join(plan['required_capabilities'])}")
        for warn in plan.get("warnings", []):
            lines.append(f"- ⚠️ {warn}")

    review = bp.get("critic_review")
    if review:
        lines.append("\n## Revision del Critico\n")
        lines.append(f"**Calidad:** {review.get('quality_score')} | **Aprobado:** {review.get('passed')}\n")
        lines.append(review.get("summary", ""))
        for issue in review.get("issues", []):
            lines.append(f"- [{issue['severity']}] {issue['pitfall']}: {issue['detail']} -> {issue['suggestion']}")

    roadmap = bp.get("validation_roadmap") or {}
    if roadmap.get("phases"):
        lines.append("\n## Roadmap de validación\n")
        for i, ph in enumerate(roadmap["phases"], 1):
            lines.append(f"{i}. **{ph.get('name','')}** ({ph.get('stage','')}, {ph.get('duration_estimate','')}) — {ph.get('goal','')}")

    decisions = bp.get("decisions") or []
    if decisions:
        lines.append("\n## Reglas de decisión (Learning Cards)\n")
        for d in decisions:
            lines.append(
                f"- **{d['hypothesis_id']} / {d['experiment_id']}** → _{d.get('recommended_decision','')}_\n"
                f"  - Si se valida: {d.get('if_validated','')}\n"
                f"  - Si no: {d.get('if_invalidated','')}"
            )

    report = bp.get("report")
    if report:
        lines.append("\n## Informe consolidado\n")
        lines.append(report.get("executive_summary", ""))
        if report.get("success_definition"):
            lines.append(f"\n**Validacion exitosa si:** {report['success_definition']}")
        if report.get("recommended_sequence"):
            lines.append("\n**Secuencia recomendada:**")
            for i, exp in enumerate(report["recommended_sequence"], 1):
                lines.append(f"{i}. {exp}")
        if report.get("next_steps"):
            lines.append("\n**Proximos pasos:**")
            for step in report["next_steps"]:
                lines.append(f"- {step}")

    return "\n".join(lines)


def _safe_filename(name: str) -> str:
    """Nombre de archivo seguro (ASCII, sin espacios) para el header
    Content-Disposition -- evita problemas con acentos/caracteres especiales
    del nombre del proyecto en distintos navegadores."""
    cleaned = "".join(c if c.isalnum() else "-" for c in (name or "blueprint"))
    cleaned = "-".join(filter(None, cleaned.split("-"))) or "blueprint"
    return cleaned[:60]


@router.get("/blueprint/{blueprint_id}/export")
def export_blueprint(
    blueprint_id: str,
    format: str = "pdf",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bp = db.get(Blueprint, blueprint_id)
    if not bp:
        raise HTTPException(status_code=404, detail="Blueprint no encontrado")
    project = db.get(Project, bp.project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Blueprint no encontrado")

    if format == "json":
        return PlainTextResponse(
            json.dumps(bp.state, ensure_ascii=False, indent=2), media_type="application/json"
        )
    if format == "md":
        return PlainTextResponse(_to_markdown(bp.state or {}), media_type="text/markdown")

    # PDF: formato principal de exportacion (incluye TODO el contenido del
    # proyecto -- lienzo, BMC, hipotesis, investigacion, experimentos, test
    # cards, plan, critico, roadmap, decisiones e informe -- ver pdf_export.py).
    pdf_bytes = build_blueprint_pdf(
        bp.state or {}, project_name=project.name, raw_idea=project.raw_idea
    )
    filename = f"blueprint-{_safe_filename(project.name)}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
