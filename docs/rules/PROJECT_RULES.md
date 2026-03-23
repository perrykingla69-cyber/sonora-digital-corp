# REGLAS DEL PROYECTO MYSTIC / SONORA DIGITAL CORP

## 1. ARQUITECTURA Y ESTRUCTURA

### 1.1 Principios Generales
- **Monorepo estricto**: Todo el código debe estar en `packages/`, `apps/`, `backend/`, `frontend/`
- **Cero código huérfano**: Todo archivo debe ser importado o referenciado en algún lugar
- **Separación de responsabilidades**:
  - `backend/`: API, lógica de negocio, integraciones
  - `frontend/`: UI, componentes React, páginas
  - `packages/`: Librerías compartidas, tipos, utilidades
  - `apps/`: Aplicaciones independientes (CLI, bots, bridges)
  - `infra/`: Configuración de infraestructura, Docker, nginx

### 1.2 Convenciones de Nombres
```
Archivos Python:      snake_case.py
Archivos TypeScript:  PascalCase.tsx (componentes), camelCase.ts (utilidades)
Clases:               PascalCase
Funciones/Variables:  snake_case (Python), camelCase (TypeScript)
Constantes:           UPPER_SNAKE_CASE
Endpoints API:        kebab-case
```

### 1.3 Estructura de Imports
```python
# Python: Orden estricto
1. Librerías estándar (typing, datetime, etc.)
2. Librerías de terceros (fastapi, pydantic, etc.)
3. Imports internos del proyecto (from app..., from packages...)
```
```typescript
// TypeScript: Orden estricto
1. React/Next.js
2. Librerías externas (framer-motion, etc.)
3. Componentes internos (@/components)
4. Utilidades internas (@/lib)
```

---

## 2. DESARROLLO Y CÓDIGO

### 2.1 Reglas de Código Python
- Siempre usar type hints en funciones públicas
- Siempre usar Pydantic para validación de datos de entrada
- Nunca usar `print()` para logging, usar `logging` module
- Siempre manejar excepciones con `try/except` específicos
- Nunca hardcodear URLs o credenciales, usar variables de entorno

### 2.2 Reglas de Código TypeScript/React
- Siempre usar componentes funcionales con hooks
- Siempre tipar props con interfaces
- Nunca usar `any`, definir tipos explícitos
- Siempre usar Tailwind para estilos, evitar CSS modules salvo excepciones
- Nunca usar `var`, solo `const` y `let`

### 2.3 Manejo de Errores
```python
# Correcto
try:
    result = await process_data()
except SpecificException as e:
    logger.error(f"Error procesando datos: {e}")
    raise HTTPException(status_code=400, detail=str(e))

# Incorrecto
try:
    result = process_data()
except:
    print("error")
    return None
```

---

## 3. INFRAESTRUCTURA Y DEPLOY

### 3.1 Docker
- Siempre usar imágenes Alpine cuando sea posible
- Nunca exponer puertos de base de datos al exterior
- Siempre usar healthchecks en servicios críticos
- Siempre usar `restart: unless-stopped`

### 3.2 Variables de Entorno
- Archivo `.env` en `infra/` para desarrollo local
- Archivo `.env.vps` en `infra/` para producción (nunca en git)
- Nunca commitear archivos `.env` con valores reales

### 3.3 Git
- Commits semánticos: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Siempre hacer pull antes de push
- Nunca hacer force push a `main`
- Siempre usar branches para features: `feat/nombre-descriptivo`

---

## 4. INTEGRACIONES Y APIs

### 4.1 WhatsApp
- Usar `whatsapp-web.js` (gratuito) para QR en dashboard
- Nunca almacenar sesiones en git (usar volumen Docker)
- Siempre reconectar automáticamente ante desconexiones

### 4.2 Telegram
- Bot token en variable de entorno `TELEGRAM_BOT_TOKEN`
- Siempre responder con contexto del tenant
- Nunca exponer información de un tenant a otro

### 4.3 SAT/Fiscal
- Siempre validar CFDI contra servicio oficial del SAT
- Nunca cachear respuestas de validación por más de 1 hora
- Siempre mantener cadena de fundamentos legales

---

## 5. MULTI-TENANT Y SEGURIDAD

### 5.1 Aislamiento de Datos
- Cada tenant tiene su propio schema en PostgreSQL (cuando aplique)
- Nunca mezclar datos de diferentes tenants
- Siempre validar `tenant_id` en cada request

### 5.2 Autenticación
- JWT con expiración de 24 horas
- Refresh tokens de 7 días
- Siempre validar token en endpoints protegidos

### 5.3 Auditoría
- Siempre loggear: quién, qué, cuándo, desde qué IP/canal

---

## 6. FRONTEND Y UX

### 6.1 Diseño
- Siempre usar tema oscuro como base
- Paleta de colores:
  - Cyan `#00D4FF` (primario)
  - Magenta `#FF006E` (secundario)
  - Emerald `#10B981` (éxito)
  - Amber `#F59E0B` (advertencia)
  - Rose `#F43F5E` (error)
- Siempre usar glassmorphism (`backdrop-blur`)
- Siempre animaciones con `framer-motion`

### 6.2 Responsive
- Mobile-first approach
- Breakpoints: `sm` (640px), `md` (768px), `lg` (1024px), `xl` (1280px)
- Nunca usar valores fijos de px para layouts

### 6.3 Performance
- Siempre usar `next/image` para imágenes
- Siempre lazy load de componentes pesados
- Nunca cargar datos en el render, usar `useEffect`

---

## 7. TESTING Y CALIDAD

### 7.1 Tests Obligatorios
- Unit tests para funciones de utilidad
- Integration tests para endpoints críticos
- Siempre testear casos de error

### 7.2 Linting
- Python: `black`, `isort`, `flake8`
- TypeScript: `eslint`, `prettier`
- Siempre correr linter antes de commit

---

## 8. PROCESOS DE NEGOCIO

### 8.1 Flujo de Cliente Nuevo
1. Landing page → Captura lead
2. Onboarding → Crear tenant
3. Configuración → Conectar WhatsApp/Telegram
4. Activación → Primera interacción con Brain
5. Retención → Alertas predictivas + contenido

### 8.2 Flujo de Facturación
1. Validar CFDI con SAT
2. Almacenar en base de datos del tenant
3. Actualizar estado contable
4. Notificar al usuario vía canal activo
5. Generar complemento de pago si aplica

### 8.3 Flujo de MVE
1. Recopilar datos de operación
2. Análisis de razonamiento fiscal
3. Validación documental
4. Generación de borrador
5. Revisión humana (si riesgo alto)
6. Presentación ante aduana

---

## 9. CHECKLIST ANTES DE COMMIT

- [ ] Código pasa linter sin errores
- [ ] No hay `console.log` o `print` de debug
- [ ] Variables de entorno documentadas en `.env.example`
- [ ] Nuevas dependencias agregadas a `requirements.txt` o `package.json`
- [ ] Tests pasan (si existen)
- [ ] Documentación actualizada (si aplica)
- [ ] Commit message sigue convención semántica

---

**Última actualización:** 2026-03-23
**Versión:** 1.0
**Aprobado por:** Marco (CEO)
