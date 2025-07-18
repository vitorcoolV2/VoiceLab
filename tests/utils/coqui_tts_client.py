#!/usr/bin/env python3
"""
Simple Coqui TTS Client for testing purposes
"""

import requests
import json
import os
from pathlib import Path

class CoquiTTSClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def synthesize(self, text, speaker=None, language=None, output_format="wav", 
                   speed=1.0, pitch=1.0, volume=1.0, voice_style=None, save_to_file=None):
        """Synthesize text to speech"""
        try:
            data = {
                "text": text,
                "output_format": output_format,
                "speed": speed,
                "pitch": pitch,
                "volume": volume
            }
            
            if speaker:
                data["speaker"] = speaker
            if language:
                data["language"] = language
            if voice_style:
                data["voice_style"] = voice_style
            
            response = requests.post(f"{self.base_url}/synthesize", json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Save to file if requested
                if save_to_file and result.get('success'):
                    audio_file = result.get('audio_file')
                    if audio_file:
                        # Create directory if it doesn't exist
                        save_dir = Path(save_to_file).parent
                        save_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Download the audio file
                        audio_response = requests.get(f"{self.base_url}/audio/{audio_file}")
                        if audio_response.status_code == 200:
                            with open(save_to_file, 'wb') as f:
                                f.write(audio_response.content)
                            print(f"✅ Audio saved to: {save_to_file}")
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_health(self):
        """Get server health status"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_models(self):
        """Get available TTS models"""
        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_speakers(self):
        """Get available speakers for current model"""
        try:
            response = requests.get(f"{self.base_url}/speakers")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def clone_voice(self, audio_file_path, text, language=None, speed=1.0, pitch=1.0, volume=1.0, voice_style=None, save_to_file=None):
        """Clone voice from audio sample"""
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'audio_file': f}
                data = {
                    'text': text,
                    'speed': speed,
                    'pitch': pitch,
                    'volume': volume
                }
                
                if language:
                    data['language'] = language
                if voice_style:
                    data['voice_style'] = voice_style
                
                response = requests.post(f"{self.base_url}/clone_voice", files=files, data=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Save to file if requested
                    if save_to_file and result.get('success'):
                        cloned_audio = result.get('cloned_audio')
                        if cloned_audio:
                            # Create directory if it doesn't exist
                            save_dir = Path(save_to_file).parent
                            save_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Copy the cloned audio file - use server output path
                            import shutil
                            # Server output path from env
                            server_output_path = os.environ.get("COQUI_TTS_OUTPUTS", "/media/vitor/ssd990/home-backup/coqui-outputs")
                            
                            if os.path.isabs(cloned_audio):
                                source_path = cloned_audio
                            else:
                                source_path = os.path.join(server_output_path, cloned_audio)
                            
                            if os.path.exists(source_path):
                                shutil.copy2(source_path, save_to_file)
                                print(f"✅ Cloned audio saved to: {save_to_file}")
                            else:
                                print(f"⚠️ Source file not found: {source_path}")
                                # Try to find the file in server output directory
                                if os.path.exists(server_output_path):
                                    for root, dirs, files in os.walk(server_output_path):
                                        if os.path.basename(cloned_audio) in files:
                                            found_path = os.path.join(root, os.path.basename(cloned_audio))
                                            shutil.copy2(found_path, save_to_file)
                                            print(f"✅ Cloned audio found and saved to: {save_to_file}")
                                            break
                                    else:
                                        print(f"❌ Could not find cloned audio file: {cloned_audio}")
                                else:
                                    print(f"❌ Server output directory not found: {server_output_path}")
                    
                    return result
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 