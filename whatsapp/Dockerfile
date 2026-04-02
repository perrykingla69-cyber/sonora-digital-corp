FROM node:20-alpine

RUN apk add --no-cache git python3 make g++

WORKDIR /app

# Deps
COPY package.json .
RUN npm install --omit=dev

# App
COPY server.js .

EXPOSE 3001

CMD ["node", "server.js"]
