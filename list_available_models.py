#!/usr/bin/env python3
"""
Script para listar modelos TTS disponíveis
"""

from TTS.api import TTS

def list_models():
    """Lista todos os modelos TTS disponíveis"""
    print("🔍 Listando modelos TTS disponíveis...")
    print("=" * 50)
    
    try:
        # Listar modelos disponíveis
        tts = TTS()
        models = tts.list_models()
        print(f"📊 Total de modelos encontrados: {len(models)}")
        print()
        
        # Agrupar por categoria
        categories = {}
        for model in models:
            parts = model.split('/')
            if len(parts) >= 2:
                category = parts[1]  # pt, multilingual, etc.
                if category not in categories:
                    categories[category] = []
                categories[category].append(model)
            else:
                if 'other' not in categories:
                    categories['other'] = []
                categories['other'].append(model)
        
        # Mostrar por categoria
        for category, model_list in sorted(categories.items()):
            print(f"📁 Categoria: {category.upper()}")
            for model in sorted(model_list):
                print(f"  • {model}")
            print()
        
        # Verificar modelos específicos para português
        print("🇵🇹 Modelos específicos para português:")
        print("-" * 30)
        pt_models = [m for m in models if 'pt' in m.lower()]
        if pt_models:
            for model in sorted(pt_models):
                print(f"  ✅ {model}")
        else:
            print("  ⚠️  Nenhum modelo específico para português encontrado")
        
        print()
        
        # Verificar modelos multilingues
        print("🌍 Modelos multilingues:")
        print("-" * 25)
        multilingual_models = [m for m in models if 'multilingual' in m.lower()]
        if multilingual_models:
            for model in sorted(multilingual_models):
                print(f"  ✅ {model}")
        else:
            print("  ⚠️  Nenhum modelo multilingue encontrado")
        
        print()
        
        # Verificar YourTTS especificamente
        print("🎯 YourTTS (para clonagem de voz):")
        print("-" * 35)
        yourtts_models = [m for m in models if 'your_tts' in m.lower()]
        if yourtts_models:
            for model in sorted(yourtts_models):
                print(f"  ✅ {model}")
        else:
            print("  ⚠️  YourTTS não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")

if __name__ == "__main__":
    list_models() 