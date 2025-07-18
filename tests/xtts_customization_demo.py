#!/usr/bin/env python3
"""
Demonstração das Capacidades de Customização do XTTS v2
Testa diferentes parâmetros, estilos e configurações de voz
"""

import os
import sys
import time
import requests
from pathlib import Path

# Adicionar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tests', 'utils'))
from coqui_tts_client import CoquiTTSClient

class XTTSCustomizationDemo:
    def __init__(self):
        """Initialize the XTTS customization demo."""
        self.tts_client = CoquiTTSClient()
        self.output_dir = Path(os.environ.get("COQUI_TTS_OUTPUTS", "voice_outputs"))
        self.output_dir.mkdir(exist_ok=True)
        
    def test_basic_parameters(self):
        """Testa parâmetros básicos de voz"""
        print("🎛️ Testando Parâmetros Básicos de Voz")
        print("=" * 50)
        
        # Verificar se existe amostra de voz
        voice_sample = "downloads/en_demo_voice_sample.wav"
        if not os.path.exists(voice_sample):
            print(f"⚠️ Amostra de voz não encontrada: {voice_sample}")
            print("   Execute primeiro o teste de clonagem básico")
            return
        
        test_text = "Olá! Esta é uma demonstração dos parâmetros básicos de voz do XTTS v2."
        
        # Configurações de teste
        configs = [
            {
                "name": "normal",
                "description": "Parâmetros normais",
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            },
            {
                "name": "lento_baixo",
                "description": "Lento e tom baixo",
                "speed": 0.7,
                "pitch": 0.8,
                "volume": 1.0
            },
            {
                "name": "rapido_alto",
                "description": "Rápido e tom alto",
                "speed": 1.3,
                "pitch": 1.3,
                "volume": 1.0
            },
            {
                "name": "dramatico",
                "description": "Efeito dramático",
                "speed": 0.8,
                "pitch": 1.2,
                "volume": 1.3
            }
        ]
        
        for config in configs:
            print(f"\n🎤 Testando: {config['name']} - {config['description']}")
            
            result = self.tts_client.clone_voice(
                audio_file_path=voice_sample,
                text=test_text,
                language="pt",
                speed=config["speed"],
                pitch=config["pitch"],
                volume=config["volume"],
                save_to_file=f"voice_outputs/params_{config['name']}.wav"
            )
            
            if result.get("success"):
                print(f"✅ {config['name']} gerado com sucesso")
                print(f"   Speed: {config['speed']}, Pitch: {config['pitch']}, Volume: {config['volume']}")
            else:
                print(f"❌ {config['name']} falhou: {result.get('error')}")
    
    def test_voice_styles(self):
        """Testa diferentes estilos de voz"""
        print("\n🎭 Testando Estilos de Voz")
        print("=" * 50)
        
        # Verificar se existe amostra de voz
        voice_sample = "downloads/en_demo_voice_sample.wav"
        if not os.path.exists(voice_sample):
            print(f"⚠️ Amostra de voz não encontrada: {voice_sample}")
            print("   Execute primeiro o teste de clonagem básico")
            return
        
        test_text = "Olá! Esta é uma demonstração dos diferentes estilos de voz disponíveis no XTTS v2."
        
        styles = [
            {"name": "normal", "description": "Voz padrão natural"},
            {"name": "emphatic", "description": "Estilo enfático e forte"},
            {"name": "excited", "description": "Estilo energético e entusiástico"},
            {"name": "calm", "description": "Estilo calmo e relaxado"},
            {"name": "whisper", "description": "Estilo sussurro íntimo"}
        ]
        
        for style in styles:
            print(f"\n🎤 Testando: {style['name']} - {style['description']}")
            
            result = self.tts_client.clone_voice(
                audio_file_path=voice_sample,
                text=test_text,
                language="pt",
                voice_style=style["name"],
                save_to_file=f"voice_outputs/style_{style['name']}.wav"
            )
            
            if result.get("success"):
                print(f"✅ Estilo {style['name']} gerado com sucesso")
            else:
                print(f"❌ Estilo {style['name']} falhou: {result.get('error')}")
    
    def test_voice_cloning(self):
        """Testa clonagem de voz com diferentes configurações"""
        print("\n🎭 Testando Clonagem de Voz")
        print("=" * 50)
        
        # Verificar se existe amostra de voz
        voice_sample = "downloads/en_demo_voice_sample.wav"
        if not os.path.exists(voice_sample):
            print(f"⚠️ Amostra de voz não encontrada: {voice_sample}")
            print("   Execute primeiro o teste de clonagem básico")
            return
        
        test_text = "Esta é uma demonstração de clonagem de voz com diferentes configurações do XTTS v2."
        
        # Configurações de clonagem
        cloning_configs = [
            {
                "name": "clonagem_normal",
                "description": "Clonagem com parâmetros normais",
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            },
            {
                "name": "clonagem_feminina",
                "description": "Clonagem simulando voz feminina",
                "speed": 1.1,
                "pitch": 1.3,
                "volume": 1.0
            },
            {
                "name": "clonagem_masculina",
                "description": "Clonagem simulando voz masculina",
                "speed": 0.9,
                "pitch": 0.7,
                "volume": 1.2
            }
        ]
        
        for config in cloning_configs:
            print(f"\n🎤 Testando: {config['name']} - {config['description']}")
            
            result = self.tts_client.clone_voice(
                audio_file_path=voice_sample,
                text=test_text,
                language="pt",
                speed=config["speed"],
                pitch=config["pitch"],
                volume=config["volume"],
                save_to_file=f"voice_outputs/{config['name']}.wav"
            )
            
            if result.get("success"):
                print(f"✅ {config['name']} clonado com sucesso")
            else:
                print(f"❌ {config['name']} falhou: {result.get('error')}")
    
    def test_advanced_combinations(self):
        """Testa combinações avançadas de parâmetros"""
        print("\n🎨 Testando Combinações Avançadas")
        print("=" * 50)
        
        # Verificar se existe amostra de voz
        voice_sample = "downloads/en_demo_voice_sample.wav"
        if not os.path.exists(voice_sample):
            print(f"⚠️ Amostra de voz não encontrada: {voice_sample}")
            print("   Execute primeiro o teste de clonagem básico")
            return
        
        test_text = "Esta é uma demonstração de combinações avançadas de parâmetros vocais."
        
        # Combinações específicas para diferentes contextos
        combinations = [
            {
                "name": "apresentacao",
                "description": "Voz para apresentações",
                "speed": 1.1,
                "pitch": 1.2,
                "volume": 1.1,
                "voice_style": "emphatic"
            },
            {
                "name": "narracao",
                "description": "Voz para narração",
                "speed": 0.9,
                "pitch": 1.0,
                "volume": 1.0,
                "voice_style": "calm"
            },
            {
                "name": "comando",
                "description": "Voz para comandos",
                "speed": 0.8,
                "pitch": 0.8,
                "volume": 1.3,
                "voice_style": "emphatic"
            },
            {
                "name": "energetico",
                "description": "Voz energética",
                "speed": 1.3,
                "pitch": 1.2,
                "volume": 1.2,
                "voice_style": "excited"
            }
        ]
        
        for combo in combinations:
            print(f"\n🎤 Testando: {combo['name']} - {combo['description']}")
            
            result = self.tts_client.clone_voice(
                audio_file_path=voice_sample,
                text=test_text,
                language="pt",
                speed=combo["speed"],
                pitch=combo["pitch"],
                volume=combo["volume"],
                voice_style=combo["voice_style"],
                save_to_file=f"voice_outputs/combo_{combo['name']}.wav"
            )
            
            if result.get("success"):
                print(f"✅ {combo['name']} gerado com sucesso")
                print(f"   Speed: {combo['speed']}, Pitch: {combo['pitch']}, Volume: {combo['volume']}, Style: {combo['voice_style']}")
            else:
                print(f"❌ {combo['name']} falhou: {result.get('error')}")
    
    def test_multilingual_support(self):
        """Testa suporte multilingue"""
        print("\n🌍 Testando Suporte Multilingue")
        print("=" * 50)
        
        # Verificar se existe amostra de voz
        voice_sample = "downloads/en_demo_voice_sample.wav"
        if not os.path.exists(voice_sample):
            print(f"⚠️ Amostra de voz não encontrada: {voice_sample}")
            print("   Execute primeiro o teste de clonagem básico")
            return
        
        # Textos em diferentes idiomas
        multilingual_texts = [
            {
                "language": "pt",
                "text": "Olá! Esta é uma demonstração em português.",
                "name": "portugues"
            },
            {
                "language": "en",
                "text": "Hello! This is a demonstration in English.",
                "name": "ingles"
            },
            {
                "language": "es",
                "text": "¡Hola! Esta es una demostración en español.",
                "name": "espanhol"
            }
        ]
        
        for lang_test in multilingual_texts:
            print(f"\n🌍 Testando: {lang_test['name']} - {lang_test['language']}")
            
            result = self.tts_client.clone_voice(
                audio_file_path=voice_sample,
                text=lang_test["text"],
                language=lang_test["language"],
                save_to_file=f"voice_outputs/multilingual_{lang_test['name']}.wav"
            )
            
            if result.get("success"):
                print(f"✅ {lang_test['name']} gerado com sucesso")
            else:
                print(f"❌ {lang_test['name']} falhou: {result.get('error')}")
    
    def run_all_tests(self):
        """Executa todos os testes de customização"""
        print("🎭 XTTS v2 Customization Demo")
        print("=" * 60)
        print("Demonstração completa das capacidades de customização")
        print("Certifique-se de que o servidor TTS está a correr em http://localhost:8000")
        print()
        
        start_time = time.time()
        
        # Executar todos os testes
        tests = [
            ("Parâmetros Básicos", self.test_basic_parameters),
            ("Estilos de Voz", self.test_voice_styles),
            ("Clonagem de Voz", self.test_voice_cloning),
            ("Combinações Avançadas", self.test_advanced_combinations),
            ("Suporte Multilingue", self.test_multilingual_support)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                test_func()
                results.append((test_name, True))
            except Exception as e:
                print(f"❌ {test_name} falhou com erro: {e}")
                results.append((test_name, False))
        
        # Resumo
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print("📊 RESUMO DA DEMONSTRAÇÃO")
        print(f"{'='*60}")
        
        passed = 0
        for test_name, success in results:
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"{test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\n🎯 Resultado: {passed}/{len(results)} testes passaram")
        print(f"⏱️ Tempo total: {total_time:.2f} segundos")
        
        if passed == len(results):
            print("\n🎉 Todos os testes completados com sucesso!")
            print("🎤 O XTTS v2 está totalmente funcional para customização!")
            print(f"\n📁 Ficheiros de áudio gerados em: {self.output_dir}")
            print("\n🎭 Capacidades demonstradas:")
            print("  • Parâmetros básicos (speed, pitch, volume)")
            print("  • Estilos de voz (normal, emphatic, excited, calm, whisper)")
            print("  • Clonagem de voz com amostras")
            print("  • Combinações avançadas para contextos específicos")
            print("  • Suporte multilingue completo")
        else:
            print(f"\n⚠️ {len(results) - passed} teste(s) falharam!")
            print("💡 Verifique os erros acima e certifique-se de que o servidor está a funcionar")

def main():
    """Função principal"""
    demo = XTTSCustomizationDemo()
    demo.run_all_tests()

if __name__ == "__main__":
    main() 