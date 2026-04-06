FROM node:22-alpine
WORKDIR /app
COPY index.html .
COPY dashboard.html .
COPY server.js .
RUN echo '{"name":"frontend","version":"1.0.0","scripts":{"start":"node server.js"}}' > package.json
EXPOSE 3000
CMD ["node", "server.js"]
