# GitHub Secrets Setup — HERMES OS Deploy

Este documento explica cómo configurar los secrets de GitHub para el workflow de auto-deploy a Vercel + VPS + Telegram.

---

## ⚡ Quick Start

1. Ir a: `https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions`
2. Hacer clic en **New repository secret**
3. Agregar cada secret según la tabla abajo
4. Verificar que todos estén presentes

---

## 📋 Secrets Requeridos

### VPS Deployment

| Secret | Valor | Ejemplo | Dónde obtenerlo |
|--------|-------|---------|-----------------|
| **VPS_HOST** | IP o hostname del VPS | `192.168.1.100` o `vps.tudominio.com` | Panel Hostinger / Terminal local |
| **VPS_SSH_USER** | Usuario SSH (root o dedicado) | `root` | Config SSH local |
| **VPS_SSH_KEY** | SSH private key (base64) | (ver instrucciones abajo) | `cat ~/.ssh/id_rsa \| base64 -w0` |

### Vercel Deployment

| Secret | Valor | Ejemplo | Dónde obtenerlo |
|--------|-------|---------|-----------------|
| **VERCEL_TOKEN** | Personal Access Token | `abc123xyz...` | [vercel.com/account/tokens](https://vercel.com/account/tokens) |
| **VERCEL_ORG_ID** | Organization ID (opcional) | `team_abc123...` | Vercel Dashboard → Settings |
| **VERCEL_PROJECT_ID** | Project ID para mission-control | `prj_xyz123...` | Vercel Dashboard → Project Settings |

### Telegram Notifications

| Secret | Valor | Ejemplo | Dónde obtenerlo |
|--------|-------|---------|-----------------|
| **TELEGRAM_TOKEN_CEO** | Bot token HERMES CEO | `123456:ABC-DEF...` | BotFather (@BotFather en Telegram) |
| **CEO_CHAT_ID** | Chat ID de Luis Daniel | `5738935134` | `@userinfobot` en Telegram |

---

## 🔧 Paso a Paso

### 1. Configurar SSH Key para VPS

**En tu máquina local** (NO en el VPS):

```bash
# Si ya tienes SSH key
cat ~/.ssh/id_rsa | base64 -w0
# Copia el output completo (termina en = o ==)

# Si NO tienes SSH key, crear una
ssh-keygen -t ed25519 -f ~/.ssh/hermes_deploy -C "github-actions"
# Presiona Enter 2 veces (sin passphrase para automatización)

# Copiar la key codificada
cat ~/.ssh/hermes_deploy | base64 -w0
```

**Qué obtuviste**: una cadena larga que comienza con `LS0tLS1C...` (es tu private key en base64).

**En GitHub**:
- Nombre: `VPS_SSH_KEY`
- Valor: Pega la cadena completa
- Clic en **Add secret**

---

### 2. Configurar VPS_HOST

**En tu máquina local**:

```bash
# Obtener IP del VPS
ssh vps "hostname -I"
# O usar el hostname directo (si lo tienes en ~/.ssh/config)
```

**En GitHub**:
- Nombre: `VPS_HOST`
- Valor: `192.168.1.100` (o `vps.tudominio.com`)
- Clic en **Add secret**

---

### 3. Configurar VPS_SSH_USER

**En GitHub**:
- Nombre: `VPS_SSH_USER`
- Valor: `root` (o el usuario con permisos docker en el VPS)
- Clic en **Add secret**

---

### 4. Configurar Vercel Token

**Ir a Vercel**:
1. [vercel.com](https://vercel.com) → Inicia sesión
2. Haz clic en tu avatar (arriba a la derecha) → **Settings**
3. Sidebar → **Tokens**
4. Clic en **Create Token**
5. Nombre: `github-actions`
6. Expiration: `7 days` (renovable) o `No expiration` (no recomendado)
7. Clic en **Create**
8. **Copia el token** (aparece una sola vez)

**En GitHub**:
- Nombre: `VERCEL_TOKEN`
- Valor: Pega el token completo
- Clic en **Add secret**

---

### 5. Configurar VERCEL_ORG_ID (Opcional)

Si usas un equipo en Vercel:

**En Vercel**:
1. Haz clic en tu avatar → **Settings**
2. Sidebar → **Teams**
3. Selecciona el equipo
4. URL será: `vercel.com/teams/tu-equipo-name/...`
5. Copia el slug del equipo

**En GitHub**:
- Nombre: `VERCEL_ORG_ID`
- Valor: `tu-equipo-name`
- Clic en **Add secret**

---

### 6. Configurar VERCEL_PROJECT_ID

**En Vercel**:
1. Abre el proyecto **mission-control**
2. Haz clic en **Settings** (engrane)
3. Busca **Project ID** en la sección general
4. Copia el valor (comienza con `prj_`)

**En GitHub**:
- Nombre: `VERCEL_PROJECT_ID`
- Valor: `prj_abc123xyz...`
- Clic en **Add secret**

---

### 7. Configurar Telegram Bot Token

**Crear bot en Telegram**:
1. Abre Telegram
2. Busca y abre **@BotFather**
3. Envía `/newbot`
4. Sigue las instrucciones (nombre, username)
5. Te dará un token: `123456:ABC-DEF1GHI2jkl-zyx57W2v1u123ew11`
6. **Copia el token completo**

**En GitHub**:
- Nombre: `TELEGRAM_TOKEN_CEO`
- Valor: `123456:ABC-DEF1GHI2jkl-zyx57W2v1u123ew11`
- Clic en **Add secret**

---

### 8. Configurar CEO_CHAT_ID

**Obtener tu Chat ID**:
1. Abre Telegram
2. Busca y abre **@userinfobot**
3. Envía cualquier mensaje
4. Recibirás tu ID de usuario (ej: `5738935134`)
5. **Copia el número**

**En GitHub**:
- Nombre: `CEO_CHAT_ID`
- Valor: `5738935134`
- Clic en **Add secret**

---

## ✅ Verificación

Después de agregar todos los secrets:

1. Ir a GitHub → **Settings → Secrets and variables → Actions**
2. Deberías ver 7 secrets:
   - `CEO_CHAT_ID`
   - `TELEGRAM_TOKEN_CEO`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
   - `VERCEL_TOKEN`
   - `VPS_HOST`
   - `VPS_SSH_KEY`
   - `VPS_SSH_USER`

3. **No abras los valores** (GitHub los oculta por seguridad)

---

## 🚀 Probar el Workflow

### Test 1: Trigger manual

```bash
# En GitHub
1. Actions → Deploy — Vercel + VPS + Notify
2. Run workflow → Branch: main
3. Clic en Run workflow
```

### Test 2: Trigger automático

```bash
# Hacer un pequeño cambio y push a main
echo "# Test deploy" >> README.md
git add README.md
git commit -m "test: trigger deploy workflow"
git push origin main

# Monitorear en GitHub → Actions
```

### Test 3: Verificar notificación en Telegram

Después de que el workflow termine (✅ o ❌), deberías recibir un mensaje en Telegram del CEO bot.

---

## 🔐 Seguridad

### ✅ Lo que está bien
- Secrets están encriptados en GitHub (no visible ni en logs)
- SSH key sin passphrase necesita acceso a repo + VPS
- Tokens de Vercel y Telegram pueden rotarse fácilmente

### ⚠️ Mejoras futuras
- Usar `VERCEL_ORG_ID` si tienes equipo (limita scope del token)
- Rotar tokens cada 30-90 días
- Usar deploy keys específicas por servicio (no reutilizar SSH keys)

---

## 🐛 Troubleshooting

### Error: "SSH key invalid"
```bash
# Verifica que el key esté en base64 correctamente
cat ~/.ssh/id_rsa | base64 -w0 | wc -c
# Debe ser > 1000 caracteres

# Si usaste ssh-keygen con passphrase, quítala
ssh-keygen -p -f ~/.ssh/id_rsa -N "" -P "old_passphrase"
```

### Error: "Permission denied (publickey)"
```bash
# Verifica que la public key esté en el VPS
ssh vps "cat ~/.ssh/authorized_keys | grep -i github"

# Si no está, agrégala
cat ~/.ssh/id_rsa.pub | ssh vps "cat >> ~/.ssh/authorized_keys"
```

### Error: "Vercel deployment failed"
- Verifica que `VERCEL_PROJECT_ID` sea correcto
- Asegúrate que `frontend/` exista en el repo
- Revisa los logs en Vercel Dashboard

### Error: "Telegram message not sent"
- Verifica que el bot tenga permisos (no fue muteado)
- Confirma que `CEO_CHAT_ID` es un número válido
- Prueba el bot manualmente: `@HERMES_CEO_bot` → `/start`

---

## 📞 Contacto

Si necesitas ayuda configurando los secrets:

1. Revisa los logs del workflow: **Actions → Deploy — Vercel + VPS + Notify → Run X**
2. El error estará en el job que falló (vercel, vps, o notify)
3. Comparte el error específico en el chat
