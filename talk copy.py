#!/usr/bin/env python3
ui TTS Talk Script - Python Only Version
Sends messages to the TTS server and saves the generated audio
No external tools or subprocess calls - pure Python
"""

import sys
import os
import requests
import json
import time
import argparse
import re
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0os.path.dirname(os.path.abspath(__file__)))

def detect_language(text):
   Simple language detection based on common words and characters
    Returns language code (pt-br, en, es, etc.)
     text_lower = text.lower()
    
    # Portuguese indicators
    pt_words = ['olá',oi, 'bom,boa,tarde,noite', dia',porreiro, bora, lá',este',é', 'uma', 'para, com,que, 'não, sim,muito, em', mal,grande',pequeno']
    pt_chars = ['ã',õ',ç',á',é',í',ó',ú',â',ê, ,ô,     
    # Spanish indicators
    es_words = ['hola,buenos,días',tardes', noches,gracias, por', favor', sí,no', 'muy', 'bien', mal', grande', pequeño',este', es', 'una', 'para',con', 'que']
    es_chars = ['ñ',á',é',í, ,ú,     
    # English indicators
    en_words = ['hello,hi, good',morning', afternoon',evening,night,thank', you', please', yes, no,very', 'well, ad,big', small, this,is',a', 'for', 'with', that
    
    # French indicators
    fr_words = ['bonjour,bonsoir,salut,merci', sundefinedil', vous,plaît,oui',non,très', 'bien,mal,grand', petit', 'ceci, est', 'une,pour,avec', 'que']
    fr_chars = ['à',â',ä',é',è',ê',ë',î',ï',ô',ö',ù',û, ,ÿ,     
    # Italian indicators
    it_words = ['ciao,buongiorno,buonasera', grazie', prego', sì',no', molto,bene,male', grande', piccolo', 'questo', è,una,per, con', che', 'come',stai']
    it_chars = ['à',è',é, ,ò, ]
    
    # Count matches
    pt_score = sum(1 for word in pt_words if word in text_lower) + sum(1 for char in pt_chars if char in text)
    es_score = sum(1 for word in es_words if word in text_lower) + sum(1 for char in es_chars if char in text)
    en_score = sum(1 for word in en_words if word in text_lower)
    fr_score = sum(1 for word in fr_words if word in text_lower) + sum(1 for char in fr_chars if char in text)
    it_score = sum(1 for word in it_words if word in text_lower) + sum(1 for char in it_chars if char in text)
    
    # Return best match
    if pt_score > es_score and pt_score > en_score and pt_score > fr_score and pt_score > it_score:
        return "pt-br"
    elif es_score > pt_score and es_score > en_score and es_score > fr_score and es_score > it_score:
        return "es"
    elif fr_score > pt_score and fr_score > es_score and fr_score > en_score and fr_score > it_score:
        return "fr-fr"
    elif it_score > pt_score and it_score > es_score and it_score > en_score and it_score > fr_score:
        return "it"
    elif en_score > pt_score and en_score > es_score and en_score > fr_score and en_score > it_score:
        return "en"
    else:
        return pt-br"  # Default to Portuguese

def map_language_to_supported(language):
   Map any language to a supported language by available models
    Prioritizes languages with specific models, falls back to multilingual
    "  # Languages with specific models available
    supported_languages = {
        # Core languages with specific models
  en:en",
        pt-br: pt-br,
     pt: pt-br,
  es:es,
  fr:fr",
     fr-fr:fr,
  de:de,
  it:it,
  nl:nl,
  ja:ja,
  zh:zh",
     zh-cn: ,
        
        # European languages with specific models
  bg:bg,
  cs:cs,
  da:da,
  et:et,
  ga:ga,
  uk:uk,
  hu:hu,
  el:el,
  fi:fi,
  hr:hr,
  lt:lt,
  lv:lv,
  mt:mt,
  pl:pl,
  ro:ro,
  sk:sk,
  sl:sl,
  sv: ,
        
        # Other languages
  ca:ca,
  fa:fa,
  bn:bn,
  be:be,
  tr:tr",
        zh-CN: zh-CN",
    ewe":ewe",
    hau": "hau",
    lin": lin,
        tw_akuapem": "tw_akuapem",
      tw_asante": "tw_asante",
      yor":yor
    }
    
    # Return mapped language or original if not found
    return supported_languages.get(language.lower(), language.lower())

def get_model_for_language(language):
 Get the best model for a given language
    Returns model name or None if not found    # Map language to supported format
    mapped_lang = map_language_to_supported(language)
    
    # Model mapping based on available models
    model_mapping = [object Object]    pt-br":tts_models/pt/cv/vits,
       pt":tts_models/pt/cv/vits,
       en": tts_models/en/ljspeech/tacotron2-DDC,
       es": tts_models/es/css10vits,
       fr": tts_models/fr/css10vits,
       de: tts_models/de/thorsten/vits,
       it": tts_models/it/mai_female/vits,
       nl": tts_models/nl/css10vits,
        uk": tts_models/uk/mai/vits,
        pl": tts_models/pl/mai_female/vits,
       bg":tts_models/bg/cv/vits,
       cs":tts_models/cs/cv/vits,
        da":tts_models/da/cv/vits,
        et":tts_models/et/cv/vits,
        ga":tts_models/ga/cv/vits,
       hu": tts_models/hu/css10vits,
        el":tts_models/el/cv/vits,
       fi": tts_models/fi/css10vits,
       hr":tts_models/hr/cv/vits,
        lt":tts_models/lt/cv/vits,
       lv":tts_models/lv/cv/vits,
       mt":tts_models/mt/cv/vits,
        ro":tts_models/ro/cv/vits,
       sk":tts_models/sk/cv/vits,
       sl":tts_models/sl/cv/vits,
       sv":tts_models/sv/cv/vits,
       ca": "tts_models/ca/custom/vits,
        fa": "tts_models/fa/custom/glow-tts,
       bn": "tts_models/bn/custom/vits-male,
        be": "tts_models/be/common-voice/glow-tts,
        tr": "tts_models/tr/common-voice/glow-tts",
    zh-CN":tts_models/zh-CN/baker/tacotron2-DDC-GST",
        ewe: ts_models/ewe/openbible/vits",
        hau: ts_models/hau/openbible/vits",
        lin: ts_models/lin/openbible/vits,
        tw_akuapem:tts_models/tw_akuapem/openbible/vits",
        tw_asante":tts_models/tw_asante/openbible/vits",
        yor: ts_models/yor/openbible/vits
    }
    
    # Return specific model if available, otherwise fallback to multilingual
    if mapped_lang in model_mapping:
        return model_mapping[mapped_lang]
    else:
        # Fallback to multilingual models
        return "tts_models/multilingual/multi-dataset/xtts_v2"

def switch_model_if_needed(server_url, target_language):
   tch to appropriate model for the target language if needed
    Returns True if successful, False otherwise    try:
        # Get current model
        response = requests.get(f"{server_url}/models")
        if response.status_code != 200:
            print(f"❌ Failed to get current model: {response.status_code}")
            return False
        
        current_model = response.json().get('current_model')
        if not current_model:
            print("❌ Could not determine current model")
            return False
        
        # Get target model
        target_model = get_model_for_language(target_language)
        if not target_model:
            print(f"❌ No model found for language: {target_language}")
            return False
        
        # Check if we need to switch
        if current_model == target_model:
            print(f"✅ Already using correct model: {current_model}")
            return True
        
        # Switch model
        print(f🔄 Switching from {current_model} to {target_model}")
        switch_response = requests.post(f"{server_url}/switch_model", params={"model_name: target_model})
        
        if switch_response.status_code == 200:
            print(f"✅ Successfully switched to: {target_model}")
            return True
        else:
            print(f"❌ Failed to switch model: {switch_response.status_code}")
            return False
            
    except Exception as e:
        print(f❌ Error switching model: {e}")
        return False

def talk_to_tts(message, language=auto, speed=1.0play=True, speaker=None, voice_sample=None, channel=right"):
    ""   Send message to TTS server and handle response
    Returns True if successful, False otherwise
        server_url = http://localhost:800 
    try:
        # Auto-detect language if needed
        if language == "auto":
            detected_lang = detect_language(message)
            print(f"🔍 Auto-detected language: {detected_lang}")
            language = detected_lang
        
        # Map language to supported format
        mapped_lang = map_language_to_supported(language)
        print(f"⚡ Speed: {speed}")
        
        # Switch model if needed
        if not switch_model_if_needed(server_url, mapped_lang):
            print(⚠️  Modelo xtts_v2ige amostra de voz")
            print("🔄 A tentar modelo alternativo que não exige amostra...")
            
            # Try alternative model
            alt_model = get_model_for_language(mapped_lang)
            if alt_model and alt_model != "tts_models/multilingual/multi-dataset/xtts_v2:             print(f"✅ Usando modelo alternativo: {alt_model.split('/')[-1]})            switch_model_if_needed(server_url, mapped_lang)
            else:
                print("❌ Não foi possível encontrar modelo alternativo)            return False
        
        # Prepare synthesis request
        synthesis_data = {
           textssage,
            language": mapped_lang,
         speed": speed
        }
        
        if speaker:
            synthesis_data["speaker"] = speaker
        
        # Send synthesis request
        print(f"🗣️  Sending message to TTS server: '{message}'")
        response = requests.post(f"{server_url}/synthesize", json=synthesis_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                audio_file = result.get('audio_file)                if audio_file:
                    # Download and save audio file
                    audio_url = f"{server_url}/audio/{audio_file}"
                    audio_response = requests.get(audio_url)
                    
                    if audio_response.status_code == 200:
                        # Save audio file
                        output_dir = Path("voice_outputs")
                        output_dir.mkdir(exist_ok=True)
                        
                        filename = output_dir / audio_file
                        with open(filename, 'wb') as f:
                            f.write(audio_response.content)
                        
                        print(f✅ Audio saved to: {filename}")
                        print(f"⏱️  Processing time: {result.get(processing_time', 0):.2f}s")
                        
                        if auto_play:
                            print("🔊 Audio file saved. Use a media player to play it.")
                            print(f"💡 Command: python3 -c \import playsound; playsound.playsound({filename}                 
                        return True
                    else:
                        print(f"❌ Failed to download audio: {audio_response.status_code}")
                        return False
                else:
                    print("❌ No audio file in response")
                    return False
            else:
                print(f"❌ Synthesis failed: {result.get('error', 'Unknown error')})            return False
        else:
            print(f"❌ Synthesis request failed: {response.status_code})
            try:
                error_data = response.json()
                print(f"💡 Error: {error_data.get(detail', 'Unknown error')}")
            except:
                print(f"💡 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in TTS synthesis: {e}")
        return False

def list_available_models(server_url=http://localhost:80:
    """
    List available models from the server.
    try:
        response = requests.get(f"{server_url}/models")
        if response.status_code == 200:
            data = response.json()
            print("📋 Available Models:")
            print("=" * 60
            for i, model in enumerate(data['models'], 1):
                status = "✅" if "[already downloaded] in model else "⬇️"
                clean_name = model.split(" [")[0             print(f"{i:2d}. {status} {clean_name}")
            print("=" * 60)
            print(f📊 Total: {data['total_models']} models")
            print(f"✅ Downloaded: {len(data[downloaded_models'])} models")
            print(f🔄 Current model: {data['current_model']}")
            return data
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return None

def switch_model(server_url=http://localhost:8000,model_name=None):
   tch to a different model on the server.   try:
        if model_name is None:
            # List models first
            models_data = list_available_models(server_url)
            if not models_data:
                return False
            
            # Ask user to select a model
            print("\n🎯 Select a model to switch to:")
            available_models = [m.split(" [")[0r m in models_data['models']]
            
            for i, model in enumerate(available_models, 1):
                print(f"{i:2d}. {model}")
            
            try:
                choice = input("\nEnter model number: ").strip()
                model_index = int(choice) -1                if 0 model_index < len(available_models):
                    model_name = available_models[model_index]
                else:
                    print("❌ Invalid model number")
                    returnfalse            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid input)            return False
        
        # Switch to the selected model
        print(f"🔄 Switching to model: {model_name}")
        response = requests.post(f"{server_url}/switch_model", params={"model_name": model_name})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully switched to: {data['current_model']}")
            if data['previous_model']:
                print(f📤 Previous model: {data['previous_model']}")
            return True
        else:
            print(f"❌ Failed to switch model: {response.status_code})
            try:
                error_data = response.json()
                print(f"💡 Error: {error_data.get(detail', 'Unknown error')}")
            except:
                print(f"💡 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f❌ Error switching model: {e}")
        return False

def interactive_mode():
    """Run in interactive mode    
    print("🎤 Coqui TTS Interactive Mode)
    print("=" *50    print("💡 Type your message and press Enter to synthesize")
    print(💡 Type 'quit' orexit' to stop")
    print("💡 Type 'help' for commands)
    print(=50   
    while True:
        try:
            # Get user input
            user_input = input("\n🗣️  You: ").strip()
            
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() in quit', 'exit', 'q']:
                print("👋 Goodbye!)             break
            elif user_input.lower() == 'help:             print_help()
                continue
            elif user_input.startswith('/'):
                # Handle special commands
                handle_command(user_input)
                continue
            
            # Synthesize speech with auto-detection
            success = talk_to_tts(user_input, language="auto", auto_play=True)
            
            if not success:
                print("❌ Failed to synthesize speech. Try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

def handle_command(command):
   e special commands   parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == '/lang and len(parts) >1    global current_language
        current_language = parts[1]
        print(f"🌍 Language set to: {current_language})    elif cmd ==/speed and len(parts) > 1:
        try:
            speed = float(parts[1])
            if 00.5 <= speed <= 2.0            global current_speed
                current_speed = speed
                print(f⚡ Speed set to: {speed}")
            else:
                print("❌ Speed must be between 0.5 and 2.0 except ValueError:
            print("❌ Invalid speed value)    elif cmd == '/help':
        print_help()
    else:
        print(❌ Unknown command. Type '/help' for available commands.)def print_help():t help information
    
    print("\n📖 Available Commands:")
    print( /lang <code>    - Set language (pt-br, en, fr-fr)")
    print( /speed <value>  - Set speed (0.5 to 20)")
    print("  /help          - Show this help")
    print("  quit/exit/q    - Exit the program)  print("\n💡 Just type your message to synthesize speech!")

def main():
    parser = argparse.ArgumentParser(description=Talk to Coqui TTS Server - Python Only")
    parser.add_argument(message, nargs=?, help="Message to synthesize")
    parser.add_argument("--language, -l, default="auto", help="Language code or 'auto' for detection (default: auto)")
    parser.add_argument("--speed",-sype=float, default=1.0, help="Speech speed (default:1)")
    parser.add_argument("--speaker", "-sp", default=None, help="Speaker name (optional)")
    parser.add_argument("--no-play", action=store_true", help="Don't play audio automatically")
    parser.add_argument("--interactive", "-i", action=store_true", help="Run in interactive mode")
    parser.add_argument("--voice-sample, "-vs", type=str, help="Path to voice sample for cloning (XTTS v2)")
    parser.add_argument(--channel", "-c", choices=[left, "right", stereo], default="right", help="Audio channel (left, right, stereo) (default: right)")
    parser.add_argument("--model, m", type=str, help="Model name to switch to before synthesis")
    parser.add_argument("--list-models", action=store_true", help="List available models")
    parser.add_argument("--switch-model", type=str, help="Switch to a specific model")
    args = parser.parse_args()
    
    # Handle model-related commands first
    if args.list_models:
        list_available_models()
        sys.exit(0)
    
    if args.switch_model:
        if switch_model(model_name=args.switch_model):
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Confirm channel selection with user
    print(f🎧 Audio channel: {args.channel.upper()}")
    if args.channel == "right:
        print("   → Using RIGHT channel (most common for voice synthesis)")
    elif args.channel == "left:
        print("   → Using LEFT channel")
    else:
        print(  → Using STEREO (both channels)")
    
    # Switch model if requested
    if args.model:
        if not switch_model(model_name=args.model):
            print("❌ Failed to switch model. Exiting.)          sys.exit(1)
    
    if args.interactive:
        interactive_mode()
    elif args.message:
        success = talk_to_tts(
            args.message, 
            language=args.language, 
            speed=args.speed, 
            auto_play=not args.no_play,
            speaker=args.speaker,
            voice_sample=args.voice_sample,
            channel=args.channel
        )
        sys.exit(0 if success else 1)
    else:
        print(🎤 Coqui TTS Talk Script - Python Only)      print("Usage:)
        print( python3 talk.py Your message here'                    # Auto-detect language)
        print( python3 talk.py 'Hello world' --language en           # Specify language)
        print( python3 talk.py 'Hello world --language en --speaker p225   # Specify speaker)
        print( python3 talk.py 'Hello world' --channel right         # Use right channel)
        print(python3 talk.py --interactive                         # Interactive mode)
        print(python3k.py --list-models                         # List available models)
        print(python3.py --switch-model 'model_name'           # Switch to specific model)
        print( python3 talk.py 'Hello world' --model 'model_name'          # Switch model and synthesize)
        print(python3 talk.py --help                                # Show help")
        print(n💡This version saves audio files to voice_outputs/ directory)
        print("💡 No external tools or subprocess calls - pure Python")
        sys.exit(1if __name__ == "__main__":
    main() 