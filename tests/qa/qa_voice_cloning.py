#!/usr/bin/env python3
"""
Refactored QA Testing Tool for Voice Cloning Pipeline
Automatically detects samples from youtube_voice_cloner.py and uses server API
"""

import os
import time
import glob
import requests
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import argparse
import sys
import wave
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.audio_utils.audio_player import AudioPlayer

# ANSI color codes for better console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class VoiceCloningQA:
    """Refactored QA testing tool for voice cloning pipeline"""
    
    def __init__(self, server_url: str = "http://localhost:8000", 
                 player: str = "auto", auto_play: bool = True, 
                 pause_between: float = 3.0, volume: int = 100):
        """
        Initialize refactored QA testing tool
        
        Args:
            server_url: TTS server URL
            player: Audio player to use
            auto_play: Whether to automatically play samples
            pause_between: Pause between samples in seconds
            volume: Volume level (0-100)
        """
        self.server_url = server_url
        self.player = AudioPlayer(player=player, volume=volume, wait_for_completion=True)
        self.auto_play = auto_play
        self.pause_between = pause_between
        self.qa_results = {}
        self.start_time = time.time()
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}{Colors.ENDC}")
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}📋 {title}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{'-'*40}{Colors.ENDC}")
        
    def print_success(self, message: str):
        """Print a success message"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
        
    def print_error(self, message: str):
        """Print an error message"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
        
    def print_warning(self, message: str):
        """Print a warning message"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
        
    def print_info(self, message: str):
        """Print an info message"""
        print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")
        
    def print_progress(self, current: int, total: int, description: str):
        """Print a progress bar"""
        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r{Colors.OKBLUE}[{bar}] {percentage:.1f}% - {description}{Colors.ENDC}", end='', flush=True)
        if current == total:
            print()  # New line when complete
        
    def check_server_health(self) -> bool:
        """Check if TTS server is running"""
        self.print_section("Server Health Check")
        try:
            print(f"🔍 Connecting to server: {self.server_url}")
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                self.print_success(f"Server is healthy: {health.get('status', 'unknown')}")
                print(f"   🎤 TTS: {'✅' if health.get('tts_initialized', False) else '❌'}")
                print(f"   🎧 Whisper: {'✅' if health.get('whisper_initialized', False) else '❌'}")
                print(f"   🚀 GPU: {'✅' if health.get('gpu_available', False) else '❌'}")
                print(f"   ⏰ Timestamp: {health.get('timestamp', 'unknown')}")
                return True
            else:
                self.print_error(f"Server unhealthy: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Cannot connect to server: {e}")
            return False
    
    def detect_youtube_samples(self) -> List[Dict]:
        """
        Detect samples with patterns: <base>.wav, <base>_voice_sample.wav, <base>_cloned.wav
        """
        self.print_section("Sample Detection")
        samples = []
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            self.print_warning("Downloads directory not found")
            return samples
            
        print(f"🔍 Scanning directory: {downloads_dir.absolute()}")
        wav_files = list(downloads_dir.glob("*.wav"))
        print(f"📁 Found {len(wav_files)} WAV files")
        
        if not wav_files:
            self.print_warning("No WAV files found in downloads directory")
            return samples
            
        # Group by base name
        file_groups = {}
        for wav_file in wav_files:
            filename = wav_file.stem
            if filename.endswith('_voice_sample'):
                base_name = filename[:-13]
                file_groups.setdefault(base_name, {})['voice_sample'] = str(wav_file)
            elif filename.endswith('_cloned'):
                base_name = filename[:-7]
                file_groups.setdefault(base_name, {})['cloned'] = str(wav_file)
            else:
                base_name = filename
                file_groups.setdefault(base_name, {})['original'] = str(wav_file)
                
        print(f"📊 Grouped into {len(file_groups)} potential samples")
        
        for base_name, files in file_groups.items():
            sample = {
                'name': base_name,
                'original': files.get('original'),
                'voice_sample': files.get('voice_sample'),
                'cloned': files.get('cloned'),
                'complete': all(files.get(k) for k in ['original', 'voice_sample', 'cloned'])
            }
            samples.append(sample)
            
            # Show sample status
            status = "✅ Complete" if sample['complete'] else "⚠️  Partial"
            print(f"   {status} - {base_name}")
            for stage, file_path in files.items():
                exists = "✅" if file_path and os.path.exists(file_path) else "❌"
                print(f"      {exists} {stage}: {os.path.basename(file_path) if file_path else 'Missing'}")
        
        return samples

    def get_wav_duration(self, file_path: str) -> float:
        """Get duration of WAV file in seconds"""
        try:
            with wave.open(file_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate)
        except Exception:
            return 0.0

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def analyze_voice_with_server(self, voice_sample_path: str) -> Optional[Dict]:
        """Analyze voice using server API"""
        self.print_section("Voice Analysis")
        try:
            print(f"🔬 Analyzing: {os.path.basename(voice_sample_path)}")
            with open(voice_sample_path, 'rb') as f:
                files = {'audio_file': f}
                response = requests.post(f"{self.server_url}/analyze_voice", files=files, timeout=30)
            
            if response.status_code == 200:
                analysis = response.json()
                self.print_success("Voice analysis completed")
                
                if 'metrics' in analysis:
                    metrics = analysis['metrics']
                    print(f"   🎭 Voice Type: {Colors.BOLD}{metrics.get('voice_type', 'Unknown')}{Colors.ENDC}")
                    print(f"   🎵 Pitch: {Colors.BOLD}{metrics.get('pitch_mean', 'Unknown'):.0f} Hz{Colors.ENDC}")
                    print(f"   ⚡ Energy: {Colors.BOLD}{metrics.get('energy_mean', 'Unknown'):.3f}{Colors.ENDC}")
                    print(f"   🗣️  Speaking Rate: {Colors.BOLD}{metrics.get('speaking_rate', 'Unknown'):.1f} words/min{Colors.ENDC}")
                    print(f"   ⏱️  Duration: {Colors.BOLD}{metrics.get('duration', 'Unknown'):.2f} seconds{Colors.ENDC}")
                    print(f"   🌟 Brightness: {Colors.BOLD}{metrics.get('brightness', 'Unknown'):.0f}{Colors.ENDC}")
                    print(f"   🔥 Warmth: {Colors.BOLD}{metrics.get('warmth', 'Unknown'):.0f}{Colors.ENDC}")
                
                return analysis
            else:
                self.print_error(f"Voice analysis failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            self.print_error(f"Error analyzing voice: {e}")
            return None
    
    def clone_voice_with_server(self, voice_sample_path: str, text: str, language: str = "en") -> Optional[str]:
        """Clone voice using server API"""
        try:
            with open(voice_sample_path, 'rb') as f:
                files = {'audio_file': f}
                data = {'text': text, 'language': language}
                response = requests.post(f"{self.server_url}/clone_voice", files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Return full path to the cloned audio file
                    cloned_filename = result.get('cloned_audio')
                    if cloned_filename:
                        # The server saves files in the output directory
                        return f"output/{cloned_filename}"
                    return None
                else:
                    self.print_error(f"Voice cloning failed: {result.get('error', 'Unknown error')}")
                    return None
            else:
                self.print_error(f"Voice cloning failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            self.print_error(f"Error cloning voice: {e}")
            return None
    
    def play_sample_stage(self, stage: str, file_path: str, sample_name: str) -> bool:
        """Play a single stage of the sample"""
        if not file_path or not os.path.exists(file_path):
            self.print_error(f"{stage.title()} file not found for {sample_name}")
            return False
        
        stage_labels = {
            'original': f"Original YouTube Audio: {sample_name}",
            'voice_sample': f"Voice Sample: {sample_name}",
            'cloned': f"Cloned Voice: {sample_name}"
        }
        
        label = stage_labels.get(stage, f"{stage.title()}: {sample_name}")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        duration = self.get_wav_duration(file_path)
        
        print(f"\n🎵 Playing {stage}: {os.path.basename(file_path)}")
        print(f"   📁 Path: {file_path}")
        print(f"   📊 Size: {self.format_file_size(file_size)}")
        print(f"   ⏱️  Duration: {duration:.2f} seconds")
        
        if self.auto_play:
            # Customize playback duration based on stage
            if stage == 'original':
                print(f"   ⏱️  Playing first 5 seconds only...")
                success = self.player.play_file(file_path, label, start_time=0, duration=5.0)
            elif stage == 'voice_sample':
                print(f"   ⏱️  Playing first 10 seconds only...")
                success = self.player.play_file(file_path, label, start_time=0, duration=10.0)
            else:  # cloned
                print(f"   ⏱️  Playing complete cloned audio...")
                success = self.player.play_file(file_path, label)
                
            if success and self.pause_between > 0:
                print(f"   ⏸️  Waiting {self.pause_between} seconds...")
                time.sleep(self.pause_between)
            return success
        else:
            print(f"   ⏸️  Auto-play disabled. Would play: {label}")
            return True
    
    def test_sample(self, sample: Dict) -> Dict:
        sample_name = sample['name']
        self.print_header(f"QA Testing Sample: {sample_name}")
        
        # File status with detailed info
        self.print_section("File Analysis")
        file_info = {}
        total_size = 0
        
        for stage in ['original', 'voice_sample', 'cloned']:
            file_path = sample.get(stage)
            exists = file_path and os.path.exists(file_path)
            size_kb = os.path.getsize(file_path) / 1024 if exists else 0
            duration = self.get_wav_duration(file_path) if exists else 0
            status = "✅" if exists else "❌"
            
            print(f"   {status} {stage.upper()}:")
            if exists:
                print(f"      📄 File: {os.path.basename(file_path)}")
                print(f"      📊 Size: {self.format_file_size(size_kb * 1024)}")
                print(f"      ⏱️  Duration: {duration:.2f} seconds")
                total_size += size_kb
            else:
                print(f"      ❌ Not found")
            
            file_info[stage] = {
                'file_path': file_path,
                'exists': exists,
                'size_kb': size_kb,
                'duration_sec': duration
            }
        
        print(f"\n📈 Total Sample Size: {self.format_file_size(total_size * 1024)}")
        
        results = {
            'sample_name': sample_name,
            'files': file_info,
            'stages': {},
            'server_analysis': None,
            'success': sample['complete'],
            'total_size_kb': total_size
        }
        
        # Play and analyze
        self.print_section("Audio Playback & Analysis")
        if sample['original']:
            self.play_sample_stage('original', sample['original'], sample_name)
            results['stages']['original'] = {'played': True}
            
        if sample['voice_sample']:
            self.play_sample_stage('voice_sample', sample['voice_sample'], sample_name)
            results['stages']['voice_sample'] = {'played': True}
            
            # Analyze with server
            analysis = self.analyze_voice_with_server(sample['voice_sample'])
            if analysis:
                results['server_analysis'] = analysis
                
        if sample['cloned']:
            self.play_sample_stage('cloned', sample['cloned'], sample_name)
            results['stages']['cloned'] = {'played': True}
            
            # Validate cloned audio with Whisper
            whisper_validation = self.validate_cloned_audio_with_whisper(sample['cloned'])
            if whisper_validation:
                results['whisper_validation'] = whisper_validation
        
        # Generate new synthesis with cloned voice
        if sample['voice_sample']:
            self.print_section("🎤 New Voice Synthesis Test")
            # Acumular dados de amostras para gerar mensagem de 15 segundos
            accumulated_data = {
                'pt-br': {
                    'texts': [
                        "Olá! Esta é uma demonstração da minha voz clonada usando inteligência artificial.",
                        "A tecnologia de síntese de voz está revolucionando a forma como interagimos com computadores.",
                        "Esta voz foi criada através de um processo chamado clonagem de voz, que analisa características únicas como tom, ritmo e entonação.",
                        "O sistema consegue capturar nuances específicas da fala, incluindo pausas naturais, variações de pitch e expressões emocionais.",
                        "Esta demonstração mostra como é possível criar vozes personalizadas de alta qualidade para diversas aplicações."
                    ],
                    'total_duration': 0
                },
                'en': {
                    'texts': [
                        "Hello! This is a demonstration of my cloned voice using artificial intelligence.",
                        "Voice synthesis technology is revolutionizing how we interact with computers.",
                        "This voice was created through a process called voice cloning, which analyzes unique characteristics like tone, rhythm, and intonation.",
                        "The system can capture specific speech nuances, including natural pauses, pitch variations, and emotional expressions.",
                        "This demonstration shows how it's possible to create high-quality personalized voices for various applications."
                    ],
                    'total_duration': 0
                }
            }
            
            # Gerar síntese acumulada de 15 segundos para cada idioma
            for lang, data in accumulated_data.items():
                print(f"\n🎤 Generating 15-second accumulated synthesis for {lang.upper()}")
                print(f"   📝 Combining {len(data['texts'])} text segments")
                
                # Combinar todos os textos em uma mensagem de 15 segundos
                combined_text = " ".join(data['texts'])
                print(f"   🎯 Target duration: 15 seconds")
                print(f"   📄 Combined text: {combined_text[:100]}...")
                
                # Sintetizar a mensagem completa
                cloned_audio_path = self.clone_voice_with_server(sample['voice_sample'], combined_text, lang)
                
                if cloned_audio_path and os.path.exists(cloned_audio_path):
                    # Converter para 48 kHz com redução de ruído e artefatos
                    # Filtros aplicados:
                    # - highpass=f=80: Remove ruídos de baixa frequência
                    # - lowpass=f=8000: Remove artefatos de alta frequência (esquiletes)
                    # - volume=1.2: Aumenta volume ligeiramente
                    # - anlmdn: Reduz ruído não-linear (artefatos de síntese)
                    # - compand: Compressão dinâmica (reduz esquiletes e picos)
                    converted_path = cloned_audio_path.replace('.wav', f'_15sec_{lang}_48khz.wav')
                    # Note: ffmpeg processing removed - using original audio
                    # For full audio processing, install ffmpeg and uncomment the subprocess call below
                    # import subprocess
                    # subprocess.run([
                    #     'ffmpeg', '-y', '-loglevel', 'error',
                    #     '-i', cloned_audio_path,
                    #     '-af', 'highpass=f=80,lowpass=f=8000,volume=1.2,anlmdn=s=7:p=0.002:r=0.01,compand=0.3|0.3:1|1:-90/-60/-40/-30/-20/-10/-3/0:6:0:-90:0.2',
                    #     '-ar', '48000',
                    #     converted_path
                    # ])
                    # For now, just copy the original file
                    import shutil
                    shutil.copy2(cloned_audio_path, converted_path)
                    
                    # Verificar duração real
                    actual_duration = self.get_wav_duration(converted_path)
                    print(f"   ⏱️  Actual duration: {actual_duration:.2f} seconds")
                    
                    # Usar Whisper para validar qualidade do áudio
                    print(f"   🎧 Validating audio quality with Whisper...")
                    whisper_validation = self.validate_cloned_audio_with_whisper(converted_path, combined_text)
                    
                    if whisper_validation:
                        confidence = whisper_validation.get('confidence', 0)
                        transcribed = whisper_validation.get('transcribed_text', '')
                        similarity = whisper_validation.get('text_similarity', 0)
                        
                        print(f"   🎯 Whisper Confidence: {confidence:.1f}%")
                        print(f"   📝 Text Similarity: {similarity:.1f}%")
                        
                        # Avaliar qualidade baseada no Whisper
                        if confidence > 70 and similarity > 80:
                            print(f"   ✅ High quality audio detected")
                            quality_score = "Excellent"
                        elif confidence > 50 and similarity > 60:
                            print(f"   ⚠️  Medium quality audio detected")
                            quality_score = "Good"
                        else:
                            print(f"   ❌ Low quality audio detected - possible artifacts")
                            quality_score = "Poor"
                    else:
                        quality_score = "Unknown"
                        print(f"   ⚠️  Whisper validation failed")
                    
                    # Play the accumulated synthesis
                    print(f"   🎵 Playing 15-second accumulated synthesis...")
                    success = self.player.play_file(converted_path, f"15-Second Accumulated Synthesis [{lang}]: {sample_name}")
                    
                    if success and self.pause_between > 0:
                        print(f"   ⏸️  Waiting {self.pause_between} seconds...")
                        time.sleep(self.pause_between)
                    
                    results['stages'][f'accumulated_15sec_{lang}'] = {
                        'played': True,
                        'text': combined_text,
                        'language': lang,
                        'audio_path': converted_path,
                        'duration': actual_duration,
                        'text_count': len(data['texts']),
                        'whisper_validation': whisper_validation,
                        'quality_score': quality_score
                    }
                else:
                    print(f"   ❌ Failed to synthesize 15-second message for {lang}")
                    results['stages'][f'accumulated_15sec_{lang}'] = {
                        'played': False,
                        'language': lang,
                        'error': 'Synthesis failed'
                    }
            

        

        
        # Server tools analysis and recommendations
        analysis = self.analyze_server_tools_performance(results)
        recommendations = self.recommend_tools_combination(analysis)
        
        # Print recommendations
        self.print_tools_recommendations(recommendations)
        
        # Generate and save tools report
        tools_report = self.generate_tools_report(analysis, recommendations)
        report_filename = f"tools_analysis_{sample_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        try:
            with open(report_filename, 'w') as f:
                f.write(tools_report)
            self.print_success(f"Tools analysis report saved: {report_filename}")
        except Exception as e:
            self.print_error(f"Could not save tools report: {e}")
        
        # Summary
        self.print_section("Test Summary")
        print(f"🎯 Sample: {sample_name}")
        print(f"✅ Complete Pipeline: {'Yes' if sample['complete'] else 'No'}")
        print(f"📁 Files Tested: {len([f for f in file_info.values() if f['exists']])}")
        print(f"🎵 Audio Played: {len(results['stages'])} stages")
        print(f"🔬 Server Analysis: {'Yes' if results['server_analysis'] else 'No'}")
        print(f"🎧 Whisper Validation: {'Yes' if results.get('whisper_validation') else 'No'}")
        
        # Count accumulated syntheses
        accumulated_syntheses = [s for s in results['stages'].keys() if s.startswith('accumulated_15sec_')]
        successful_accumulated = [s for s in accumulated_syntheses if results['stages'][s].get('played', False)]
        print(f"🎤 15-Second Accumulated Syntheses: {len(successful_accumulated)}/{len(accumulated_syntheses)} successful")
        
        # Show durations and quality scores
        for synth_key in successful_accumulated:
            synth_data = results['stages'][synth_key]
            lang = synth_data.get('language', 'unknown')
            duration = synth_data.get('duration', 0)
            quality = synth_data.get('quality_score', 'Unknown')
            whisper_data = synth_data.get('whisper_validation', {})
            
            print(f"   📊 {lang.upper()}: {duration:.2f} seconds | Quality: {quality}")
            
            if whisper_data:
                confidence = whisper_data.get('confidence', 0)
                similarity = whisper_data.get('text_similarity', 0)
                print(f"      🎯 Confidence: {confidence:.1f}% | Similarity: {similarity:.1f}%")
                
                # Sugerir melhorias baseadas no Whisper
                if confidence < 70:
                    print(f"      💡 Suggestion: Increase audio clarity - possible artifacts detected")
                if similarity < 80:
                    print(f"      💡 Suggestion: Check pronunciation accuracy")
        
        print(f"🛠️ Tools Recommendations: {len([t for tools in recommendations.values() for t in tools])}")
        
        # Add analysis to results
        results['tools_analysis'] = analysis
        results['tools_recommendations'] = recommendations
        
        return results
    
    def list_samples(self) -> List[str]:
        """List all available samples"""
        samples = self.detect_youtube_samples()
        return [sample['name'] for sample in samples]
    
    def test_all_samples(self) -> Dict:
        """Test all available samples"""
        samples = self.detect_youtube_samples()
        
        if not samples:
            self.print_error("No samples found")
            return {}
        
        self.print_header(f"Batch QA Testing - {len(samples)} Samples")
        results = {}
        
        for i, sample in enumerate(samples, 1):
            self.print_progress(i, len(samples), f"Testing {sample['name']}")
            result = self.test_sample(sample)
            results[sample['name']] = result
            
            if i < len(samples):
                print(f"\n⏸️  Waiting 2 seconds before next sample...")
                time.sleep(2)
        
        # Batch summary
        self.print_section("Batch Test Summary")
        successful = sum(1 for r in results.values() if r.get('success', False))
        total_size = sum(r.get('total_size_kb', 0) for r in results.values())
        
        print(f"📊 Samples Tested: {len(samples)}")
        print(f"✅ Complete Pipelines: {successful}")
        print(f"❌ Partial Pipelines: {len(samples) - successful}")
        print(f"📁 Total Data Size: {self.format_file_size(total_size * 1024)}")
        print(f"⏱️  Total Test Time: {time.time() - self.start_time:.1f} seconds")
        
        return results
    
    def save_report(self, results: Dict, filename: str = None) -> str:
        """Save QA report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qa_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'server_url': self.server_url,
            'test_duration_seconds': time.time() - self.start_time,
            'results': results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.print_success(f"QA report saved: {filename}")
        return filename

    def validate_cloned_audio_with_whisper(self, cloned_audio_path: str, original_text: str = None) -> Optional[Dict]:
        """Validate cloned audio using Whisper transcription"""
        self.print_section("Whisper Validation")
        try:
            print(f"🎧 Transcribing cloned audio: {os.path.basename(cloned_audio_path)}")
            
            with open(cloned_audio_path, 'rb') as f:
                files = {'audio_file': f}
                response = requests.post(f"{self.server_url}/transcribe", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    transcribed_text = result.get('text', '').strip()
                    confidence = result.get('confidence', 0.0)
                    language = result.get('language', 'unknown')
                    
                    self.print_success("Whisper transcription completed")
                    print(f"   🗣️  Transcribed Text: {Colors.BOLD}\"{transcribed_text}\"{Colors.ENDC}")
                    print(f"   🎯 Confidence: {Colors.BOLD}{confidence:.2f}%{Colors.ENDC}")
                    print(f"   🌍 Language: {Colors.BOLD}{language}{Colors.ENDC}")
                    
                    # Compare with original text if provided
                    if original_text:
                        print(f"   📝 Original Text: {Colors.BOLD}\"{original_text}\"{Colors.ENDC}")
                        similarity = self.calculate_text_similarity(original_text, transcribed_text)
                        print(f"   📊 Text Similarity: {Colors.BOLD}{similarity:.1f}%{Colors.ENDC}")
                    
                    return {
                        'transcribed_text': transcribed_text,
                        'confidence': confidence,
                        'language': language,
                        'original_text': original_text,
                        'similarity': similarity if original_text else None
                    }
                else:
                    self.print_error(f"Whisper transcription failed: {result.get('error', 'Unknown error')}")
                    return None
            else:
                self.print_error(f"Whisper transcription failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            self.print_error(f"Error validating with Whisper: {e}")
            return None
    

    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simple implementation)"""
        # Convert to lowercase and remove punctuation for comparison
        import re
        clean1 = re.sub(r'[^\w\s]', '', text1.lower())
        clean2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        if not words1 and not words2:
            return 100.0
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return (len(intersection) / len(union)) * 100

    def analyze_server_tools_performance(self, results: Dict) -> Dict[str, Any]:
        """Analyze server tools performance and recommend best combinations"""
        self.print_section("Server Tools Analysis")
        
        analysis = {
            'tts_performance': {},
            'whisper_performance': {},
            'voice_cloning_performance': {},
            'recommendations': [],
            'bottlenecks': [],
            'optimizations': []
        }
        
        # Check if results is None or empty
        if not results:
            analysis['bottlenecks'].append("❌ No results available for analysis")
            return analysis
        
        # Analyze TTS performance
        if 'server_analysis' in results and results['server_analysis'] is not None:
            tts_metrics = results['server_analysis'].get('metrics', {})
            analysis['tts_performance'] = {
                'voice_type': tts_metrics.get('voice_type', 'Unknown'),
                'pitch': tts_metrics.get('pitch_mean', 0),
                'energy': tts_metrics.get('energy_mean', 0),
                'speaking_rate': tts_metrics.get('speaking_rate', 0),
                'brightness': tts_metrics.get('brightness', 0),
                'warmth': tts_metrics.get('warmth', 0)
            }
            
            # TTS recommendations
            pitch = tts_metrics.get('pitch_mean', 0)
            energy = tts_metrics.get('energy_mean', 0)
            speaking_rate = tts_metrics.get('speaking_rate', 0)
            
            if pitch > 2000:
                analysis['recommendations'].append("🎵 High pitch detected - Consider using lower pitch models for better naturalness")
            elif pitch < 100:
                analysis['recommendations'].append("🎵 Low pitch detected - Consider using higher pitch models for clarity")
            
            if energy < 0.1:
                analysis['recommendations'].append("⚡ Low energy detected - Consider using energy enhancement tools")
            elif energy > 0.3:
                analysis['recommendations'].append("⚡ High energy detected - Consider using energy normalization")
            
            if speaking_rate < 1.0:
                analysis['recommendations'].append("🗣️ Very slow speaking rate - Consider using speed adjustment tools")
            elif speaking_rate > 5.0:
                analysis['recommendations'].append("🗣️ Very fast speaking rate - Consider using rate normalization")
        
        # Analyze Whisper performance
        if 'whisper_validation' in results:
            whisper_data = results['whisper_validation']
            analysis['whisper_performance'] = {
                'confidence': whisper_data.get('confidence', 0),
                'language': whisper_data.get('language', 'unknown'),
                'text_length': len(whisper_data.get('transcribed_text', ''))
            }
            
            confidence = whisper_data.get('confidence', 0)
            if confidence < 50:
                analysis['bottlenecks'].append("🎧 Low Whisper confidence - Audio quality may need improvement")
                analysis['optimizations'].append("🎧 Consider using audio preprocessing tools for better Whisper performance")
            elif confidence > 90:
                analysis['recommendations'].append("🎧 Excellent Whisper performance - Audio quality is optimal")
        
        # Analyze voice cloning performance
        if 'files' in results:
            files = results['files']
            cloned_file = files.get('cloned', {})
            
            if cloned_file.get('exists'):
                cloned_size = cloned_file.get('size_kb', 0)
                cloned_duration = cloned_file.get('duration_sec', 0)
                
                analysis['voice_cloning_performance'] = {
                    'output_size_kb': cloned_size,
                    'output_duration_sec': cloned_duration,
                    'efficiency': cloned_size / cloned_duration if cloned_duration > 0 else 0
                }
                
                # Voice cloning recommendations
                if cloned_size < 50:
                    analysis['recommendations'].append("🎭 Small cloned audio - Consider longer input text for better quality")
                elif cloned_size > 500:
                    analysis['recommendations'].append("🎭 Large cloned audio - Consider text compression for efficiency")
                
                if cloned_duration < 2.0:
                    analysis['recommendations'].append("⏱️ Short cloned audio - Consider longer voice samples")
                elif cloned_duration > 30.0:
                    analysis['recommendations'].append("⏱️ Long cloned audio - Consider chunking for better processing")
        
        # Overall system analysis
        total_size = results.get('total_size_kb', 0)
        if total_size > 10000:  # 10MB
            analysis['bottlenecks'].append("💾 Large file sizes - Consider compression tools")
            analysis['optimizations'].append("💾 Use audio compression tools to reduce storage requirements")
        
        # GPU/CPU recommendations
        if self.check_gpu_availability():
            analysis['recommendations'].append("🚀 GPU available - Consider GPU-optimized models for better performance")
        else:
            analysis['bottlenecks'].append("🚀 GPU not available - Processing may be slower")
            analysis['optimizations'].append("🚀 Consider enabling GPU support for faster processing")
        
        return analysis
    
    def check_gpu_availability(self) -> bool:
        """Check if GPU is available for processing"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                return health.get('gpu_available', False)
        except:
            pass
        return False
    
    def recommend_tools_combination(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Recommend best tools combination based on analysis"""
        recommendations = {
            'audio_processing': [],
            'tts_optimization': [],
            'voice_cloning': [],
            'quality_improvement': [],
            'performance_boost': []
        }
        
        # Audio processing recommendations
        if any('audio' in bottleneck.lower() for bottleneck in analysis.get('bottlenecks', [])):
            recommendations['audio_processing'].extend([
                "tools/audio_utils/voice_sample_preprocessor.py - Clean and normalize audio",
                "tools/audio_utils/simple_voice_processor.py - Basic audio processing",
                "tools/audio_utils/simple_clone_optimizer.py - Optimize for cloning"
            ])
        
        # TTS optimization
        tts_perf = analysis.get('tts_performance', {})
        if tts_perf.get('pitch', 0) > 2000 or tts_perf.get('pitch', 0) < 100:
            recommendations['tts_optimization'].append("Use pitch normalization tools")
        
        if tts_perf.get('energy', 0) < 0.1 or tts_perf.get('energy', 0) > 0.3:
            recommendations['tts_optimization'].append("Use energy adjustment tools")
        
        # Voice cloning recommendations
        cloning_perf = analysis.get('voice_cloning_performance', {})
        if cloning_perf.get('output_size_kb', 0) > 500:
            recommendations['voice_cloning'].append("Use audio compression tools")
        
        if cloning_perf.get('output_duration_sec', 0) < 2.0:
            recommendations['voice_cloning'].append("Use longer voice samples")
        
        # Quality improvement
        if analysis.get('whisper_performance', {}).get('confidence', 0) < 50:
            recommendations['quality_improvement'].extend([
                "Use noise reduction tools",
                "Use audio enhancement tools",
                "Improve recording quality"
            ])
        
        # Performance boost
        if not self.check_gpu_availability():
            recommendations['performance_boost'].append("Enable GPU support for faster processing")
        
        if any('large' in bottleneck.lower() for bottleneck in analysis.get('bottlenecks', [])):
            recommendations['performance_boost'].append("Use batch processing tools")
        
        return recommendations
    
    def print_tools_recommendations(self, recommendations: Dict[str, List[str]]):
        """Print tools recommendations in a structured way"""
        self.print_section("Recommended Tools Combination")
        
        for category, tools in recommendations.items():
            if tools:
                print(f"\n🔧 {category.replace('_', ' ').title()}:")
                for tool in tools:
                    print(f"   • {tool}")
        
        if not any(tools for tools in recommendations.values()):
            print("   ✅ No specific tools needed - Current setup is optimal!")
    
    def generate_tools_report(self, analysis: Dict[str, Any], recommendations: Dict[str, List[str]]) -> str:
        """Generate a comprehensive tools report"""
        report = []
        report.append("# 🛠️ Server Tools Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Performance Analysis
        report.append("## 📊 Performance Analysis")
        
        if analysis.get('tts_performance'):
            tts = analysis['tts_performance']
            report.append("### TTS Performance:")
            report.append(f"- Voice Type: {tts.get('voice_type', 'Unknown')}")
            report.append(f"- Pitch: {tts.get('pitch', 0):.0f} Hz")
            report.append(f"- Energy: {tts.get('energy', 0):.3f}")
            report.append(f"- Speaking Rate: {tts.get('speaking_rate', 0):.1f} words/min")
            report.append("")
        
        if analysis.get('whisper_performance'):
            whisper = analysis['whisper_performance']
            report.append("### Whisper Performance:")
            report.append(f"- Confidence: {whisper.get('confidence', 0):.1f}%")
            report.append(f"- Language: {whisper.get('language', 'unknown')}")
            report.append(f"- Text Length: {whisper.get('text_length', 0)} chars")
            report.append("")
        
        if analysis.get('voice_cloning_performance'):
            cloning = analysis['voice_cloning_performance']
            report.append("### Voice Cloning Performance:")
            report.append(f"- Output Size: {cloning.get('output_size_kb', 0):.1f} KB")
            report.append(f"- Duration: {cloning.get('output_duration_sec', 0):.2f} seconds")
            report.append(f"- Efficiency: {cloning.get('efficiency', 0):.1f} KB/sec")
            report.append("")
        
        # Issues and Recommendations
        if analysis.get('bottlenecks'):
            report.append("## 🚨 Identified Bottlenecks")
            for bottleneck in analysis['bottlenecks']:
                report.append(f"- {bottleneck}")
            report.append("")
        
        if analysis.get('recommendations'):
            report.append("## 💡 Recommendations")
            for rec in analysis['recommendations']:
                report.append(f"- {rec}")
            report.append("")
        
        if analysis.get('optimizations'):
            report.append("## ⚡ Optimization Opportunities")
            for opt in analysis['optimizations']:
                report.append(f"- {opt}")
            report.append("")
        
        # Tools Recommendations
        report.append("## 🛠️ Recommended Tools Combination")
        for category, tools in recommendations.items():
            if tools:
                report.append(f"### {category.replace('_', ' ').title()}")
                for tool in tools:
                    report.append(f"- {tool}")
                report.append("")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Enhanced QA Testing Tool for Voice Cloning")
    parser.add_argument("--sample", help="Specific sample name to test")
    parser.add_argument("--list", action="store_true", help="List available samples")
    parser.add_argument("--all", action="store_true", help="Test all samples")

    parser.add_argument("--server", default="http://localhost:8000", help="TTS server URL")
    parser.add_argument("--player", default="auto", choices=["auto", "playsound", "vlc", "mpv", "ffplay"], help="Audio player")
    parser.add_argument("--no-play", action="store_true", help="Disable auto-play")
    parser.add_argument("--pause", type=float, default=3.0, help="Pause between samples")
    parser.add_argument("--volume", type=int, default=100, help="Volume level (0-100)")
    parser.add_argument("--report", help="Save report to file")
    parser.add_argument("--tools-report", action="store_true", help="Generate detailed tools analysis report")
    
    args = parser.parse_args()
    
    # Initialize QA tool
    qa = VoiceCloningQA(
        server_url=args.server,
        player=args.player,
        auto_play=not args.no_play,
        pause_between=args.pause,
        volume=args.volume
    )
    
    # Check server health
    if not qa.check_server_health():
        qa.print_error("Cannot proceed without server connection")
        return 1
    
    # List samples
    if args.list:
        samples = qa.list_samples()
        if samples:
            qa.print_section("Available Samples")
        for i, sample in enumerate(samples, 1):
            print(f"   {i}. {sample}")
        else:
            qa.print_error("No samples found")
        return 0
    
    # Test specific sample
    if args.sample:
        samples = qa.detect_youtube_samples()
        sample = next((s for s in samples if s['name'] == args.sample), None)
        
        if sample:
            result = qa.test_sample(sample)
            results = {args.sample: result}
        else:
            qa.print_error(f"Sample '{args.sample}' not found")
            return 1
    
    # Test all samples
    elif args.all:
        results = qa.test_all_samples()
        
    else:
        qa.print_error("Please specify --sample, --list, or --all")
        return 1
    
    # Save report
    if args.report or results:
        filename = args.report or "qa_report.json"
        qa.save_report(results, filename)
    
    # Generate tools report if requested
    if args.tools_report and results:
        for sample_name, result in results.items():
            if 'tools_analysis' in result and 'tools_recommendations' in result:
                analysis = result['tools_analysis']
                recommendations = result['tools_recommendations']
                tools_report = qa.generate_tools_report(analysis, recommendations)
                
                report_filename = f"tools_analysis_{sample_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                try:
                    with open(report_filename, 'w') as f:
                        f.write(tools_report)
                    print(f"✅ Tools analysis report saved: {report_filename}")
                except Exception as e:
                    print(f"❌ Could not save tools report: {e}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 