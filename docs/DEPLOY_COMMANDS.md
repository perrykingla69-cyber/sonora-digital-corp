# 🚀 COMANDOS PARA DEPLOY - MYSTIC Security + Data Ingestion

## Copia y pega estos comandos en tu VPS (187.124.85.191)

---

## 1️⃣ PULL DEL CÓDIGO ACTUALIZADO

```bash
cd /home/mystic/sonora-digital-corp
sudo git pull origin main
```

---

## 2️⃣ GENERAR API KEY SEGURA PARA WHATSAPP

```bash
# Generar clave aleatoria segura
WHATSAPP_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "TU_API_KEY=$WHATSAPP_API_KEY"

# Guardar en .env.vps
cd /home/mystic/sonora-digital-corp/infra
echo "WHATSAPP_API_KEY=$WHATSAPP_API_KEY" >> .env.vps

# Verificar que se guardó
grep WHATSAPP_API_KEY .env.vps
```

---

## 3️⃣ RECREAR CONTENEDORES CON NUEVAS VARIABLES

```bash
cd /home/mystic/sonora-digital-corp/infra

# Recrear WhatsApp API con nueva variable
docker compose -f docker-compose.vps.yml --env-file .env.vps up -d --force-recreate wa

# Recrear API backend
docker compose -f docker-compose.vps.yml --env-file .env.vps up -d --force-recreate api

# Ver logs
docker logs -f mystic-wa-1 --tail 20
docker logs -f mystic-api-1 --tail 20
```

---

## 4️⃣ IMPORTAR WORKFLOWS ACTUALIZADOS A N8N

```bash
# Los workflows ya están en infra/n8n-workflows/
# Importar manualmente desde UI de N8N o usar script:

cd /home/mystic/sonora-digital-corp
python3 scripts/import_n8n_workflows.py 2>&1 | tail -20

# O importar uno por uno desde https://sonoradigitalcorp.com/n8n
# Workflows actualizados (sin password hardcodeada):
# - Cierre_Mensual_Cerrado_WA.json
# - Recordatorio_SAT_Dia_17.json
# - Webhook_Factura_Nueva_WA.json
```

---

## 5️⃣ CONFIGURAR DATA INGESTION PARA FOURGEA

### Opción A: Carpeta Local (Recomendado para empezar)

```bash
# Crear carpeta de ingestión para Fourgea
mkdir -p /home/fourgea/facturas-entrada
chown -R mystic:mystic /home/fourgea/facturas-entrada

# Registrar fuente de datos
cd /home/mystic/sonora-digital-corp
python3 scripts/data_ingestor.py \
  --source folder \
  --path /home/fourgea/facturas-entrada \
  --tenant fourgea \
  --interval 300 \
  --action register

# Copiar XMLs de prueba
cp /home/mystic/sonora-digital-corp/backend/tests/sample_xmls/*.xml /home/fourgea/facturas-entrada/

# Ejecutar sync manual para probar
python3 scripts/data_ingestor.py \
  --action sync \
  --source-id SOURCE_ID_DEL_OUTPUT_ANTERIOR \
  --tenant fourgea
```

### Opción B: Gmail con OAuth

```bash
# Paso 1: Generar URL OAuth
cd /home/mystic/sonora-digital-corp
python3 scripts/data_ingestor.py \
  --source gmail \
  --email nathaly@fourgea.mx \
  --tenant fourgea \
  --action oauth-url

# Paso 2: Nathaly debe:
# 1. Abrir la URL que aparece
# 2. Autorizar acceso a su Gmail
# 3. Copiar el código de autorización

# Paso 3: Registrar con el código
python3 scripts/data_ingestor.py \
  --source gmail \
  --token CODIGO_COPIADO \
  --tenant fourgea \
  --interval 1800
```

### Opción C: Dropbox

```bash
# Nathaly debe generar token en https://www.dropbox.com/developers/apps
# Luego:
python3 scripts/data_ingestor.py \
  --source dropbox \
  --token SL.Bearer_TOKEN_DE_DROPBOX \
  --tenant fourgea \
  --interval 3600
```

---

## 6️⃣ VERIFICAR QUE TODO FUNCIONA

```bash
# Test WhatsApp API con nueva clave
curl -X POST http://localhost:3001/send \
  -H "Content-Type: application/json" \
  -H "x-api-key: TU_API_KEY_GENERADA" \
  -d '{"to": "6622681111@s.whatsapp.net", "message": "Test seguridad OK"}'

# Test endpoint data sources
curl http://localhost:8000/api/data-sources/list?tenant=fourgea \
  -H "Authorization: Bearer TU_JWT_TOKEN"

# Ver logs del backend
docker logs mystic-api-1 --tail 50 | grep -i "ingest\|data\|source"
```

---

## 7️⃣ AGREGAR ENDPOINTS AL FRONTEND

### Dashboard de Fuentes de Datos

Agregar esta sección en el dashboard después del login:

