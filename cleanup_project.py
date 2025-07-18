#!/usr/bin/env python
"""
Script de Análise do Projeto VoiceForge
Analisa o projeto sem remover nada - usa .gitignore para controlo
"""

import os
from pathlib import Path

def analyze_project():
    """Analisa o projeto e mostra o que será incluído/excluído pelo .gitignore"""
    
    print("🔍 ANÁLISE DO PROJETO VOICEFORGE")
    print("="*50)
    print("📋 Este script apenas analisa - NÃO remove nada!")
    print("🎯 Use .gitignore para controlar o que vai para GitHub")
    print("="*50)
    
    # Verificar tamanho atual
    print("\n📊 ESTATÍSTICAS ATUAIS:")
    total_size = 0
    file_count = 0
    ignored_count = 0
    ignored_size = 0
    
    for root, dirs, files in os.walk("."):
        # Ignorar .git
        if ".git" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(file_path)
                total_size += file_size
                file_count += 1
                
                # Verificar se seria ignorado pelo .gitignore
                relative_path = os.path.relpath(file_path, ".")
                if would_be_ignored(relative_path):
                    ignored_count += 1
                    ignored_size += file_size
                    
            except:
                pass
    
    print(f"  📁 Total de arquivos: {file_count}")
    print(f"  💾 Tamanho total: {total_size / (1024*1024):.1f} MB")
    print(f"  🚫 Arquivos ignorados: {ignored_count}")
    print(f"  💾 Tamanho ignorado: {ignored_size / (1024*1024):.1f} MB")
    print(f"  ✅ Tamanho para GitHub: {(total_size - ignored_size) / (1024*1024):.1f} MB")
    
    # Mostrar arquivos essenciais que serão incluídos
    print("\n✅ ARQUIVOS ESSENCIAIS (INCLUÍDOS NO GITHUB):")
    essential_files = [
        "src/tts_server.py",
        "talk.py", 
        "test_talk_comprehensive.py",
        "GOALS.md",
        "README.md",
        "requirements.txt",
        "environment.yml",
        "setup.py",
        "XTTS_VOICE_CUSTOMIZATION_GUIDE.md",
        "TESTING.md",
        "SETUP.md",
        "ENVIRONMENT_VARIABLES_GUIDE.md",
        "GPU_COEXISTENCE_GUIDE.md",
        ".gitignore"
    ]
    
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️  {file_path} (não encontrado)")
    
    # Mostrar arquivos dev_*.md que serão mantidos
    print("\n📚 ARQUIVOS DEV_*.MD (MANTIDOS):")
    dev_files = list(Path(".").glob("dev_*.md"))
    for dev_file in dev_files:
        print(f"  📄 {dev_file}")
    
    # Mostrar maiores arquivos que serão ignorados
    print("\n🚫 MAIORES ARQUIVOS IGNORADOS:")
    large_ignored = []
    
    for root, dirs, files in os.walk("."):
        if ".git" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(file_path)
                relative_path = os.path.relpath(file_path, ".")
                
                if would_be_ignored(relative_path) and file_size > 1024*1024:  # > 1MB
                    large_ignored.append((relative_path, file_size))
                    
            except:
                pass
    
    # Ordenar por tamanho
    large_ignored.sort(key=lambda x: x[1], reverse=True)
    
    for file_path, size in large_ignored[:10]:  # Top 10
        print(f"  📁 {file_path} ({size / (1024*1024):.1f} MB)")
    
    print("\n🎯 RECOMENDAÇÕES:")
    print("  ✅ Projeto está otimizado para GitHub")
    print("  ✅ Todos os arquivos dev_*.md serão mantidos")
    print("  ✅ .gitignore controla exclusões automaticamente")
    print("  ✅ Apenas código e documentação essencial no repo")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("  1. git add .")
    print("  2. git commit -m 'Initial commit: VoiceForge'")
    print("  3. Criar repo no GitHub")
    print("  4. git remote add origin [URL]")
    print("  5. git push -u origin main")

def would_be_ignored(file_path):
    """Verifica se um arquivo seria ignorado pelo .gitignore"""
    # Padrões do .gitignore
    ignore_patterns = [
        "voice_outputs/",
        "logs/",
        "downloads/",
        "output/",
        "__pycache__/",
        ".pytest_cache/",
        "cuda/",
        "*.wav",
        "*.log",
        "*.tar.gz",
        "*.tar.xz",
        "Miniconda3-latest-Linux-x86_64.sh",
        "config.env",
        ".envrc",
        "*.tmp",
        "*.temp"
    ]
    
    for pattern in ignore_patterns:
        if pattern.endswith("/"):
            if file_path.startswith(pattern):
                return True
        elif pattern.startswith("*"):
            if file_path.endswith(pattern[1:]):
                return True
        else:
            if file_path == pattern or file_path.endswith("/" + pattern):
                return True
    
    return False

if __name__ == "__main__":
    analyze_project() 