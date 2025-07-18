#!/usr/bin/env python3
"""
Configuration Switcher for Coqui TTS
Switch between coexistence mode (with Ollama) and speed mode (dedicated GPU)
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def check_gpu_usage():
    """Check current GPU memory usage"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                used, total = map(int, line.split(', '))
                usage_percent = (used / total) * 100
                print(f"📊 GPU Memory: {used}MB / {total}MB ({usage_percent:.1f}%)")
                return used, total, usage_percent
    except Exception as e:
        print(f"⚠️ Could not check GPU usage: {e}")
    return None, None, None

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        result = subprocess.run(['pgrep', 'ollama'], capture_output=True)
        return result.returncode == 0
    except:
        return False

def switch_config(mode):
    """Switch to specified configuration mode"""
    config_dir = Path("config")
    main_config = config_dir / "settings.yaml"
    
    if mode == "coexistence":
        source_config = config_dir / "settings_coexistence.yaml"
        print("🔄 Switching to COEXISTENCE mode (optimized for Ollama + Coqui TTS)")
    elif mode == "speed":
        source_config = config_dir / "settings_speed.yaml"
        print("🚀 Switching to SPEED mode (dedicated GPU for maximum performance)")
    else:
        print(f"❌ Unknown mode: {mode}")
        return False
    
    if not source_config.exists():
        print(f"❌ Configuration file not found: {source_config}")
        return False
    
    # Backup current config
    backup_config = config_dir / f"settings_backup_{int(time.time())}.yaml"
    if main_config.exists():
        shutil.copy2(main_config, backup_config)
        print(f"💾 Backup created: {backup_config}")
    
    # Switch configuration
    shutil.copy2(source_config, main_config)
    print(f"✅ Switched to {mode} configuration")
    
    return True

def restart_server():
    """Restart the TTS server with new configuration"""
    print("\n🔄 Restarting TTS server...")
    
    # Kill existing server
    try:
        subprocess.run(['pkill', '-f', 'python src/tts_server.py'], 
                      capture_output=True, timeout=5)
        time.sleep(2)
    except:
        pass
    
    # Start new server
    try:
        subprocess.Popen(['python', 'src/tts_server.py'], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Server restarted in background")
        return True
    except Exception as e:
        print(f"❌ Failed to restart server: {e}")
        return False

def main():
    """Main function"""
    print("🎛️  Coqui TTS Configuration Switcher")
    print("=" * 50)
    
    # Check current status
    print("\n📊 Current Status:")
    used, total, usage_percent = check_gpu_usage()
    ollama_running = check_ollama_running()
    
    print(f"🤖 Ollama running: {'✅ Yes' if ollama_running else '❌ No'}")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        # Auto-detect mode based on Ollama status
        if ollama_running:
            mode = "coexistence"
            print("🤖 Ollama detected - recommending COEXISTENCE mode")
        else:
            mode = "speed"
            print("🚀 No Ollama detected - recommending SPEED mode")
        
        # Ask for confirmation
        response = input(f"\nSwitch to {mode.upper()} mode? (y/n): ").lower()
        if response not in ['y', 'yes']:
            print("❌ Operation cancelled")
            return
    
    # Switch configuration
    if switch_config(mode):
        # Show configuration details
        if mode == "coexistence":
            print("\n📋 Coexistence Mode Settings:")
            print("   • GPU Memory: 30% (3.7GB)")
            print("   • Batch Size: 1")
            print("   • Audio Quality: Low")
            print("   • Whisper Model: Tiny")
            print("   • Workers: 1")
        else:
            print("\n📋 Speed Mode Settings:")
            print("   • GPU Memory: 85% (10.4GB)")
            print("   • Batch Size: 4")
            print("   • Audio Quality: Medium")
            print("   • Whisper Model: Tiny")
            print("   • Workers: 2")
        
        # Ask if user wants to restart server
        restart = input("\nRestart server with new configuration? (y/n): ").lower()
        if restart in ['y', 'yes']:
            restart_server()
        else:
            print("ℹ️  Server not restarted. Restart manually to apply changes.")
    
    print("\n✅ Configuration switch completed!")

if __name__ == "__main__":
    main() 