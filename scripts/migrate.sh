#!/bin/bash
set -e

# Sistema de estado
STATE_FILE="/tmp/coqui_tts_migrate.state"

echo "🚀 Starting Model Migration to External SSD"
echo "=============================================="

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
  echo "CONDA_ATIVADO" > "$STATE_FILE"
fi

# Verificar diretório
if [ "$CURRENT_STATE" = "CONDA_ATIVADO" ] || [ "$CURRENT_STATE" = "INICIADO" ]; then
  if [ ! -f "src/tts_server.py" ]; then
    echo "❌ Please run this script from the coqui-tts root directory"
    exit 1
  fi
  echo "DIRETORIO_VERIFICADO" > "$STATE_FILE"
fi

# Executar migração
if [ "$CURRENT_STATE" = "DIRETORIO_VERIFICADO" ]; then
  echo "📦 Running migration script..."
  python tools/migration/migrate_models_to_ssd.py
  
  if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Migration completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Restart the TTS server: ./start.sh"
    echo "2. Test GPU acceleration: python tests/whisper/test_gpu_compatibility.py"
    echo ""
    echo "✅ Your models are now on the external SSD and GPU acceleration is enabled!"
    echo ""
    echo "✅ Variáveis de ambiente carregadas do .env para modelos externos."
    
    # Limpar estado
    rm -f "$STATE_FILE"
  else
    echo ""
    echo "❌ Migration failed. Please check the error messages above."
    echo "💡 Para tentar novamente: rm -f $STATE_FILE"
    exit 1
  fi
fi 