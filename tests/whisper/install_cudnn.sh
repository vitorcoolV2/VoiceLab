#!/bin/bash

# Script para instalar cuDNN automaticamente
# Compatível com diferentes versões do CUDA

set -e  # Para o script se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para detectar versão do CUDA
detect_cuda_version() {
    log_info "Detectando versão do CUDA..."
    
    if command_exists nvcc; then
        CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
        log_success "CUDA detectado via nvcc: $CUDA_VERSION"
    elif command_exists nvidia-smi; then
        CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | sed 's/.*CUDA Version: \([0-9]\+\.[0-9]\+\).*/\1/')
        log_success "CUDA detectado via nvidia-smi: $CUDA_VERSION"
    else
        log_error "CUDA não encontrado. Instale o CUDA primeiro."
        exit 1
    fi
    
    # Mapear versão CUDA para versão cuDNN compatível
    case $CUDA_VERSION in
        "12.6"|"12.5"|"12.4"|"12.3"|"12.2"|"12.1"|"12.0")
            CUDNN_VERSION="8.9"
            CUDNN_URL="https://developer.nvidia.com/compute/cudnn/secure/8.9.7/local_installers/12.0/cudnn-linux-x86_64-8.9.7.29_cuda12-archive.tar.xz"
            ;;
        "11.8"|"11.7"|"11.6")
            CUDNN_VERSION="8.6"
            CUDNN_URL="https://developer.nvidia.com/compute/cudnn/secure/8.6.0/local_installers/11.8/cudnn-linux-x86_64-8.6.0.163_cuda11-archive.tar.xz"
            ;;
        "11.5"|"11.4"|"11.3"|"11.2")
            CUDNN_VERSION="8.4"
            CUDNN_URL="https://developer.nvidia.com/compute/cudnn/secure/8.4.1/local_installers/11.6/cudnn-linux-x86_64-8.4.1.50_cuda11.6-archive.tar.xz"
            ;;
        "11.1"|"11.0")
            CUDNN_VERSION="8.2"
            CUDNN_URL="https://developer.nvidia.com/compute/cudnn/secure/8.2.4/local_installers/11.4/cudnn-linux-x86_64-8.2.4.15_cuda11.4-archive.tar.xz"
            ;;
        "10.2"|"10.1")
            CUDNN_VERSION="8.0"
            CUDNN_URL="https://developer.nvidia.com/compute/cudnn/secure/8.0.5/local_installers/10.2/cudnn-linux-x86_64-8.0.5.39_cuda10.2-archive.tar.xz"
            ;;
        *)
            log_error "Versão CUDA $CUDA_VERSION não suportada"
            exit 1
            ;;
    esac
    
    log_info "Versão cuDNN recomendada: $CUDNN_VERSION"
}

# Função para verificar se cuDNN já está instalado
check_cudnn_installed() {
    log_info "Verificando se cuDNN já está instalado..."
    
    if [ -f "/usr/local/cuda/lib64/libcudnn.so" ] || [ -f "/usr/lib/x86_64-linux-gnu/libcudnn.so" ]; then
        log_success "cuDNN já está instalado!"
        return 0
    else
        log_info "cuDNN não encontrado. Prosseguindo com instalação..."
        return 1
    fi
}

# Função para baixar cuDNN
# Novo: aceita caminho do arquivo como argumento

download_cudnn() {
    log_info "Baixando cuDNN..."
    
    # Se o usuário passou o caminho do arquivo como argumento
    if [ -n "$1" ]; then
        FILENAME_PATH="$1"
        FILENAME=$(basename "$FILENAME_PATH")
        if [ ! -f "$FILENAME_PATH" ]; then
            log_error "Arquivo $FILENAME_PATH não encontrado!"
            exit 1
        fi
        cp "$FILENAME_PATH" .
        log_success "Arquivo $FILENAME copiado para o diretório temporário!"
        return 0
    fi
    
    # Modo interativo (antigo)
    # Nome do arquivo baseado na URL
    FILENAME=$(basename "$CUDNN_URL")
    log_info "URL: $CUDNN_URL"
    log_warning "Você precisa baixar manualmente o cuDNN do site da NVIDIA"
    log_info "1. Acesse: https://developer.nvidia.com/cudnn"
    log_info "2. Faça login na sua conta NVIDIA"
    log_info "3. Baixe: $FILENAME"
    log_info "4. Coloque o arquivo em: $TEMP_DIR"
    while [ ! -f "$FILENAME" ]; do
        echo -n "Pressione Enter quando o arquivo $FILENAME estiver em $TEMP_DIR: "
        read -r
        if [ ! -f "$FILENAME" ]; then
            log_warning "Arquivo não encontrado. Tente novamente."
        fi
    done
    log_success "Arquivo $FILENAME encontrado!"
}

