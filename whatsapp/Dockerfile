FROM node:20-alpine

WORKDIR /app

# Deps
COPY package.json .
RUN npm install --production

# App
COPY server.js .

EXPOSE 3001

CMD ["node", "server.js"]
