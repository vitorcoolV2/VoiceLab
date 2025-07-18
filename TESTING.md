# Testing Guide for Coqui TTS Server

This document explains how to run tests for the Coqui TTS Server project, including the test organization, recommended order, and available test categories.

## 📋 Test Organization

The tests are organized into logical categories based on functionality:

```
tests/
├── integration/          # Server integration and client tests
├── tts/                  # Core TTS functionality tests
├── whisper/              # Whisper STT functionality tests
├── voice_cloning/        # Voice cloning and analysis tests
├── utils/                # Utility and helper tests
└── qa/                   # Quality assurance tests
```

## 🚀 Quick Start

### Prerequisites
1. **Server must be running** - Start the server first:
   ```bash
   ./start.sh
   ```

2. **Verify server is healthy**:
   ```bash
   curl http://localhost:8000/health
   ```

### Running Tests

#### Option 1: Comprehensive Test Runner (Recommended)
```bash
# Run all tests in recommended order
python run_tests.py

# Run specific test categories
python run_tests.py integration
python run_tests.py tts
python run_tests.py whisper
python run_tests.py voice_cloning
```

#### Option 2: Manual Test Execution
```bash
# Navigate to specific test directories and run individual tests
cd tests/integration
python test_server_complete.py
python test_client.py
```

## 📊 Test Categories & Order

### 1. Integration Tests (`tests/integration/`)
**Purpose**: Verify server health and basic client-server communication
**Order**: Run first to ensure server is working

- `test_server_complete.py` - Comprehensive server functionality test
- `test_client.py` - Client integration test

**What it tests**:
- Server health check
- Model listing and switching
- Basic synthesis functionality
- Multi-speaker models
- Model download capabilities

### 2. Core TTS Tests (`tests/tts/`)
**Purpose**: Test basic text-to-speech functionality
**Order**: Run after integration tests pass

- `teste_simples_tts.py` - Simple TTS synthesis test
- `test_tts_integration.py` - TTS integration test
- `teste_yourtts_pt_br.py` - YourTTS Portuguese/Brazilian test
- `teste_modelos_pt_br.py` - Portuguese model tests
- `teste_vozes_genero.py` - Gender voice tests
- `teste_voz_humana_customizada.py` - Custom human voice tests
- `teste_todas_vozes_yourtts.py` - All YourTTS voices test

**What it tests**:
- Basic text synthesis
- Speaker selection
- Language-specific models
- Voice customization
- Audio output generation

### 3. Whisper STT Tests (`tests/whisper/`)
**Purpose**: Test speech-to-text functionality
**Order**: Run after TTS tests

- `test_whisper_integration.py` - Whisper integration test
- `test_whisper_params.py` - Whisper parameter tests
- `test_whisper_attributes.py` - Whisper attribute tests
- `test_gpu_compatibility.py` - GPU compatibility test

**What it tests**:
- Audio transcription
- Model switching
- Parameter validation
- GPU/CPU compatibility
- Batch processing

### 4. Voice Cloning Tests (`tests/voice_cloning/`)
**Purpose**: Test voice cloning and analysis features
**Order**: Run after core functionality tests

- `test_yourtts_direct.py` - Direct YourTTS test
- `test_yourtts_speakers.py` - YourTTS speakers test
- `test_voice_analysis.py` - Voice analysis test
- `test_complete_pipeline.py` - Complete cloning pipeline
- `test_processed_voice_cloning.py` - Processed voice cloning
- `test_youtube_cloning.py` - YouTube voice cloning
- `test_youtube_cloning_pt.py` - Portuguese YouTube cloning
- `test_different_videos.py` - Multiple video sources
- `test_voice_cloning_with_processed_samples.py` - Advanced cloning

**What it tests**:
- Voice cloning from samples
- YouTube video processing
- Voice analysis and characteristics
- Complete cloning workflows
- Multi-source voice extraction

