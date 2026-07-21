// La Content-Security-Policy se mueve a middleware.ts: necesita un nonce
// distinto por request (script-src 'nonce-...'), y headers() aca solo
// admite valores estaticos conocidos en build time. Las demas cabeceras
// no necesitan variar por request, se quedan aca.
const securityHeaders = [
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
