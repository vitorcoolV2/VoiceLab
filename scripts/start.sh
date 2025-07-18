#!/bin/bash
set -e

# Sistema de estado
STATE_FILE="/tmp/coqui_tts_start.state"

echo " Starting Coqui TTS & Whisper Server"
echo "======================================"

# Carregar variáveis de ambiente do config.env, se existir
if [ -f "$(dirname "$0")/../config.env" ]; then
  set -a
  source "$(dirname "$0")/../config.env"
  set +a
  echo "🌱 Variáveis de ambiente do config.env carregadas."
fi

# Verificar estado atual
CURRENT_STATE=$(cat "$STATE_FILE" 2>/dev/null || echo "INICIADO")
echo " Continuando de: $CURRENT_STATE"

# Ativar conda
if [ "$CURRENT_STATE" = "INICIADO" ]; then
  echo "🔧 Ativando conda..."
  source "$MINICONDA_SSD/etc/profile.d/conda.sh"
  conda activate "$ENV_NAME"
  echo " Ambiente: $MINICONDA_SSD/envs/$ENV_NAME"
  echo "🔧 GPU: NVIDIA GeForce RTX 3060 (CUDA 12.8)"
  echo "$CURRENT_STATE" > "$STATE_FILE"
  echo "CONDA_ATIVADO" > "$STATE_FILE"
fi

# Verificar servidor em execução
if [ "$CURRENT_STATE" = "CONDA_ATIVADO" ] || [ "$CURRENT_STATE" = "INICIADO" ]; then
  if pgrep -f "python src/tts_server.py" > /dev/null; then
    echo "⚠️  Server is already running. Stopping existing instance..."
    pkill -f "python src/tts_server.py"
    sleep 2
  fi
  echo "SERVIDOR_PARADO" > "$STATE_FILE"
fi

# Verificar porta
if [ "$CURRENT_STATE" = "SERVIDOR_PARADO" ]; then
  if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use. Stopping existing process..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
  fi
  echo "PORTA_LIVRE" > "$STATE_FILE"
fi

# Criar diretórios
if [ "$CURRENT_STATE" = "PORTA_LIVRE" ]; then
  mkdir -p output logs downloads
  echo "DIRETORIOS_CRIADOS" > "$STATE_FILE"
fi

# Iniciar servidor
if [ "$CURRENT_STATE" = "DIRETORIOS_CRIADOS" ]; then
  echo "🎤 Starting TTS & Whisper server..."
  echo "📡 Server will be available at: http://localhost:8000"
  echo " API Documentation: http://localhost:8000/docs"
  echo ""
  echo "Press Ctrl+C to stop the server"
  echo ""
  
  # Limpar estado antes de iniciar
  rm -f "$STATE_FILE"
  
  python src/tts_server.py
fi 