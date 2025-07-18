#!/usr/bin/env python3
"""
Model Manager Tool
Handles listing and switching TTS models via the server API
"""

import requests
from typing import Optional

def list_available_models(server_url: str = "http://localhost:8000") -> None:
    """
    List available TTS models from the server.
    """
    try:
        response = requests.get(f"{server_url}/models")
        if response.status_code == 200:
            data = response.json()
            print("📋 Available Models:")
            print("=" * 60)
            for i, model in enumerate(data['models'], 1):
                status = "✅" if "[already downloaded]" in model else "⬇️"
                clean_name = model.split(" [")[0]
                print(f"{i:2d}. {status} {clean_name}")
            print("=" * 60)
            print(f"📊 Total: {data['total_models']} models")
            print(f"✅ Downloaded: {len(data['downloaded_models'])} models")
            print(f"🔄 Current model: {data['current_model']}")
        else:
            print(f"❌ Failed to get models: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

def list_available_speakers(server_url: str = "http://localhost:8000") -> None:
    """
    List available speakers from the server.
    """
    try:
        response = requests.get(f"{server_url}/speakers")
        if response.status_code == 200:
            data = response.json()
            speakers = data.get('speakers', [])
            if speakers:
                print("🎤 Available Speakers:")
                print("=" * 40)
                for i, speaker in enumerate(speakers, 1):
                    print(f"{i:2d}. {speaker}")
                print("=" * 40)
                print(f"📊 Total: {len(speakers)} speakers")
            else:
                print("❌ No speakers available for current model")
        else:
            print(f"❌ Failed to get speakers: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing speakers: {e}")

def switch_model(server_url: str = "http://localhost:8000", model_name: Optional[str] = None) -> bool:
    """
    Switch to a specific TTS model on the server.
    """
    try:
        if not model_name:
            print("❌ Please specify a model name.")
            return False
        response = requests.post(f"{server_url}/switch_model", params={"model_name": model_name})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully switched to: {data['current_model']}")
            return True
        else:
            print(f"❌ Failed to switch model: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error switching model: {e}")
        return False 