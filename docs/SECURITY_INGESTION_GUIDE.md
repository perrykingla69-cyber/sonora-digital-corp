# 🔐 MYSTIC Security & Data Ingestion Guide

## ✅ Fixes de Seguridad Completados

### 1. Credenciales WhatsApp API Key

**Problema:** Password `MysticWA2026!` hardcodeada en 3 workflows N8N y main.py

**Solución:** 
- Workflows N8N ahora usan `{{ $env.WHATSAPP_API_KEY }}`
- main.py usa `os.getenv("WA_API_KEY", "fallback")`

**Archivos modificados:**
```
infra/n8n-workflows/Cierre_Mensual_Cerrado_WA.json
infra/n8n-workflows/Recordatorio_SAT_Dia_17.json  
infra/n8n-workflows/Webhook_Factura_Nueva_WA.json
backend/main.py
```

**Configuración requerida en VPS:**
```bash
# En /home/mystic/sonora-digital-corp/infra/.env.vps
WHATSAPP_API_KEY=tu_clave_segura_generada_aqui

# Generar clave segura
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📥 Data Ingestion Framework

### ¿Qué es?

Sistema que permite a usuarios conectar fuentes de datos externas (correo, cloud storage, carpetas) para ingestión automática de XMLs, PDFs y documentos fiscales.

### Fuentes Soportadas

| Fuente | Tipo | Autenticación | Uso |
|--------|------|---------------|-----|
| Gmail | IMAP OAuth2 | Google OAuth | Facturas por email |
| Outlook | Microsoft Graph | Azure AD | Corporate email |
| Dropbox | REST API | Access token | Cloud storage |
| Google Drive | REST API | Google OAuth | Cloud storage |
| Carpeta Local | Filesystem watch | N/A | Sync local |
| Webhook | HTTP POST | API Key | Integraciones |

---

## 🚀 Cómo Usar

### 1. Registrar Fuente de Datos

**Gmail:**
```bash
# Paso 1: Generar URL OAuth
python3 scripts/data_ingestor.py --source gmail --email nathaly@fourgea.mx --tenant fourgea --action oauth-url

# Paso 2: Abrir URL, autorizar, copiar código

# Paso 3: Registrar con token
python3 scripts/data_ingestor.py --source gmail --token CODIGO_OAUTH --tenant fourgea --interval 1800
```

**Dropbox:**
```bash
python3 scripts/data_ingestor.py --source dropbox --token SL.Bearer_TOKEN --tenant fourgea
```

**Carpeta Local:**
```bash
python3 scripts/data_ingestor.py --source folder --path /home/fourgea/facturas --tenant fourgea --interval 300
```

### 2. Sincronización Manual

```bash
python3 scripts/data_ingestor.py --action sync --source-id abc123 --tenant fourgea
```

### 3. Listar Fuentes

```bash
python3 scripts/data_ingestor.py --action list --tenant fourgea
```

---

## 🔄 Flujo Automático

```
Usuario registra fuente
        ↓
OAuth flow (si aplica)
        ↓
Guarda configuración en PostgreSQL
        ↓
Scheduler (cada N segundos)
        ↓
Conecta a fuente → Descarga archivos
        ↓
Procesa XML/PDF → Extrae datos
        ↓
Indexa en Qdrant (RAG)
        ↓
Guarda en PostgreSQL (tablas facturas/nomina)
        ↓
Notifica por WhatsApp si hay errores
```

---

## 📊 Endpoint API para Frontend

### POST /api/data-sources/register

```json
{
  "source_type": "gmail",
  "tenant_id": "fourgea",
  "email": "nathaly@fourgea.mx",
  "sync_interval": 1800,
  "filters": {
    "from": ["facturacion@proveedor.com"],
    "subject_contains": ["factura", "cfdi"],
    "extensions": [".xml", ".pdf"]
  }
}
```

### GET /api/data-sources/list?tenant=fourgea

```json
{
  "ok": true,
  "sources": [
    {
      "source_id": "abc123",
      "source_type": "gmail",
      "status": "active",
      "last_sync": "2026-01-15T10:30:00",
      "items_processed": 145,
      "next_sync": "2026-01-15T11:00:00"
    }
  ]
}
```

### POST /api/data-sources/sync

```json
{
  "source_id": "abc123",
  "tenant_id": "fourgea"
}
```

---

## 🔒 Consideraciones de Seguridad

### 1. Credenciales Encriptadas

En producción, las credenciales OAuth/tokens deben guardarse encriptadas en PostgreSQL:

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)
encrypted_token = cipher.encrypt(access_token.encode())
```

### 2. Permisos por Tenant

Cada tenant solo ve sus propias fuentes de datos:

```python
@app.get("/api/data-sources")
async def list_sources(tenant_id: str, current_user: User = Depends(get_current_user)):
    if current_user.tenant_id != tenant_id:
        raise HTTPException(403, "Acceso denegado")
```

### 3. Rate Limiting

Evitar abuso de APIs externas:

```python
@rate_limit(max_requests=10, window_seconds=60)
async def sync_source(...):
    ...
```

---

## 🧪 Testing

```bash
# Test carpeta local
mkdir -p /tmp/mystic-test
cp backend/tests/sample_xmls/*.xml /tmp/mystic-test/

python3 scripts/data_ingestor.py \
  --source folder \
  --path /tmp/mystic-test \
  --tenant test \
  --interval 60

# Verificar detección de archivos
python3 scripts/data_ingestor.py --action sync --source-id TEST123 --tenant test
```

---

## 📋 Próximos Pasos

1. **Implementar conexiones reales** a Gmail/Dropbox (ahora son stubs)
2. **Agregar encriptación** de credenciales en PostgreSQL
3. **Crear endpoint API** completo en main.py
4. **Integrar con frontend** dashboard de fuentes de datos
5. **Agregar webhooks** reversos para notificaciones push
6. **Soporte OneDrive** y Box.com

---

## 🆘 Troubleshooting

### Error: "OAuth token expired"
```bash
# Regenerar token
python3 scripts/data_ingestor.py --source gmail --email usuario@gmail.com --tenant fourgea --action oauth-url
```

### Error: "Folder not found"
```bash
# Verificar permisos
ls -la /ruta/carpeta
chmod 755 /ruta/carpeta
```

### Error: "Too many requests" (API rate limit)
```bash
# Aumentar intervalo de sync
python3 scripts/data_ingestor.py --source dropbox --token XXX --tenant fourgea --interval 7200
```
