"""Export del Blueprint a PDF -- reportlab (Platypus), sin dependencias de
sistema (a diferencia de WeasyPrint/wkhtmltopdf, que necesitan librerias
nativas tipo Pango/Cairo): funciona igual en dev local (Windows) y en el
contenedor Docker de produccion sin instalar nada extra.

Cubre el mismo contenido que `_to_markdown` (export.py) mas lo que esa
version dejaba afuera (Investigacion, Plan de estimacion) -- el objetivo es
que el PDF sea la exportacion completa del proyecto, no un resumen.
"""
from __future__ import annotations

import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Paleta: azul "blueprint" (identidad de la app) + grises neutros para texto.
_INK = colors.HexColor("#0f172a")
_BLUEPRINT = colors.HexColor("#1d4ed8")
_BLUEPRINT_SOFT = colors.HexColor("#eef2ff")
_MUTED = colors.HexColor("#475569")
_LINE = colors.HexColor("#cbd5e1")
_DANGER = colors.HexColor("#b91c1c")
_OK = colors.HexColor("#15803d")


def _esc(value) -> str:
    """Escapa texto para el mini-XML de Paragraph de reportlab.

    El contenido viene de un LLM: puede traer '<', '>' o '&' sueltos (ej. una
    metrica como "ROI < 20%") que romperian el parser de Paragraph si no se
    escapan. `None`/no-string se normalizan a "".
    """
    if value is None:
        return ""
    return escape(str(value))


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontSize=26, leading=30,
            textColor=_INK, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"], fontSize=13, leading=18,
            textColor=_BLUEPRINT, alignment=TA_CENTER, spaceAfter=4,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", parent=base["Normal"], fontSize=10, leading=14,
            textColor=_MUTED, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontSize=16, leading=20,
            textColor=_INK, spaceBefore=4, spaceAfter=10,
            borderWidth=0, borderPadding=0,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontSize=12.5, leading=16,
            textColor=_BLUEPRINT, spaceBefore=12, spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontSize=11, leading=14,
            textColor=_INK, spaceBefore=8, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontSize=9.5, leading=14, textColor=_INK,
        ),
        "muted": ParagraphStyle(
            "muted", parent=base["Normal"], fontSize=9, leading=13, textColor=_MUTED,
        ),
        "label": ParagraphStyle(
            "label", parent=base["Normal"], fontSize=8.5, leading=11,
            textColor=_BLUEPRINT, spaceAfter=1,
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"], fontSize=8.5, leading=11.5, textColor=_INK,
        ),
    }


def _section_header(title: str, s: dict) -> Table:
    """Encabezado de seccion con una franja de color -- da estructura visual
    clara al recorrer el PDF (equivalente a los paneles con color de la UI)."""
    t = Table([[Paragraph(_esc(title), s["h1"])]], colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BLUEPRINT_SOFT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, _BLUEPRINT),
    ]))
    return t


def _kv_table(rows: list[tuple[str, str]], s: dict) -> Table | None:
    """Tabla etiqueta/valor de 2 columnas (para bloques tipo 'Problema: ...')."""
    data = [
        [Paragraph(_esc(label), s["label"]), Paragraph(_esc(value), s["cell"])]
        for label, value in rows
        if value
    ]
    if not data:
        return None
    t = Table(data, colWidths=[3.5 * cm, 13.5 * cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, _LINE),
    ]))
    return t


def _bullets(items: list, s: dict, style_key: str = "body"):
    if not items:
        return None
    return ListFlowable(
        [ListItem(Paragraph(_esc(it), s[style_key]), spaceAfter=2) for it in items],
        bulletType="bullet", start="circle", leftIndent=12,
    )


