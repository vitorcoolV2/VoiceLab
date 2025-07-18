#!/usr/bin/env python3
"""
YouTube Voice Cloner
Downloads YouTube videos and clones their voices using Coqui TTS
"""

import os
import sys
import json
import requests
import yt_dlp
import librosa
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeVoiceCloner:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        # Usar variável de ambiente para downloads
        self.download_dir = Path(os.environ.get("COQUI_TTS_DOWNLOADS", "downloads"))
        self.download_dir.mkdir(exist_ok=True)
        
        # Carregar variáveis de ambiente do .env se existir
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value
            except Exception as e:
                logger.warning(f"Could not load .env file: {e}")
        
        # Diretório de outputs dinâmico
        self.output_dir = os.environ.get("COQUI_TTS_OUTPUTS", "output")
        
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace spaces with underscores
        filename = re.sub(r'\s+', '_', filename)
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        return filename
        
    def generate_filename_with_language(self, base_name: str, language: str, suffix: str = "") -> str:
        """Generate filename with language suffix"""
        # Sanitize base name
        sanitized_name = self.sanitize_filename(base_name)
        
        # Add language suffix
        if suffix:
            filename = f"{sanitized_name}_{language}_{suffix}.wav"
        else:
            filename = f"{sanitized_name}_{language}.wav"
            
        return filename
        
    def play_audio(self, audio_file: str) -> bool:
        try:
            from playsound import playsound
            logger.info(f"🎵 Playing audio: {audio_file}")
            playsound(audio_file)
            return True
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
        
    def download_youtube_video(self, url: str, language: str = "en", quality: str = "bestaudio") -> Optional[str]:
        try:
            # First, get video info to generate proper filename
            ydl_opts_info = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'unknown')
                duration = info.get('duration', 0)
                
                # Generate filename with language
                base_filename = self.generate_filename_with_language(video_title, language)
                output_template = str(self.download_dir / base_filename.replace('.wav', '.%(ext)s'))
                
                logger.info(f"Downloading audio from: {url}")
                logger.info(f"Video: {video_title}")
                logger.info(f"Duration: {duration} seconds")
                logger.info(f"Output filename: {base_filename}")
            
            # Download with custom filename
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
                # Find the downloaded file
                downloaded_file = None
                for file in self.download_dir.glob("*.wav"):
                    if file.stat().st_size > 0 and language in file.name:
                        downloaded_file = str(file)
                        break
                        
                if downloaded_file:
                    logger.info(f"Downloaded: {downloaded_file}")
                    return downloaded_file
                else:
                    logger.error("No audio file found after download")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def extract_voice_sample(self, audio_file: str, language: str = "en", start_time: float = 10.0, duration: float = 30.0) -> Optional[str]:
        try:
            import librosa
            y, sr = librosa.load(audio_file, sr=None)
            start_sample = int(start_time * sr)
            end_sample = int((start_time + duration) * sr)
            voice_sample = y[start_sample:end_sample]
            
            # Generate voice sample filename with language
            base_name = Path(audio_file).stem
            if base_name.endswith(f"_{language}"):
                base_name = base_name[:-len(f"_{language}")]
            
            output_file = self.generate_filename_with_language(base_name, language, "voice_sample")
            output_path = self.download_dir / output_file
            
            import soundfile as sf
            sf.write(str(output_path), voice_sample, sr)
            logger.info(f"Voice sample extracted: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error extracting voice sample: {e}")
            return None
    
    def analyze_voice(self, audio_file: str) -> Optional[Dict[str, Any]]:
        try:
            with open(audio_file, 'rb') as f:
                files = {'audio_file': f}
                response = requests.post(f"{self.server_url}/analyze_voice", files=files)
            if response.status_code == 200:
                result = response.json()
                logger.info("Voice analysis completed")
                return result
            else:
                logger.error(f"Voice analysis failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error analyzing voice: {e}")
            return None
    
    def clone_voice(self, reference_audio: str, text: str, language: str = "en", model_name: str = None) -> Optional[str]:
        try:
            # Normalize language for TTS compatibility
            normalized_language = self.normalize_language(language)
            
            with open(reference_audio, 'rb') as f:
                files = {'audio_file': f}
                data = {'text': text}
                # Only add language parameter for multilingual models
                if model_name and 'multilingual' in model_name:
                    data['language'] = normalized_language
                if model_name:
                    data['model_name'] = model_name
                response = requests.post(f"{self.server_url}/clone_voice", files=files, data=data)
            if response.status_code == 200:
                # Check if response is JSON (success/error) or audio (direct)
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type or response.content.startswith(b'{'):
                    # Response is JSON
                    result = response.json()
                    if result.get('success'):
                        # Success - copy file from server output directory
                        server_file = result.get('cloned_audio')
                        if server_file:
                            server_path = os.path.join(self.output_dir, server_file)
                            if os.path.exists(server_path):
                                # Generate cloned filename with language
                                base_name = Path(reference_audio).stem
                                if base_name.endswith("_voice_sample"):
                                    base_name = base_name[:-13]  # Remove _voice_sample
                                
                                cloned_filename = self.generate_filename_with_language(base_name, language, "cloned")
                                cloned_path = self.download_dir / cloned_filename
                                
                                import shutil
                                shutil.copy2(server_path, cloned_path)
                                logger.info(f"Voice cloned successfully: {cloned_path}")
                                return str(cloned_path)
                            else:
                                logger.error(f"Server file not found: {server_path}")
                                return None
                        else:
                            logger.error("No cloned_audio path in response")
                            return None
                    else:
                        # Error
                        logger.error(f"Voice cloning failed: {result}")
                        return None
                else:
                    # Response is audio (direct) - not used in current implementation
                    logger.error("Direct audio response not supported")
                    return None
            else:
                logger.error(f"Voice cloning failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error cloning voice: {e}")
            return None

    def normalize_language(self, language: str) -> str:
        # XTTS v2 só aceita 'pt' para português
        lang = language.lower().replace('_', '-').strip()
        if lang in ['pt', 'pt-pt', 'pt-br']:
            return 'pt'
        if lang in ['en', 'en-us']:
            return 'en'
        if lang in ['fr', 'fr-fr']:
            return 'fr'
        # Adicione outros idiomas conforme necessário
        return lang
        
    def process_viral_video(self, url: str, text_to_speak: str = "Olá! Esta é uma demonstração de clonagem de voz.", auto_play: bool = True, language: str = "pt-br") -> dict:
        """
        Complete pipeline: download video, extract voice, analyze, clone, and optionally play
        """
        # Normalize language for TTS compatibility
        normalized_language = self.normalize_language(language)
        
        result = {
            'success': False,
            'video_url': url,
            'language': language,  # Keep original for display
            'normalized_language': normalized_language,  # Add normalized version
            'downloaded_file': None,
            'voice_sample': None,
            'voice_analysis': None,
            'cloned_audio': None,
            'error': None
        }
        try:
            # Step 1: Download YouTube video with language in filename
            downloaded_file = self.download_youtube_video(url, language)  # Use original for filename
            if not downloaded_file:
                result['error'] = "Failed to download video"
                return result
            result['downloaded_file'] = downloaded_file
            
            # Step 2: Extract voice sample with language in filename
            voice_sample = self.extract_voice_sample(downloaded_file, language)  # Use original for filename
            if not voice_sample:
                result['error'] = "Failed to extract voice sample"
                return result
            result['voice_sample'] = voice_sample
            
            # Step 3: Analyze voice
            voice_analysis = self.analyze_voice(voice_sample)
            if voice_analysis:
                result['voice_analysis'] = voice_analysis
                
            # Step 4: Clone voice with normalized language for TTS
            cloned_audio = self.clone_voice(
                reference_audio=voice_sample,
                text=text_to_speak,
                language="pt-br",
                model_name="tts_models/multilingual/multi-dataset/xtts_v2"
            )
            if cloned_audio:
                result['cloned_audio'] = cloned_audio
                result['success'] = True
                if auto_play:
                    self.play_audio(cloned_audio)
            else:
                result['error'] = "Failed to clone voice"
                
        except Exception as e:
            result['error'] = str(e)
        return result 

    def process_video(self, url: str, text_to_speak: str = "Olá! Esta é uma demonstração de clonagem de voz.", auto_play: bool = True, language: str = "pt-br") -> dict:
        """
        Alias para process_viral_video, para compatibilidade com scripts antigos.
        """
        return self.process_viral_video(url, text_to_speak, auto_play, language) 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Voice Cloner CLI")
    parser.add_argument('--download', type=str, help='YouTube URL para baixar')
    parser.add_argument('--language', type=str, default='en', help='Idioma do áudio')
    parser.add_argument('--output', type=str, help='Nome do arquivo de saída WAV')
    args = parser.parse_args()

    cloner = YouTubeVoiceCloner()

    if args.download:
        # Se --output for especificado, passar para yt_dlp como outtmpl, removendo .wav se necessário
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        output_name = None
        if args.output:
            output_name = args.output
            if output_name.lower().endswith('.wav'):
                output_name = output_name[:-4]
            ydl_opts['outtmpl'] = output_name
        else:
            ydl_opts['outtmpl'] = 'downloads/%(title)s_%(id)s'

        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(args.download, download=True)
            final_wav = ydl.prepare_filename(info)
            if not final_wav.lower().endswith('.wav'):
                final_wav += '.wav'
            print(f"Arquivo salvo como: {final_wav}")
            if args.output and not final_wav.endswith('.wav'):
                print(f"Atenção: nome final ajustado para {final_wav} para garantir extensão correta.") 