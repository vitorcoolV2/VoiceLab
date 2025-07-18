#!/usr/bin/env python3
"""
Script para validar automaticamente todos os samples de áudio no projeto
usando o servidor Whisper para detectar o idioma real de cada ficheiro.
"""

import os
import requests
import json
from pathlib import Path
from datetime import datetime

def validate_audio_sample(audio_path, server_url="http://localhost:8000"):
    """Valida um sample de áudio usando Whisper"""
    try:
        with open(audio_path, "rb") as f:
            files = {"audio_file": f}
            response = requests.post(f"{server_url}/transcribe", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "language": result.get("language", "unknown"),
                    "transcription": result.get("transcribed_text", ""),
                    "confidence": result.get("confidence", 0),
                    "processing_time": result.get("processing_time", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def find_audio_samples(directory="downloads"):
    """Encontra todos os ficheiros de áudio na pasta downloads"""
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    samples = []
    
    downloads_path = Path(directory)
    if not downloads_path.exists():
        print(f"❌ Diretório {directory} não encontrado")
        return samples
    
    for ext in audio_extensions:
        samples.extend(downloads_path.glob(f"*{ext}"))
    
    return sorted(samples)

def analyze_sample_name(filename):
    """Analisa o nome do ficheiro para tentar identificar o idioma esperado"""
    filename_lower = filename.lower()
    
    if any(lang in filename_lower for lang in ['pt', 'portuguese', 'portugues']):
        return "pt"
    elif any(lang in filename_lower for lang in ['en', 'english', 'ingles']):
        return "en"
    elif any(lang in filename_lower for lang in ['es', 'spanish', 'espanhol']):
        return "es"
    elif any(lang in filename_lower for lang in ['fr', 'french', 'frances']):
        return "fr"
    else:
        return "unknown"

def main():
    """Função principal"""
    print("🎧 Validação Automática de Samples de Áudio")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor Whisper não está respondendo corretamente")
            return
        print("✅ Servidor Whisper está ativo")
    except:
        print("❌ Servidor Whisper não está rodando")
        print("   Inicie o servidor primeiro: python src/tts_server.py")
        return
    
    # Encontrar samples
    samples = find_audio_samples()
    if not samples:
        print("❌ Nenhum sample de áudio encontrado em downloads/")
        return
    
    print(f"📁 Encontrados {len(samples)} samples de áudio")
    print()
    
    # Validar cada sample
    results = []
    for i, sample_path in enumerate(samples, 1):
        print(f"🔍 Validando {i}/{len(samples)}: {sample_path.name}")
        
        # Analisar nome do ficheiro
        expected_lang = analyze_sample_name(sample_path.name)
        
        # Validar com Whisper
        validation = validate_audio_sample(sample_path)
        
        if validation["success"]:
            detected_lang = validation["language"]
            transcription = validation["transcription"]
            confidence = validation["confidence"]
            
            # Verificar se o idioma detectado corresponde ao esperado
            lang_match = "✅" if detected_lang == expected_lang else "❌"
            
            print(f"   Idioma esperado: {expected_lang}")
            print(f"   Idioma detectado: {detected_lang} {lang_match}")
            print(f"   Confiança: {confidence:.1f}%")
            print(f"   Transcrição: {transcription[:100]}{'...' if len(transcription) > 100 else ''}")
            
            results.append({
                "file": sample_path.name,
                "expected_language": expected_lang,
                "detected_language": detected_lang,
                "transcription": transcription,
                "confidence": confidence,
                "language_match": detected_lang == expected_lang
            })
        else:
            print(f"   ❌ Erro: {validation['error']}")
            results.append({
                "file": sample_path.name,
                "expected_language": expected_lang,
                "error": validation["error"],
                "language_match": False
            })
        
        print()
    
    # Resumo
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 60)
    
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    
    print(f"✅ Samples válidos: {len(successful)}")
    print(f"❌ Samples com erro: {len(failed)}")
    
    if successful:
        # Análise por idioma
        languages = {}
        for result in successful:
            lang = result["detected_language"]
            languages[lang] = languages.get(lang, 0) + 1
        
        print(f"\n🌍 Distribuição por idioma:")
        for lang, count in sorted(languages.items()):
            print(f"   {lang}: {count} samples")
        
        # Samples que não correspondem ao esperado
        mismatched = [r for r in successful if not r["language_match"]]
        if mismatched:
            print(f"\n⚠️  Samples com idioma inesperado ({len(mismatched)}):")
            for result in mismatched:
                print(f"   {result['file']}: esperado {result['expected_language']}, detectado {result['detected_language']}")
    
    # Salvar relatório
    report_file = f"audio_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(samples),
            "successful_validations": len(successful),
            "failed_validations": len(failed),
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo: {report_file}")

if __name__ == "__main__":
    main() 