# QUICK START — Mystic Content Generator
## HERMES AI — Campaña de Redes Sociales

---

## 1. Obtener FAL_KEY (gratis)

1. Ve a [https://fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)
2. Crea una cuenta gratuita con tu correo
3. En el dashboard, haz clic en **"Create API Key"**
4. Copia la key generada (empieza con `fal-...`)
5. Configúrala en tu terminal:

```bash
export FAL_KEY=fal-xxxxxxxxxxxxxxxxxxxxxxxx
```

> Costo aproximado: ~$0.01 USD por imagen. Con $5 generas ~500 imágenes.

---

## 2. Comandos principales

### Ver escenas disponibles
```bash
python3 generate_content.py --list
```

### Generar una escena específica
```bash
python3 generate_content.py --scene ceo
python3 generate_content.py --scene sat_warning
python3 generate_content.py --scene whatsapp_demo
```

### Generar múltiples variaciones de una escena
```bash
python3 generate_content.py --scene ceo --count 4
```

### Generar todas las escenas (batch completo)
```bash
python3 generate_content.py --batch
# o usar el script lanzador:
./launch_campaign.sh
```

---

## 3. Escenas disponibles

| Escena | Caption |
|---|---|
| `ceo` | La CEO. No pide permiso. Construye el sistema. |
| `podcast` | La Academia. Donde el conocimiento se convierte en poder. |
| `oracle` | La Oráculo. Todo tiene un propósito. Nada es accidente. |
| `rooftop` | El amanecer es para los que no durmieron construyendo. |
| `blockchain` | El dinero del futuro. Ella ya lo entiende. Y tú? |
| `boardroom` | Cuando ella habla, todos escuchan. Así funciona la autoridad. |
| `sat_warning` | El SAT no espera. Tú tampoco deberías. |
| `whatsapp_demo` | Tu contador en WhatsApp. 24/7. Sin excusas. |

---

## 4. Archivos generados

Cada imagen genera dos archivos en `./generated/`:

```
generated/
  mystic_ceo_20260326_143022_1.jpg         ← imagen para publicar
  mystic_ceo_20260326_143022_1_caption.txt ← texto listo para Instagram
```

El archivo `_caption.txt` contiene:
- Texto en español mexicano
- Hashtags relevantes (#HermesAI #ContabilidadMX #PYMEsMexicanas etc.)
- Call to action hacia sonoradigitalcorp.com

---

## 5. Publicar en redes sociales

### Instagram / TikTok
1. Descarga la imagen de `./generated/`
2. Abre el archivo `_caption.txt` correspondiente
3. Copia el texto completo
4. Publica la imagen y pega el caption

### Telegram automático
Configura las variables adicionales para envío automático al canal:

```bash
export TELEGRAM_TOKEN_BOT=tu_bot_token
export TELEGRAM_CHANNEL_ID=@TuCanal
```

Luego genera normalmente — la imagen se envía sola al canal.

---

## 6. Variables de entorno completas

```bash
# Requerida
export FAL_KEY=fal-xxxxxxxxxxxxxxxxxxxxxxxx

# Opcionales (para envío automático a Telegram)
export TELEGRAM_TOKEN_BOT=123456:ABCdef...
export TELEGRAM_CHANNEL_ID=@HermesAI
```

---

## 7. Flujo recomendado semanal

```bash
# Lunes: generar contenido de la semana
export FAL_KEY=fal-tu-key
./launch_campaign.sh

# Revisar imágenes generadas
ls ./generated/

# Programar publicaciones en Instagram
# (copiar imagen + caption de los .txt)
```
