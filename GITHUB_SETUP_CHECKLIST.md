# GitHub Setup Checklist — HERMES OS Deploy

Checklist interactivo para configurar el workflow de auto-deploy.

---

## PASO 1: Preparar Valores

- [ ] Ejecutar script helper
  ```bash
  bash scripts/setup-github-secrets.sh
  ```
  Esto te pedirá valores y mostrará qué copiar.

---

## PASO 2: Configurar Secrets en GitHub

Ir a: `https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions`

### VPS Deployment

- [ ] **VPS_HOST**
  - [ ] Obtenido de: `ssh vps "hostname -I"` o ~/.ssh/config
  - [ ] Ingresado en GitHub
  - [ ] Valor: `________________`

- [ ] **VPS_SSH_USER**
  - [ ] Obtenido de: SSH config (~/.ssh/config o "root")
  - [ ] Ingresado en GitHub
  - [ ] Valor: `root` (típicamente)

- [ ] **VPS_SSH_KEY**
  - [ ] SSH key sin passphrase verificada: `ssh-keygen -p -f ~/.ssh/id_rsa -N "" -P "old_pass"`
  - [ ] Convertido a base64: `cat ~/.ssh/id_rsa | base64 -w0`
  - [ ] Ingresado en GitHub
  - [ ] Largo: _____ caracteres (debe ser > 1000)

### Vercel Deployment

- [ ] **VERCEL_TOKEN**
  - [ ] Ir a: https://vercel.com/account/tokens
  - [ ] Create Token → "github-actions"
  - [ ] Copiado
  - [ ] Ingresado en GitHub
  - [ ] Formato: `xxxxx-yyyyy-zzzzz`

- [ ] **VERCEL_PROJECT_ID**
  - [ ] Ir a: https://vercel.com
  - [ ] Proyecto "mission-control" → Settings
  - [ ] Buscar "Project ID" (comienza con "prj_")
  - [ ] Copiado
  - [ ] Ingresado en GitHub
  - [ ] Valor: `prj_________________`

- [ ] **VERCEL_ORG_ID** (Opcional — dejar vacío si no tienes equipo)
  - [ ] Si usas equipo: Settings → Teams → copia slug
  - [ ] Ingresado en GitHub (o skip si no aplica)
  - [ ] Valor: `________________` (opcional)

### Telegram Notifications

- [ ] **TELEGRAM_TOKEN_CEO**
  - [ ] Ir a: Telegram → @BotFather
  - [ ] /newbot → sigue instrucciones
  - [ ] Copiar token (formato: `123456:ABC-DEF...`)
  - [ ] Ingresado en GitHub
  - [ ] Valor: `________________`

- [ ] **CEO_CHAT_ID**
  - [ ] Ir a: Telegram → @userinfobot
  - [ ] Enviar cualquier mensaje
  - [ ] Copiar ID (número largo)
  - [ ] Ingresado en GitHub
  - [ ] Valor: `5738935134` (Luis Daniel)

---

## PASO 3: Verificar Configuración

- [ ] Ir a GitHub → Settings → Secrets → Verificar que existen 8 (o 7 si omitiste VERCEL_ORG_ID)
  ```
  □ CEO_CHAT_ID
  □ TELEGRAM_TOKEN_CEO
  □ VERCEL_ORG_ID (opcional)
  □ VERCEL_PROJECT_ID
  □ VERCEL_TOKEN
  □ VPS_HOST
  □ VPS_SSH_KEY
  □ VPS_SSH_USER
  ```

---

## PASO 4: Test del Workflow

### Opción A: Manual (recomendado para primer test)

- [ ] GitHub → Actions
- [ ] Sidebar → Deploy — Vercel + VPS + Notify
- [ ] Botón azul **Run workflow**
- [ ] Branch: `main`
- [ ] Botón **Run workflow**
- [ ] Esperar a que termine (8-15 minutos)

### Opción B: Automático (push a main)

- [ ] Hacer cambio pequeño
  ```bash
  echo "# Deploy test" >> README.md
  git add README.md
  git commit -m "test: deploy workflow"
  git push origin main
  ```
- [ ] Monitorear en GitHub → Actions
- [ ] Esperar a que termine

---

## PASO 5: Verificar Resultados

- [ ] GitHub Actions UI muestra:
  - [ ] ✅ deploy-vercel: success
  - [ ] ✅ deploy-vps: success
  - [ ] ✅ notify: success

- [ ] Vercel:
  - [ ] [ ] Ir a https://vercel.com
  - [ ] [ ] Proyecto mission-control → Deployments
  - [ ] [ ] Último deployment: success
  - [ ] [ ] URL accesible: https://mission-control-*.vercel.app

