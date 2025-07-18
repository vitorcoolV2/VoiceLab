#!/usr/bin/env python3
"""
Coqui TTS Server
A FastAPI-based server for text-to-speech synthesis using Coqui TTS.
"""

import os
import sys
import time
import hashlib
import librosa
import numpy as np
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import yaml
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, File, UploadFile, Form, Depends, Request, Body, Path as FastAPIPath
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

import shutil
import json

SPEAKERS_DIR = Path(__file__).parent / "speakers"
SPEAKERS_DIR.mkdir(exist_ok=True)
SPEAKERS_JSON = SPEAKERS_DIR / "speakers.json"

def load_speakers():
    if SPEAKERS_JSON.exists():
        with open(SPEAKERS_JSON, "r") as f:
            return json.load(f)
    return {}

def save_speakers(speakers):
    with open(SPEAKERS_JSON, "w") as f:
        json.dump(speakers, f, indent=2)

# Definir COQUI_TTS_HOME a partir do settings.yaml
with open(os.path.join(os.path.dirname(__file__), '../config/settings.yaml'), 'r') as f:
    config_yaml = yaml.safe_load(f)
    coqui_tts_home = config_yaml.get('models', {}).get('path')
    if coqui_tts_home:
        os.environ['COQUI_TTS_HOME'] = coqui_tts_home

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Coqui TTS Server")
    parser.add_argument("--cpu-only", action="store_true", help="Force CPU-only mode to avoid CUDNN issues")
    parser.add_argument("--whisper-gpu", action="store_true", help="Allow Whisper to use GPU even in CPU-only mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    return parser.parse_args()

# Parse arguments early
args = parse_args()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from TTS.api import TTS
except ImportError:
    logger.error("TTS not installed. Please run: pip install TTS")
    sys.exit(1)

try:
    import whisper
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("Whisper not installed. Speech recognition features will be disabled.")
    WHISPER_AVAILABLE = False

# Load configuration
def load_config():
    """Load configuration from YAML file."""
    config_path = project_root / "config" / "settings.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override config paths with environment variables if available
    if 'COQUI_TTS_OUTPUTS' in os.environ:
        config['output']['path'] = os.environ['COQUI_TTS_OUTPUTS']
        logger.info(f"Using COQUI_TTS_OUTPUTS: {config['output']['path']}")
    
    if 'COQUI_TTS_DOWNLOADS' in os.environ:
        config['downloads']['path'] = os.environ['COQUI_TTS_DOWNLOADS']
        logger.info(f"Using COQUI_TTS_DOWNLOADS: {config['downloads']['path']}")
    
    if 'COQUI_TTS_HOME' in os.environ:
        config['models']['path'] = os.environ['COQUI_TTS_HOME']
        logger.info(f"Using COQUI_TTS_HOME: {config['models']['path']}")
    
    if 'TTS_CACHE_DIR' in os.environ:
        config['models']['cache_dir'] = os.environ['TTS_CACHE_DIR']
        logger.info(f"Using TTS_CACHE_DIR: {config['models']['cache_dir']}")
    
    # Override config with command line arguments
    if args.cpu_only:
        config['performance']['use_gpu'] = False
        config['whisper']['force_cpu'] = True
        logger.info("Forcing CPU-only mode due to --cpu-only argument")
    
    if args.debug:
        config['server']['debug'] = True
        config['logging']['level'] = 'DEBUG'
        logger.info("Debug mode enabled")
    
    return config

config = load_config()

# Setup logging
logger.remove()
if config['logging'].get('logging_to_file', True):
    os.makedirs("logs", exist_ok=True)
logger.add(
        "logs/tts_server.log",
    level=config['logging']['level'],
        rotation="10 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}"
)
logger.add(sys.stderr, level=config['logging']['level'])

# Initialize FastAPI app
app = FastAPI(
    title="Coqui TTS Server",
    description="A FastAPI server for text-to-speech synthesis using Coqui TTS",
    version="1.0.0"
)

# Add a utility to log incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"[REQUEST] {request.method} {request.url.path} - Query: {dict(request.query_params)}")
    if config['server'].get('debug', False):
        try:
            body = await request.body()
            logger.debug(f"[REQUEST BODY] {body.decode(errors='replace')}")
        except Exception as e:
            logger.debug(f"[REQUEST BODY] <unavailable> ({e})")
    response = await call_next(request)
    return response

# Global TTS instance
tts_instance = None
# Cache de instâncias TTS
tts_model_cache = {}

# Global Whisper instance
whisper_instance = None
whisper_model_name = None

# Global model cache for fast responses
model_cache = {
    "models": [],
    "downloaded_models": [],
    "total_models": 0,
    "last_updated": None
}

def update_model_cache():
    """Update the global model cache."""
    global model_cache
    try:
        from TTS.utils.manage import ModelManager
        model_manager = ModelManager()
        models = model_manager.list_models()
        
        model_cache = {
            "models": models,
            "downloaded_models": [model for model in models if "[already downloaded]" in model],
            "total_models": len(models),
            "last_updated": datetime.now().isoformat()
        }
        logger.info(f"Model cache updated: {len(models)} models available")
        return True
    except Exception as e:
        logger.error(f"Error updating model cache: {e}")
        return False

def initialize_whisper():
    """Initialize the Whisper instance."""
    global whisper_instance, whisper_model_name
    if not WHISPER_AVAILABLE:
        logger.warning("Whisper not available. Speech recognition features disabled.")
        return False
    try:
        logger.info("Initializing Whisper...")
        # Check for GPU (respect force_cpu setting and command line args)
        force_cpu = config['whisper'].get('force_cpu', False) or (args.cpu_only and not args.whisper_gpu)
        # Test GPU compatibility first
        gpu_available = False
        if not force_cpu and torch.cuda.is_available() and config['performance']['use_gpu']:
            try:
                # Test GPU with a simple operation
                test_tensor = torch.zeros(1, device="cuda")
                del test_tensor
                # Test CUDNN availability
                try:
                    import torch.backends.cudnn as cudnn
                    if cudnn.is_available():
                        cudnn.benchmark = True
                        logger.info("CUDNN is available and enabled")
                    else:
                        logger.warning("CUDNN not available, falling back to CPU")
                        gpu_available = False
                        device = "cpu"
                        compute_type = "int8"
                        return False
                except Exception as cudnn_error:
                    logger.warning(f"CUDNN test failed: {cudnn_error}, falling back to CPU")
                    gpu_available = False
                    device = "cpu"
                    compute_type = "int8"
                    return False
                
                gpu_available = True
                logger.info("GPU compatibility test passed")
            except Exception as e:
                logger.warning(f"GPU compatibility test failed: {e}")
                gpu_available = False
        device = "cuda" if gpu_available else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        logger.info(f"Using device: {device} with compute_type: {compute_type}")
        model_name = config['whisper']['default_model']
        try:
            whisper_instance = WhisperModel(
                model_size_or_path=model_name,
                device=device,
                compute_type=compute_type
            )
            whisper_model_name = model_name
            logger.info(f"Whisper initialized with model: {model_name}")
            return True
        except Exception as e:
            # Se erro for relacionado a CUDA/CUDNN, tenta fallback para CPU
            error_str = str(e).lower()
            if (not force_cpu) and any(keyword in error_str for keyword in ["cuda", "cudnn", "libcudnn", "cudnncreatetensordescriptor"]):
                logger.warning(f"Erro de CUDA/CUDNN detectado ao inicializar Whisper: {e}\nTentando inicializar em modo CPU...")
                try:
                    # Força modo CPU e compute_type int8
                    whisper_instance = WhisperModel(
                        model_size_or_path=model_name,
                        device="cpu",
                        compute_type="int8"
                    )
                    whisper_model_name = model_name
                    logger.info(f"Whisper inicializado com sucesso em modo CPU após erro de GPU.")
                    return True
                except Exception as e2:
                    logger.error(f"Falha ao inicializar Whisper em modo CPU após erro de GPU: {e2}")
                    return False
            else:
                logger.error(f"Failed to initialize Whisper: {e}")
                return False
    except Exception as e:
        logger.error(f"Failed to initialize Whisper (outer): {e}")
        return False

class SynthesisRequest(BaseModel):
    """Request model for text-to-speech synthesis."""
    text: str = Field(..., min_length=1, max_length=config['api']['max_text_length'])
    model_name: Optional[str] = None
    speaker: Optional[str] = None
    language: Optional[str] = None  # Let the code handle default language
    voice_style: str = config['tts']['default_voice_style']
    output_format: str = config['tts']['default_output_format']
    speed: float = Field(config['tts']['default_speed'], ge=0.5, le=2.0)
    pitch: float = Field(config['tts']['default_pitch'], ge=0.5, le=2.0)
    volume: float = Field(config['tts']['default_volume'], ge=0.1, le=3.0)
    speaker_wav: Optional[str] = None # Added for voice cloning

class SynthesisResponse(BaseModel):
    """Response model for text-to-speech synthesis."""
    success: bool
    audio_file: Optional[str] = None
    error: Optional[str] = None
    timestamp: str
    processing_time: Optional[float] = None

class TranscriptionRequest(BaseModel):
    """Request model for speech-to-text transcription."""
    model_name: Optional[str] = None
    language: Optional[str] = None
    word_timestamps: bool = False
    temperature: float = 0.0
    compression_ratio_threshold: float = 2.4
    logprob_threshold: float = -1.0
    no_speech_threshold: float = 0.6

class TranscriptionResponse(BaseModel):
    """Response model for speech-to-text transcription."""
    success: bool
    text: Optional[str] = None
    language: Optional[str] = None
    segments: Optional[List[Dict]] = None
    word_timestamps: Optional[List[Dict]] = None
    error: Optional[str] = None
    timestamp: str
    processing_time: Optional[float] = None

class WhisperModelInfo(BaseModel):
    """Model information for Whisper."""
    name: str
    size: str
    languages: List[str]
    multilingual: bool

def initialize_tts():
    """Initialize the TTS instance."""
    global tts_instance
    try:
        logger.info("Initializing TTS...")
        # Check for GPU (respect CPU-only mode)
        force_cpu = args.cpu_only
        device = "cuda" if not force_cpu and torch.cuda.is_available() and config['performance']['use_gpu'] else "cpu"
        logger.info(f"Using device: {device}")
        model_name = config['tts']['default_model']
        try:
            tts_instance = TTS(model_name=model_name).to(device)
            logger.info(f"TTS initialized with model: {model_name}")
            return True
        except Exception as e:
            # Se erro for relacionado a CUDA/CUDNN, tenta fallback para CPU
            if (not force_cpu) and ("cuda" in str(e).lower() or "cudnn" in str(e).lower()):
                logger.warning(f"Erro de CUDA/CUDNN detectado ao inicializar TTS: {e}\nTentando inicializar em modo CPU...")
                try:
                    tts_instance = TTS(model_name=model_name).to("cpu")
                    logger.info(f"TTS inicializado com sucesso em modo CPU após erro de GPU.")
                    return True
                except Exception as e2:
                    logger.error(f"Falha ao inicializar TTS em modo CPU após erro de GPU: {e2}")
                    return False
            else:
                logger.error(f"Failed to initialize TTS: {e}")
                return False
    except Exception as e:
        logger.error(f"Failed to initialize TTS (outer): {e}")
        return False

# Carregar speakers no arranque
global_speakers = load_speakers()

@app.on_event("startup")
async def startup_event():
    """Initialize TTS and Whisper on startup."""
    logger.info("🚀 Starting Coqui TTS Server...")
    
    # Initialize TTS
    if not initialize_tts():
        logger.error("❌ Failed to initialize TTS")
        return
    
    # Initialize Whisper
    if not initialize_whisper():
        logger.warning("⚠️  Whisper initialization failed, speech recognition disabled")
    
    # Pre-load model cache for fast responses
    logger.info("📋 Pre-loading model cache...")
    if update_model_cache():
        logger.info(f"✅ Model cache loaded: {model_cache['total_models']} models available")
    else:
        logger.warning("⚠️ Failed to pre-load model cache")  
    logger.info("✅ Server startup completed")
    global global_speakers
    global_speakers = load_speakers()
    logger.info(f"Speakers carregados: {list(global_speakers.keys())}")
    # Validação dos ficheiros sample_path e reposição automática se faltar
    fallback_sample = Path(__file__).parent.parent / "sample.wav"
    speakers_changed = False
    for name, speaker in global_speakers.items():
        sample_path = speaker.get("sample_path")
        if not sample_path or not Path(sample_path).exists():
            logger.warning(f"[SPEAKER] Sample file em falta para '{name}': {sample_path}")
            if fallback_sample.exists():
                speaker_dir = Path(__file__).parent / "speakers" / name
                speaker_dir.mkdir(parents=True, exist_ok=True)
                new_sample = speaker_dir / "sample.wav"
                try:
                    import shutil
                    shutil.copy2(fallback_sample, new_sample)
                    speaker["sample_path"] = str(new_sample.resolve())
                    logger.info(f"[SPEAKER] Fallback sample.wav copiado para {new_sample}")
                    speakers_changed = True
                except Exception as e:
                    logger.error(f"[SPEAKER] Falha ao copiar fallback para '{name}': {e}")
            else:
                logger.warning(f"[SPEAKER] Fallback sample.wav não encontrado. Speaker '{name}' ficará inválido.")
        else:
            logger.info(f"[SPEAKER] '{name}' pronto: {sample_path}")
    if speakers_changed:
        save_speakers(global_speakers)
        logger.info("[SPEAKER] speakers.json atualizado com paths corrigidos.")

@app.get("/")
async def root():
    """Status/info do servidor."""
    return {
        "message": "Coqui TTS Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tts_initialized": tts_instance is not None,
        "whisper_initialized": whisper_instance is not None,
        "whisper_available": WHISPER_AVAILABLE,
        "gpu_available": torch.cuda.is_available(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models/refresh")
async def refresh_models():
    try:
        if update_model_cache():
            return {
                "success": True,
                "message": f"Model cache refreshed: {model_cache['total_models']} models available",
                "total_models": model_cache["total_models"]
            }
        else:
            logger.error("Failed to refresh model cache")
            raise HTTPException(status_code=500, detail="Failed to refresh model cache")
    except Exception as e:
        logger.error(f"Error refreshing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    global model_cache
    try:
        if (model_cache["models"] and model_cache["last_updated"] and (datetime.now() - datetime.fromisoformat(model_cache["last_updated"])).seconds < 300):
            return {
                "models": model_cache["models"],
                "current_model": tts_instance.model_name if tts_instance else None,
                "total_models": model_cache["total_models"],
                "downloaded_models": model_cache["downloaded_models"],
                "cache_status": "cached",
                "cache_age_seconds": (datetime.now() - datetime.fromisoformat(model_cache["last_updated"])).seconds
            }
        if update_model_cache():
            return {
                "models": model_cache["models"],
                "current_model": tts_instance.model_name if tts_instance else None,
                "total_models": model_cache["total_models"],
                "downloaded_models": model_cache["downloaded_models"],
                "cache_status": "updated",
                "cache_age_seconds": 0
            }
        else:
            from TTS.utils.manage import ModelManager
            model_manager = ModelManager()
            models = model_manager.list_models()
            return {
                "models": models,
                "current_model": tts_instance.model_name if tts_instance else None,
                "total_models": len(models),
                "downloaded_models": [model for model in models if "[already downloaded]" in model],
                "cache_status": "fallback",
                "cache_age_seconds": None
            }
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/speakers")
async def list_speakers():
    try:
        speakers = load_speakers()
        return {
            "speakers": speakers,
            "total": len(speakers),
            "success": True
        }
    except Exception as e:
        logger.error(f"Error listing speakers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/switch_model")
async def switch_model(model_name: str = Query(..., description="Name of the model to switch to")):
    global tts_instance
    try:
        logger.info(f"Switching to model: {model_name}")
        from TTS.utils.manage import ModelManager
        model_manager = ModelManager()
        available_models = model_manager.list_models()
        clean_model_name = model_name.split(" [")[0]
        if clean_model_name not in [m.split(" [")[0] for m in available_models]:
            raise HTTPException(status_code=400, detail=f"Model {clean_model_name} not found in available models")
        device = "cuda" if torch.cuda.is_available() and config['performance']['use_gpu'] else "cpu"
        new_tts = TTS(model_name=clean_model_name).to(device)
        old_model = tts_instance.model_name if tts_instance else None
        tts_instance = new_tts
        logger.info(f"Successfully switched from {old_model} to {clean_model_name}")
        return {
            "success": True,
            "previous_model": old_model,
            "current_model": clean_model_name,
            "message": f"Switched to {clean_model_name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download_model")
async def download_model(model_name: str):
    import os
    from TTS.utils.manage import ModelManager
    model_base_dir = Path.home() / ".local" / "share" / "tts"
    model_dir = model_base_dir / model_name.replace('/', '--')
    complete_flag = model_dir / ".complete"
    downloading_flag = model_dir / ".downloading"
    if complete_flag.exists():
        return {
            "success": True,
            "model": model_name,
            "message": f"Model {model_name} is already downloaded and ready."
        }
    if downloading_flag.exists():
        return {
            "success": False,
            "model": model_name,
            "message": f"Download for {model_name} is already in progress."
        }
    try:
        downloading_flag.touch()
        os.environ["COQUI_TOS_AGREED"] = "1"
        model_manager = ModelManager()
        model_manager.download_model(model_name)
        complete_flag.touch()
        downloading_flag.unlink(missing_ok=True)
        return {
            "success": True,
            "model": model_name,
            "message": f"Download of {model_name} completed successfully."
        }
    except Exception as e:
        downloading_flag.unlink(missing_ok=True)
        logger.error(f"Error downloading model: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading {model_name}: {e}")

@app.post("/analyze_voice")
async def analyze_voice(audio_file: UploadFile = File(...)):
    try:
        logger.info(f"Analyzing voice from file: {audio_file.filename}")
        temp_path = Path(config['output']['path']) / f"temp_{int(time.time())}_{audio_file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        try:
            y, sr = librosa.load(str(temp_path), sr=None)
        except Exception as e:
            temp_path.unlink(missing_ok=True)
            logger.error(f"Failed to load audio: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid or unreadable audio file: {e}")
        metrics = {}
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[magnitudes > np.percentile(magnitudes, 85)]
            if len(pitch_values) > 0:
                metrics['pitch_mean'] = float(np.mean(pitch_values))
                metrics['pitch_std'] = float(np.std(pitch_values))
                metrics['pitch_range'] = float(np.max(pitch_values) - np.min(pitch_values))
            rms = librosa.feature.rms(y=y)[0]
            metrics['energy_mean'] = float(np.mean(rms))
            metrics['energy_std'] = float(np.std(rms))
            metrics['energy_range'] = float(np.max(rms) - np.min(rms))
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            metrics['speaking_rate'] = float(tempo / 60)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            metrics['brightness'] = float(np.mean(spectral_centroids))
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            metrics['warmth'] = float(np.mean(spectral_rolloff))
            metrics['duration'] = float(len(y) / sr)
            if 'pitch_mean' in metrics:
                if metrics['pitch_mean'] > 200:
                    metrics['voice_type'] = "Feminina"
                elif metrics['pitch_mean'] > 150:
                    metrics['voice_type'] = "Masculina"
                else:
                    metrics['voice_type'] = "Grave"
        except Exception as e:
            temp_path.unlink(missing_ok=True)
            logger.error(f"Voice analysis failed: {e}")
            raise HTTPException(status_code=422, detail=f"Voice analysis failed: {e}")
        temp_path.unlink(missing_ok=True)
        logger.info(f"Voice analysis completed: {len(metrics)} metrics calculated")
        return {
            "success": True,
            "filename": audio_file.filename,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing voice: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.post("/clone_voice")
async def clone_voice(
    audio_file: UploadFile = File(...),
    text: str = Form(...),
    language: str = Form(None),
    model_name: str = Form(None)
):
    try:
        logger.info(f"Cloning voice from file: {audio_file.filename}")
        if tts_instance is None:
            raise HTTPException(status_code=503, detail="TTS not initialized")
        from TTS.api import TTS
        device = "cuda" if torch.cuda.is_available() and config['performance']['use_gpu'] else "cpu"
        temp_path = Path(config['output']['path']) / f"clone_{int(time.time())}_{audio_file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        if temp_path.stat().st_size == 0:
            temp_path.unlink(missing_ok=True)
            logger.error(f"Ficheiro de áudio vazio: {temp_path}")
            raise HTTPException(status_code=400, detail="Ficheiro de áudio vazio ou inválido.")
        tts_to_use = tts_instance
        if model_name is None or model_name == tts_instance.model_name:
            logger.info(f"Using global TTS instance with model: {tts_instance.model_name}")
        else:
            if model_name in tts_model_cache:
                tts_to_use = tts_model_cache[model_name]
                logger.info(f"Using cached TTS model: {model_name}")
            else:
                try:
                    logger.info(f"Loading requested TTS model: {model_name} (device: {device})")
                    tts_to_use = TTS(model_name=model_name).to(device)
                    tts_model_cache[model_name] = tts_to_use
                    logger.info(f"Loaded and cached new TTS model: {model_name}")
                except Exception as e:
                    temp_path.unlink(missing_ok=True)
                    logger.error(f"Failed to load requested model {model_name}: {e}")
                    raise HTTPException(status_code=500, detail=f"Failed to load requested model: {e}")
        timestamp = int(time.time())
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        output_filename = f"cloned_voice_{timestamp}_{text_hash}.wav"
        output_path = Path(config['output']['path']) / output_filename
        tts_args = {
            'text': text,
            'file_path': str(output_path),
            'speaker_wav': str(temp_path)
        }
        if language:
            tts_args['language'] = language
        try:
            tts_to_use.tts_to_file(**tts_args)
        except Exception as e:
            temp_path.unlink(missing_ok=True)
            logger.error(f"Error cloning voice: {e}")
            raise HTTPException(status_code=422, detail=f"Error cloning voice: {e}")
        temp_path.unlink(missing_ok=True)
        if not output_path.exists() or output_path.stat().st_size == 0:
            logger.error(f"Cloned audio file was not created: {output_path.resolve()}")
            raise HTTPException(status_code=500, detail=f"Cloned audio file was not created: {output_path.resolve()}")
        logger.info(f"Voice cloning completed: {output_filename}")
        return {
            "success": True,
            "original_file": audio_file.filename,
            "cloned_audio": output_filename,
            "text": text,
            "model_used": model_name or tts_instance.model_name,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cloning voice: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(request: SynthesisRequest):
    start_time = time.time()
    try:
        if tts_instance is None:
            raise HTTPException(status_code=503, detail="TTS not initialized")
        
        # Generate unique filename
        timestamp = int(time.time())
        text_hash = hashlib.md5(request.text.encode()).hexdigest()[:8]
        filename = f"speech_{timestamp}_{text_hash}.{request.output_format}"
        output_path = Path(config['output']['path']) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Synthesizing text: {request.text[:50]}...")
        
        use_default_voice = config['tts'].get('use_default_voice_sample', False)
        default_voice_sample = config['tts'].get('default_voice_sample')
        
        if use_default_voice and default_voice_sample and Path(default_voice_sample).exists():
            logger.info(f"Using default voice sample: {default_voice_sample}")
            device = "cuda" if torch.cuda.is_available() and config['performance']['use_gpu'] else "cpu"
            # Usar o modelo padrão (XTTS v2) em vez de YourTTS
            synthesis_params = {
                'text': request.text,
                'file_path': str(output_path),
                'speaker_wav': default_voice_sample,
                'speed': request.speed
            }
            if request.language:
                synthesis_params["language"] = request.language
            else:
                # Usar idioma padrão da configuração
                default_language = config['tts'].get('default_language', 'pt')
                synthesis_params["language"] = default_language
                logger.info(f"Using default language: {default_language}")
            
            # Mapear pt-br para pt para compatibilidade com XTTS v2
            if synthesis_params.get("language") == "pt-br":
                synthesis_params["language"] = "pt"
                logger.info("Mapped pt-br to pt for XTTS v2 compatibility")
            
            try:
                tts_instance.tts_to_file(**synthesis_params)
            except Exception as e:
                logger.error(f"Voice synthesis with default sample failed: {e}")
                raise HTTPException(status_code=422, detail=f"Voice synthesis with default sample failed: {e}")
        else:
            synthesis_params = {
                "text": request.text,
                "file_path": str(output_path),
                "speed": request.speed
            }
            
            # Sempre usar voice cloning (XTTS v2)
            if request.speaker_wav:
                synthesis_params["speaker_wav"] = request.speaker_wav
                logger.info(f"Using provided voice sample: {request.speaker_wav}")
            elif use_default_voice and default_voice_sample and Path(default_voice_sample).exists():
                synthesis_params["speaker_wav"] = default_voice_sample
                logger.info(f"Using default voice sample: {default_voice_sample}")
            else:
                raise HTTPException(status_code=422, detail="Voice sample required. Please provide speaker_wav or configure default_voice_sample")
            
            if request.language:
                synthesis_params["language"] = request.language
            else:
                # Usar idioma padrão da configuração
                default_language = config['tts'].get('default_language', 'pt')
                synthesis_params["language"] = default_language
                logger.info(f"Using default language: {default_language}")
            
            # Mapear pt-br para pt para compatibilidade com XTTS v2
            if synthesis_params.get("language") == "pt-br":
                synthesis_params["language"] = "pt"
                logger.info("Mapped pt-br to pt for XTTS v2 compatibility")
            
            try:
                tts_instance.tts_to_file(**synthesis_params)
            except Exception as e:
                logger.error(f"Voice cloning synthesis failed: {e}")
                raise HTTPException(status_code=422, detail=f"Voice cloning synthesis failed: {e}")

        # Model multilingual check - XTTS v2 is multi-lingual, so skip this check
        # if request.language and not getattr(tts_instance, 'is_multilingual', False):
        #     raise HTTPException(status_code=400, detail="Model is not multi-lingual but `language` is provided.")
        
        # Speaker validity check - Not needed for voice cloning models
        # if request.speaker:
        #     if not getattr(tts_instance, 'is_multi_speaker', False):
        #         raise HTTPException(status_code=400, detail="Model is not multi-speaker but `speaker` is provided.")
        #     if request.speaker.strip() not in getattr(tts_instance, 'speakers', []):
        #         raise HTTPException(status_code=404, detail=f"Speaker '{request.speaker}' not found for the current model.")
        # Output file check
        if not output_path.exists() or output_path.stat().st_size == 0:
            logger.error(f"Ficheiro de áudio não foi criado: {output_path.resolve()}")
            raise HTTPException(status_code=500, detail=f"Ficheiro de áudio não foi criado: {output_path.resolve()}")
        else:
            logger.info(f"Ficheiro de áudio criado com sucesso: {output_path.resolve()} ({output_path.stat().st_size} bytes)")

        processing_time = time.time() - start_time
        logger.info(f"Speech synthesized successfully: {filename} ({processing_time:.2f}s)")
        return SynthesisResponse(
            success=True,
            audio_file=filename,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/audio/get/{filename}")
async def get_audio(filename: str):
    """Obter ficheiro de áudio."""
    try:
        file_path = Path(config['output']['path']) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=file_path,
            media_type=f"audio/{file_path.suffix[1:]}",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whisper/model/list")
async def list_whisper_models():
    """Listar modelos Whisper."""
    if not WHISPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Whisper not available")
    
    try:
        models = config['whisper']['available_models']
        current_model = whisper_model_name if whisper_instance else None
        
        return {
            "models": models,
            "current_model": current_model,
            "total_models": len(models),
            "multilingual": True  # All Whisper models are multilingual
        }
    except Exception as e:
        logger.error(f"Error listing Whisper models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/whisper/model/switch")
async def switch_whisper_model(model_name: str = Query(..., description="Name of the Whisper model to switch to")):
    """Mudar de modelo Whisper."""
    global whisper_instance, whisper_model_name
    
    if not WHISPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Whisper not available")
    
    try:
        logger.info(f"Switching to Whisper model: {model_name}")
        
        # Check if model is available
        available_models = config['whisper']['available_models']
        if model_name not in available_models:
            raise HTTPException(status_code=400, detail=f"Model {model_name} not found in available models")
        
        # Initialize new Whisper instance (respect force_cpu setting)
        force_cpu = config['whisper'].get('force_cpu', False) or (args.cpu_only and not args.whisper_gpu)
        
        # Test GPU compatibility first
        gpu_available = False
        if not force_cpu and torch.cuda.is_available() and config['performance']['use_gpu']:
            try:
                # Test GPU with a simple operation
                test_tensor = torch.zeros(1, device="cuda")
                del test_tensor
                gpu_available = True
            except Exception as e:
                logger.warning(f"GPU compatibility test failed: {e}")
                gpu_available = False
        
        device = "cuda" if gpu_available else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        new_whisper = WhisperModel(
            model_size_or_path=model_name,
            device=device,
            compute_type=compute_type
        )
        
        # Replace the old instance
        old_model = whisper_model_name if whisper_instance else None
        whisper_instance = new_whisper
        whisper_model_name = model_name
        
        logger.info(f"Successfully switched from {old_model} to {model_name}")
        
        return {
            "success": True,
            "previous_model": old_model,
            "current_model": model_name,
            "message": f"Switched to {model_name}"
        }
        
    except Exception as e:
        logger.error(f"Error switching Whisper model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    request: TranscriptionRequest = None
):
    start_time = time.time()
    
    if not WHISPER_AVAILABLE or whisper_instance is None:
        raise HTTPException(status_code=503, detail="Whisper not available")
    
    try:
        logger.info(f"Transcribing audio file: {audio_file.filename}")
        
        # Save uploaded file temporarily
        temp_path = Path(config['output']['path']) / f"temp_transcribe_{int(time.time())}_{audio_file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        # Get transcription parameters
        if request is None:
            request = TranscriptionRequest()
        
        # Transcribe audio (force CPU for stability)
        try:
            segments, info = whisper_instance.transcribe(
                str(temp_path),
                language=request.language,
                word_timestamps=request.word_timestamps,
                temperature=request.temperature,
                compression_ratio_threshold=request.compression_ratio_threshold,
                log_prob_threshold=request.logprob_threshold,
                no_speech_threshold=request.no_speech_threshold
            )
        except Exception as gpu_error:
            logger.warning(f"GPU transcription failed, falling back to CPU: {gpu_error}")
            # Fallback: reinitialize Whisper with CPU
            device = "cpu"
            compute_type = "int8"
            cpu_whisper = WhisperModel(
                model_size_or_path=whisper_model_name,
                device=device,
                compute_type=compute_type
            )
            segments, info = cpu_whisper.transcribe(
                str(temp_path),
                language=request.language,
                word_timestamps=request.word_timestamps,
                temperature=request.temperature,
                compression_ratio_threshold=request.compression_ratio_threshold,
                log_prob_threshold=request.logprob_threshold,
                no_speech_threshold=request.no_speech_threshold
            )
        
        # Process results
        text = " ".join([segment.text for segment in segments])
        segments_data = [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "words": segment.words if hasattr(segment, 'words') else None
            }
            for segment in segments
        ]
        
        processing_time = time.time() - start_time
        
        # Clean up temp file
        temp_path.unlink()
        
        logger.info(f"Transcription completed: {len(text)} characters ({processing_time:.2f}s)")
        
        return TranscriptionResponse(
            success=True,
            text=text,
            language=info.language,
            segments=segments_data,
            word_timestamps=segments_data if request.word_timestamps else None,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Transcription failed: {e}")
        
        return TranscriptionResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )

@app.post("/transcribe/batch")
async def batch_transcribe(
    audio_files: List[UploadFile] = File(...),
    request: TranscriptionRequest = None
):
    if not WHISPER_AVAILABLE or whisper_instance is None:
        raise HTTPException(status_code=503, detail="Whisper not available")
    
    results = []
    
    for i, audio_file in enumerate(audio_files):
        try:
            # Create a single file upload for each file
            result = await transcribe_audio(audio_file, request)
            results.append({
                "index": i,
                "filename": audio_file.filename,
                "result": result.dict()
            })
        except Exception as e:
            results.append({
                "index": i,
                "filename": audio_file.filename,
                "result": {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            })
    
    return {
        "batch_results": results,
        "total_processed": len(audio_files),
        "successful": sum(1 for r in results if r["result"]["success"]),
        "failed": sum(1 for r in results if not r["result"]["success"])
    }

@app.post("/synthesize/batch")
async def batch_synthesize(requests: List[SynthesisRequest]):
    results = []
    
    for i, request in enumerate(requests):
        try:
            result = await synthesize_speech(request)
            results.append({
                "index": i,
                "result": result.dict()
            })
        except Exception as e:
            results.append({
                "index": i,
                "result": {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            })
    
    return {
        "batch_results": results,
        "total_processed": len(requests),
        "successful": sum(1 for r in results if r["result"]["success"]),
        "failed": sum(1 for r in results if not r["result"]["success"])
    }

@app.get("/model/status")
async def model_status(model_name: str):
    from pathlib import Path
    from TTS.utils.manage import ModelManager
    model_manager = ModelManager()
    model_dir = Path.home() / ".local" / "share" / "tts" / model_name.replace('/', '--')
    if not model_dir.exists():
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    complete_flag = model_dir / ".complete"
    downloading_flag = model_dir / ".downloading"
    status = "not_downloaded"
    if complete_flag.exists():
        status = "downloaded"
    elif downloading_flag.exists():
        status = "downloading"
    return {
        "model": model_name,
        "status": status
    }

@app.post(
    "/speaker/register",
    summary="Registar Speaker",
    description="Regista um novo perfil de voz (speaker) persistente. Deve fornecer um ficheiro .wav e um nome único. Se o nome já existir, retorna erro. Campos extra são guardados como propriedades. Exemplo de erro: {\"success\": false, \"error\": \"Speaker 'joana' already exists.\"}"
)
async def register_speaker(
    name: str = Form(..., title="Nome do Speaker", description="Nome único para o perfil de voz."),
    audio_file: UploadFile = File(..., title="Ficheiro de Áudio", description="Amostra de voz em .wav para registo."),
    request: Request = None
):
    speakers = load_speakers()
    if name in speakers:
        return JSONResponse(status_code=400, content={"success": False, "error": f"Speaker '{name}' already exists."})
    wav_path = SPEAKERS_DIR / f"{name}.wav"
    with open(wav_path, "wb") as f:
        shutil.copyfileobj(audio_file.file, f)
    props = {}
    if request:
        form = await request.form()
        for k, v in form.items():
            if k not in ["name", "audio_file"]:
                props[k] = v
    speakers[name] = {"voice_sample_path": str(wav_path), "props": props}
    save_speakers(speakers)
    return {"success": True, "name": name, "voice_sample_path": str(wav_path), "props": props}

@app.post(
    "/speaker/update",
    summary="Atualizar Speaker",
    description="Atualiza um perfil de voz existente. Pode enviar novo ficheiro .wav e/ou propriedades extra. Se o speaker não existir, retorna erro. Exemplo de erro: {\"success\": false, \"error\": \"Speaker 'joana' not found.\"}"
)
async def update_speaker(
    name: str = Form(..., title="Nome do Speaker", description="Nome do perfil de voz a atualizar."),
    audio_file: Optional[UploadFile] = File(None, title="Novo Ficheiro de Áudio", description="Nova amostra de voz em .wav (opcional)."),
    request: Request = None
):
    speakers = load_speakers()
    if name not in speakers:
        return JSONResponse(status_code=404, content={"success": False, "error": f"Speaker '{name}' not found."})
    if audio_file:
        wav_path = SPEAKERS_DIR / f"{name}.wav"
        with open(wav_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)
        speakers[name]["voice_sample_path"] = str(wav_path)
    if request:
        form = await request.form()
        for k, v in form.items():
            if k not in ["name", "audio_file"]:
                speakers[name]["props"][k] = v
    save_speakers(speakers)
    return {"success": True, "name": name, "voice_sample_path": speakers[name]["voice_sample_path"], "props": speakers[name]["props"]}

@app.delete(
    "/speaker/delete",
    summary="Remover Speaker",
    description="Remove um perfil de voz existente. Se o speaker não existir, retorna erro. Exemplo de erro: {\"success\": false, \"error\": \"Speaker 'joana' not found.\"}"
)
async def delete_speaker(
    name: str = Form(..., title="Nome do Speaker", description="Nome do perfil de voz a remover.")
):
    speakers = load_speakers()
    if name not in speakers:
        return JSONResponse(status_code=404, content={"success": False, "error": f"Speaker '{name}' not found."})
    wav_path = Path(speakers[name]["voice_sample_path"])
    if wav_path.exists():
        wav_path.unlink()
    del speakers[name]
    save_speakers(speakers)
    return {"success": True, "deleted": name}

@app.get(
    "/speaker/list",
    summary="Listar Speakers",
    description="Lista todos os perfis de voz (speakers) registados no servidor. Retorna um dicionário com nome, caminho do sample e propriedades."
)
async def list_registered_speakers():
    speakers = load_speakers()
    return {"success": True, "speakers": speakers, "total": len(speakers)}

@app.post("/speakers")
async def add_or_update_speaker(
    name: str = Body(..., description="Nome do speaker"),
    sample_path: str = Body(..., description="Caminho para o ficheiro de sample .wav"),
    language: str = Body(..., description="Idioma do speaker, ex: pt, pt-br, en"),
    metadata: Optional[dict] = Body(None, description="Metadados opcionais: género, descrição, etc.")
):
    """Adicionar ou atualizar um speaker personalizado (persistente)."""
    try:
        sample_file = Path(sample_path)
        if not sample_file.exists():
            # Fallback para coqui-tts/sample.wav
            fallback_path = Path(__file__).parent.parent / "sample.wav"
            if fallback_path.exists():
                sample_file = fallback_path
        else:
                raise HTTPException(status_code=400, detail=f"Sample file not found: {sample_path} nem fallback sample.wav")
        # Carregar speakers atuais
        speakers = load_speakers()
        speakers[name] = {
            "name": name,
            "sample_path": str(sample_file),
            "language": language,
            "metadata": metadata or {}
        }
        save_speakers(speakers)
        # Atualizar global
        global global_speakers
        global_speakers = speakers
        logger.info(f"Speaker '{name}' adicionado/atualizado com sucesso.")
        return {"success": True, "speaker": speakers[name]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar/atualizar speaker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/speakers/{name}")
async def get_speaker(name: str = FastAPIPath(..., description="Nome do speaker")):
    """Obter detalhes de um speaker personalizado."""
    try:
        speakers = load_speakers()
        if name not in speakers:
            raise HTTPException(status_code=404, detail=f"Speaker '{name}' não encontrado.")
        return {"success": True, "speaker": speakers[name]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter speaker '{name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/speakers/{name}")
async def delete_speaker(name: str = FastAPIPath(..., description="Nome do speaker")):
    """Remover um speaker personalizado."""
    try:
        speakers = load_speakers()
        if name not in speakers:
            raise HTTPException(status_code=404, detail=f"Speaker '{name}' não encontrado.")
        removed = speakers.pop(name)
        save_speakers(speakers)
        global global_speakers
        global_speakers = speakers
        logger.info(f"Speaker '{name}' removido com sucesso.")
        return {"success": True, "removed": removed}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover speaker '{name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speakers/upload")
async def upload_speaker(
    audio_file: UploadFile = File(..., description="Ficheiro de áudio .wav do speaker"),
    name: str = Form(..., description="Nome do speaker"),
    language: str = Form(..., description="Idioma do speaker, ex: pt, pt-br, en"),
    metadata: Optional[str] = Form(None, description="Metadados opcionais em JSON: género, descrição, etc.")
):
    """Fazer upload de um ficheiro .wav e registar um speaker personalizado."""
    import json as pyjson
    try:
        if not audio_file.filename.lower().endswith('.wav'):
            raise HTTPException(status_code=400, detail="O ficheiro deve ser .wav.")
        # Guardar ficheiro em downloads/
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        safe_name = name.replace(" ", "_").lower()
        dest_path = downloads_dir / f"{safe_name}.wav"
        with open(dest_path, "wb") as f:
            f.write(await audio_file.read())
        # Validar tamanho
        if dest_path.stat().st_size < 1024:
            dest_path.unlink()
            raise HTTPException(status_code=400, detail="Ficheiro de áudio demasiado pequeno ou inválido.")
        # Parse metadata se fornecido
        meta = {}
        if metadata:
            try:
                meta = pyjson.loads(metadata)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erro a ler metadata JSON: {e}")
        # Registar speaker
        speakers = load_speakers()
        speakers[name] = {
            "name": name,
            "sample_path": str(dest_path),
            "language": language,
            "metadata": meta
        }
        save_speakers(speakers)
        global global_speakers
        global_speakers = speakers
        logger.info(f"Speaker '{name}' registado com upload.")
        return {"success": True, "speaker": speakers[name], "file_path": str(dest_path)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload de speaker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Coqui TTS Server...")
    
    uvicorn.run(
        "src.tts_server:app",
        host=args.host,
        port=args.port,
        reload=False,  # Desativado para evitar reinícios automáticos
        workers=config['server']['workers']
