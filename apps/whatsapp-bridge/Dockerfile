FROM node:20-alpine

# Puppeteer deps
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    git

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser \
    NODE_ENV=production

WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY server.js .
RUN mkdir -p sessions

EXPOSE 3002
CMD ["node", "server.js"]
