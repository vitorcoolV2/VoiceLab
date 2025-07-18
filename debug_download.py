#!/usr/bin/env python3
"""
Script de debug para testar downloads do YouTube
"""

import yt_dlp
import sys
import os

def test_video_access(url):
    """Testa se consegue acessar um vídeo"""
    print(f"🔍 Testando acesso ao vídeo: {url}")
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("📡 Extraindo informações do vídeo...")
            info = ydl.extract_info(url, download=False)
            
            print(f"✅ Vídeo acessível!")
            print(f"   Título: {info.get('title', 'N/A')}")
            print(f"   Duração: {info.get('duration', 'N/A')} segundos")
            print(f"   Canal: {info.get('uploader', 'N/A')}")
            print(f"   Views: {info.get('view_count', 'N/A')}")
            
            # Verificar formatos disponíveis
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none']
            
            print(f"   Formatos de áudio disponíveis: {len(audio_formats)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao acessar vídeo: {e}")
        return False

def test_download(url, output_name="test_download"):
    """Testa o download completo"""
    print(f"\n📥 Testando download: {url}")
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{output_name}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("🔄 Iniciando download...")
            ydl.download([url])
            
            # Verificar se o arquivo foi criado
            for file in os.listdir('downloads'):
                if file.startswith(output_name) and file.endswith('.wav'):
                    file_path = os.path.join('downloads', file)
                    size = os.path.getsize(file_path)
                    print(f"✅ Download concluído: {file} ({size} bytes)")
                    return file_path
            
            print("❌ Arquivo não encontrado após download")
            return None
            
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return None

def main():
    # Criar diretório downloads se não existir
    os.makedirs('downloads', exist_ok=True)
    
    print("🔧 DEBUG: Teste de Download do YouTube")
    print("=" * 50)
    
    # Lista de vídeos para testar
    test_videos = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "name": "test_rick",
            "description": "Vídeo de teste (Rick Astley)"
        },
        {
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw", 
            "name": "test_me_at_zoo",
            "description": "Primeiro vídeo do YouTube"
        }
    ]
    
    for video in test_videos:
        print(f"\n🎬 Testando: {video['description']}")
        print("-" * 30)
        
        # Testar acesso
        if test_video_access(video['url']):
            # Testar download
            result = test_download(video['url'], video['name'])
            if result:
                print(f"✅ Sucesso: {result}")
            else:
                print("❌ Falha no download")
        else:
            print("❌ Falha no acesso")
    
    print(f"\n📁 Arquivos em downloads/:")
    if os.path.exists('downloads'):
        for file in os.listdir('downloads'):
            if file.endswith('.wav'):
                size = os.path.getsize(os.path.join('downloads', file))
                print(f"   {file} ({size} bytes)")

if __name__ == "__main__":
    main() 