```html
<!-- Sección: Fuentes de Datos -->
<div class="card">
  <h3>📥 Fuentes de Datos</h3>
  
  <!-- Botón agregar fuente -->
  <button onclick="showAddSourceModal()">+ Nueva Fuente</button>
  
  <!-- Lista de fuentes -->
  <div id="sources-list">
    <!-- Se llena dinámicamente con GET /api/data-sources -->
  </div>
</div>

<!-- Modal agregar fuente -->
<div id="add-source-modal">
  <select id="source-type">
    <option value="folder">📁 Carpeta Local</option>
    <option value="gmail">📧 Gmail</option>
    <option value="dropbox">☁️ Dropbox</option>
  </select>
  
  <input id="source-path" placeholder="Ruta de carpeta" />
  <input id="source-email" placeholder="Email (para OAuth)" />
  
  <button onclick="registerSource()">Registrar</button>
</div>

<script>
async function registerSource() {
  const type = document.getElementById('source-type').value;
  const path = document.getElementById('source-path').value;
  const email = document.getElementById('source-email').value;
  
  const response = await fetch('/api/data-sources/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      source_type: type,
      tenant_id: 'fourgea',
      path: path || null,
      email: email || null,
      sync_interval: 1800
    })
  });
  
  const result = await response.json();
  alert(result.message);
}
</script>
```

---

## 8️⃣ AUTOMATIZACIÓN CON CRON

```bash
# Agregar al crontab de mystic
crontab -e

# Sync automático cada hora para todas las fuentes
0 * * * * cd /home/mystic/sonora-digital-corp && python3 scripts/sync_all_sources.py >> /var/log/mystic-ingest.log 2>&1

# Limpieza semanal de cachés
0 3 * * 0 /home/mystic/sonora-digital-corp/scripts/optimize_ram.sh >> /var/log/mystic-optimize.log 2>&1
```

---

## 9️⃣ MONITOREO Y ALERTAS

```bash
# Script de monitoreo
cat > /home/mystic/sonora-digital-corp/scripts/monitor_ingestion.sh << 'EOF'
#!/bin/bash
# Verificar estado de ingestión

SOURCES=$(docker exec mystic-api psql -U mystic -d mystic_db -c \
  "SELECT COUNT(*) FROM data_sources WHERE enabled=true;" 2>/dev/null)

LAST_SYNC=$(docker exec mystic-api psql -U mystic -d mystic_db -c \
  "SELECT MAX(last_sync) FROM data_sources;" 2>/dev/null)

echo "📊 Estado Data Ingestion"
echo "Fuentes activas: $SOURCES"
echo "Último sync: $LAST_SYNC"

# Alertar si último sync fue hace más de 2 horas
if [ $(date -d "$LAST_SYNC" +%s) -lt $(($(date +%s) - 7200)) ]; then
  echo "⚠️ ALERTA: Sync atrasado más de 2 horas"
  # Enviar notificación WhatsApp aquí
fi
EOF

chmod +x /home/mystic/sonora-digital-corp/scripts/monitor_ingestion.sh

# Ejecutar cada 30 minutos
(crontab -l 2>/dev/null; echo "*/30 * * * * /home/mystic/sonora-digital-corp/scripts/monitor_ingestion.sh") | crontab -
```

---

## 🔟 TESTING COMPLETO

```bash
# 1. Subir XML a carpeta monitoreada
cp /home/mystic/sonora-digital-corp/backend/tests/sample_xmls/factura_001.xml /home/fourgea/facturas-entrada/

# 2. Esperar 5 minutos o forzar sync
python3 scripts/data_ingestor.py --action sync --source-id XXX --tenant fourgea

# 3. Verificar en PostgreSQL
docker exec mystic-postgres psql -U mystic -d mystic_db -c \
  "SELECT uuid, proveedor, total, fecha FROM facturas ORDER BY created_at DESC LIMIT 5;"

# 4. Preguntar al Brain
curl -X POST http://localhost:8000/api/brain/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuántas facturas tengo de este mes?", "tenant_id": "fourgea"}'
```

---

## 📋 CHECKLIST FINAL

- [ ] Código actualizado en VPS (`git pull`)
- [ ] API Key WhatsApp generada y guardada en `.env.vps`
- [ ] Contenedores recreados (`docker compose up -d --force-recreate`)
- [ ] Workflows N8N importados (sin passwords hardcodeadas)
- [ ] Al menos una fuente de datos registrada para Fourgea
- [ ] Testing de ingestión completado exitosamente
- [ ] Frontend actualizado con sección de fuentes de datos
- [ ] Cron jobs configurados para sync automático
- [ ] Monitoreo activo con alertas

---

## 🆘 SOPORTE

Si algo falla:

```bash
# Ver logs completos
docker logs mystic-api-1 --tail 200
docker logs mystic-wa-1 --tail 200
docker logs mystic-n8n-1 --tail 200

# Reiniciar todo
cd /home/mystic/sonora-digital-corp/infra
docker compose -f docker-compose.vps.yml down
docker compose -f docker-compose.vps.yml up -d

# Verificar variables de entorno
docker exec mystic-api env | grep -i "WA_API\|WHATSAPP"
```

---

## 📞 CONTACTO

Problemas con OAuth de Google/Microsoft:
- Revisar que el dominio esté verificado en consola de desarrollador
- Asegurar que los scopes sean correctos

Problemas con Dropbox/Drive:
- Verificar que el token no haya expirado
- Regenerar token si es necesario

Problemas con carpetas locales:
- `ls -la /ruta/carpeta` para verificar permisos
- `chmod 755 /ruta/carpeta` si es necesario
