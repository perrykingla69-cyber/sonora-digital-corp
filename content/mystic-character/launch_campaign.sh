#!/bin/bash
# Lanzador de campaña Mystic — HERMES
# Uso: ./launch_campaign.sh

echo "🚀 HERMES — Generador de Campaña Mystic"
echo "========================================"

# Verificar FAL_KEY
if [ -z "$FAL_KEY" ]; then
  echo "❌ FAL_KEY no configurada."
  echo "   1. Ve a https://fal.ai/dashboard/keys"
  echo "   2. Crea una cuenta gratuita"
  echo "   3. Copia tu API key"
  echo "   4. Ejecuta: export FAL_KEY=tu_key"
  echo "   5. Vuelve a correr este script"
  exit 1
fi

echo "✅ FAL_KEY detectada"
echo ""
echo "Generando batch completo de imágenes..."
cd "$(dirname "$0")"
python3 generate_content.py --batch
echo ""
echo "✅ Imágenes generadas en ./generated/"
echo "   Listas para Instagram, TikTok y Telegram"
