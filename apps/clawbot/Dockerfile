FROM node:22-alpine

WORKDIR /app

RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser

COPY package.json .
RUN npm install --omit=dev

COPY . .

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 3003

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3003/health || exit 1

CMD ["node", "index.js"]
