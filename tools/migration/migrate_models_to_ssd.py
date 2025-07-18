#!/usr/bin/env python3
"""
Migrate LLM models to external SSD to free up space and enable GPU acceleration
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import yaml

# Configuration
EXTERNAL_SSD_PATH = os.environ.get("EXTERNAL_SSD_PATH", "/media/vitor/ssd990")
MODELS_DIR = os.environ.get("TTS_CACHE_DIR", f"{EXTERNAL_SSD_PATH}/ai_models")
TTS_MODELS_DIR = os.environ.get("COQUI_TTS_HOME", f"{MODELS_DIR}/tts")
WHISPER_MODELS_DIR = os.environ.get("WHISPER_CACHE_DIR", f"{MODELS_DIR}/whisper")

# Current model locations
CURRENT_TTS_PATH = os.path.expanduser("~/.local/share/tts")
CURRENT_WHISPER_PATH = os.path.expanduser("~/.cache/huggingface/hub")

def check_external_ssd():
    """Check if external SSD is available"""
    print("🔍 Checking external SSD availability...")
    
    if not os.path.exists(EXTERNAL_SSD_PATH):
        print(f"❌ External SSD not found at {EXTERNAL_SSD_PATH}")
        return False
    
    # Check available space
    result = subprocess.run(['df', '-h', EXTERNAL_SSD_PATH], capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 4:
                available = parts[3]
                print(f"✅ External SSD available with {available} free space")
                return True
    
    print("❌ Cannot determine external SSD space")
    return False

def create_directories():
    """Create necessary directories on external SSD"""
    print("\n📁 Creating directories on external SSD...")
    
    directories = [
        MODELS_DIR,
        TTS_MODELS_DIR,
        WHISPER_MODELS_DIR
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def migrate_tts_models():
    """Migrate TTS models to external SSD"""
    print("\n🎤 Migrating TTS models...")
    
    if not os.path.exists(CURRENT_TTS_PATH):
        print("❌ TTS models directory not found")
        return False
    
    # Get list of TTS models
    tts_models = [d for d in os.listdir(CURRENT_TTS_PATH) 
                  if os.path.isdir(os.path.join(CURRENT_TTS_PATH, d))]
    
    if not tts_models:
        print("❌ No TTS models found")
        return False
    
    print(f"Found {len(tts_models)} TTS models:")
    for model in tts_models:
        print(f"  - {model}")
    
    # Migrate each model
    for model in tts_models:
        src = os.path.join(CURRENT_TTS_PATH, model)
        dst = os.path.join(TTS_MODELS_DIR, model)
        
        if os.path.exists(dst):
            print(f"⚠️  {model} already exists on SSD, skipping...")
            continue
        
        print(f"📦 Migrating {model}...")
        try:
            shutil.copytree(src, dst)
            print(f"✅ Migrated {model}")
        except Exception as e:
            print(f"❌ Failed to migrate {model}: {e}")
            return False
    
    return True

def migrate_whisper_models():
    """Migrate Whisper models to external SSD"""
    print("\n🎧 Migrating Whisper models...")
    
    if not os.path.exists(CURRENT_WHISPER_PATH):
        print("❌ Whisper models directory not found")
        return False
    
    # Get list of Whisper models
    whisper_models = [d for d in os.listdir(CURRENT_WHISPER_PATH) 
                     if d.startswith('models--Systran--faster-whisper-')]
    
    if not whisper_models:
        print("❌ No Whisper models found")
        return False
    
    print(f"Found {len(whisper_models)} Whisper models:")
    for model in whisper_models:
        print(f"  - {model}")
    
    # Migrate each model
    for model in whisper_models:
        src = os.path.join(CURRENT_WHISPER_PATH, model)
        dst = os.path.join(WHISPER_MODELS_DIR, model)
        
        if os.path.exists(dst):
            print(f"⚠️  {model} already exists on SSD, skipping...")
            continue
        
        print(f"📦 Migrating {model}...")
        try:
            shutil.copytree(src, dst)
            print(f"✅ Migrated {model}")
        except Exception as e:
            print(f"❌ Failed to migrate {model}: {e}")
            return False
    
    return True

def create_symlinks():
    """Create symlinks from original locations to external SSD"""
    print("\n🔗 Creating symlinks...")
    
    # Backup original directories
    tts_backup = f"{CURRENT_TTS_PATH}_backup"
    whisper_backup = f"{CURRENT_WHISPER_PATH}_backup"
    
    # Backup TTS models
    if os.path.exists(CURRENT_TTS_PATH) and not os.path.exists(tts_backup):
        print(f"📋 Backing up TTS models to {tts_backup}")
        shutil.move(CURRENT_TTS_PATH, tts_backup)
    
    # Create symlink for TTS
    if not os.path.exists(CURRENT_TTS_PATH):
        os.symlink(TTS_MODELS_DIR, CURRENT_TTS_PATH)
        print(f"✅ Created symlink: {CURRENT_TTS_PATH} -> {TTS_MODELS_DIR}")
    
    # For Whisper, we need to be more careful since it's in cache
    # We'll update the configuration instead of creating symlinks
    print("ℹ️  Whisper models will be configured via environment variables")

def update_configuration():
    """Update configuration to use external SSD and enable GPU"""
    print("\n⚙️  Updating configuration...")
    
    config_file = "config/settings.yaml"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    # Read current config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update TTS model path
    config['models']['path'] = TTS_MODELS_DIR
    config['models']['cache_dir'] = f"{MODELS_DIR}/cache"
    
    # Enable GPU for Whisper
    config['whisper']['force_cpu'] = False
    
    # Write updated config
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ Updated configuration:")
    print(f"   TTS models path: {TTS_MODELS_DIR}")
    print(f"   Cache directory: {MODELS_DIR}/cache")
    print(f"   Whisper GPU enabled: {not config['whisper']['force_cpu']}")
    
    return True

def create_environment_script():
    """Create environment setup script"""
    print("\n📝 Creating environment setup script...")
    
    env_script = "setup_external_models.sh"
    content = f"""#!/bin/bash
