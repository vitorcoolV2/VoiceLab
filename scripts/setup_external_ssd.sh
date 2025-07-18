#!/bin/bash
set -e

# Sistema de estado
STATE_FILE="/tmp/coqui_tts_setup_ssd.state"

echo "🔧 Setting up External SSD for Coqui TTS"
echo "========================================"

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

# Criar diretórios
if [ "$CURRENT_STATE" = "CONDA_ATIVADO" ] || [ "$CURRENT_STATE" = "INICIADO" ]; then
  echo " Criando diretórios no SSD..."
  mkdir -p "$COQUI_TTS_HOME" "$COQUI_TTS_OUTPUTS" "$COQUI_TTS_DOWNLOADS"
  echo "DIRETORIOS_CRIADOS" > "$STATE_FILE"
fi

# Ajustar permissões
if [ "$CURRENT_STATE" = "DIRETORIOS_CRIADOS" ]; then
  echo "🔐 Ajustando permissões..."
  chown -R $(whoami):$(whoami) "$COQUI_TTS_HOME" "$COQUI_TTS_OUTPUTS" "$COQUI_TTS_DOWNLOADS"
  chmod -R 770 "$COQUI_TTS_HOME" "$COQUI_TTS_OUTPUTS" "$COQUI_TTS_DOWNLOADS"
  echo "PERMISSOES_AJUSTADAS" > "$STATE_FILE"
fi

# Criar link simbólico
if [ "$CURRENT_STATE" = "PERMISSOES_AJUSTADAS" ]; then
  echo "🔗 Criando link simbólico..."
  if [ ! -L "$HOME/.local/share/tts" ]; then
    rm -rf "$HOME/.local/share/tts"
    ln -s "$COQUI_TTS_HOME" "$HOME/.local/share/tts"
  fi
  echo "LINK_CRIADO" > "$STATE_FILE"
fi

# Mostrar status
if [ "$CURRENT_STATE" = "LINK_CRIADO" ]; then
  echo "📊 Status final:"
  ls -lh "$COQUI_TTS_HOME"
  echo ""
  echo "✅ SSD externo preparado para uso com Coqui TTS!"
  echo "📁 Outputs: $COQUI_TTS_OUTPUTS"
  echo "📁 Downloads: $COQUI_TTS_DOWNLOADS"
  echo "📁 Modelos: $COQUI_TTS_HOME (link em ~/.local/share/tts)"
  
  # Limpar estado
  rm -f "$STATE_FILE"
fi 