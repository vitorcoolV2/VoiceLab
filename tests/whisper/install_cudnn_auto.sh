#!/bin/bash

# Script automático para instalar cuDNN
# Tenta download automático ou fornece instruções claras

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detectar versão CUDA
detect_cuda() {
    if command -v nvcc >/dev/null 2>&1; then
        CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
        log_success "CUDA detectado: $CUDA_VERSION"
    else
        log_error "CUDA não encontrado. Instale o CUDA primeiro."
        exit 1
    fi
}

# Mapear CUDA para cuDNN
get_cudnn_info() {
    case $CUDA_VERSION in
        "12.6"|"12.5"|"12.4"|"12.3"|"12.2"|"12.1"|"12.0")
            CUDNN_VERSION="8.9.7"
            CUDNN_FILE="cudnn-linux-x86_64-8.9.7.29_cuda12-archive.tar.xz"
            CUDNN_URL="https://developer.nvidia.com/compute/cudnn/secure/8.9.7/local_installers/12.0/cudnn-linux-x86_64-8.9.7.29_cuda12-archive.tar.xz"
            ;;
        "11.8"|"11.7"|"11.6")
            CUDNN_VERSION="8.6.0"
            CUDNN_FILE="cudnn-linux-x86_64-8.6.0.163_cuda11-archive.tar.xz"
            CUDNN_URL="https://developer.nvidia.com/compute/cudnn/secure/8.6.0/local_installers/11.8/cudnn-linux-x86_64-8.6.0.163_cuda11-archive.tar.xz"
            ;;
        *)
            log_error "Versão CUDA $CUDA_VERSION não suportada"
            exit 1
            ;;
    esac
}

# Verificar se cuDNN já está instalado
check_installed() {
    if [ -f "/usr/local/cuda/lib64/libcudnn.so" ] || [ -f "/usr/lib/x86_64-linux-gnu/libcudnn.so" ]; then
        log_success "cuDNN já está instalado!"
        return 0
    fi
    return 1
}

# Tentar download automático
try_auto_download() {
    log_info "Tentando download automático..."
    
    # Verificar se wget ou curl estão disponíveis
    if command -v wget >/dev/null 2>&1; then
        log_info "Usando wget para download..."
        if wget --quiet --show-progress "$CUDNN_URL" -O "$CUDNN_FILE"; then
            log_success "Download automático bem-sucedido!"
            return 0
        fi
    elif command -v curl >/dev/null 2>&1; then
        log_info "Usando curl para download..."
        if curl -L -o "$CUDNN_FILE" "$CUDNN_URL"; then
            log_success "Download automático bem-sucedido!"
            return 0
        fi
    fi
    
    log_warning "Download automático falhou. Usando modo manual."
    return 1
}

# Instalar cuDNN
install_cudnn() {
    log_info "Instalando cuDNN..."
    
    if [ ! -f "$CUDNN_FILE" ]; then
        log_error "Arquivo $CUDNN_FILE não encontrado!"
        return 1
    fi
    
    # Descompactar
    log_info "Descompactando $CUDNN_FILE..."
    tar -xf "$CUDNN_FILE"
    
    if [ ! -d "cuda" ]; then
        log_error "Pasta 'cuda' não encontrada após descompactação!"
        return 1
    fi
    
    # Copiar arquivos
    log_info "Copiando bibliotecas..."
    sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64/
    sudo cp cuda/include/cudnn*.h /usr/local/cuda/include/
    
    # Atualizar cache
    log_info "Atualizando cache de bibliotecas..."
    sudo ldconfig
    
    log_success "cuDNN instalado com sucesso!"
    return 0
}

# Verificar instalação
verify_installation() {
    log_info "Verificando instalação..."
    
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
    
    # Teste Python
    if command -v python3 >/dev/null 2>&1; then
        log_info "Testando cuDNN com Python..."
        if python3 -c "import torch; print('✓ cuDNN disponível' if torch.backends.cudnn.is_available() else '✗ cuDNN não disponível')" 2>/dev/null; then
            log_success "✓ cuDNN funcionando no PyTorch"
        else
            log_warning "⚠ Teste Python falhou"
        fi
    fi
    
    return 0
}

# Configurar ambiente
setup_environment() {
    log_info "Configurando variáveis de ambiente..."
    
    if ! grep -q "LD_LIBRARY_PATH.*cuda" ~/.bashrc; then
        echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
        log_success "LD_LIBRARY_PATH adicionado ao .bashrc"
    fi
    
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    log_success "Variáveis aplicadas"
}

# Instruções manuais
show_manual_instructions() {
    echo
    echo "=========================================="
    echo "    INSTRUÇÕES PARA DOWNLOAD MANUAL"
    echo "=========================================="
    echo
    echo "1. Acesse: https://developer.nvidia.com/cudnn"
    echo "2. Faça login na sua conta NVIDIA"
    echo "3. Baixe: $CUDNN_FILE"
    echo "4. Execute este script novamente com o arquivo:"
    echo "   ./install_cudnn_auto.sh /caminho/para/$CUDNN_FILE"
    echo
    echo "OU coloque o arquivo no diretório atual e execute:"
    echo "   ./install_cudnn_auto.sh"
    echo
}

# Função principal
main() {
    echo "=========================================="
    echo "    Instalador Automático de cuDNN v2"
    echo "=========================================="
    echo
    
    # Verificar se é root
    if [ "$EUID" -eq 0 ]; then
        log_error "Não execute como root!"
        exit 1
    fi
    
    # Detectar CUDA
    detect_cuda
    get_cudnn_info
    
    # Verificar se já está instalado
    if check_installed; then
        log_success "cuDNN já está instalado e funcionando!"
        exit 0
    fi
    
    # Se arquivo foi fornecido como argumento
    if [ -n "$1" ]; then
        if [ -f "$1" ]; then
            log_info "Usando arquivo fornecido: $1"
            cp "$1" .
            CUDNN_FILE=$(basename "$1")
        else
            log_error "Arquivo $1 não encontrado!"
            exit 1
        fi
    else
        # Tentar download automático primeiro
        if ! try_auto_download; then
            show_manual_instructions
            exit 1
        fi
    fi
    
    # Instalar
    if install_cudnn; then
        if verify_installation; then
            setup_environment
            echo
            echo "=========================================="
            log_success "Instalação concluída!"
            echo "=========================================="
            echo
            log_info "Para aplicar as mudanças:"
            echo "  source ~/.bashrc"
            echo
            log_info "Para testar o Whisper com GPU:"
            echo "  ./start.sh"
            echo "  python tests/whisper/test_gpu_compatibility.py"
            echo
        else
            log_error "Falha na verificação da instalação"
            exit 1
        fi
    else
        log_error "Falha na instalação"
        exit 1
    fi
}

main "$@" 