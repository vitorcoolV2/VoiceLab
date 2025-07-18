#!/usr/bin/env python3
"""
TTS Client Tool
Handles communication with the TTS server for text-to-speech synthesis
"""

import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
import time

class TTSClient:
    """Client for communicating with the TTS server."""
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url

    def get_available_speakers(self) -> List[str]:
        """Get available speakers from the server."""
        try:
            response = requests.get(f"{self.server_url}/speaker/list")
            if response.status_code == 200:
                data = response.json()
                return data.get('speakers', [])
            else:
                print(f"❌ Failed to get speakers: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting speakers: {e}")
            return []

    def get_default_speaker_for_language(self, language: str) -> Optional[str]:
        """Get a default speaker for the given language.
        Args:
            language: Language code
        Returns:
            Default speaker name or None
        """
        speakers = self.get_available_speakers()
        if not speakers:
            return None
        
        # Try to find a speaker that matches the language
        language_prefix = language.split('-')[0]  # 'pt-br' -> 'pt'
        for speaker in speakers:
            if speaker.startswith(language_prefix):
                return speaker
        
        # If no language-specific speaker, return the first available
        return list(speakers.keys())[0] if speakers else None

    def synthesize(self,
                   text: str,
                   language: str = 'pt-br',
                   speed: float = 1.0,
                   speaker: Optional[str] = None,
                   channel: str = 'right',
                   speaker_wav: Optional[str] = None) -> Dict[str, Any]:
        """
        Send text to TTS server for synthesis.
        Args:
            text: Text to synthesize
            language: Language code (pt-br, en, es, fr, it)
            speed: Speech speed multiplier
            speaker: Optional speaker name
            channel: Audio channel (left, right, stereo)
            speaker_wav: Optional path to voice sample for XTTS v2
        Returns:
            Dictionary with success status and audio file path if successful
        """
        payload = {
            "text": text,
            "language": language,
            "speed": speed,
            "channel": channel
        }
        if speaker:
            payload["speaker"] = speaker
        if speaker_wav:
            payload["speaker_wav"] = speaker_wav
        try:
            t0 = time.time()
            response = requests.post(f"{self.server_url}/synthesize", json=payload)
            latency = time.time() - t0
            if response.status_code == 200:
                result = response.json()
                print(f"⏱️  Tempo de request: {latency:.2f}s")
                if 'processing_time' in result:
                    print(f"⏱️  Tempo de processamento no servidor: {result['processing_time']:.2f}s")
                return result
            else:
                print(f"⏱️  Tempo de request: {latency:.2f}s")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }

    def download_audio(self, audio_file: str, output_dir: str = "voice_outputs") -> Optional[Path]:
        """
        Download audio file from server and save to local directory.
        Args:
            audio_file: Name of the audio file to download
            output_dir: Directory to save the audio file
        Returns:
            Path to saved file if successful, None otherwise
        """
        try:
            audio_url = f"{self.server_url}/audio/get/{audio_file}"
            t0 = time.time()
            audio_response = requests.get(audio_url)
            latency = time.time() - t0
            if audio_response.status_code == 200:
                print(f"⏱️  Tempo de download do áudio: {latency:.2f}s")
                output_path = Path(output_dir)
                output_path.mkdir(exist_ok=True)
                filename = output_path / audio_file
                with open(filename, 'wb') as f:
                    f.write(audio_response.content)
                return filename
            else:
                print(f"❌ Failed to download audio: {audio_response.status_code}")
                print(f"⏱️  Tempo de download do áudio: {latency:.2f}s")
                return None
        except Exception as e:
            print(f"❌ Error downloading audio: {e}")
            return None

    def get_registered_speakers(self) -> Dict[str, Any]:
        """Get registered speakers from the server."""
        try:
            t0 = time.time()
            response = requests.get(f"{self.server_url}/speaker/list")
            latency = time.time() - t0
            if response.status_code == 200:
                print(f"⏱️  Tempo de request: {latency:.2f}s")
                data = response.json()
                return data.get('speakers', {})
            else:
                print(f"❌ Failed to get registered speakers: {response.status_code}")
                print(f"⏱️  Tempo de request: {latency:.2f}s")
                return {}
        except Exception as e:
            print(f"❌ Error getting registered speakers: {e}")
            return {}

    def synthesize_and_save(self,
                            text: str,
                            language: str = 'pt-br',
                            speed: float = 1.0,
                            speaker: Optional[str] = None,
                            channel: str = 'right',
                            output_dir: str = "voice_outputs",
                            voice_sample_path: Optional[str] = None) -> Optional[Path]:
        """
        Complete synthesis and save workflow.
        Args:
            text: Text to synthesize
            language: Language code
            speed: Speech speed
            speaker: Optional speaker name
            channel: Audio channel
            output_dir: Directory to save audio
            voice_sample_path: Optional path to a reference .wav for voice cloning
        Returns:
            Path to saved audio file if successful, None otherwise
        """
        print(f"🗣️  Sending message to TTS server: '{text}'")

        # 1. Se speaker está registado no servidor, usar /synthesize com o nome
        registered_speakers = self.get_registered_speakers()
        if speaker and speaker in registered_speakers:
            print(f"🎤 Using registered server speaker: {speaker}")
            # Para XTTS v2, precisamos do speaker_wav
            speaker_info = registered_speakers.get(speaker, {})
            speaker_wav = speaker_info.get('sample_path')
            if speaker_wav and Path(speaker_wav).exists():
                print(f"🎤 Using voice sample: {speaker_wav}")
                result = self.synthesize(text, language, speed, speaker, channel, speaker_wav)
            else:
                print(f"❌ Voice sample not found or doesn't exist: {speaker_wav}")
                result = self.synthesize(text, language, speed, speaker, channel)
            if not result.get('success'):
                print(f"❌ Synthesis failed: {result.get('error', 'Unknown error')}")
                return None
            audio_file = result.get('audio_file')
            if not audio_file:
                print("❌ No audio file in response")
                return None
            filename = self.download_audio(audio_file, output_dir)
            if filename:
                print(f"✅ Audio saved to: {filename}")
                processing_time = result.get('processing_time', 0)
                print(f"⏱️  Processing time: {processing_time:.2f}s")
                print(f"🔊 Use your preferred player to listen to the file.")
                return filename
            return None

        # 2. Se não, tentar síntese normal (multi-speaker tradicional ou single)
        # Se temos voice_sample_path, usar voice cloning
        if voice_sample_path and Path(voice_sample_path).exists():
            print(f"🎤 Using voice cloning with sample: {voice_sample_path}")
            result = self.synthesize(text, language, speed, speaker, channel, voice_sample_path)
        else:
            result = self.synthesize(text, language, speed, speaker, channel)

        # 3. Se falhar por erro de speaker, tentar voice cloning ad-hoc
        if not result.get('success') and "speaker" in result.get('error', ''):
            print("🔍 Multi-speaker model detected, trying to find default speaker...")
            default_speaker = self.get_default_speaker_for_language(language)
            if default_speaker:
                print(f"🎤 Using default speaker: {default_speaker}")
                result = self.synthesize(text, language, speed, default_speaker, channel)
            else:
                # Fallback: try voice cloning with a reference sample if available
                if not voice_sample_path:
                    # Try to find a default sample in output/
                    sample_candidates = list(Path("output").glob("*.wav"))
                    if sample_candidates:
                        voice_sample_path = str(sample_candidates[0])
                if voice_sample_path and Path(voice_sample_path).exists():
                    print(f"🔄 Trying voice cloning with sample: {voice_sample_path}")
                    # Use the /clone_voice endpoint
                    try:
                        files = {'audio_file': open(voice_sample_path, 'rb')}
                        data = {'text': text, 'language': language}
                        response = requests.post(f"{self.server_url}/clone_voice", files=files, data=data)
                        if response.status_code == 200:
                            result = response.json()
                            audio_file = result.get('cloned_audio')
                            if audio_file:
                                filename = self.download_audio(audio_file, output_dir)
                                if filename:
                                    print(f"✅ Audio saved to: {filename}")
                                    print(f"🔊 Use your preferred player to listen to the file.")
                                    return filename
                        print(f"❌ Voice cloning failed: {response.text}")
                        return None
                    except Exception as e:
                        print(f"❌ Voice cloning request failed: {e}")
                        return None
                else:
                    print("❌ No default speaker or voice sample found. Please specify a speaker with --speaker or provide a .wav sample.")
                    return None

        if not result.get('success'):
            print(f"❌ Synthesis failed: {result.get('error', 'Unknown error')}")
            return None

        audio_file = result.get('audio_file')
        if not audio_file:
            print("❌ No audio file in response")
            return None

        filename = self.download_audio(audio_file, output_dir)
        if filename:
            print(f"✅ Audio saved to: {filename}")
            processing_time = result.get('processing_time', 0)
            print(f"⏱️  Processing time: {processing_time:.2f}s")
            print(f"🔊 Use your preferred player to listen to the file.")
            return filename
        return None

def create_tts_client(server_url: str = "http://localhost:8000") -> TTSClient:
    """Factory function to create a TTS client instance."""
    return TTSClient(server_url) 