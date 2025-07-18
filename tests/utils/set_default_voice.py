#!/usr/bin/env python3
"""
Set Default Voice Sample for Coqui TTS
Configures the TTS server to use a specific voice sample as default
"""

import os
import sys
import yaml
import argparse
from pathlib import Path

def set_default_voice_sample(sample_path: str, enable: bool = True):
    """
    Set a voice sample as default for the TTS server
    
    Args:
        sample_path: Path to the voice sample file
        enable: Whether to enable using the default voice sample
    """
    
    # Load current configuration
    config_path = Path("config/settings.yaml")
    
    if not config_path.exists():
        print("❌ Configuration file not found: config/settings.yaml")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate sample file
    sample_file = Path(sample_path)
    if not sample_file.exists():
        print(f"❌ Voice sample file not found: {sample_path}")
        return False
    
    if not sample_file.suffix.lower() in ['.wav', '.mp3', '.flac', '.m4a']:
        print(f"❌ Unsupported audio format: {sample_file.suffix}")
        return False
    
    # Update configuration
    config['tts']['default_voice_sample'] = str(sample_file.absolute())
    config['tts']['use_default_voice_sample'] = enable
    
    # Save updated configuration
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"✅ Default voice sample configured:")
    print(f"   📁 Sample: {sample_file.absolute()}")
    print(f"   🔧 Enabled: {enable}")
    
    if enable:
        print("\n🔄 Restart the TTS server for changes to take effect:")
        print("   python src/tts_server.py")
    
    return True

def remove_default_voice_sample():
    """Remove the default voice sample configuration"""
    
    config_path = Path("config/settings.yaml")
    
    if not config_path.exists():
        print("❌ Configuration file not found: config/settings.yaml")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Reset configuration
    config['tts']['default_voice_sample'] = None
    config['tts']['use_default_voice_sample'] = False
    
    # Save updated configuration
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print("✅ Default voice sample removed")
    print("\n🔄 Restart the TTS server for changes to take effect:")
    print("   python src/tts_server.py")
    
    return True

def show_current_config():
    """Show current default voice sample configuration"""
    
    config_path = Path("config/settings.yaml")
    
    if not config_path.exists():
        print("❌ Configuration file not found: config/settings.yaml")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("📋 Current Default Voice Sample Configuration:")
    print(f"   📁 Sample: {config['tts'].get('default_voice_sample', 'None')}")
    print(f"   🔧 Enabled: {config['tts'].get('use_default_voice_sample', False)}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Set default voice sample for Coqui TTS")
    parser.add_argument("--sample", "-s", help="Path to voice sample file")
    parser.add_argument("--enable", "-e", action="store_true", help="Enable default voice sample")
    parser.add_argument("--disable", "-d", action="store_true", help="Disable default voice sample")
    parser.add_argument("--remove", "-r", action="store_true", help="Remove default voice sample")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    
    args = parser.parse_args()
    
    if args.show:
        show_current_config()
    elif args.remove:
        remove_default_voice_sample()
    elif args.sample:
        set_default_voice_sample(args.sample, args.enable)
    elif args.disable:
        set_default_voice_sample("", False)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 