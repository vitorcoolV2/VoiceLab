# QA Testing Guide for Voice Cloning Pipeline

This guide covers the enhanced QA testing system that automatically plays samples at each stage of the voice cloning process for quality confirmation.

## 🎯 Overview

The QA testing system ensures quality at every stage:
1. **Original Download** - YouTube audio quality
2. **Processed Audio** - Cleaned/optimized for TTS
3. **Synthesized Voice** - Final voice clone output

## 🛠️ Tools Overview

### 1. Generic Audio Player (`tools/audio_player.py`)
- **Purpose**: Universal audio playback with multiple player support
- **Features**: Auto-detection, multiple formats, configurable options
- **Players**: VLC, mpv, ffplay, aplay, paplay
- **Formats**: .wav, .mp3, .flac, .ogg, .m4a, .aac, .wma

### 2. QA Testing Tool (`qa_voice_cloning.py`)
- **Purpose**: Comprehensive testing of all pipeline stages
- **Features**: File discovery, quality analysis, batch testing, reporting
- **Modes**: Interactive, batch, single sample
- **Status**: ⚠️ Requires server running and proper imports

### 3. Simplified QA Tool (`qa_test.py`) ⭐ **NEW**
- **Purpose**: Fixed version without complex import dependencies
- **Features**: Same functionality as qa_voice_cloning.py but with simplified imports
- **Status**: ✅ Ready to use, no import issues
- **Dependencies**: Only requires requests, wave, pathlib (standard libraries)

### 4. Quick QA Tool (`quick_qa_test.py`)
- **Purpose**: Fast quality confirmation for immediate feedback
- **Features**: Simple interface, latest sample testing, all samples testing

### 5. Enhanced Pipeline (`download_and_process_with_qa.py`)
- **Purpose**: Complete pipeline with automatic QA testing
- **Features**: Stage-by-stage QA, interactive ratings, comprehensive reporting

## 🚀 Quick Start

### Test the Latest Sample (Simplified)
```bash
python qa_test.py --sample "sample_name"
```

### Test All Samples (Simplified)
```bash
python qa_test.py --all
```

### List Available Samples
```bash
python qa_test.py --list
```

### Test the Latest Sample (Original)
```bash
python quick_qa_test.py --latest
```

### Test All Samples (Original)
```bash
python qa_voice_cloning.py --batch
```

### Test Specific Sample (Original)
```bash
python qa_voice_cloning.py --sample "sample_name"
```

### Interactive Testing with Quality Ratings
```bash
python qa_voice_cloning.py --sample "sample_name" --interactive
```

## 📋 Detailed Usage

### 1. Simplified QA Testing (Recommended) ⭐

#### List Available Samples
```bash
python qa_test.py --list
```

#### Test Single Sample
```bash
python qa_test.py --sample "sample_name"
```

#### Batch Testing
```bash
python qa_test.py --all
```

#### Custom Server URL
```bash
python qa_test.py --sample "sample_name" --server "http://localhost:8000"
```

#### Custom Audio Player
```bash
python qa_test.py --sample "sample_name" --player mpv
```

#### Disable Auto-play
```bash
python qa_test.py --sample "sample_name" --no-play
```

### 2. Quick QA Testing

#### Test Latest Sample
```bash
python quick_qa_test.py --latest
```
- Automatically finds and tests the most recent sample
- Plays all stages: Original → Processed → Synthesized

#### Test All Samples
```bash
python quick_qa_test.py --all
```
- Tests all available samples in sequence
- Useful for batch quality assessment

#### Test Specific Sample
```bash
python quick_qa_test.py "sample_name"
```
- Tests a specific sample by name
- Example: `python quick_qa_test.py "How_to_get_a_deeper_voice"`

#### Interactive Mode
```bash
python quick_qa_test.py --interactive
```
- Prompts for quality ratings (1-5) at each stage
- Saves quality assessments for analysis

### 3. Comprehensive QA Testing (Original)

#### List Available Samples
```bash
python qa_voice_cloning.py --list
```

#### Test Single Sample
```bash
python qa_voice_cloning.py --sample "sample_name"
```

#### Batch Testing
```bash
python qa_voice_cloning.py --batch
```

#### Interactive Testing
```bash
python qa_voice_cloning.py --sample "sample_name" --interactive
```

#### Custom Player
```bash
python qa_voice_cloning.py --sample "sample_name" --player mpv
```

### 4. Enhanced Pipeline with QA

#### Basic Usage
```bash
python download_and_process_with_qa.py "https://youtube.com/watch?v=..."
```

#### Interactive QA Testing
```bash
python download_and_process_with_qa.py "youtube_url" --qa-interactive
```

#### Custom Text for Synthesis
```bash
python download_and_process_with_qa.py "youtube_url" --text "Custom test text"
```

#### Disable QA Testing
```bash
python download_and_process_with_qa.py "youtube_url" --no-qa
```

#### Multiple URLs
```bash
python download_and_process_with_qa.py "url1" "url2" "url3"
```

### 5. Generic Audio Player

#### Play Single File
```bash
python tools/audio_player.py sample.wav
```

#### Play Multiple Files
```bash
python tools/audio_player.py file1.wav file2.wav file3.wav
```

#### Play Directory
```bash
python tools/audio_player.py downloads/ --pattern "*.wav"
```

#### Custom Player
```bash
python tools/audio_player.py sample.wav --player mpv
```

## 🎵 Audio Player Options

### Supported Players
- **vlc** - VLC Media Player (default)
- **mpv** - MPV Media Player
- **ffplay** - FFmpeg Player
- **aplay** - ALSA Player
- **paplay** - PulseAudio Player
- **auto** - Auto-detect best available

