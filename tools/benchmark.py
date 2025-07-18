#!/usr/bin/env python3
"""
Simple Benchmark tool for Coqui TTS Server
Tests performance and latency of TTS operations.
"""

import os
import sys
import time
import requests
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TTSBenchmark:
    """Simple benchmark tool for TTS server performance."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.results = []
        
        # Test texts
        self.test_texts = {
            'en': [
                "Hello, this is a test of the text-to-speech system.",
                "The quick brown fox jumps over the lazy dog.",
                "Artificial intelligence is transforming the world."
            ],
            'pt': [
                "Olá, este é um teste do sistema de síntese de voz.",
                "O rato roeu a roupa do rei de Roma.",
                "A inteligência artificial está transformando o mundo."
            ]
        }
    
    def test_tts_synthesis(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Test TTS synthesis performance."""
        start_time = time.time()
        
        try:
            payload = {
                'text': text
            }
            # Only add language if it's different from default
            if language != 'en':
                payload['language'] = language
            
            response = requests.post(
                f"{self.server_url}/synthesize",
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'duration': duration,
                    'text_length': len(text),
                    'audio_size': len(result.get('audio', '')),
                    'model_used': result.get('model', 'unknown'),
                    'language': language,
                    'text': text[:50] + "..." if len(text) > 50 else text,
                    'audio_file': result.get('audio_file', '')
                }
            else:
                return {
                    'success': False,
                    'duration': duration,
                    'error': f"HTTP {response.status_code}",
                    'text': text[:50] + "..." if len(text) > 50 else text
                }
                
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e),
                'text': text[:50] + "..." if len(text) > 50 else text
            }
    
    def run_benchmark(self, iterations: int = 10, language: str = "en", play_audio: bool = False) -> Dict[str, Any]:
        """Run TTS benchmark."""
        print(f"🎤 Running TTS Benchmark ({iterations} iterations, language: {language})")
        print("=" * 50)
        
        texts = self.test_texts.get(language, self.test_texts['en'])
        results = []
        
        for i in range(iterations):
            text = texts[i % len(texts)]
            result = self.test_tts_synthesis(text, language)
            results.append(result)
            
            if result['success']:
                print(f"   ✅ {result['duration']:.2f}s - {result['text']}")
                
                # Play audio if requested
                if play_audio and 'audio_file' in result and result['audio_file']:
                    try:
                        from tools.audio_utils.audio_player import AudioPlayer
                        import time
                        
                        # Get the local file path
                        audio_file = f"output/{result['audio_file']}"
                        if os.path.exists(audio_file):
                            print(f"   🎵 Playing: {result['audio_file']}")
                            player = AudioPlayer()
                            player.play_file(audio_file, f"Benchmark {i+1}")
                            time.sleep(1)  # Wait between audio files
                        else:
                            print(f"   ⚠️  Audio file not found: {audio_file}")
                    except Exception as e:
                        print(f"   ⚠️  Could not play audio: {e}")
            else:
                print(f"   ❌ {result['duration']:.2f}s - {result['error']}")
        
        return self.analyze_results(results, f"TTS {language.upper()}")
    
    def analyze_results(self, results: List[Dict[str, Any]], test_name: str) -> Dict[str, Any]:
        """Analyze benchmark results."""
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if not successful:
            return {
                'test_name': test_name,
                'total_tests': len(results),
                'successful': 0,
                'failed': len(failed),
                'success_rate': 0.0,
                'error': 'All tests failed'
            }
        
        durations = [r['duration'] for r in successful]
        
        analysis = {
            'test_name': test_name,
            'total_tests': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(results) * 100,
            'duration_stats': {
                'min': min(durations),
                'max': max(durations),
                'mean': statistics.mean(durations),
                'median': statistics.median(durations),
                'std': statistics.stdev(durations) if len(durations) > 1 else 0
            }
        }
        
        # Add throughput metrics
        text_lengths = [r['text_length'] for r in successful]
        total_chars = sum(text_lengths)
        total_time = sum(durations)
        analysis['throughput'] = {
            'chars_per_second': total_chars / total_time if total_time > 0 else 0,
            'total_chars': total_chars,
            'avg_text_length': statistics.mean(text_lengths)
        }
        
        return analysis
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print benchmark summary."""
        print("\n📊 Benchmark Summary")
        print("=" * 50)
        
        for result in results:
            if 'error' in result:
                print(f"❌ {result['test_name']}: {result['error']}")
                continue
            
            print(f"\n🎯 {result['test_name']}")
            print(f"   Tests: {result['successful']}/{result['total_tests']} successful ({result['success_rate']:.1f}%)")
            
            if 'duration_stats' in result:
                stats = result['duration_stats']
                print(f"   Duration: {stats['mean']:.2f}s avg ({stats['min']:.2f}s - {stats['max']:.2f}s)")
                print(f"   Std Dev: {stats['std']:.2f}s")
            
            if 'throughput' in result:
                throughput = result['throughput']
                print(f"   Throughput: {throughput['chars_per_second']:.1f} chars/sec")
                print(f"   Total Chars: {throughput['total_chars']}")

def main():
    parser = argparse.ArgumentParser(description="Simple Benchmark tool for Coqui TTS Server")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    parser.add_argument("--iterations", type=int, default=10, help="Test iterations")
    parser.add_argument("--language", choices=['en', 'pt'], default='en', help="Language for tests")
    parser.add_argument("--play", action="store_true", help="Play audio for each iteration")
    
    args = parser.parse_args()
    
    benchmark = TTSBenchmark(args.server)
    result = benchmark.run_benchmark(args.iterations, args.language, args.play)
    benchmark.print_summary([result])

if __name__ == "__main__":
    main() 