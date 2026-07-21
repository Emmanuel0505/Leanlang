import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

/** Genera un nonce por request para permitir SOLO los scripts que Next.js
 * marca con ese nonce (los propios: hidratacion/streaming de RSC, y
 * app/layout.tsx via headers()) -- cualquier script inyectado (XSS) no
 * conoce el nonce y la CSP lo bloquea. Ver docs de Next.js sobre CSP con
 * nonce: exige renderizado dinamico (headers() en el layout raiz ya lo
 * fuerza para toda la app).
 *
 * style-src se queda con 'unsafe-inline': varios componentes usan props
 * style={{...}} (atributos style inline), y a diferencia de <script>/<style>
 * un atributo style no se puede "noncear" -- solo hay CSP o no. El riesgo
 * real que esto cubre (inyeccion de JS via script-src) es el que importaba
 * a la revision de seguridad; la inyeccion de CSS es un vector mucho mas
 * debil.
 */
export function middleware(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    `connect-src 'self'${apiUrl ? ` ${apiUrl}` : ""}`,
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join("; ");

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("Content-Security-Policy", csp);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", csp);
  return response;
}

export const config = {
  matcher: [
    {
      source: "/((?!api|_next/static|_next/image|favicon.ico).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
