#!/usr/bin/env python3

from TTS.api import TTS

def list_models():
    print("Listando todos os modelos TTS disponíveis...")
    tts = TTS()
    model_manager = tts.list_models()
    # Tentar acessar .model_ids, se existir
    if hasattr(model_manager, 'model_ids'):
        models = model_manager.model_ids
    elif hasattr(model_manager, 'list'):
        models = model_manager.list()
    else:
        models = []
    print(f"\nTotal de modelos: {len(models)}")
    
    # Filtrar modelos em português
    portuguese_models = []
    for model in models:
        if any(keyword in model.lower() for keyword in ['pt', 'portuguese', 'br', 'brazil']):
            portuguese_models.append(model)
    
    print(f"\nModelos em português encontrados: {len(portuguese_models)}")
    for model in portuguese_models:
        print(f"- {model}")
    
    if not portuguese_models:
        print("Nenhum modelo específico para português encontrado.")
        print("\nModelos multilíngues que podem suportar português:")
        multilingual_models = []
        for model in models:
            if any(keyword in model.lower() for keyword in ['multilingual', 'multi', 'mms']):
                multilingual_models.append(model)
        
        for model in multilingual_models:
            print(f"- {model}")
    
    return portuguese_models

if __name__ == "__main__":
    list_models() 