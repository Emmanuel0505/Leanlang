const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

// CSP permisiva en connect-src hacia el backend (fetch + EventSource/SSE del
// streaming de agentes, ver lib/stream.ts) y hacia 'self'. next/font/google
// autohospeda las fuentes en el build (ver app/layout.tsx) -- no hace falta
// permitir fonts.googleapis.com/fonts.gstatic.com en runtime.
const csp = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: https:",
  "font-src 'self' data:",
  `connect-src 'self'${apiUrl ? ` ${apiUrl}` : ""}`,
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: csp },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains" },
];

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false, // saca la cabecera "X-Powered-By: Next.js" (divulgacion de tecnologia)
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
