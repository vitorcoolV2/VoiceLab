#!/usr/bin/env python3
"""
Install Portuguese (Portugal) TTS Models
Instala modelos de TTS específicos para português de Portugal
"""

import os
import sys
from TTS.api import TTS

def install_portugal_models():
    """Install models specific for Portuguese from Portugal"""
    
    print("🇵🇹 INSTALANDO MODELOS PARA PORTUGUÊS DE PORTUGAL")
    print("=" * 60)
    
    # Lista de modelos que podem funcionar para português de Portugal
    portugal_models = [
        "tts_models/multilingual/multi-dataset/your_tts",  # YourTTS - pode ser configurado para pt-pt
        "tts_models/multilingual/multi-dataset/xtts_v2",   # XTTS v2 - suporta pt-pt
        "tts_models/en/ljspeech/tacotron2-DDC",           # Modelo inglês como base
        "tts_models/en/vctk/vits",                        # VITS inglês como base
    ]
    
    print("🔍 Tentando instalar modelos para português de Portugal...")
    
    try:
        for model in portugal_models:
            try:
                print(f"\n📥 Tentando: {model}")
                tts = TTS(model)
                
                # Testar com português de Portugal
                test_text = "Olá! Este é um teste de português de Portugal."
                output_file = f"test_pt_pt_{model.replace('/', '_').replace('tts_models_', '')}.wav"
                
                print(f"🧪 Testando com: '{test_text}'")
                
                # Tentar diferentes configurações de idioma
                try:
                    # Tentar pt-pt
                    tts.tts_to_file(text=test_text, file_path=output_file, language="pt-pt")
                    print(f"✅ Sucesso com pt-pt: {output_file}")
                except:
                    try:
                        # Tentar pt
                        tts.tts_to_file(text=test_text, file_path=output_file, language="pt")
                        print(f"✅ Sucesso com pt: {output_file}")
                    except:
                        try:
                            # Tentar sem especificar idioma
                            tts.tts_to_file(text=test_text, file_path=output_file)
                            print(f"✅ Sucesso sem idioma: {output_file}")
                        except Exception as e:
                            print(f"❌ Falha: {e}")
                            continue
                
            except Exception as e:
                print(f"❌ Erro ao instalar {model}: {e}")
                continue
        
        print("\n🎉 Testes concluídos!")
        print("\n💡 Para melhor qualidade com português de Portugal:")
        print("   1. Use voice cloning com samples de voz portuguesa")
        print("   2. Configure o YourTTS para pt-pt")
        print("   3. Use o XTTS v2 se disponível")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False
    
    return True

def test_portugal_voice_cloning():
    """Test voice cloning with Portuguese samples"""
    
    print("\n🎭 TESTANDO VOICE CLONING PARA PORTUGUÊS DE PORTUGAL")
    print("=" * 50)
    
    # Verificar se temos o sample do YouTube
    if os.path.exists("output_voice_sample.wav"):
        print("✅ Sample de voz portuguesa encontrado!")
        print("📁 Arquivo: output_voice_sample.wav")
        
        # Configurar como padrão
        os.system("python set_default_voice.py --enable --sample output_voice_sample.wav")
        
        print("\n🧪 Teste de voice cloning:")
        test_text = "Olá! Esta é uma voz clonada de um falante português. A entonação deve ser mais próxima do português de Portugal."
        
        os.system(f'python talk.py "{test_text}" --language pt-br')
        
    else:
        print("❌ Sample de voz portuguesa não encontrado!")
        print("💡 Baixe um vídeo com falante português primeiro")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clone":
        test_portugal_voice_cloning()
    else:
        install_portugal_models() 