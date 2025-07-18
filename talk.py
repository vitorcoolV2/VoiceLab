#!/usr/bin/env python
"""
Coqui TTS Talk Script - Python Only Version
Sends messages to the TTS server and saves the generated audio
No external tools or subprocess calls - pure Python
"""

import sys
import argparse
from pathlib import Path
import json
import os

from tools.talk.tts_client import TTSClient
from tools.talk.language_detector import detect_language
from tools.talk.model_manager import list_available_models, list_available_speakers, switch_model
from tools.audio_utils.audio_player import play_wav_python
from tools.talk.talk_utils import (
    print_feedback_speaker_missing,
    print_endpoint_called,
    suggest_register_command,
    list_local_samples,
    print_success_speaker_registered,
    print_speakers_list,
    print_error_and_exit
)
from tools.talk import swagger_utils

SPEAKERS_DIR = Path("speakers")
SPEAKERS_DIR.mkdir(exist_ok=True)
SPEAKERS_JSON = SPEAKERS_DIR / "speakers.json"

# Utilitário para carregar e guardar speakers
def load_speakers():
    if SPEAKERS_JSON.exists():
        with open(SPEAKERS_JSON, "r") as f:
            return json.load(f)
    return {}

def save_speakers(speakers):
    with open(SPEAKERS_JSON, "w") as f:
        json.dump(speakers, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Talk to Coqui TTS Server - Python Only")
    parser.add_argument("message", nargs="?", help="Message to synthesize")
    parser.add_argument("--language", "-l", default="auto", help="Language code or 'auto' for detection (default: auto)")
    parser.add_argument("--speed", "-s", type=float, default=1.0, help="Speech speed (default: 1.0)")
    parser.add_argument("--speaker", "-sp", default=None, help="Speaker name (optional, or registered speaker)")
    parser.add_argument("--channel", "-c", choices=["left", "right", "stereo"], default="right", help="Audio channel (left, right, stereo) (default: right)")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--list-speakers", action="store_true", help="List available speakers")
    parser.add_argument("--switch-model", type=str, help="Switch to a specific model")
    parser.add_argument("--volume", "-v", type=int, default=100, help="Playback volume (0-100, default: 100)")
    parser.add_argument("--voice-sample", type=str, default=None, help="Path to a reference .wav file for XTTS/voice cloning")
    parser.add_argument("--define-speaker", type=str, default=None, help="Register a new speaker name for voice cloning")
    parser.add_argument("--speaker-props", nargs="*", help="Optional properties for the speaker (key=value)")
    parser.add_argument("--list-registered-speakers", action="store_true", help="List locally registered speakers")
    parser.add_argument("--update-speaker", type=str, default=None, help="Update a registered speaker on the server")
    parser.add_argument("--delete-speaker", type=str, default=None, help="Delete a registered speaker from the server")
    parser.add_argument("--list-endpoints", action="store_true", help="Listar endpoints disponíveis no servidor TTS")
    args = parser.parse_args()

    # Carregar catálogo local de speakers
    speakers_catalog = load_speakers()

    # NOVA LÓGICA: Listar endpoints dinâmicos
    if args.list_endpoints:
        spec = swagger_utils.fetch_openapi_spec()
        if spec:
            endpoints = swagger_utils.list_endpoints(spec)
            print("\nEndpoints disponíveis no servidor TTS:")
            for path, methods in endpoints.items():
                print(f"  {path}: {', '.join(methods)}")
            print("\n💡 Usa --help para ver exemplos de uso CLI.")
        else:
            print("❌ Não foi possível obter o spec OpenAPI do servidor.")
        sys.exit(0)

    if args.list_models:
        list_available_models()
        sys.exit(0)
    if args.list_speakers:
        list_available_speakers()  # Esta função já deve usar /speaker/list
        sys.exit(0)
    if args.switch_model:
        switch_model(model_name=args.switch_model)  # Deve usar /model/switch
        sys.exit(0)

    # Sintetizar
    if args.message:
        from tools.talk.tts_client import create_tts_client
        tts_client = TTSClient()
        
        language = args.language
        if language == 'auto':
            language = detect_language(args.message)
            print(f"🔍 Auto-detected language: {language}")
        
        # Usar voice sample se fornecido, senão deixar o TTSClient usar o speaker do servidor
        voice_sample_path = args.voice_sample
        
        filename = tts_client.synthesize_and_save(
            args.message,
            language=language,
            speed=args.speed if args.speed else 1.0,
            speaker=args.speaker,
            channel=args.channel if args.channel else "right",
            output_dir="voice_outputs",
            voice_sample_path=voice_sample_path
        )
        if filename:
            play_wav_python(str(filename), volume=args.volume)
        sys.exit(0)
    
    # Sintetizar com speaker específico (lógica antiga mantida para compatibilidade)
    if args.speaker:
        from tools.talk.tts_client import create_tts_client
        client = create_tts_client()
        registered_speakers = client.get_registered_speakers()  # Usa /speaker/list
        if args.speaker not in registered_speakers:
            print_feedback_speaker_missing(args.speaker, registered_speakers)
            print_endpoint_called("POST", "/synthesize")
            exit(1)
        print_endpoint_called("POST", "/synthesize")
        tts_client = TTSClient()

        if args.message:
            language = args.language
            if language == 'auto':
                language = detect_language(args.message)
                print(f"🔍 Auto-detected language: {language}")
            # Procurar amostra de voz por omissão para fallback de voice cloning
            default_voice_sample = None
            output_dir = "output"
            sample_candidates = list(Path(output_dir).glob("*.wav"))
            if sample_candidates:
                default_voice_sample = str(sample_candidates[0])
            # Usar voice sample se fornecido, senão deixar o TTSClient usar o speaker do servidor
            voice_sample_path = args.voice_sample
            filename = tts_client.synthesize_and_save(
                args.message,
                language=language,
                speed=args.speed if args.speed else 1.0,
                speaker=args.speaker,
                channel=args.channel if args.channel else "right",
                output_dir="voice_outputs",
                voice_sample_path=voice_sample_path
            )
            if filename:
                play_wav_python(str(filename), volume=args.volume)
            sys.exit(0)
        print("\nUsage:")
        print("  python3 talk.py 'Your message here'                    # Auto-detect language")
        print("  python3 talk.py 'Hello world' --language en           # Specify language")
        print("  python3 talk.py 'Hello world' --voice-sample myvoice.wav   # Use custom voice sample")
        print("  python3 talk.py --define-speaker 'my_voice' --voice-sample myvoice.wav --speaker-props accent=pt age=30")
        print("  python3 talk.py 'Olá' --speaker my_voice              # Use registered speaker")
        print("  python3 talk.py --list-registered-speakers            # List registered speakers")
        print("  python3 talk.py --list-models                         # List available models")
        print("  python3 talk.py --list-speakers                       # List available speakers")
        print("  python3 talk.py --switch-model 'model_name'           # Switch to specific model")
        print("  python3 talk.py --update-speaker 'my_voice' --voice-sample new.wav --speaker-props age=40")
        print("  python3 talk.py --delete-speaker 'my_voice'")
        print("  python3 talk.py --help                                # Show help")
        print("\n💡 This version saves audio files to voice_outputs/ directory.")
        print("💡 No external tools or subprocess calls - pure Python.")
        sys.exit(1)

    # Atualizar speaker
    if args.update_speaker:
        from tools.talk.tts_client import create_tts_client
        client = create_tts_client()
        registered_speakers = client.get_registered_speakers()
        if args.update_speaker not in registered_speakers:
            print_feedback_speaker_missing(args.update_speaker, registered_speakers)
            print_endpoint_called("POST", "/speaker/update")
            exit(1)
        print_endpoint_called("POST", "/speaker/update")
        files = {}
        data = {"name": args.update_speaker}
        if args.voice_sample:
            if not Path(args.voice_sample).exists():
                print(f"❌ Voice sample file not found: {args.voice_sample}")
                sys.exit(1)
            files["audio_file"] = open(args.voice_sample, "rb")
        if args.speaker_props:
            for prop in args.speaker_props:
                if '=' in prop:
                    k, v = prop.split('=', 1)
                    data[k] = v
        import requests
        response = requests.post(f"http://localhost:8000/speaker/update", data=data, files=files if files else None)
        if files:
            for f in files.values():
                f.close()
        try:
            resp_json = response.json()
        except Exception:
            print(f"❌ Invalid response from server: {response.text}")
            sys.exit(1)
        if response.status_code == 200 and resp_json.get("success"):
            print(f"✅ Speaker '{args.update_speaker}' updated: {resp_json}")
        else:
            print(f"❌ Failed to update speaker: {resp_json.get('error', response.text)}")
        sys.exit(0)

    # Remover speaker
    if args.delete_speaker:
        from tools.talk.tts_client import create_tts_client
        client = create_tts_client()
        registered_speakers = client.get_registered_speakers()
        if args.delete_speaker not in registered_speakers:
            print_feedback_speaker_missing(args.delete_speaker, registered_speakers)
            print_endpoint_called("DELETE", "/speaker/delete")
            exit(1)
        print_endpoint_called("DELETE", "/speaker/delete")
        import requests
        data = {"name": args.delete_speaker}
        response = requests.request("DELETE", f"http://localhost:8000/speaker/delete", data=data)
        try:
            resp_json = response.json()
        except Exception:
            print(f"❌ Invalid response from server: {response.text}")
            sys.exit(1)
        if response.status_code == 200 and resp_json.get("success"):
            print(f"✅ Speaker '{args.delete_speaker}' deleted: {resp_json}")
        else:
            print(f"❌ Failed to delete speaker: {resp_json.get('error', response.text)}")
        sys.exit(0)

    # Registar speaker
    if args.define_speaker:
        print_endpoint_called("POST", "/speaker/register")
        from tools.talk.tts_client import create_tts_client
        client = create_tts_client()
        if not args.voice_sample:
            print("❌ To define a speaker, you must provide --voice-sample <path_to_wav>")
            sys.exit(1)
        files = {"audio_file": open(args.voice_sample, "rb")}
        data = {"name": args.define_speaker}
        if args.speaker_props:
            for prop in args.speaker_props:
                if '=' in prop:
                    k, v = prop.split('=', 1)
                    data[k] = v
        import requests
        response = requests.post(f"http://localhost:8000/speaker/register", data=data, files=files)
        files["audio_file"].close()
        try:
            resp_json = response.json()
        except Exception:
            print(f"❌ Invalid response from server: {response.text}")
            sys.exit(1)
        if response.status_code == 200 and resp_json.get("success"):
            print_success_speaker_registered(args.define_speaker)
        else:
            print(f"❌ Failed to register speaker: {resp_json.get('error', response.text)}")
        sys.exit(0)

    # Listar speakers
    if args.list_registered_speakers:
        print_endpoint_called("GET", "/speaker/list")
        from tools.talk.tts_client import create_tts_client
        client = create_tts_client()
        registered_speakers = client.get_registered_speakers()
        print_speakers_list(registered_speakers)
        sys.exit(0)

if __name__ == "__main__":
    main()
