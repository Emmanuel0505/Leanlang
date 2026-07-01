import { Logo } from "./Logo";

/** Layout dividido para autenticación: panel de plano + formulario. */
export function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Panel de marca */}
      <aside className="relative hidden overflow-hidden bg-night lg:block">
        <div className="bp-grid-dark absolute inset-0" />
        <div
          className="absolute inset-0"
          style={{ background: "radial-gradient(60% 50% at 15% 0%, rgba(36,86,230,0.35), transparent 60%)" }}
        />
        <div className="relative flex h-full flex-col justify-between p-12">
          <Logo invert />
          <div>
            <span className="annot text-accent-400">El plano de tu validación</span>
            <h2 className="mt-3 max-w-md text-balance font-display text-4xl font-bold leading-tight text-white">
              De la idea a un plan con método.
            </h2>
            <p className="mt-5 max-w-md text-lg leading-relaxed text-white/70">
              Hipótesis, riesgos D/F/V, priorización 2×2 y los experimentos correctos del catálogo de
              Testing Business Ideas — trazados por agentes, validados por ti.
            </p>
            <ul className="mt-8 space-y-3">
              {[
                "7 agentes especialistas orquestados",
                "44 experimentos del libro, sin inventos",
                "Tú apruebas cada paso clave",
              ].map((t) => (
                <li key={t} className="flex items-center gap-3 text-white/85">
                  <span className="grid h-6 w-6 place-items-center rounded-full bg-viab text-white">✓</span>
                  {t}
                </li>
              ))}
            </ul>
          </div>
          <p className="annot text-white/40">Tesis · Design Science Research</p>
        </div>
      </aside>

      {/* Formulario */}
      <main className="flex items-center justify-center bg-surface px-5 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Logo />
          </div>
          {children}
        </div>
      </main>
    </div>
  );
}
