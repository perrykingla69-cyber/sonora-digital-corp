FROM node:22-alpine
WORKDIR /app
RUN echo '{"name":"frontend","version":"1.0.0","scripts":{"start":"node server.js"}}' > package.json && \
    echo 'const http=require("http");http.createServer((_,r)=>{r.writeHead(200,{"Content-Type":"text/html"});r.end("<h1>HERMES OS — Frontend coming soon</h1>")}).listen(3000)' > server.js
EXPOSE 3000
CMD ["node", "server.js"]