# Função para instalar cuDNN
install_cudnn() {
    log_info "Instalando cuDNN..."
    
    FILENAME=$(basename "$CUDNN_URL")
    
    # Verificar se arquivo existe
    if [ ! -f "$FILENAME" ]; then
        log_error "Arquivo $FILENAME não encontrado!"
        exit 1
    fi
    
    # Descompactar
    log_info "Descompactando $FILENAME..."
    tar -xf "$FILENAME"
    
    # Verificar se pasta cuda foi criada
    if [ ! -d "cuda" ]; then
        log_error "Pasta 'cuda' não encontrada após descompactação!"
        exit 1
    fi
    
    # Copiar arquivos
    log_info "Copiando bibliotecas..."
    sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64/
    sudo cp cuda/include/cudnn*.h /usr/local/cuda/include/
    
    # Atualizar cache de bibliotecas
    log_info "Atualizando cache de bibliotecas..."
    sudo ldconfig
    
    log_success "cuDNN instalado com sucesso!"
}

# Função para verificar instalação
verify_installation() {
    log_info "Verificando instalação do cuDNN..."
    
    # Verificar se arquivos existem
    if [ -f "/usr/local/cuda/lib64/libcudnn.so" ]; then
        log_success "✓ libcudnn.so encontrado"
    else
        log_error "✗ libcudnn.so não encontrado"
        return 1
    fi
    
    if [ -f "/usr/local/cuda/include/cudnn.h" ]; then
        log_success "✓ cudnn.h encontrado"
    else
        log_error "✗ cudnn.h não encontrado"
        return 1
    fi
    
    # Verificar versão
    if command_exists python3; then
        log_info "Testando cuDNN com Python..."
        python3 -c "
import torch
if torch.backends.cudnn.is_available():
    print('✓ cuDNN disponível no PyTorch')
else:
    print('✗ cuDNN não disponível no PyTorch')
    exit(1)
"
    fi
    
    # Verificar se bibliotecas são carregáveis
    if ldconfig -p | grep -q libcudnn; then
        log_success "✓ cuDNN registrado no sistema"
    else
        log_warning "⚠ cuDNN não encontrado no cache do sistema"
    fi
    
    return 0
}

# Função para configurar variáveis de ambiente
setup_environment() {
    log_info "Configurando variáveis de ambiente..."
    
    # Adicionar ao .bashrc se não existir
    if ! grep -q "LD_LIBRARY_PATH.*cuda" ~/.bashrc; then
        echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
        log_success "LD_LIBRARY_PATH adicionado ao .bashrc"
    else
        log_info "LD_LIBRARY_PATH já configurado no .bashrc"
    fi
    
    # Aplicar agora
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    log_success "Variáveis de ambiente aplicadas"
}

# Função principal
main() {
    echo "=========================================="
    echo "    Instalador Automático de cuDNN"
    echo "=========================================="
    echo
    
    # Verificar se é root
    if [ "$EUID" -eq 0 ]; then
        log_error "Não execute este script como root!"
        exit 1
    fi
    
    # Detectar versão CUDA
    detect_cuda_version
    
    # Verificar se já está instalado
    if check_cudnn_installed; then
        log_success "cuDNN já está instalado e funcionando!"
        exit 0
    fi
    
    # Criar diretório temporário
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Baixar cuDNN (passa argumento se fornecido)
    download_cudnn "$1"
    
    # Instalar cuDNN
    install_cudnn
    
    # Verificar instalação
    if verify_installation; then
        log_success "Instalação do cuDNN concluída com sucesso!"
    else
        log_error "Falha na verificação da instalação"
        exit 1
    fi
    
    # Configurar ambiente
    setup_environment
    
    echo
    echo "=========================================="
    log_success "Instalação concluída!"
    echo "=========================================="
    echo
    log_info "Para aplicar as mudanças, execute:"
    echo "  source ~/.bashrc"
    echo
    log_info "Para testar o Whisper com GPU, reinicie o servidor TTS"
    echo "  ./start.sh"
    echo
}

# Executar função principal
main "$@" 