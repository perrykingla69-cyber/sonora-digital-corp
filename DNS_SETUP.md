# DNS Setup para HERMES OS

## 🎯 Objetivo
Hacer que los 6 subdomios de HERMES resuelvan correctamente en DNS.

## 📊 Estado Actual
- ✅ `sonoradigitalcorp.com` → `187.124.85.191` (FUNCIONANDO)
- ❌ `restaurante.sonoradigitalcorp.com` → NO RESUELVE
- ❌ `contador.sonoradigitalcorp.com` → NO RESUELVE
- ❌ `pastelero.sonoradigitalcorp.com` → NO RESUELVE
- ❌ `abogado.sonoradigitalcorp.com` → NO RESUELVE
- ❌ `fontanero.sonoradigitalcorp.com` → NO RESUELVE
- ❌ `consultor.sonoradigitalcorp.com` → NO RESUELVE

## ⚙️ Configuración Necesaria (Hostinger Panel)

### Opción 1: WILDCARD (Recomendado - 1 registro)
Panel → DNS Zone Editor → sonoradigitalcorp.com → Add Record

```
Type:   A Record
Name:   * (asterisco)
Value:  187.124.85.191
TTL:    3600 (default)
```

**Resultado:** `*.sonoradigitalcorp.com` → `187.124.85.191`

---

### Opción 2: Registros Individuales (6 registros)

Panel → DNS Zone Editor → sonoradigitalcorp.com → Add Record (x6)

```
#1
Type:   A Record
Name:   restaurante
Value:  187.124.85.191
TTL:    3600

#2
Type:   A Record
Name:   contador
Value:  187.124.85.191
TTL:    3600

#3
Type:   A Record
Name:   pastelero
Value:  187.124.85.191
TTL:    3600

#4
Type:   A Record
Name:   abogado
Value:  187.124.85.191
TTL:    3600

#5
Type:   A Record
Name:   fontanero
Value:  187.124.85.191
TTL:    3600

#6
Type:   A Record
Name:   consultor
Value:  187.124.85.191
TTL:    3600
```

## ✅ Verificación

Después de guardar, espera **5-15 minutos** para propagación y verifica:

```bash
# En terminal/VPS:
dig restaurante.sonoradigitalcorp.com
dig contador.sonoradigitalcorp.com
# etc...

# Debe mostrar:
# restaurante.sonoradigitalcorp.com. 3600 IN A 187.124.85.191
```

O en navegador:
```
https://restaurante.sonoradigitalcorp.com/
https://contador.sonoradigitalcorp.com/
# etc...
```

## 🔗 Nginx ya está configurado

Los subdomios apuntan internamente a `localhost:3000` (frontend):

```nginx
server_name restaurante.sonoradigitalcorp.com contador.sonoradigitalcorp.com ...;
location / {
    proxy_pass http://127.0.0.1:3000;
    ...
}
```

Una vez DNS esté listo, todo funcionará automáticamente.

## 📞 Soporte Hostinger

Si necesitas ayuda en el panel:
- Hostinger Help: https://support.hostinger.com/en/articles/4672018-dns-zone-editor
- Chat: support@hostinger.com