# Setup environment for external SSD models

export HF_HOME="{MODELS_DIR}/huggingface"
export TTS_HOME="{TTS_MODELS_DIR}"
export COQUI_TTS_CACHE_DIR="{MODELS_DIR}/cache"

echo "✅ Environment variables set for external SSD models:"
echo "   HF_HOME: $HF_HOME"
echo "   TTS_HOME: $TTS_HOME"
echo "   COQUI_TTS_CACHE_DIR: $COQUI_TTS_CACHE_DIR"
"""
    
    with open(env_script, 'w') as f:
        f.write(content)
    
    os.chmod(env_script, 0o755)
    print(f"✅ Created: {env_script}")

def verify_migration():
    """Verify that migration was successful"""
    print("\n🔍 Verifying migration...")
    
    # Check TTS models
    if os.path.exists(TTS_MODELS_DIR):
        tts_models = os.listdir(TTS_MODELS_DIR)
        print(f"✅ TTS models on SSD: {len(tts_models)}")
        for model in tts_models:
            print(f"   - {model}")
    
    # Check Whisper models
    if os.path.exists(WHISPER_MODELS_DIR):
        whisper_models = os.listdir(WHISPER_MODELS_DIR)
        print(f"✅ Whisper models on SSD: {len(whisper_models)}")
        for model in whisper_models:
            print(f"   - {model}")
    
    # Check symlink
    if os.path.islink(CURRENT_TTS_PATH):
        target = os.readlink(CURRENT_TTS_PATH)
        print(f"✅ TTS symlink: {CURRENT_TTS_PATH} -> {target}")
    
    return True

def main():
    """Main migration function"""
    print("🚀 Starting Model Migration to External SSD")
    print("=" * 60)
    
    # Check external SSD
    if not check_external_ssd():
        return False
    
    # Create directories
    create_directories()
    
    # Migrate models
    if not migrate_tts_models():
        return False
    
    if not migrate_whisper_models():
        return False
    
    # Create symlinks
    create_symlinks()
    
    # Update configuration
    if not update_configuration():
        return False
    
    # Create environment script
    create_environment_script()
    
    # Verify migration
    verify_migration()
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart the TTS server to use new configuration")
    print("2. Run: source setup_external_models.sh")
    print("3. Test GPU acceleration with: python tests/whisper/test_gpu_compatibility.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 