def build_blueprint_pdf(bp: dict, project_name: str = "", raw_idea: str = "") -> bytes:
    """Arma el PDF completo del blueprint. Devuelve los bytes del archivo."""
    s = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        title=f"Validation Blueprint — {project_name}" if project_name else "Validation Blueprint",
    )
    story: list = []

    # ---- Portada ----
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph("Validation Blueprint", s["cover_title"]))
    if project_name:
        story.append(Paragraph(_esc(project_name), s["cover_sub"]))
    if raw_idea:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(_esc(raw_idea), s["cover_meta"]))
    constraints = bp.get("constraints") or {}
    if constraints:
        meta = (
            f"Presupuesto: {constraints.get('budget_level', '-')}  ·  "
            f"Horizonte: {constraints.get('time_horizon', '-')}  ·  "
            f"Etapa: {constraints.get('stage', '-')}"
        )
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(_esc(meta), s["cover_meta"]))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        _esc(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"), s["cover_meta"]
    ))
    story.append(PageBreak())

    # ---- Lienzo (Problema / Segmento / Propuesta de valor) ----
    problem = bp.get("problem") or {}
    segment = bp.get("customer_segment") or {}
    vp = bp.get("value_proposition") or {}
    if problem or segment or vp:
        story.append(_section_header("Lienzo de validación", s))
        if problem:
            story.append(Paragraph("Problema", s["h2"]))
            t = _kv_table([
                ("Problema", problem.get("statement", "")),
                ("Contexto", problem.get("context", "")),
                ("Causas raíz", "; ".join(problem.get("root_causes", []))),
                ("Jobs-to-be-done", "; ".join(problem.get("customer_jobs", []))),
                ("Dolores", "; ".join(problem.get("pains", []))),
            ], s)
            if t:
                story.append(t)
        if segment:
            story.append(Paragraph("Segmento de clientes", s["h2"]))
            t = _kv_table([
                ("Segmento", segment.get("name", "")),
                ("Descripción", segment.get("description", "")),
                ("Características", "; ".join(segment.get("characteristics", []))),
                ("Ganancias buscadas", "; ".join(segment.get("gains", []))),
                ("Early adopters", segment.get("early_adopters", "")),
            ], s)
            if t:
                story.append(t)
        if vp:
            story.append(Paragraph("Propuesta de valor", s["h2"]))
            t = _kv_table([
                ("Propuesta", vp.get("statement", "")),
                ("Productos/servicios", "; ".join(vp.get("products_services", []))),
                ("Aliviadores de dolor", "; ".join(vp.get("pain_relievers", []))),
                ("Creadores de ganancia", "; ".join(vp.get("gain_creators", []))),
                ("Diferenciador", vp.get("differentiator", "")),
            ], s)
            if t:
                story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    # ---- Business Model Canvas ----
    bm = bp.get("business_model") or {}
    if any(bm.get(k) for k in ("revenue_streams", "channels", "key_activities", "key_resources", "key_partners", "cost_structure", "customer_relationships")):
        story.append(_section_header("Modelo de negocio (BMC)", s))
        labels = [
            ("channels", "Canales"), ("customer_relationships", "Relación con el cliente"),
            ("revenue_streams", "Fuentes de ingreso"), ("key_resources", "Recursos clave"),
            ("key_activities", "Actividades clave"), ("key_partners", "Socios clave"),
            ("cost_structure", "Estructura de costos"),
        ]
        t = _kv_table([(label, "; ".join(bm.get(k, []))) for k, label in labels], s)
        if t:
            story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    # ---- Hipotesis + priorizacion ----
    hyps = bp.get("hypotheses") or []
    if hyps:
        story.append(_section_header("Hipótesis y priorización", s))
        cls = {c["hypothesis_id"]: c for c in bp.get("classifications", [])}
        prio = {p["hypothesis_id"]: p for p in bp.get("prioritization", [])}
        header = ["ID", "Hipótesis", "Riesgo", "Importancia", "Evidencia", "Riesgosa"]
        rows = [[Paragraph(f"<b>{h}</b>", s["cell"]) for h in header]]
        for h in hyps:
            hid = h.get("id", "")
            c = cls.get(hid, {})
            p = prio.get(hid, {})
            rows.append([
                Paragraph(_esc(hid), s["cell"]),
                Paragraph(_esc(h.get("statement", "")), s["cell"]),
                Paragraph(_esc(c.get("risk_type", "-")), s["cell"]),
                Paragraph(_esc(p.get("importance", "-")), s["cell"]),
                Paragraph(_esc(p.get("evidence", "-")), s["cell"]),
                Paragraph("Sí" if p.get("is_riskiest") else "", s["cell"]),
            ])
        t = Table(rows, colWidths=[1.3 * cm, 7.2 * cm, 2.5 * cm, 2 * cm, 2 * cm, 2 * cm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _BLUEPRINT),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, _LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _BLUEPRINT_SOFT]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    # ---- Investigacion (evidencia externa) ----
    research = bp.get("research") or {}
    if research and research.get("status") not in (None, "failed", "empty"):
        story.append(_section_header("Investigación (evidencia externa)", s))
        t = _kv_table([
            ("Confianza", research.get("confidence", "")),
            ("Resumen de mercado", research.get("market_summary", "")),
        ], s)
        if t:
            story.append(t)
        if research.get("queries"):
            story.append(Paragraph("Consultas realizadas", s["h3"]))
            b = _bullets(research["queries"], s, "body")
            if b:
                story.append(b)
        if research.get("competitors"):
            story.append(Paragraph("Competidores identificados", s["h3"]))
            comp_lines = [
                f"{c.get('name', '')} — {c.get('description', '')}".strip(" —")
                for c in research["competitors"]
            ]
            b = _bullets(comp_lines, s, "body")
            if b:
                story.append(b)
        for field, label in [("trends", "Tendencias"), ("benchmarks", "Benchmarks"), ("regulations", "Regulaciones"), ("studies", "Estudios")]:
            if research.get(field):
                story.append(Paragraph(label, s["h3"]))
                b = _bullets(research[field], s, "body")
                if b:
                    story.append(b)
        story.append(Spacer(1, 0.3 * cm))

    # ---- Experimentos disenados ----
    recs = sorted(bp.get("recommendations", []), key=lambda x: x.get("sequence_order", 99))
    if recs:
        story.append(_section_header("Experimentos diseñados", s))
        for r in recs:
            block = [
                Paragraph(
                    f"<b>{_esc(r.get('sequence_order', ''))}. {_esc(r.get('experiment_name', r.get('experiment_id', '')))}</b> "
                    f"<font color='#475569'>({_esc(r.get('stage', ''))}, evidencia {_esc(r.get('expected_evidence_strength', ''))}/5, "
                    f"costo {_esc(r.get('cost', ''))}/5 → hipótesis {_esc(r.get('hypothesis_id', ''))})</font>",
                    s["body"],
                ),
                Paragraph(_esc(r.get("rationale", "")), s["muted"]),
            ]
            if r.get("design_detail"):
                block.append(Paragraph(f"<i>Diseño:</i> {_esc(r['design_detail'])}", s["body"]))
            story.append(KeepTogether(block))
            story.append(Spacer(1, 0.2 * cm))

    # ---- Test Cards ----
    cards = bp.get("test_cards") or []
    if cards:
        story.append(_section_header("Test Cards", s))
        for tc in cards:
            title = tc.get("experiment_name") or tc.get("experiment_id", "")
            block = [
                Paragraph(f"<b>{_esc(title)}</b> <font color='#475569'>({_esc(tc.get('hypothesis_id', ''))})</font>", s["h3"]),
            ]
            kv = _kv_table([
                ("Creemos que", tc.get("hypothesis_statement", "")),
                ("Para verificarlo", tc.get("test_description", "")),
                ("Mediremos", tc.get("metric", "")),
                ("Acertamos si", tc.get("success_criteria", "")),
                ("Evidencia / Costo / Duración", f"{tc.get('expected_evidence_strength', '')}/5  ·  {tc.get('cost', '')}/5  ·  {tc.get('duration_estimate', '')}"),
            ], s)
            if kv:
                block.append(kv)
            story.append(KeepTogether(block))
            story.append(Spacer(1, 0.25 * cm))

    # ---- Plan estimado ----
    plan = bp.get("plan_estimate") or {}
    if plan:
        story.append(_section_header("Plan estimado", s))
        t = _kv_table([
            ("Experimentos", plan.get("experiment_count", "")),
            ("Costo total (puntos)", plan.get("total_cost_points", "")),
            ("Esfuerzo total (puntos)", plan.get("total_effort_points", "")),
            ("Costo máximo de un experimento", plan.get("max_cost", "")),
            ("Capacidades requeridas", "; ".join(plan.get("required_capabilities", []))),
            ("Dentro del presupuesto", "Sí" if plan.get("within_budget", True) else "No"),
            ("Dentro del tiempo disponible", "Sí" if plan.get("within_time", True) else "No"),
        ], s)
        if t:
            story.append(t)
        b = _bullets(plan.get("warnings", []), s, "body")
        if b:
            story.append(Paragraph("Advertencias", s["h3"]))
            story.append(b)
        story.append(Spacer(1, 0.3 * cm))

    # ---- Revision del Critico ----
    review = bp.get("critic_review") or {}
    if review:
        story.append(_section_header("Revisión del Crítico / Coach", s))
        passed = review.get("passed")
        score_color = _OK if passed else _DANGER
        story.append(Paragraph(
            f"Calidad: <b>{_esc(review.get('quality_score', ''))}</b>/1.0 &nbsp;·&nbsp; "
            f"<font color='{score_color.hexval()}'><b>{'Aprobado' if passed else 'Requiere mejoras'}</b></font>",
            s["body"],
        ))
        if review.get("summary"):
            story.append(Paragraph(_esc(review["summary"]), s["muted"]))
        for issue in review.get("issues", []):
            sev = issue.get("severity", "")
            sev_color = {"high": _DANGER, "medium": colors.HexColor("#b45309"), "low": _MUTED}.get(sev, _MUTED)
            story.append(Paragraph(
                f"<font color='{sev_color.hexval()}'><b>[{_esc(sev)}]</b></font> "
                f"<b>{_esc(issue.get('pitfall', ''))}</b>: {_esc(issue.get('detail', ''))} "
                f"<i>→ {_esc(issue.get('suggestion', ''))}</i>",
                s["body"],
            ))
        story.append(Spacer(1, 0.3 * cm))

    # ---- Roadmap ----
    roadmap = bp.get("validation_roadmap") or {}
    if roadmap.get("phases"):
        story.append(_section_header("Roadmap de validación", s))
        for i, ph in enumerate(roadmap["phases"], 1):
            story.append(Paragraph(
                f"<b>{i}. {_esc(ph.get('name', ''))}</b> "
                f"<font color='#475569'>({_esc(ph.get('stage', ''))}, {_esc(ph.get('duration_estimate', ''))})</font> — "
                f"{_esc(ph.get('goal', ''))}",
                s["body"],
            ))
        if roadmap.get("rationale"):
            story.append(Paragraph(_esc(roadmap["rationale"]), s["muted"]))
        story.append(Spacer(1, 0.3 * cm))

    # ---- Decisiones (Learning Cards) ----
    decisions = bp.get("decisions") or []
    if decisions:
        story.append(_section_header("Reglas de decisión (Learning Cards)", s))
        for d in decisions:
            story.append(Paragraph(
                f"<b>{_esc(d.get('hypothesis_id', ''))} / {_esc(d.get('experiment_id', ''))}</b> → "
                f"<i>{_esc(d.get('recommended_decision', ''))}</i>",
                s["body"],
            ))
            story.append(Paragraph(f"Si se valida: {_esc(d.get('if_validated', ''))}", s["muted"]))
            story.append(Paragraph(f"Si no: {_esc(d.get('if_invalidated', ''))}", s["muted"]))
            story.append(Spacer(1, 0.15 * cm))

    # ---- Informe consolidado ----
    report = bp.get("report") or {}
    if report:
        story.append(_section_header("Informe consolidado", s))
        if report.get("executive_summary"):
            story.append(Paragraph(_esc(report["executive_summary"]), s["body"]))
        t = _kv_table([
            ("Problema", report.get("problem_summary", "")),
            ("Propuesta de valor", report.get("value_proposition_summary", "")),
            ("Validación exitosa si", report.get("success_definition", "")),
        ], s)
        if t:
            story.append(t)
        if report.get("riskiest_hypotheses"):
            story.append(Paragraph("Hipótesis más riesgosas", s["h3"]))
            b = _bullets(report["riskiest_hypotheses"], s, "body")
            if b:
                story.append(b)
        if report.get("recommended_sequence"):
            story.append(Paragraph("Secuencia recomendada", s["h3"]))
            b = _bullets(report["recommended_sequence"], s, "body")
            if b:
                story.append(b)
        if report.get("next_steps"):
            story.append(Paragraph("Próximos pasos", s["h3"]))
            b = _bullets(report["next_steps"], s, "body")
            if b:
                story.append(b)

    def _footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(_MUTED)
        canvas.drawString(2 * cm, 1.2 * cm, "Validation Blueprint")
        canvas.drawRightString(LETTER[0] - 2 * cm, 1.2 * cm, f"Página {_doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
