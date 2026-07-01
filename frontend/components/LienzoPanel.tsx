"use client";

import type { Blueprint } from "@/lib/types";

function Chips({ items, tone = "paper" }: { items?: string[]; tone?: string }) {
  if (!items?.length) return <p className="text-sm text-ink/45">—</p>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((t, i) => (
        <span key={i} className={`badge ${tone === "paper" ? "bg-paper text-ink/70" : tone}`}>{t}</span>
      ))}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="annot mb-1">{label}</div>
      {children}
    </div>
  );
}

const BMC_BLOCKS: { key: keyof NonNullable<Blueprint["business_model"]>; label: string }[] = [
  { key: "key_partners", label: "Socios clave" },
  { key: "key_activities", label: "Actividades clave" },
  { key: "key_resources", label: "Recursos clave" },
  { key: "channels", label: "Canales" },
  { key: "customer_relationships", label: "Relación con cliente" },
  { key: "revenue_streams", label: "Ingresos" },
  { key: "cost_structure", label: "Costos" },
];

/** Lienzo del negocio: VPC (Problem/Segment/ValueProp) + bloques BMC. */
export function LienzoPanel({ bp }: { bp: Blueprint }) {
  const p = bp.problem;
  const s = bp.customer_segment;
  const v = bp.value_proposition;
  const bm = bp.business_model;

  return (
    <div className="space-y-4">
    <div className="grid gap-4 lg:grid-cols-3">
      {/* Problema */}
      <section className="card p-5">
        <div className="mb-3 flex items-center gap-2">
          <span className="grid h-7 w-7 place-items-center rounded-lg bg-desire-soft text-desire-ink">①</span>
          <h3 className="font-display font-semibold text-ink">Problema</h3>
        </div>
        {p ? (
          <div className="space-y-3">
            <p className="text-sm font-medium leading-relaxed text-ink/85">{p.statement}</p>
            {p.context && <p className="text-sm text-ink/60">{p.context}</p>}
            <Field label="Jobs del cliente"><Chips items={p.customer_jobs} /></Field>
            <Field label="Dolores"><Chips items={p.pains} /></Field>
            {p.root_causes?.length > 0 && <Field label="Causas raíz"><Chips items={p.root_causes} /></Field>}
          </div>
        ) : <p className="text-sm text-ink/45">Pendiente.</p>}
      </section>

      {/* Segmento */}
      <section className="card p-5">
        <div className="mb-3 flex items-center gap-2">
          <span className="grid h-7 w-7 place-items-center rounded-lg bg-feas-soft text-feas-ink">②</span>
          <h3 className="font-display font-semibold text-ink">Segmento</h3>
        </div>
        {s ? (
          <div className="space-y-3">
            <p className="text-sm font-medium leading-relaxed text-ink/85">{s.name}</p>
            {s.description && <p className="text-sm text-ink/60">{s.description}</p>}
            <Field label="Características"><Chips items={s.characteristics} /></Field>
            <Field label="Ganancias buscadas"><Chips items={s.gains} /></Field>
            {s.early_adopters && <Field label="Early adopters"><p className="text-sm text-ink/70">{s.early_adopters}</p></Field>}
          </div>
        ) : <p className="text-sm text-ink/45">Pendiente.</p>}
      </section>

      {/* Propuesta de valor */}
      <section className="card p-5">
        <div className="mb-3 flex items-center gap-2">
          <span className="grid h-7 w-7 place-items-center rounded-lg bg-viab-soft text-viab-ink">③</span>
          <h3 className="font-display font-semibold text-ink">Propuesta de valor</h3>
        </div>
        {v ? (
          <div className="space-y-3">
            <p className="text-sm font-medium leading-relaxed text-ink/85">{v.statement}</p>
            <Field label="Productos / servicios"><Chips items={v.products_services} /></Field>
            <Field label="Alivia dolores"><Chips items={v.pain_relievers} /></Field>
            <Field label="Crea ganancias"><Chips items={v.gain_creators} /></Field>
            {v.differentiator && <Field label="Diferenciador"><p className="text-sm text-ink/70">{v.differentiator}</p></Field>}
          </div>
        ) : <p className="text-sm text-ink/45">Pendiente.</p>}
      </section>
    </div>

    {/* Modelo de negocio (BMC) */}
    {bm && (
      <section className="card p-5">
        <div className="mb-3 flex items-center gap-2">
          <span className="grid h-7 w-7 place-items-center rounded-lg bg-blueprint-50 text-blueprint-700 dark:text-blueprint-300">▦</span>
          <h3 className="font-display font-semibold text-ink">Modelo de negocio</h3>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {BMC_BLOCKS.map((b) => {
            const items = bm[b.key];
            if (!items?.length) return null;
            return (
              <div key={b.key}>
                <div className="annot mb-1">{b.label}</div>
                <Chips items={items} />
              </div>
            );
          })}
        </div>
      </section>
    )}
    </div>
  );
}
