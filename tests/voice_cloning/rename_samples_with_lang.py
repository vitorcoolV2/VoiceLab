#!/usr/bin/env python3
"""
Rename Sample Files with Language
Adds language suffix to sample files for better organization
"""

import os
import re
from pathlib import Path
import shutil

def detect_language_from_filename(filename):
    """Detect language from filename or content"""
    filename_lower = filename.lower()
    
    # Portuguese indicators
    if any(word in filename_lower for word in ['portugal', 'português', 'joana', 'anjos', 'justiça']):
        return 'pt'
    
    # English indicators
    if any(word in filename_lower for word in ['deeper', 'voice', 'shorts', 'deepvoice']):
        return 'en'
    
    # Default to English if uncertain
    return 'en'

def rename_samples_with_language():
    """Rename sample files to include language suffix"""
    
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        print("❌ Downloads directory not found")
        return
    
    print("🏷️ Renaming samples with language suffixes...")
    print("=" * 50)
    
    # Get all WAV files
    wav_files = list(downloads_dir.glob("*.wav"))
    
    if not wav_files:
        print("❌ No WAV files found")
        return
    
    renamed_count = 0
    
    for wav_file in wav_files:
        filename = wav_file.stem
        extension = wav_file.suffix
        
        # Skip if already has language suffix
        if re.search(r'_(en|pt|pt-br|pt-pt)$', filename):
            print(f"⏭️  Skipping (already has language): {filename}{extension}")
            continue
        
        # Detect language
        language = detect_language_from_filename(filename)
        
        # Create new filename
        new_filename = f"{filename}_{language}{extension}"
        new_path = wav_file.parent / new_filename
        
        # Check if target file already exists
        if new_path.exists():
            print(f"⚠️  Target exists, skipping: {new_filename}")
            continue
        
        try:
            # Rename file
            shutil.move(str(wav_file), str(new_path))
            print(f"✅ Renamed: {filename}{extension} → {new_filename}")
            renamed_count += 1
            
        except Exception as e:
            print(f"❌ Error renaming {filename}: {e}")
    
    print("=" * 50)
    print(f"🎯 Renamed {renamed_count} files")
    
    # Show new structure
    print("\n📁 New file structure:")
    for wav_file in sorted(downloads_dir.glob("*.wav")):
        size_mb = wav_file.stat().st_size / (1024 * 1024)
        print(f"   {wav_file.name} ({size_mb:.1f} MB)")

def create_language_mapping():
    """Create a mapping file for language detection"""
    
    mapping = {
        'en': [
            'How to get a deeper voice in 30 seconds! #shorts #deepvoice',
            'deeper voice',
            'shorts',
            'deepvoice'
        ],
        'pt': [
            'Joana Marques vs Anjos',
            'Justiça Cega',
            'português',
            'portugal'
        ]
    }
    
    mapping_file = Path("language_mapping.json")
    import json
    
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✅ Language mapping saved: {mapping_file}")

if __name__ == "__main__":
    print("🏷️ Sample Language Renaming Tool")
    print("=" * 40)
    
    # Create language mapping
    create_language_mapping()
    
    # Rename files
    rename_samples_with_language()
    
    print("\n💡 Next steps:")
    print("   1. Update QA tools to detect language from filename")
    print("   2. Update voice cloning scripts to use language suffix")
    print("   3. Test with new naming convention") 