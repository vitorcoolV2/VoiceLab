#!/usr/bin/env bash
set -e

echo "🔍 Verificação da Configuração Coqui TTS"
echo "========================================"

# Verificar se estamos no diretório correto
if [ ! -f "environment.yml" ]; then
    echo "❌ Execute este script a partir do diretório coqui-tts/"
    exit 1
fi

# Verificar Conda
echo "🔧 Verificando Conda..."
if command -v conda >/dev/null 2>&1; then
    echo "✅ Conda encontrado: $(which conda)"
    CONDA_BASE=$(conda info --base)
    echo "📁 Base: $CONDA_BASE"
else
    echo "❌ Conda não encontrado no PATH"
    exit 1
fi

# Verificar ambiente
echo "🔧 Verificando ambiente coqui-tts..."
if conda env list | grep -q "coqui-tts"; then
    echo "✅ Ambiente coqui-tts encontrado"
else
    echo "❌ Ambiente coqui-tts não encontrado"
    echo "Execute: ./scripts/install.sh"
    exit 1
fi

# Verificar ficheiro de configuração
echo "🔧 Verificando config.env..."
if [ -f "config.env" ]; then
    echo "✅ config.env encontrado"
    source config.env
    echo "📁 MINICONDA_SSD: $MINICONDA_SSD"
    echo "📁 ENV_NAME: $ENV_NAME"
else
    echo "❌ config.env não encontrado"
    exit 1
fi

# Verificar scripts
echo "🔧 Verificando scripts..."
for script in install.sh run.sh download_models.sh; do
    if [ -x "scripts/$script" ]; then
        echo "✅ scripts/$script (executável)"
    else
        echo "❌ scripts/$script (não executável)"
        echo "Execute: chmod +x scripts/*.sh"
    fi
done

# Verificar dependências do sistema
echo "🔧 Verificando dependências do sistema..."
for dep in ffmpeg sox espeak-ng; do
    if command -v $dep >/dev/null 2>&1; then
        echo "✅ $dep encontrado"
    else
        echo "❌ $dep não encontrado"
    fi
done

# Verificar espaço em disco
echo "🔧 Verificando espaço em disco..."
df -h /media/vitor/ssd990 | grep sdb1 | awk '{print "📊 SSD: " $3 " usados, " $4 " livres"}'

# Verificar modelos TTS (se ambiente estiver ativo)
echo "🔧 Verificando modelos TTS..."
if conda info --envs | grep -q "\*.*coqui-tts"; then
    echo "✅ Ambiente coqui-tts ativo"
    python -c "
import os
from TTS.api import TTS

models_dir = os.path.expanduser('~/.local/share/tts')
if os.path.exists(models_dir):
    print(f'✅ Diretório de modelos: {models_dir}')
    models = os.listdir(models_dir)
    print(f'📁 Modelos encontrados: {len(models)}')
    for model in models[:5]:  # Mostrar apenas os primeiros 5
        print(f'  - {model}')
    if len(models) > 5:
        print(f'  ... e mais {len(models) - 5} modelos')
else:
    print('❌ Diretório de modelos não encontrado')
    print('Execute: ./scripts/download_models.sh')
" 2>/dev/null || echo "⚠️ Erro ao verificar modelos TTS"
else
    echo "⚠️ Ambiente coqui-tts não está ativo"
    echo "Execute: conda activate coqui-tts"
fi

echo ""
echo "🎯 Resumo:"
echo "Para executar o servidor:"
echo "  ./scripts/run.sh"
echo ""
echo "Para baixar modelos:"
echo "  ./scripts/download_models.sh"
echo ""
echo "Para reinstalar:"
echo "  ./scripts/install.sh" 