- [ ] VPS:
  - [ ] [ ] SSH al VPS: `ssh vps`
  - [ ] [ ] Verificar containers: `docker ps`
  - [ ] [ ] Health check: `curl http://localhost:8000/health`
  - [ ] [ ] Status code: 200/204 ✅

- [ ] Telegram:
  - [ ] [ ] Abre Telegram
  - [ ] [ ] CEO bot (HERMES_CEO_bot) o chats
  - [ ] [ ] Mensaje recibido:
    ```
    ✅ HERMES OS Deploy
    
    Resultado: ✅ SUCCESS
    Vercel: ✅ success
    VPS: ✅ success (HEALTHY)
    
    Detalles:
    Commit: xxxxxxxx
    Rama: main
    Actor: @username
    Timestamp: YYYY-MM-DD HH:MM UTC
    
    [Ver en GitHub](link)
    ```

---

## PASO 6: Troubleshooting (Si algo falla)

### GitHub Actions muestra error

- [ ] Haz clic en el job que falló
- [ ] Lee el log completo
- [ ] Busca `❌` o `error`
- [ ] Compara con la tabla abajo

| Error | Solución |
|-------|----------|
| `Permission denied (publickey)` | SSH key no en VPS: `ssh vps "cat >> ~/.ssh/authorized_keys" < ~/.ssh/id_rsa.pub` |
| `vercel/action@v8: command not found` | VERCEL_TOKEN incorrecto o proyecto inexistente |
| `fatal: ambiguous argument 'HEAD~1'` | Normal en primer push a main, workflow continúa |
| `curl: (7) Failed to connect` | VPS no responde, revisar: `docker logs hermes-api` en VPS |
| `Telegram: 400 Bad Request` | TELEGRAM_TOKEN_CEO o CEO_CHAT_ID inválido |

### Vercel deployment falla

- [ ] Verifica VERCEL_PROJECT_ID correcto
- [ ] Verifica que frontend/ exista en repo
- [ ] Ve a Vercel → Deployments → ve el error completo

### VPS health check falla

- [ ] SSH al VPS: `ssh vps`
- [ ] Revisa logs: `docker logs hermes-api`
- [ ] Verifica que hermes-api esté up: `docker ps | grep hermes-api`
- [ ] Reinicia manual:
  ```bash
  cd /home/mystic/hermes-os
  docker compose up -d hermes-api
  sleep 5
  curl http://localhost:8000/health
  ```

### No recibe mensaje Telegram

- [ ] Abre Telegram → @userinfobot → envía mensaje
- [ ] Verifica que CEO_CHAT_ID es un número válido
- [ ] Verifica que el bot no está mutedo (mute notifications)
- [ ] Test manual:
  ```bash
  CHAT_ID="5738935134"
  TOKEN="tu-token-aqui"
  curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}&text=Test"
  ```

---

## PASO 7: Producción Ready

- [ ] Todos los tests pasando
- [ ] SSH public key en VPS:
  ```bash
  ssh vps "cat ~/.ssh/authorized_keys | grep -i github"
  # Debe mostrar tu SSH public key
  ```

- [ ] Documentación leída:
  - [ ] [ ] docs/DEPLOY_QUICK_START.md
  - [ ] [ ] docs/CI_CD_WORKFLOW.md
  - [ ] [ ] docs/GITHUB_SECRETS_SETUP.md

- [ ] Rollback procedure conocida (en DEPLOY_QUICK_START.md)

- [ ] GitHub secrets seguros:
  - [ ] No hacerles push a repo
  - [ ] Rotar cada 30-90 días
  - [ ] No usar en logs o comentarios

---

## REFERENCIAS RÁPIDAS

```bash
# Ver logs del último deploy
# GitHub → Actions → Deploy workflow → last run → expand job

# SSH key info
ssh-keygen -l -f ~/.ssh/id_rsa

# Verificar SSH acceso
ssh -v vps "echo OK"

# Test Vercel token
curl -H "Authorization: Bearer $VERCEL_TOKEN" \
  https://api.vercel.com/v2/user

# Test Telegram token
curl -s "https://api.telegram.org/bot$TELEGRAM_TOKEN_CEO/getMe"
```

---

## Notas

- **Secrets encriptados**: No se muestran en logs de GitHub Actions
- **SSH sin passphrase**: Necesario para automatización
- **Retry logic**: Health check reintenta hasta 3 veces
- **Parallel jobs**: Vercel y VPS se deplayan simultáneamente
- **Duration**: Total 8-15 minutos (típicamente 10)

---

**Última actualización**: 2026-04-16

¿Preguntas? Ver: `docs/GITHUB_SECRETS_SETUP.md` (troubleshooting detallado)
