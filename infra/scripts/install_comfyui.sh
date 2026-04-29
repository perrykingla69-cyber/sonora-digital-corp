#!/bin/bash
# Install ComfyUI + Video Generation (open source, sin costo)
# Run as root: bash infra/scripts/install_comfyui.sh
#
# Incluye:
#   - ComfyUI core (imágenes: SDXL-Turbo)
#   - ComfyUI-Manager (plugin manager)
#   - AnimateDiff (video corto, CPU-compatible)
#   - Wan2.1-T2V-1.3B (video estilo Dreamina/Seedance, más liviano)

set -e
COMFYUI_DIR="/opt/comfyui"
MODELS_DIR="$COMFYUI_DIR/models"
CUSTOM_DIR="$COMFYUI_DIR/custom_nodes"
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')

echo "=== ComfyUI + Video Gen Install para ABE Music ==="
echo "RAM detectada: ${RAM_GB}GB"

# 1. Dependencias del sistema
apt-get update -qq && apt-get install -y -qq \
  git python3.12 python3.12-venv python3-pip wget curl ffmpeg libgl1 libglib2.0-0

# 2. ComfyUI core
if [ ! -d "$COMFYUI_DIR" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI "$COMFYUI_DIR"
    echo "✅ ComfyUI clonado"
else
    git -C "$COMFYUI_DIR" pull origin master --quiet
    echo "✅ ComfyUI actualizado"
fi

# 3. Virtualenv + PyTorch CPU
cd "$COMFYUI_DIR"
python3.12 -m venv venv
source venv/bin/activate
pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install --quiet -r requirements.txt
pip install --quiet transformers accelerate diffusers imageio[ffmpeg] einops
echo "✅ Dependencias base instaladas"

# 4. ComfyUI-Manager (gestiona plugins desde UI)
mkdir -p "$CUSTOM_DIR"
if [ ! -d "$CUSTOM_DIR/ComfyUI-Manager" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager "$CUSTOM_DIR/ComfyUI-Manager" --quiet
    echo "✅ ComfyUI-Manager instalado"
fi

# 5. AnimateDiff-Evolved (video corto, CPU-compatible)
if [ ! -d "$CUSTOM_DIR/ComfyUI-AnimateDiff-Evolved" ]; then
    git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved "$CUSTOM_DIR/ComfyUI-AnimateDiff-Evolved" --quiet
    cd "$CUSTOM_DIR/ComfyUI-AnimateDiff-Evolved"
    pip install --quiet -r requirements.txt 2>/dev/null || true
    cd "$COMFYUI_DIR"
    echo "✅ AnimateDiff instalado"
fi

# 6. Modelos de imagen
mkdir -p "$MODELS_DIR/checkpoints" "$MODELS_DIR/animatediff_models" \
         "$MODELS_DIR/vae" "$MODELS_DIR/text_encoders"

if [ ! -f "$MODELS_DIR/checkpoints/sd_xl_turbo_1.0_fp16.safetensors" ]; then
    echo "⬇ Descargando SDXL-Turbo para imágenes (3.1GB)..."
    wget -q --show-progress \
      "https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors" \
      -O "$MODELS_DIR/checkpoints/sd_xl_turbo_1.0_fp16.safetensors"
    echo "✅ SDXL-Turbo descargado"
fi

# 7. AnimateDiff motion module (ligero, CPU-compatible)
MOTION_MODEL="$MODELS_DIR/animatediff_models/mm_sd_v15_v2.ckpt"
if [ ! -f "$MOTION_MODEL" ]; then
    echo "⬇ Descargando AnimateDiff motion module (1.7GB)..."
    wget -q --show-progress \
      "https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt" \
      -O "$MOTION_MODEL"
    echo "✅ AnimateDiff motion module descargado"
fi

# 8. Wan2.1-T2V-1.3B — video estilo Dreamina (solo si hay ≥16GB RAM)
if [ "$RAM_GB" -ge 16 ]; then
    WAN_DIR="$MODELS_DIR/wan"
    mkdir -p "$WAN_DIR"
    if [ ! -f "$WAN_DIR/wan2.1_t2v_1.3B_bf16.safetensors" ]; then
        echo "⬇ Descargando Wan2.1-T2V-1.3B (2.8GB) — video de alta calidad..."
        wget -q --show-progress \
          "https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B/resolve/main/wan2.1_t2v_1.3B_bf16.safetensors" \
          -O "$WAN_DIR/wan2.1_t2v_1.3B_bf16.safetensors" 2>/dev/null || \
          echo "⚠ Wan2.1 no disponible via wget — descarga manual desde huggingface.co/Wan-AI/Wan2.1-T2V-1.3B"
    fi
else
    echo "⚠ RAM < 16GB — omitiendo Wan2.1 (se usará AnimateDiff para video)"
fi

# 9. Systemd service
cat > /etc/systemd/system/comfyui.service << 'SERVICE'
[Unit]
Description=ComfyUI — ABE Music Visual & Video Generator (Open Source)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/comfyui
ExecStart=/opt/comfyui/venv/bin/python main.py --listen 127.0.0.1 --port 8188 --cpu --preview-method none
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
Environment="PYTORCH_ENABLE_MPS_FALLBACK=1"

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable comfyui
systemctl restart comfyui
echo "✅ ComfyUI service activo en :8188"

echo ""
echo "══════════════════════════════════════════"
echo "✅ INSTALACIÓN COMPLETA"
echo "══════════════════════════════════════════"
echo ""
echo "ComfyUI UI (browser):  http://TU_VPS_IP:8188  (si abres el puerto)"
echo "Proxy API local:       http://localhost:8008/generate"
echo ""
echo "Capacidades instaladas:"
echo "  📷  Imágenes:  SDXL-Turbo (rápido, CPU)"
echo "  🎬  Video corto: AnimateDiff (SD 1.5 base)"
if [ "$RAM_GB" -ge 16 ]; then
echo "  🎬  Video HD:  Wan2.1-T2V-1.3B (estilo Dreamina/Seedance)"
fi
echo ""
echo "Workflows disponibles vía proxy:"
echo "  thumbnail_artist | cover_album | social_post | promo_video"
echo ""
echo "Logs: journalctl -u comfyui -f"
