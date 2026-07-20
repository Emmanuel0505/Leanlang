FROM node:20-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package.json ./
RUN npm install

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Next.js incrusta las variables NEXT_PUBLIC_* en el bundle durante `npm run
# build`, no en tiempo de ejecucion. Render traduce las env vars del dashboard
# a build args automaticamente, pero hay que declararlas con ARG para que
# lleguen a este stage (si no, cae al fallback hardcodeado del codigo).
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM base AS runner
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["npm", "start"]
