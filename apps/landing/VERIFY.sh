#!/bin/bash

# Sonora Landing — Verification script
# Verifica que todos los archivos están en su lugar

set -e

echo "🔍 Verificando estructura de Sonora Landing..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
  if [ -f "$1" ]; then
    echo -e "${GREEN}✓${NC} $1"
  else
    echo -e "${RED}✗${NC} $1"
    return 1
  fi
}

check_dir() {
  if [ -d "$1" ]; then
    echo -e "${GREEN}✓${NC} $1/"
  else
    echo -e "${RED}✗${NC} $1/"
    return 1
  fi
}

# Config files
echo "📋 Archivos de configuración:"
check_file "package.json"
check_file "tsconfig.json"
check_file "tailwind.config.ts"
check_file "postcss.config.js"
check_file "next.config.ts"
check_file ".eslintrc.json"
check_file ".gitignore"

echo ""
echo "📂 Directorios:"
check_dir "app"
check_dir "components"
check_dir "lib"

echo ""
echo "📄 Archivos en app/:"
check_file "app/layout.tsx"
check_file "app/page.tsx"
check_file "app/globals.css"

echo ""
echo "🎨 Componentes:"
check_file "components/Navbar.tsx"
check_file "components/Hero.tsx"
check_file "components/VisionStatement.tsx"
check_file "components/CasosDeUso.tsx"
check_file "components/Pilares.tsx"
check_file "components/Stats.tsx"
check_file "components/DemoChat.tsx"
check_file "components/Testimonios.tsx"
check_file "components/Footer.tsx"

echo ""
echo "📚 Librerías:"
check_file "lib/animations.ts"
check_file "lib/utils.ts"

echo ""
echo "📖 Documentación:"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "ARCHITECTURE.md"

echo ""
echo "✨ Verificación completada!"
echo ""
echo "🚀 Próximo paso:"
echo "  npm install"
echo "  npm run dev"
echo ""
