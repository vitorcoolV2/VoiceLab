#!/usr/bin/env python3
"""
Lista os speakers disponíveis do modelo YourTTS
"""
from TTS.api import TTS

def list_yourtts_speakers():
    print("Listando speakers disponíveis do modelo YourTTS...")
    model_name = "tts_models/multilingual/multi-dataset/your_tts"
    tts = TTS(model_name)
    if hasattr(tts, 'speakers'):
        speakers = tts.speakers
        print(f"Total de speakers: {len(speakers)}")
        for s in speakers:
            print(f"- {s}")
    else:
        print("Este modelo não possui atributo 'speakers'.")

if __name__ == "__main__":
    list_yourtts_speakers() 