import type { Config } from "tailwindcss";

const withAlpha = (v: string) => `rgb(var(${v}) / <alpha-value>)`;

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["var(--font-display)", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      colors: {
        // — Neutros semánticos (adaptan a tema vía variables CSS) —
        paper: withAlpha("--bg"), // fondo de la app + rellenos sutiles
        surface: withAlpha("--surface"), // tarjetas / inputs
        ink: withAlpha("--text"), // texto principal
        line: withAlpha("--border"), // bordes / hairlines
        tint: withAlpha("--tint"), // realce de selección/activo
        night: "#0c1a2e", // superficie oscura fija (paneles dark)

        // Azul cianotipo — color estructural y de acción
        blueprint: {
          50: "#eff4ff", 100: "#dbe6fe", 200: "#bfd3fe", 300: "#93b4fd", 400: "#608ffa",
          500: "#3a6bf4", 600: "#2456e6", 700: "#1d44c0", 800: "#1d3a9b", 900: "#1d357a", 950: "#14224d",
        },
        // Ámbar de calco — acento de firma
        accent: { 300: "#fad776", 400: "#f7c948", 500: "#f2b100", 600: "#d99700", 700: "#b07700" },

        // Trío de riesgo (Testing Business Ideas)
        desire: { DEFAULT: "#c97a0e", soft: withAlpha("--desire-soft"), ink: withAlpha("--desire-ink") },
        feas: { DEFAULT: "#0e8fa8", soft: withAlpha("--feas-soft"), ink: withAlpha("--feas-ink") },
        viab: { DEFAULT: "#1f9d57", soft: withAlpha("--viab-soft"), ink: withAlpha("--viab-ink") },

        // Semaforización (estado: verde / ámbar / rojo) — adapta a claro/oscuro
        ok: { DEFAULT: withAlpha("--ok"), soft: withAlpha("--ok-soft"), ink: withAlpha("--ok-ink") },
        warn: { DEFAULT: withAlpha("--warn"), soft: withAlpha("--warn-soft"), ink: withAlpha("--warn-ink") },
        danger: { DEFAULT: withAlpha("--danger"), soft: withAlpha("--danger-soft"), ink: withAlpha("--danger-ink") },
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(12 26 46 / 0.04), 0 2px 6px -1px rgb(12 26 46 / 0.06)",
        lift: "0 16px 40px -16px rgb(12 26 46 / 0.22)",
        glow: "0 0 0 1px rgb(36 86 230 / 0.15), 0 14px 40px -14px rgb(36 86 230 / 0.4)",
        amber: "0 0 0 1px rgb(242 177 0 / 0.25), 0 12px 32px -14px rgb(242 177 0 / 0.5)",
      },
      borderRadius: { xl: "0.75rem", "2xl": "1.1rem" },
      keyframes: {
        "fade-up": { "0%": { opacity: "0", transform: "translateY(10px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        "fade-in": { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        "draw-in": { "0%": { opacity: "0", transform: "scale(0.96)" }, "100%": { opacity: "1", transform: "scale(1)" } },
        pulse2: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.35" } },
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-6px)" } },
      },
      animation: {
        "fade-up": "fade-up 0.5s cubic-bezier(0.22,1,0.36,1) both",
        "fade-in": "fade-in 0.4s ease both",
        "draw-in": "draw-in 0.4s cubic-bezier(0.22,1,0.36,1) both",
      },
    },
  },
  plugins: [],
};
export default config;
