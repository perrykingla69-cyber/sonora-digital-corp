#!/bin/bash
# Install ComfyUI on VPS for ABE Music visual generation
# Run as root: bash infra/scripts/install_comfyui.sh

set -e
COMFYUI_DIR="/opt/comfyui"
MODELS_DIR="$COMFYUI_DIR/models/checkpoints"

echo "=== ComfyUI Install para ABE Music ==="

# 1. Dependencias del sistema
apt-get update -qq && apt-get install -y -qq git python3.12 python3.12-venv python3-pip wget curl

# 2. Clonar ComfyUI
if [ ! -d "$COMFYUI_DIR" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI "$COMFYUI_DIR"
    echo "✅ ComfyUI clonado"
else
    git -C "$COMFYUI_DIR" pull origin master --quiet
    echo "✅ ComfyUI actualizado"
fi

# 3. Virtualenv + dependencias
cd "$COMFYUI_DIR"
python3.12 -m venv venv
source venv/bin/activate
pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install --quiet -r requirements.txt
echo "✅ Dependencias instaladas"

# 4. Modelo SDXL-Turbo (CPU-friendly, rápido)
mkdir -p "$MODELS_DIR"
if [ ! -f "$MODELS_DIR/sd_xl_turbo_1.0_fp16.safetensors" ]; then
    echo "Descargando SDXL-Turbo (3.1GB) — puede tardar ~10 min..."
    wget -q --show-progress \
      "https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors" \
      -O "$MODELS_DIR/sd_xl_turbo_1.0_fp16.safetensors"
    echo "✅ Modelo descargado"
else
    echo "✅ Modelo ya existe"
fi

# 5. Systemd service
cat > /etc/systemd/system/comfyui.service << 'SERVICE'
[Unit]
Description=ComfyUI — ABE Music Visual Generator
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/comfyui
ExecStart=/opt/comfyui/venv/bin/python main.py --listen 0.0.0.0 --port 8188 --cpu
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable comfyui
systemctl start comfyui
echo "✅ ComfyUI service activo en :8188"
echo ""
echo "=== LISTO ==="
echo "ComfyUI UI:   http://localhost:8188"
echo "Proxy API:    http://localhost:8008/generate"
echo "Workflows:    thumbnail_artist | cover_album | social_post | promo_video"
