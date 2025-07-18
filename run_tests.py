#!/usr/bin/env python3
"""
Comprehensive test runner for Coqui TTS Server
Runs tests in logical order with proper error handling
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.test_results = []
        self.server_running = False
        
    def check_server(self):
        """Check if server is running"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running")
                self.server_running = True
                return True
        except:
            pass
        
        print("❌ Server is not running")
        print("   Please start the server first with: ./scripts/script_start.sh")
        return False
    
    def run_test(self, test_path, description):
        """Run a single test file"""
        print(f"\n🧪 {description}")
        print("=" * 50)
        
        try:
            # Change to test directory
            test_dir = test_path.parent
            test_file = test_path.name
            
            # Run the test
            result = subprocess.run(
                [sys.executable, test_file],
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Test passed")
                self.test_results.append((description, "PASS"))
                return True
            else:
                print("❌ Test failed")
                print(f"Error: {result.stderr}")
                self.test_results.append((description, "FAIL"))
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Test timed out")
            self.test_results.append((description, "TIMEOUT"))
            return False
        except Exception as e:
            print(f"❌ Test error: {e}")
            self.test_results.append((description, "ERROR"))
            return False
    
    def run_test_suite(self, suite_name, tests):
        """Run a suite of tests"""
        print(f"\n📋 Running {suite_name} Tests")
        print("=" * 60)
        
        passed = 0
        total = len(tests)
        
        for test_path, description in tests:
            if self.run_test(test_path, description):
                passed += 1
        
        print(f"\n📊 {suite_name} Results: {passed}/{total} passed")
        return passed == total
    
    def run_all_tests(self):
        """Run all tests in recommended order"""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        # Check if server is running
        if not self.check_server():
            return False
        
        # Define test suites in order
        test_suites = [
            ("Integration Tests", [
                (self.base_dir / "tests" / "integration" / "test_server_complete.py", "Server Complete Integration"),
                (self.base_dir / "tests" / "integration" / "test_client.py", "Client Integration"),
            ]),
            
            ("Core TTS Tests", [
                (self.base_dir / "tests" / "tts" / "test_simples_tts.py", "Simple TTS"),
                (self.base_dir / "tests" / "tts" / "test_tts_integration.py", "TTS Integration"),
            ]),
            
            ("Whisper STT Tests", [
                (self.base_dir / "tests" / "whisper" / "test_whisper_server_integration.py", "Whisper Server Integration"),
                (self.base_dir / "tests" / "whisper" / "test_cpu_compatibility.py", "CPU Compatibility"),
                # OBSOLETE TESTS (commented out):
                # (self.base_dir / "tests" / "whisper" / "test_whisper_integration.py", "Whisper Integration"),
                # (self.base_dir / "tests" / "whisper" / "test_whisper_params.py", "Whisper Parameters"),
                # (self.base_dir / "tests" / "whisper" / "test_whisper_attributes.py", "Whisper Attributes"),
                # (self.base_dir / "tests" / "whisper" / "test_gpu_compatibility.py", "GPU Compatibility"),
            ]),
            
            ("Voice Cloning Tests", [
                (self.base_dir / "tests" / "voice_cloning" / "test_yourtts_direct.py", "YourTTS Direct"),
                (self.base_dir / "tests" / "voice_cloning" / "test_yourtts_speakers.py", "YourTTS Speakers"),
                (self.base_dir / "tests" / "voice_cloning" / "test_voice_analysis.py", "Voice Analysis"),
            ]),
            
            ("Portuguese Language Tests", [
                        (self.base_dir / "tests" / "tts" / "test_yourtts_pt_br.py", "YourTTS Portuguese"),
        (self.base_dir / "tests" / "tts" / "test_modelos_pt_br.py", "Portuguese Models"),
        (self.base_dir / "tests" / "tts" / "test_vozes_genero.py", "Gender Voices"),
            ]),
        ]
        
        # Run each test suite
        all_passed = True
        for suite_name, tests in test_suites:
            suite_passed = self.run_test_suite(suite_name, tests)
            if not suite_passed:
                all_passed = False
        
        # Print final results
        self.print_final_results()
        
        return all_passed
    
    def print_final_results(self):
        """Print final test results summary"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for _, status in self.test_results if status == "PASS")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for description, status in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"  {status_icon} {description}: {status}")

def main():
    """Main function"""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        # Run specific test category
        category = sys.argv[1].lower()
        if category == "integration":
            runner.run_test_suite("Integration", [
                (Path("tests/integration/test_server_complete.py"), "Server Complete Integration"),
                (Path("tests/integration/test_client.py"), "Client Integration"),
            ])
        elif category == "tts":
            runner.run_test_suite("TTS", [
                (Path("tests/tts/test_simples_tts.py"), "Simple TTS"),
                (Path("tests/tts/test_tts_integration.py"), "TTS Integration"),
            ])
        elif category == "whisper":
            runner.run_test_suite("Whisper", [
                (Path("tests/whisper/test_whisper_integration.py"), "Whisper Integration"),
                (Path("tests/whisper/test_whisper_params.py"), "Whisper Parameters"),
            ])
        elif category == "voice_cloning":
            runner.run_test_suite("Voice Cloning", [
                (Path("tests/voice_cloning/test_yourtts_direct.py"), "YourTTS Direct"),
                (Path("tests/voice_cloning/test_voice_analysis.py"), "Voice Analysis"),
            ])
        else:
            print(f"Unknown category: {category}")
            print("Available categories: integration, tts, whisper, voice_cloning")
    else:
        # Run all tests
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 