### 5. Quality Assurance Tests (`tests/qa/`)
**Purpose**: Quality assurance and validation
**Order**: Run last for comprehensive validation

- `QA_TESTING_GUIDE.md` - QA testing procedures
- `qa_report.json` - QA test results

## 🔧 Test Runner Features

The `run_tests.py` script provides:

- **Automatic server health check** before running tests
- **Logical test ordering** based on dependencies
- **Timeout protection** (5 minutes per test)
- **Detailed reporting** with pass/fail statistics
- **Category-specific execution** for focused testing
- **Error handling** and graceful failure recovery

### Test Runner Output Example
```
🚀 Starting Comprehensive Test Suite
============================================================
✅ Server is running

📋 Running Integration Tests
============================================================

🧪 Server Complete Integration
==================================================
✅ Test passed

🧪 Client Integration
==================================================
✅ Test passed

📊 Integration Tests Results: 2/2 passed

📊 FINAL TEST RESULTS
============================================================
Total Tests: 15
Passed: 14
Failed: 1
Success Rate: 93.3%

Detailed Results:
  ✅ Server Complete Integration: PASS
  ✅ Client Integration: PASS
  ✅ Simple TTS: PASS
  ❌ Whisper Integration: FAIL
  ...
```

## 🛠️ Troubleshooting

### Common Issues

1. **Server not running**
   ```bash
   # Start the server first
   ./start.sh
   # Wait for server to fully start (check logs)
   ```

2. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   # Kill existing process if needed
   kill -9 <PID>
   ```

3. **GPU compatibility issues**
   - Tests will automatically fall back to CPU mode
   - Check `test_gpu_compatibility.py` for detailed diagnostics

4. **Model download failures**
   - Check internet connection
   - Verify disk space availability
   - Check model cache directory permissions

### Debug Mode
For detailed debugging, run individual tests with verbose output:
```bash
cd tests/tts
python -u teste_simples_tts.py 2>&1 | tee test_output.log
```

## 📈 Test Coverage

The test suite covers:

- ✅ **Server Health**: Basic server functionality
- ✅ **TTS Synthesis**: Text-to-speech generation
- ✅ **STT Transcription**: Speech-to-text conversion
- ✅ **Voice Cloning**: Voice replication from samples
- ✅ **YouTube Integration**: Video-to-voice extraction
- ✅ **Multi-language Support**: Portuguese/Brazilian models
- ✅ **Model Management**: Download, switch, and list models
- ✅ **Error Handling**: Graceful failure scenarios
- ✅ **Performance**: Processing time and resource usage

## 🔄 Continuous Testing

For development workflow:

1. **Quick Tests** (before commits):
   ```bash
   python run_tests.py integration
   python run_tests.py tts
   ```

2. **Full Test Suite** (before releases):
   ```bash
   python run_tests.py
   ```

3. **Specific Feature Tests** (during development):
   ```bash
   python run_tests.py whisper  # When working on STT
   python run_tests.py voice_cloning  # When working on cloning
   ```

## 📝 Adding New Tests

When adding new tests:

1. **Place in appropriate category**:
   - Integration tests → `tests/integration/`
   - TTS tests → `tests/tts/`
   - Whisper tests → `tests/whisper/`
   - Voice cloning tests → `tests/voice_cloning/`

2. **Follow naming convention**:
   - `test_*.py` for test files
   - Descriptive names indicating functionality

3. **Update test runner**:
   - Add new tests to `run_tests.py` in appropriate category
   - Maintain logical ordering

4. **Include proper error handling**:
   - Check server availability
   - Handle timeouts gracefully
   - Provide clear error messages

## 🎯 Best Practices

1. **Always start server first** before running tests
2. **Run tests in order** for best results
3. **Check logs** if tests fail unexpectedly
4. **Use specific categories** for focused testing
5. **Monitor resource usage** during long test runs
6. **Clean up test outputs** periodically

---

For more information about specific test functionality, see the individual test files and their documentation. 