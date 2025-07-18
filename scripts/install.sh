#!/usr/bin/env bash
set -e

# Carregar variáveis de ambiente do .env, se existir
if [ -f "$(dirname "$0")/../.env" ]; then
    echo "🌱 Carregando variáveis de ambiente do .env..."
    source "$(dirname "$0")/../.env"
    echo "🌱 Variáveis de ambiente do .env carregadas."
fi

# Tentar encontrar o conda.sh automaticamente
if command -v conda >/dev/null 2>&1; then
    # Encontrar o diretório base do conda
    CONDA_BASE=$(conda info --base)
    CONDA_SH="$CONDA_BASE/etc/profile.d/conda.sh"
    if [ -f "$CONDA_SH" ]; then
        source "$CONDA_SH"
    else
        echo "❌ Não foi possível encontrar $CONDA_SH. Verifique a instalação do Conda." >&2
        exit 1
    fi
else
    # Tentar caminhos comuns
    for CANDIDATO in \
        "$HOME/miniconda3/etc/profile.d/conda.sh" \
        "/media/vitor/ssd990/miniconda3/etc/profile.d/conda.sh" \
        "/opt/miniconda3/etc/profile.d/conda.sh"; do
        if [ -f "$CANDIDATO" ]; then
            source "$CANDIDATO"
            break
        fi
    done
    if ! command -v conda >/dev/null 2>&1; then
        echo "❌ Conda não encontrado no PATH nem em locais comuns. Instale o Miniconda/Anaconda ou adicione ao PATH." >&2
        exit 1
    fi
fi

# Verificar e instalar dependências do sistema
echo "🔧 Verificando dependências do sistema..."
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "📦 Instalando ffmpeg..."
    sudo apt-get update && sudo apt-get install -y ffmpeg
fi

if ! command -v sox >/dev/null 2>&1; then
    echo "📦 Instalando sox..."
    sudo apt-get install -y sox
fi

if ! command -v espeak-ng >/dev/null 2>&1; then
    echo "📦 Instalando espeak-ng..."
    sudo apt-get install -y espeak-ng
fi

# Definir diretório temporário no SSD externo para evitar encher o disco do sistema
TMPDIR="/media/vitor/ssd990/tmp"
mkdir -p "$TMPDIR"
export TMPDIR

# Verificar se o ambiente atual está ativo e desativá-lo
CURRENT_ENV=$(conda info --envs | grep '*' | awk '{print $1}' | sed 's/*//')
if [ "$CURRENT_ENV" = "coqui-tts" ]; then
    echo "🔄 Desativando ambiente coqui-tts atual..."
    conda deactivate
fi

# Remover ambiente antigo (opcional)
echo "🗑️ Removendo ambiente antigo (se existir)..."
conda env remove -n coqui-tts -y || true

# Criar ambiente a partir do ficheiro environment.yml
echo "📦 Criando ambiente Conda..."
conda env create -f environment.yml

# Ativar ambiente
echo "🔧 Ativando ambiente..."
conda activate coqui-tts

# Download de modelos TTS essenciais
echo "📥 Baixando modelos TTS essenciais..."
python -c "
import os
from TTS.api import TTS

# Criar diretório para modelos se não existir
models_dir = os.path.expanduser('~/.local/share/tts')
os.makedirs(models_dir, exist_ok=True)

# Lista de modelos essenciais
models = [
    'tts_models/multilingual/multi-dataset/xtts_v2',
    'tts_models/pt/mai/tacotron2-DDC',
    'tts_models/en/ljspeech/tacotron2-DDC'
]

for model in models:
    try:
        print(f'Baixando {model}...')
        tts = TTS(model)
        print(f'✅ {model} baixado com sucesso!')
    except Exception as e:
        print(f'⚠️ Erro ao baixar {model}: {e}')
"

echo "✅ Ambiente Conda criado e ativado!"
echo "✅ Modelos TTS baixados!"
echo ""
echo "🎯 Para ativar o ambiente manualmente:"
echo "   conda activate coqui-tts"
echo ""
echo "🚀 Para executar o servidor:"
echo "   ./scripts/run.sh" 