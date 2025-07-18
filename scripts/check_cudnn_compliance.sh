#!/usr/bin/env bash
# check_cudnn_compliance.sh
# Verifica se o projeto está em conformidade com a licença da NVIDIA para cuDNN

set -e

CUDA_DIR="$(dirname "$0")/../cuda"
GITIGNORE_FILE="$(dirname "$0")/../.gitignore"

# 1. Verificar se existem binários ou headers do cuDNN no repositório
FOUND=0
if ls "$CUDA_DIR"/lib64/libcudnn* 1> /dev/null 2>&1; then
  echo "[ALERTA] Encontrados binários cuDNN em $CUDA_DIR/lib64/ (NÃO DEVEM ser versionados!)"
  FOUND=1
fi
if ls "$CUDA_DIR"/include/cudnn.h 1> /dev/null 2>&1; then
  echo "[ALERTA] Encontrado cudnn.h em $CUDA_DIR/include/ (NÃO DEVE ser versionado!)"
  FOUND=1
fi
if ls "$CUDA_DIR"/*.tar.xz "$CUDA_DIR"/*.tgz 1> /dev/null 2>&1; then
  echo "[ALERTA] Encontrados arquivos .tar.xz ou .tgz de cuDNN em $CUDA_DIR/ (NÃO DEVEM ser versionados!)"
  FOUND=1
fi

# 2. Verificar se .gitignore está correto
if ! grep -q 'cuda/lib64/' "$GITIGNORE_FILE" || ! grep -q 'cuda/include/' "$GITIGNORE_FILE"; then
  echo "[ALERTA] .gitignore não está a ignorar cuda/lib64/ e cuda/include/!"
  FOUND=1
fi

if [ "$FOUND" -eq 0 ]; then
  echo "[OK] Projeto em conformidade: cuDNN não está a ser distribuído e .gitignore está correto."
  exit 0
else
  echo "[ERRO] Projeto NÃO está em conformidade com a licença da NVIDIA para cuDNN."
  exit 1
fi 