# 🚀 Coqui TTS & Whisper Server - Complete Setup Guide

This guide will walk you through the complete installation and setup of the Coqui TTS & Whisper Server.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows
- **Python**: 3.11 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB+ free space
- **GPU**: NVIDIA GPU with CUDA support (optional)

### Required Software
- **Conda/Miniconda**: [Download here](https://docs.conda.io/en/latest/miniconda.html)
- **Git**: For cloning the repository

## 🛠️ Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Clone the repository
cd /secure/flows-feedback-loop/coqui-tts

# Run the automated installation script
./install.sh
```

### Method 2: Manual Installation

```bash
# 1. Create conda environment
conda create -n coqui-tts python=3.11 -y

# 2. Activate environment
conda activate coqui-tts

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create directories
mkdir -p output logs downloads

# 5. Set up logging
touch logs/tts.log
```

## 🚀 Quick Start

### Start the Server

```bash
# Method 1: Use the start script
./start.sh

# Method 2: Manual start
conda activate coqui-tts
python src/tts_server.py
```

### Access the API

- **Server URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing the Installation

### Run Integration Tests

```bash
# Test Whisper integration
python tests/test_whisper_integration.py

# Test TTS functionality
python tests_scripts/teste_simples_tts.py
```

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test Whisper models
curl http://localhost:8000/whisper/models

# Test TTS models
curl http://localhost:8000/models
```

## ⚙️ Configuration

### Basic Configuration

Edit `config/settings.yaml` to customize:

```yaml
# Server settings
server:
  host: 0.0.0.0
  port: 8000
  debug: false

# TTS settings
tts:
  default_model: tts_models/pt/cv/vits
  default_output_format: wav
  default_speed: 1.0

# Whisper settings
whisper:
  default_model: base
  force_cpu: true  # Set to false for GPU mode
  language_detection: true

# Performance settings
performance:
  use_gpu: true
  batch_size: 1
```

### GPU Configuration

To enable GPU mode:

1. **Ensure CUDA is installed**:
   ```bash
   nvidia-smi  # Check GPU availability
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Update configuration**:
   ```yaml
   whisper:
     force_cpu: false  # Enable GPU mode
   ```

3. **Install CUDA dependencies** (if needed):
   ```bash
   pip install nvidia-cudnn-cu12==9.5.1.17
   ```

## 📊 Performance Optimization

### CPU Mode (Recommended for Stability)

- Use smaller Whisper models (tiny, base)
- Process audio in smaller chunks
- Close other applications to free RAM

### GPU Mode (For Better Performance)

- Monitor GPU memory usage
- Use appropriate batch sizes
- Ensure CUDA and cuDNN compatibility

## 🚨 Troubleshooting

### Common Issues

#### 1. CUDA/GPU Issues
```bash
# Force CPU mode in config/settings.yaml:
whisper:
  force_cpu: true
```

#### 2. Disk Space Issues
```bash
# Clean up old files
rm -f output*.wav test_*.wav
echo "" > logs/tts.log
conda clean --all -y
```

#### 3. Port Already in Use
```bash
# Kill existing process
pkill -f "python src/tts_server.py"
# Or change port in config/settings.yaml
```

#### 4. Model Download Issues
```bash
# Check internet connection
# Ensure sufficient disk space
# Try downloading models manually
```

### Performance Issues

#### Slow Transcription
- Use smaller Whisper models (tiny, base)
- Process shorter audio files
- Close other applications

#### Memory Issues
- Reduce batch size in configuration
- Use CPU mode instead of GPU
- Increase system RAM

### Log Analysis

Check logs for detailed error information:
```bash
tail -f logs/tts.log
```

## 🔧 Advanced Configuration

### Custom Models

1. **Add custom TTS models**:
   ```bash
   # Download models to downloads/ directory
   # Update config/settings.yaml with model paths
   ```

2. **Use custom Whisper models**:
   ```bash
   # Download Whisper models
   # Update available_models in configuration
   ```

### Environment Variables

Set these environment variables for customization:

```bash
export COQUI_TTS_ROOT=/path/to/coqui-tts
export CUDA_VISIBLE_DEVICES=0  # Use specific GPU
export TORCH_HOME=/path/to/torch/cache
```

### Production Deployment

For production use:

1. **Use a process manager** (systemd, supervisor)
2. **Set up reverse proxy** (nginx, Apache)
3. **Configure SSL/TLS**
4. **Set up monitoring** and logging
5. **Use environment-specific configurations**

## 📚 API Usage Examples

### Text-to-Speech

```python
import requests

# Basic synthesis
response = requests.post("http://localhost:8000/synthesize", json={
    "text": "Hello, this is a test!",
    "language": "en",
    "speed": 1.0
})

# Voice cloning
files = {"audio_file": open("voice_sample.wav", "rb")}
data = {"text": "This will be spoken in the cloned voice"}
response = requests.post("http://localhost:8000/clone_voice", files=files, data=data)
```

### Speech-to-Text

```python
# Transcribe audio
files = {"audio_file": open("audio.wav", "rb")}
response = requests.post("http://localhost:8000/transcribe", files=files)

# With specific parameters
files = {"audio_file": open("audio.wav", "rb")}
data = {
    "model_name": "base",
    "language": "en",
    "word_timestamps": True
}
response = requests.post("http://localhost:8000/transcribe", files=files, data=data)
```

## 🔄 Updates and Maintenance

### Updating Dependencies

```bash
# Update Python packages
pip install -r requirements.txt --upgrade

# Update conda environment
conda env update -f environment.yml
```

### Backup and Restore

```bash
# Backup configuration
cp config/settings.yaml config/settings.yaml.backup

# Backup models (if custom)
tar -czf models_backup.tar.gz downloads/

# Restore from backup
cp config/settings.yaml.backup config/settings.yaml
```

## 📞 Support

For issues and questions:

1. **Check the troubleshooting section**
2. **Review the logs** in `logs/tts.log`
3. **Run the integration tests**
4. **Check the API documentation** at http://localhost:8000/docs
5. **Open an issue** with detailed error information

## 🎯 Next Steps

After successful installation:

1. **Test the API endpoints**
2. **Integrate with your application**
3. **Configure for your use case**
4. **Set up monitoring and logging**
5. **Optimize performance** based on your needs

---

**🎉 Congratulations!** Your Coqui TTS & Whisper Server is now ready for use! 