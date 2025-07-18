#!/usr/bin/env python3
"""
Script para coletar amostras de áudio em português de alta qualidade
Usado para melhorar a qualidade do TTS em português
"""

import os
import sys
import argparse
from pathlib import Path

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'audio_utils'))
from youtube_voice_cloner import YouTubeVoiceCloner

def main():
    parser = argparse.ArgumentParser(description="Coletar amostras de áudio em português")
    parser.add_argument('--url', help='URL do vídeo do YouTube')
    parser.add_argument('--text', help='Texto para sintetizar')
    parser.add_argument('--output', default='portuguese_sample', help='Nome base do arquivo de saída')
    parser.add_argument('--duration', type=float, default=30.0, help='Duração da amostra (segundos)')
    parser.add_argument('--start', type=float, default=10.0, help='Segundo inicial')
    parser.add_argument('--auto-play', action='store_true', help='Reproduzir áudio automaticamente')
    parser.add_argument('--list-suggestions', action='store_true', help='Listar sugestões de vídeos e textos')
    
    args = parser.parse_args()
    
    if args.list_suggestions:
        print_suggestions()
        return
    
    if not args.url:
        print("❌ URL do vídeo é obrigatória!")
        print("Use --list-suggestions para ver sugestões de vídeos")
        return
    
    if not args.text:
        print("❌ Texto para sintetizar é obrigatório!")
        print("Use --list-suggestions para ver sugestões de textos")
        return
    
    # Criar diretório para amostras
    samples_dir = Path("portuguese_samples")
    samples_dir.mkdir(exist_ok=True)
    
    print(f"🇧🇷 Coletando amostra de português...")
    print(f"🔗 URL: {args.url}")
    print(f"📝 Texto: {args.text}")
    print(f"⏱️  Duração: {args.duration}s (a partir do segundo {args.start})")
    
    cloner = YouTubeVoiceCloner()
    
    # Baixar vídeo
    print(f"\n📥 Baixando vídeo...")
    downloaded_file = cloner.download_youtube_video(args.url)
    if not downloaded_file:
        print("❌ Falha ao baixar o vídeo!")
        return
    
    # Extrair amostra de voz
    print(f"\n🎤 Extraindo amostra de voz...")
    voice_sample = cloner.extract_voice_sample(
        downloaded_file, 
        start_time=args.start, 
        duration=args.duration
    )
    if not voice_sample:
        print("❌ Falha ao extrair amostra de voz!")
        return
    
    # Mover para diretório de amostras
    sample_path = samples_dir / f"{args.output}_voice_sample.wav"
    os.rename(voice_sample, sample_path)
    print(f"✅ Amostra salva: {sample_path}")
    
    # Analisar voz
    print(f"\n🔍 Analisando voz...")
    analysis = cloner.analyze_voice(str(sample_path))
    if analysis:
        print(f"✅ Análise concluída")
        print(f"   Gênero: {analysis.get('gender', 'N/A')}")
        print(f"   Idade estimada: {analysis.get('age_estimate', 'N/A')}")
        print(f"   Qualidade: {analysis.get('quality_score', 'N/A')}")
    
    # Clonar voz
    print(f"\n🗣️ Clonando voz...")
    cloned_path = samples_dir / f"{args.output}_cloned.wav"
    success = cloner.clone_voice(str(sample_path), args.text, str(cloned_path), language="pt-br")
    
    if success:
        print(f"✅ Voz clonada com sucesso: {cloned_path}")
        
        if args.auto_play:
            print(f"\n🎵 Reproduzindo áudio clonado...")
            cloner.play_audio(str(cloned_path))
    else:
        print("❌ Falha ao clonar voz!")
    
    # Limpar arquivo baixado
    if os.path.exists(downloaded_file):
        os.remove(downloaded_file)
        print(f"🧹 Arquivo temporário removido")

def print_suggestions():
    """Imprimir sugestões de vídeos e textos para coleta de amostras"""
    
    print("🇧🇷 SUGESTÕES PARA COLETA DE AMOSTRAS EM PORTUGUÊS")
    print("=" * 60)
    
    print("\n📺 VÍDEOS SUGERIDOS (YouTube):")
    print("-" * 40)
    
    videos = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "description": "Vídeo com fala clara e pausada",
            "start": 15.0,
            "duration": 20.0
        },
        {
            "url": "https://www.youtube.com/watch?v=example2",
            "description": "Podcast em português brasileiro",
            "start": 30.0,
            "duration": 25.0
        },
        {
            "url": "https://www.youtube.com/watch?v=example3", 
            "description": "Notícias em português",
            "start": 10.0,
            "duration": 30.0
        }
    ]
    
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['description']}")
        print(f"   URL: {video['url']}")
        print(f"   Sugestão: --start {video['start']} --duration {video['duration']}")
        print()
    
    print("\n📝 TEXTOS SUGERIDOS PARA TESTE:")
    print("-" * 40)
    
    texts = [
        "Olá! Esta é uma demonstração de síntese de voz em português brasileiro. A qualidade deve estar muito boa agora.",
        "Bom dia! Como você está? Espero que esteja tendo um ótimo dia. Esta é uma amostra de voz clonada.",
        "A inteligência artificial está revolucionando a forma como interagimos com a tecnologia. Cada dia surgem novas possibilidades.",
        "O português é uma língua muito rica e expressiva. Temos muitas palavras bonitas e uma pronúncia única.",
        "A tecnologia de síntese de voz tem evoluído muito nos últimos anos. Agora podemos criar vozes muito naturais."
    ]
    
    for i, text in enumerate(texts, 1):
        print(f"{i}. {text}")
        print()
    
    print("\n💡 EXEMPLOS DE USO:")
    print("-" * 40)
    print("python collect_portuguese_samples.py --url <URL> --text 'Seu texto aqui' --output minha_amostra")
    print("python collect_portuguese_samples.py --url <URL> --text 'Seu texto aqui' --auto-play")
    print("python collect_portuguese_samples.py --url <URL> --text 'Seu texto aqui' --duration 25 --start 20")

if __name__ == "__main__":
    main() 