### Player Configuration
```bash
# Volume control
python qa_test.py --sample "sample" --volume 80

# Pause between samples
python qa_test.py --sample "sample" --pause 5.0

# Custom interface
python qa_test.py --sample "sample" --player vlc --interface dummy
```

## 📊 Quality Assessment

### Interactive Quality Ratings
When using `--interactive` mode, you can rate each stage:

1. **Original Download** (1-5)
   - 1: Poor quality, lots of noise
   - 3: Acceptable quality
   - 5: Excellent quality, clear voice

2. **Processed Audio** (1-5)
   - 1: Processing degraded quality
   - 3: Acceptable processing
   - 5: Excellent processing, optimized for TTS

3. **Synthesized Voice** (1-5)
   - 1: Poor cloning, doesn't sound like original
   - 3: Acceptable cloning
   - 5: Excellent cloning, very similar to original

### Quality Factors
- **Clarity**: How clear is the voice?
- **Similarity**: How similar to the original?
- **Naturalness**: How natural does it sound?
- **Volume**: Appropriate volume levels?
- **Artifacts**: Any audio artifacts or distortions?

## 🔧 Troubleshooting

### Import Issues (Fixed in qa_test.py)

#### Problem: ModuleNotFoundError for TTS
```bash
# Old version (qa_voice_cloning.py)
ModuleNotFoundError: No module named 'TTS'

# Solution: Use simplified version
python qa_test.py --list
```

#### Problem: Complex import dependencies
```bash
# Old version tries to import from tools/ which has TTS dependencies
# Solution: Use qa_test.py which has simplified imports
```

### Server Connection Issues

#### Check if server is running
```bash
curl http://localhost:8000/health
```

#### Start server if needed
```bash
cd /secure/flows-feedback-loop/coqui-tts
bash scripts/script_start_server.sh
```

### Audio Player Issues

#### No Audio Player Found
```bash
# Install VLC
sudo apt-get install vlc

# Or use alternative player
python qa_test.py --sample "sample" --player mpv
```

#### Audio Playback Issues
```bash
# Test audio player
python tools/audio_player.py sample.wav

# Check audio system
aplay -l  # List audio devices
```

### File Issues

#### No Samples Found
```bash
# Check available samples
python qa_test.py --list

# Verify file structure
ls -la downloads/
ls -la output/
```

#### Permission Issues
```bash
# Fix file permissions
chmod +x qa_test.py
chmod +x quick_qa_test.py
```

## 📁 File Organization

### Directory Structure
```
coqui-tts/
├── downloads/           # Original YouTube downloads
│   ├── sample.wav      # Original audio
│   ├── sample_voice_sample.wav  # Processed voice sample
│   └── sample_cloned.wav        # Cloned voice output
├── output/             # Synthesized voice clones
│   └── cloned_voice_*.wav  # Voice clones
└── tests/qa/           # QA testing tools
    ├── qa_test.py      # Simplified QA tool ⭐
    ├── qa_voice_cloning.py  # Original QA tool
    ├── quick_qa_test.py     # Quick QA tool
    └── QA_TESTING_GUIDE.md  # This guide
```

### File Naming Convention
- **Original**: `sample_name.wav`
- **Voice Sample**: `sample_name_voice_sample.wav`
- **Cloned**: `sample_name_cloned.wav`
- **Output**: `cloned_voice_timestamp_hash.wav`

## 🎯 Best Practices

### For Quality Testing
1. **Use qa_test.py** for reliable testing without import issues
2. **Test in quiet environment** for accurate assessment
3. **Use consistent volume levels** across tests
4. **Rate objectively** based on technical quality, not personal preference
5. **Document issues** for improvement tracking

### For Pipeline Integration
1. **Enable QA testing** for new samples
2. **Use interactive mode** for important samples
3. **Review QA reports** regularly
4. **Adjust processing parameters** based on QA feedback

### For Batch Processing
1. **Start with small batches** to verify quality
2. **Monitor QA results** during processing
3. **Save detailed reports** for analysis
4. **Iterate on parameters** based on results

## 📚 Examples

### Complete Workflow Example
```bash
# 1. Check server status
curl http://localhost:8000/health

# 2. List available samples
python qa_test.py --list

# 3. Test specific sample
python qa_test.py --sample "sample_name"

# 4. Test all samples
python qa_test.py --all

# 5. Generate report
python qa_test.py --sample "sample" --report "detailed_report.json"
```

### Quality Improvement Workflow
```bash
# 1. Test current quality
python qa_test.py --sample "sample_name"

# 2. Adjust processing parameters
# Edit voice processing tools

# 3. Re-process with new parameters
python tools/audio_utils/youtube_voice_cloner.py

# 4. Re-test quality
python qa_test.py --sample "sample_name"

# 5. Compare results
# Check generated reports
```

## 🆕 Recent Updates

### Version 2.0 - Simplified QA Tool
- ✅ **Fixed import issues** - No more TTS module dependencies
- ✅ **Simplified audio player** - Built-in player without complex imports
- ✅ **Better error handling** - Clear error messages and fallbacks
- ✅ **DRY principle** - Cleaner code structure
- ✅ **Server health checks** - Automatic server connection verification

### Migration Guide
```bash
# Old way (may have import issues)
python qa_voice_cloning.py --list

# New way (recommended)
python qa_test.py --list
```

This QA testing system ensures that every stage of your voice cloning pipeline meets quality standards and provides immediate feedback for optimization. The simplified version (`qa_test.py`) is recommended for most use cases as it avoids import issues while maintaining all functionality. 