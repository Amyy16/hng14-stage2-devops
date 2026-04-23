
# -------- STAGE 1: Builder --------
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .

# -------- STAGE 2: Runtime --------
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app .

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && chown -R appuser:appgroup /app
USER appuser

# Expose frontend port
EXPOSE 3000

# Healthcheck (checks server is up)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000 || exit 1

# Start server
CMD ["node", "app.js"]

