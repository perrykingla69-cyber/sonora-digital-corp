# CREDENCIALES DE DEMO — Sonora Digital Corp

## 🔐 Acceso a sonoradigitalcorp.com

### CEO (Luis Daniel) — Acceso Completo

```
Email:    luis@sonoradigitalcorp.com
Password: SonoraAdmin2024!Secure

Roles: CEO
Panel: Dashboard Completo (Mission Control)
Acceso: Todos los tenants (6 empresas)
```

**Qué puede ver:**
- ✅ Dashboard central (Docker, API, DB status)
- ✅ Todos los logs del sistema
- ✅ Todos los agents (HERMES, MYSTIC, ClawBot)
- ✅ Panel de MCP integrations
- ✅ Tareas de Claude Code (#1, #2, #3)
- ✅ Ejecución de comandos vía Telegram (/status, /tasks, /logs, /deploy)
- ✅ Administración de usuarios y tenants
- ✅ Configuración del sistema

---

### Usuario Demo — Restaurante (Cliente)

```
Email:    demo@restaurante.sonoradigitalcorp.com
Password: ClienteDemo2024!Test

Roles: Usuario/Cliente
Tenant: Restaurante El Faro (demo)
Panel: Dashboard Cliente
Acceso: Solo su tenant
```

**Qué puede ver:**
- ✅ Dashboard de su restaurante
- ✅ Estadísticas de uso
- ✅ Chat con HERMES (ayuda inteligente)
- ✅ Alertas y recomendaciones
- ✅ Biblioteca de documentos
- ✅ Soporte multi-canal (Telegram, WhatsApp)

---

## 🌐 Acceso a Dominios

### Mission Control (Dashboard Centralizado)
- **URL**: https://sonoradigitalcorp.com/mission-control/
- **URL Vercel**: https://mission-control-hermes.vercel.app (fallback)
- **Acceso**: CEO

### Dashboard Cliente (Tenant)
- **URL**: https://sonoradigitalcorp.com/dashboard/
- **Acceso**: Cliente (solo su tenant)

### API Backend
- **Base URL**: https://api.sonoradigitalcorp.com/ (VPS)
- **Docs**: https://api.sonoradigitalcorp.com/docs (OpenAPI)
- **Health**: https://api.sonoradigitalcorp.com/health

### HERMES IA Bot
- **Telegram Bot**: @HERMESsonomx_bot (CEO)
- **Telegram Public**: @HERMESsonomx_public (clientes)
- **WhatsApp**: +52 1 555 1234567 (Integration)

---

## 🚀 Cómo Iniciar Sesión

### Desde Web (sonoradigitalcorp.com)

1. Ir a: **https://sonoradigitalcorp.com/**
2. Click en **"Entrar"** (esquina superior derecha)
3. Seleccionar **"Email y Contraseña"**
4. Ingresar credenciales (CEO o Cliente)
5. Click **"Continuar"**

**Primera vez:**
- Sistema valida 2FA (si está habilitado)
- Redirige a dashboard respectivo

---

### Desde Telegram (@HERMESsonomx_bot)

**CEO**:
```
/start → "Bienvenido Luis Daniel"
/status → Estado del sistema
/tasks → Mis tareas en Claude Code
/logs hermes-api → Logs en vivo
/mission-control → Link al dashboard
```

**Cliente**:
```
/start → "Bienvenido a HERMES"
/help → Ayuda disponible
/chat [pregunta] → Consulta a HERMES IA
/alert → Últimas alertas
```

---

## 🔐 Seguridad

- **Contraseñas**: Bcrypt 12-round (seguras)
- **JWT**: Token con TTL 24 horas
- **Revocación**: Por JTI en Redis
- **RLS**: PostgreSQL row-level security activado
- **HTTPS**: Solo HTTPS en producción

### Cambiar Contraseña

1. Login → Perfil (esquina arriba a derecha)
2. "Cambiar Contraseña"
3. Ingresa actual + nueva 2x
4. Confirma

**Requiere re-login después de cambio.**

---

## 🧪 Casos de Prueba Recomendados

### CEO — Full Exploration
- [ ] Login como CEO
- [ ] Ver Mission Control (todos los paneles)
- [ ] Ver logs en vivo
- [ ] Ejecutar `/status` en Telegram
- [ ] Ver tasks #1, #2, #3
- [ ] Verificar MCP integrations (GitHub, HF, etc)

### Cliente — Limited Access
- [ ] Login como Cliente
- [ ] Ver Dashboard Cliente (solo su tenant)
- [ ] Hacer pregunta a HERMES ("¿Cuáles son las mejores prácticas para restaurantes?")
- [ ] Recibir alertas (simula evento)
- [ ] Chat en Telegram: `/chat ¿horario?`

---

## 📊 Tenant Demo (Restaurante)

| Campo | Valor |
|-------|-------|
| ID | `tenant-restaurant-001` |
| Nombre | Restaurante El Faro |
| Plan | Pro |
| Users | 8 |
| Storage | 2.3GB / 10GB |
| Health | Healthy ✅ |

---

## 🆘 Troubleshooting

### "Credenciales inválidas"
→ Verifica email exacto (sensible a mayúsculas)
→ Password debe coincidir exactamente

### "Usuario no activado"
→ CEO debe activar user desde Admin Panel
→ O contacta: luis@sonoradigitalcorp.com

### "No puedo ver Mission Control"
→ Solo CEO tiene acceso
→ Login con luis@sonoradigitalcorp.com

### "JWT Token inválido"
→ Sesión expiró (24 horas)
→ Login de nuevo
→ O limpiar cookies + localStorage

---

## 📝 Notas de Desarrollo

**Contraseñas en DEMO**:
- NO son reales
- Cambialas en producción
- Usa `docker compose exec postgres psql` para actualizar

**Crear más usuarios**:
```sql
-- Insertar en usuarios tabla
INSERT INTO usuarios (email, nombre, contraseña_hash, rol, tenant_id, activo)
VALUES ('nuevo@email.com', 'Nombre', crypt('password123', gen_salt('bf')), 'user', 'tenant-id', true);
```

**Reset de contraseña**:
```bash
# Desde CLI VPS
curl -X POST https://api.sonoradigitalcorp.com/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email": "luis@sonoradigitalcorp.com"}'
```

---

**Última actualización**: 2026-04-16  
**Versión**: 1.0 (Demo)  
**Estado**: ✅ Listo para explorar
