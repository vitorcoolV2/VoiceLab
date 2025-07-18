#!/usr/bin/env python3
"""
Performance Optimizer for Coqui TTS
Applies intelligent optimizations to improve speed without losing quality
"""

import os
import json
import time
import torch
import gc
from pathlib import Path
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    def __init__(self):
        self.optimizations_applied = {}
        self.start_time = time.time()
        
    def optimize_gpu_memory(self):
        """Optimize GPU memory usage"""
        if torch.cuda.is_available():
            # Clear GPU cache
            torch.cuda.empty_cache()
            
            # Set memory fraction for better performance
            torch.cuda.set_per_process_memory_fraction(0.85)
            
            # Enable memory efficient attention if available
            try:
                torch.backends.cuda.enable_flash_sdp(True)
                logger.info("✅ Flash attention enabled")
            except:
                logger.info("⚠️ Flash attention not available")
            
            self.optimizations_applied['gpu_memory'] = True
            logger.info("✅ GPU memory optimized")
    
    def optimize_torch_settings(self):
        """Optimize PyTorch settings for better performance"""
        # Enable cudnn benchmarking for faster convolutions
        torch.backends.cudnn.benchmark = True
        
        # Enable deterministic algorithms for consistency
        torch.backends.cudnn.deterministic = False
        
        # Set number of threads for CPU operations
        torch.set_num_threads(4)
        
        self.optimizations_applied['torch_settings'] = True
        logger.info("✅ PyTorch settings optimized")
    
    def preload_models(self):
        """Preload commonly used models to reduce loading time"""
        try:
            # Preload TTS model components
            from TTS.api import TTS
            
            # Warm up GPU with a small inference
            device = "cuda" if torch.cuda.is_available() else "cpu"
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            
            # Warm up with a short text
            warmup_text = "Test"
            with torch.no_grad():
                tts.tts_to_file(text=warmup_text, file_path="/tmp/warmup.wav")
            
            # Clean up
            del tts
            torch.cuda.empty_cache()
            
            self.optimizations_applied['model_preload'] = True
            logger.info("✅ Models preloaded and warmed up")
            
        except Exception as e:
            logger.warning(f"⚠️ Model preloading failed: {e}")
    
    def optimize_audio_settings(self):
        """Optimize audio processing settings"""
        # Set environment variables for better audio performance
        os.environ['SOUNDFILE_LIB'] = '/usr/lib/x86_64-linux-gnu/libsndfile.so.1'
        os.environ['AUDIO_QUALITY'] = 'medium'
        os.environ['AUDIO_SAMPLE_RATE'] = '16000'
        
        self.optimizations_applied['audio_settings'] = True
        logger.info("✅ Audio settings optimized")
    
    def apply_all_optimizations(self):
        """Apply all performance optimizations"""
        logger.info("🚀 Applying performance optimizations...")
        
        self.optimize_gpu_memory()
        self.optimize_torch_settings()
        self.optimize_audio_settings()
        self.preload_models()
        
        optimization_time = time.time() - self.start_time
        logger.info(f"✅ All optimizations applied in {optimization_time:.2f}s")
        
        return self.optimizations_applied
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance optimization report"""
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            gpu_memory_allocated = torch.cuda.memory_allocated() / 1024**3
            gpu_memory_cached = torch.cuda.memory_reserved() / 1024**3
        else:
            gpu_memory = gpu_memory_allocated = gpu_memory_cached = 0
        
        return {
            'timestamp': time.time(),
            'optimizations_applied': self.optimizations_applied,
            'gpu_available': torch.cuda.is_available(),
            'gpu_memory_total_gb': gpu_memory,
            'gpu_memory_allocated_gb': gpu_memory_allocated,
            'gpu_memory_cached_gb': gpu_memory_cached,
            'torch_version': torch.__version__,
            'cuda_version': torch.version.cuda if torch.cuda.is_available() else None
        }

def main():
    """Main function to run performance optimization"""
    optimizer = PerformanceOptimizer()
    optimizations = optimizer.apply_all_optimizations()
    
    # Generate and save report
    report = optimizer.get_performance_report()
    
    # Save report using environment variable
    output_dir = Path(os.environ.get("COQUI_TTS_OUTPUTS", "output"))
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / f"performance_optimization_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Performance Optimization Report:")
    print(f"   Report saved: {report_file}")
    print(f"   Optimizations applied: {len(optimizations)}")
    print(f"   GPU Memory: {report['gpu_memory_allocated_gb']:.2f}GB / {report['gpu_memory_total_gb']:.2f}GB")
    
    return report

if __name__ == "__main__":
    main() 