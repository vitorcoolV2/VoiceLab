#!/bin/bash
# run_fixed_tests.sh

echo "🧪 Running Fixed Coqui TTS Tests"
echo "================================"

cd coqui-tts/tests

# Check if server is running
echo "🔍 Checking server status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server not running. Please start it first with: bash run.sh"
    exit 1
fi

# Create output directory
mkdir -p voice_outputs

echo ""
echo "1️⃣ Testing YourTTS Portuguese variations..."
python teste_todas_vozes_yourtts_fixed.py

echo ""
echo "2️⃣ Testing Portuguese Brazilian synthesis..."
python teste_yourtts_pt_br_fixed.py

echo ""
echo "3️⃣ Testing human voice customization..."
python teste_voz_humana_customizada_fixed.py

echo ""
echo "🎉 All fixed tests completed!"
echo " Check voice_outputs/ directory for generated audio files" 