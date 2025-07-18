#!/usr/bin/env python3
"""
Install Portuguese TTS Models
Instala modelos de TTS de alta qualidade para português
"""

import os
import sys
from TTS.api import TTS

os.environ["COQUI_TOS_AGREED"] = "1"

def install_portuguese_models():
    """Install high-quality Portuguese TTS models"""
    
    print("🇵🇹 INSTALANDO MODELOS DE PORTUGUÊS DE ALTA QUALIDADE")
    print("=" * 60)
    
    # Lista de modelos recomendados para português
    portuguese_models = [
        "tts_models/multilingual/multi-dataset/your_tts",  # YourTTS - multilíngue de alta qualidade
        "tts_models/pt/mai/tacotron2-DDC",  # Modelo específico para português
        "tts_models/pt/cv/vits",  # VITS para português
        "tts_models/multilingual/multi-dataset/xtts_v2",  # XTTS v2 - muito boa qualidade
    ]
    
    print("🔍 Verificando modelos disponíveis...")
    
    try:
        # Inicializar TTS
        tts = TTS()
        
        print("📋 Modelos recomendados para português:")
        for i, model in enumerate(portuguese_models, 1):
            print(f"  {i}. {model}")
        
        print("\n🚀 Instalando modelos...")
        
        for model in portuguese_models:
            try:
                print(f"\n📥 Instalando: {model}")
                print("⏳ Isso pode demorar alguns minutos...")
                
                # Tentar carregar o modelo (isso fará o download automático)
                tts_model = TTS(model)
                
                print(f"✅ Modelo instalado com sucesso: {model}")
                
                # Testar com uma frase simples
                test_text = "Olá! Este é um teste do modelo de português."
                print(f"🧪 Testando com: '{test_text}'")
                
                # Gerar áudio de teste
                output_file = f"test_{model.replace('/', '_').replace('tts_models_', '')}.wav"
                tts_model.tts_to_file(text=test_text, file_path=output_file)
                
                print(f"✅ Teste concluído! Arquivo: {output_file}")
                
            except Exception as e:
                print(f"❌ Erro ao instalar {model}: {e}")
                continue
        
        print("\n🎉 Instalação concluída!")
        print("\n📝 Para usar um modelo específico, atualize o settings.yaml:")
        print("   tts:")
        print("     default_model: tts_models/multilingual/multi-dataset/your_tts")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False
    
    return True

def test_models():
    """Test all installed Portuguese models"""
    
    print("\n🧪 TESTANDO MODELOS INSTALADOS")
    print("=" * 40)
    
    test_texts = [
        "Olá! Como você está hoje?",
        "Este é um teste de qualidade de voz em português brasileiro.",
        "A inteligência artificial está revolucionando o mundo.",
        "Bom dia! Tenha um excelente dia!"
    ]
    
    models_to_test = [
        "tts_models/multilingual/multi-dataset/your_tts",
        "tts_models/multilingual/multi-dataset/xtts_v2"
    ]
    
    for model in models_to_test:
        try:
            print(f"\n🎯 Testando modelo: {model}")
            tts = TTS(model)
            
            for i, text in enumerate(test_texts, 1):
                output_file = f"test_{model.replace('/', '_').replace('tts_models_', '')}_{i}.wav"
                print(f"  {i}. Gerando: '{text[:30]}...'")
                tts.tts_to_file(text=text, file_path=output_file, language="pt")
                print(f"     ✅ Salvo como: {output_file}")
                
        except Exception as e:
            print(f"❌ Erro ao testar {model}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_models()
    else:
        install_portuguese_models() 