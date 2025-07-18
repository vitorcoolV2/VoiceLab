#!/usr/bin/env bash
set -e

echo "📥 Script de download de modelos TTS"
echo "=================================="

# Carregar configurações
if [ -f "$(dirname "$0")/../config.env" ]; then
  source "$(dirname "$0")/../config.env"
fi

# Ativar conda
if command -v conda >/dev/null 2>&1; then
    CONDA_BASE=$(conda info --base)
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    conda activate coqui-tts
else
    echo "❌ Conda não encontrado. Execute ./scripts/install.sh primeiro."
    exit 1
fi

# Criar diretórios de cache
mkdir -p "$TTS_CACHE_DIR"
mkdir -p "$WHISPER_CACHE_DIR"

echo "🔧 Configurando diretórios de cache..."
export HF_HOME="$TTS_CACHE_DIR"
export TRANSFORMERS_CACHE="$TTS_CACHE_DIR"

# Lista de modelos TTS essenciais
MODELS=(
    "tts_models/multilingual/multi-dataset/xtts_v2"
    "tts_models/pt/cv/vits"
    "tts_models/pt/mai/tacotron2-DDC"
    "tts_models/en/ljspeech/tacotron2-DDC"
    "tts_models/en/vctk/vits"
    "tts_models/multilingual/multi-dataset/your_tts"
)

echo "📥 Baixando modelos TTS..."
for model in "${MODELS[@]}"; do
    echo "🔄 Baixando: $model"
    python -c "
import os
from TTS.api import TTS

try:
    print(f'Iniciando download de $model...')
    tts = TTS('$model')
    print(f'✅ $model baixado com sucesso!')
except Exception as e:
    print(f'❌ Erro ao baixar $model: {e}')
    exit(1)
" || {
        echo "⚠️ Erro ao baixar $model, continuando..."
    }
done

echo ""
echo "🎯 Modelos disponíveis:"
python -c "
from TTS.api import TTS
try:
    models = TTS().list_models()
    for model in models:
        print(f'  - {model}')
except Exception as e:
    print(f'❌ Erro ao listar modelos: {e}')
"

echo ""
echo "✅ Download de modelos concluído!"
echo "📁 Cache salvo em: $TTS_CACHE_DIR" 