# 🌐 DNS Setup — sonoradigitalcorp.com

## Objetivo

Conectar **sonoradigitalcorp.com** a infraestructura HERMES OS:
- **Frontend (Mission Control)**: Vercel
- **API Backend**: VPS (Hostinger)
- **Email**: Custom domain

---

## 📋 Prerrequisitos

- [ ] Dominio `sonoradigitalcorp.com` registrado (GoDaddy, Namecheap, etc)
- [ ] Acceso a panel de DNS registrar
- [ ] Proyecto "mission-control" creado en Vercel
- [ ] VPS Hostinger con IP pública (ej: 192.168.1.100)

---

## 🔧 Paso 1: Configurar DNS en Registrador

Accede a tu registrador (GoDaddy, Namecheap, etc) y edita los **DNS Records**:

### Records Requeridos

```
TYPE    NAME                    VALUE                           TTL
A       @                       (Vercel IP o VPS IP)            3600
CNAME   www                     cname.vercel-dns.com            3600
CNAME   api                     (VPS hostname o IP)             3600
CNAME   mission-control         cname.vercel-dns.com            3600
TXT     @                       v=spf1 include:sendgrid.net ~all 3600
CNAME   mail                    sendgrid.net                    3600
```

**Detalle**:

#### A Record (Raíz)
```
NAME: @ (o sonoradigitalcorp.com)
VALUE: Depende de tu setup:
  - Si Vercel es raíz: usa Vercel's DNS A record
  - Si VPS es raíz: usa IP del VPS (ej: 192.168.1.100)
TTL: 3600 (1 hora)
```

#### CNAME: www
```
NAME: www
VALUE: cname.vercel-dns.com (o tu CNAME de Vercel)
TTL: 3600
```

#### CNAME: api
```
NAME: api
VALUE: VPS hostname o IP
TTL: 3600
Ejemplo: api.sonoradigitalcorp.com → 192.168.1.100
```

#### CNAME: mission-control
```
NAME: mission-control
VALUE: cname.vercel-dns.com (Vercel)
TTL: 3600
Resultado: mission-control.sonoradigitalcorp.com → Vercel
```

#### TXT: SPF (Email)
```
NAME: @ (raíz)
VALUE: v=spf1 include:sendgrid.net ~all
TTL: 3600
(Necesario para SendGrid / email)
```

#### CNAME: mail
```
NAME: mail
VALUE: sendgrid.net
TTL: 3600
(Para redirigir email via SendGrid)
```

---

## 🔗 Paso 2: Configurar Vercel

1. Ve a **Vercel Dashboard** → Proyecto "mission-control"
2. Settings → Domains
3. Agregar dominio: `sonoradigitalcorp.com` y `www.sonoradigitalcorp.com`
4. Vercel te dará:
   - **A Record** value (IP de Vercel)
   - **CNAME** value (para www)
5. Copia estos valores a tu registrador de DNS

---

## 🖥️ Paso 3: Configurar VPS (Nginx)

En tu VPS, configura Nginx para escuchar en `api.sonoradigitalcorp.com`:

### Nginx Config
```nginx
# /etc/nginx/sites-available/api.sonoradigitalcorp.com

server {
    listen 80;
    server_name api.sonoradigitalcorp.com;

    # Redirect HTTP → HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.sonoradigitalcorp.com;

    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.sonoradigitalcorp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sonoradigitalcorp.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Proxy to FastAPI (hermes-api:8000)
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

### Instalar/Activar
```bash
# Crear symlink
sudo ln -s /etc/nginx/sites-available/api.sonoradigitalcorp.com \
           /etc/nginx/sites-enabled/api.sonoradigitalcorp.com

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

---

## 🔒 Paso 4: SSL con Let's Encrypt

```bash
# Instalar certbot (si no está)
sudo apt-get install certbot python3-certbot-nginx

# Generar certificado
sudo certbot certonly --nginx -d api.sonoradigitalcorp.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## ✅ Paso 5: Verificación

### 1. DNS Propagación
```bash
# Esperar 5-30 minutos para que DNS se propague
# Verifica con:
nslookup sonoradigitalcorp.com
nslookup api.sonoradigitalcorp.com
dig api.sonoradigitalcorp.com
```

### 2. Vercel Deployment
```bash
# Visita
https://sonoradigitalcorp.com/
https://mission-control.sonoradigitalcorp.com/

# Debe cargar Mission Control dashboard
```

### 3. VPS API
```bash
# Verifica API disponible
curl -I https://api.sonoradigitalcorp.com/health
# Debe retornar 200 OK

curl -I https://api.sonoradigitalcorp.com/docs
# Debe retornar 200 OK (OpenAPI)
```

### 4. Telegram Notification
```bash
# Envía test push
curl -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN_CEO/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"5738935134\", \"text\": \"✅ DNS Setup Completo!\"}"
```

---

## 🗺️ Arquitectura Final

```
sonoradigitalcorp.com (A record → Vercel)
├─ https://sonoradigitalcorp.com/
│  └─ Vercel: Mission Control Frontend
│
├─ https://www.sonoradigitalcorp.com/
│  └─ Vercel: mismo dashboard
│
├─ https://mission-control.sonoradigitalcorp.com/
│  └─ Vercel: Mission Control Dashboard (alias)
│
└─ https://api.sonoradigitalcorp.com/ (CNAME → VPS)
   └─ VPS Nginx → FastAPI (hermes-api:8000)
   ├─ /docs → OpenAPI
   ├─ /health → Status
   ├─ /api/v1/agents/hermes/chat → Chat IA
   ├─ /api/v1/agents/mystic/analyze → Análisis
   └─ /api/v1/...
```

---

## 🚨 Troubleshooting

### "Dominio no resuelve"
```bash
# Verifica DNS
dig sonoradigitalcorp.com +short
# Si no retorna IP, espera más tiempo o revisa DNS records

# Fuerza refresh de DNS
sudo systemctl restart systemd-resolved
```

### "Certificado SSL inválido"
```bash
# Verifica certificado
openssl s_client -connect api.sonoradigitalcorp.com:443
# Debe mostrar certificado válido

# Si falta, regenera con certbot:
sudo certbot certonly --nginx -d api.sonoradigitalcorp.com --force-renewal
```

### "API no responde en api.sonoradigitalcorp.com"
```bash
# Verifica Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log

# Verifica FastAPI en localhost
curl -I http://localhost:8000/health
# Si retorna 200, problema está en Nginx config

# Verifica firewall
sudo ufw status
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
```

### "Mission Control no carga en Vercel"
```bash
# Verifica en Vercel Deployments
# Debe estar en "Ready" state

# Si falla, redeploy:
git push origin main
# GitHub Actions disparará redeploy automático
```

---

## 📝 Checklist Final

- [ ] DNS records agregados en registrador
- [ ] Vercel dominio confirmado
- [ ] Nginx config en VPS
- [ ] SSL certificado instalado
- [ ] DNS propagado (5-30 min)
- [ ] `https://sonoradigitalcorp.com` carga Mission Control ✅
- [ ] `https://api.sonoradigitalcorp.com/health` retorna 200
- [ ] `https://api.sonoradigitalcorp.com/docs` carga OpenAPI ✅
- [ ] Telegram recibe notificación de deploy ✅

---

**Última actualización**: 2026-04-16  
**Estado**: Listo para implementar
