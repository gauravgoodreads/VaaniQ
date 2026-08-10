# syntax=docker/dockerfile:1
# VaaniQ frontend — build → nginx (ROADMAP-009 / REQ-112)

FROM node:22-bookworm-slim AS build

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# Empty base → browser calls same origin; nginx proxies /health and /api.
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# --- nginx runtime ---
FROM nginx:1.27-alpine AS runtime

RUN addgroup -g 10001 -S vaaniq \
    && adduser -S -D -H -u 10001 -G vaaniq vaaniq \
    && mkdir -p /var/cache/nginx /var/run \
    && chown -R vaaniq:vaaniq /var/cache/nginx /var/run /usr/share/nginx/html

COPY deployment/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /build/dist /usr/share/nginx/html

# nginx master needs root for port 80 binding in alpine default layout;
# keep official entrypoint; healthcheck uses wget/curl as root in HEALTHCHECK context.
EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
  CMD wget -qO- http://127.0.0.1/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
