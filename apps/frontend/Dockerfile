# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@10.15.1

# Copy root and workspace files
COPY package.json pnpm-lock.yaml ./
COPY apps/frontend ./apps/frontend
COPY packages ./packages

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build
WORKDIR /app/apps/frontend
RUN pnpm build

# Production stage
FROM node:22-alpine

WORKDIR /app

# Install http-server for static serving
RUN npm install -g http-server@14.1.1

# Copy built artifacts from builder
COPY --from=builder /app/apps/frontend/dist /app

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Serve static files
CMD ["http-server", ".", "-p", "3000", "--gzip"]
