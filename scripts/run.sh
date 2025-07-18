#!/bin/bash
set -e

# Sistema de estado
STATE_FILE="/tmp/coqui_tts_run.state"

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

# Ativar conda e ambiente correto
if [ "$CURRENT_STATE" = "INICIADO" ]; then
  echo "🔧 Ativando conda..."
  source "$MINICONDA_SSD/etc/profile.d/conda.sh"
  conda activate "$ENV_NAME"
  echo " Ambiente: $MINICONDA_SSD/envs/$ENV_NAME"
  echo "CONDA_ATIVADO" > "$STATE_FILE"
fi

# Verificar se os modelos TTS estão disponíveis
if [ "$CURRENT_STATE" = "CONDA_ATIVADO" ] || [ "$CURRENT_STATE" = "INICIADO" ]; then
  echo "🔍 Verificando modelos TTS..."
  python -c "
import os
from TTS.api import TTS

models_dir = os.path.expanduser('~/.local/share/tts')
required_models = [
    'tts_models/multilingual/multi-dataset/xtts_v2'
]

missing_models = []
for model in required_models:
    try:
        tts = TTS(model)
        print(f'✅ {model} - OK')
    except Exception as e:
        print(f'❌ {model} - FALTANDO: {e}')
        missing_models.append(model)

if missing_models:
    print(f'\\n⚠️ Modelos em falta: {missing_models}')
    print('Execute: ./scripts/install.sh para baixar os modelos')
    exit(1)
else:
    print('\\n✅ Todos os modelos TTS estão disponíveis!')
    exit(0)
" || {
    echo "❌ Alguns modelos TTS estão em falta. Execute ./scripts/install.sh primeiro."
    exit 1
  }
  
  echo "MODELOS_VERIFICADOS" > "$STATE_FILE"
fi

# Executar comando Python
if [ "$CURRENT_STATE" = "MODELOS_VERIFICADOS" ] || [ "$CURRENT_STATE" = "CONDA_ATIVADO" ] || [ "$CURRENT_STATE" = "INICIADO" ]; then
  echo "🚀 Iniciando o servidor Coqui TTS..."
  # Limpar estado antes de executar
  rm -f "$STATE_FILE"
  python src/tts_server.py
fi 