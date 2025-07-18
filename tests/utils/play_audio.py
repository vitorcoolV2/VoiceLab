#!/usr/bin/env python3
"""
Simple command-line tool to play audio files.
Usage: python play_audio.py <file> [options]
"""

import sys
import argparse
from pathlib import Path
from tools.audio_player import AudioPlayer, play_single_file, play_multiple_files, play_directory_files

def main():
    parser = argparse.ArgumentParser(
        description="Play audio files with various players",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python play_audio.py sample.wav
  python play_audio.py sample.wav --player mpv
  python play_audio.py *.wav --player vlc
  python play_audio.py downloads/ --pattern "*_cleaned_full.wav"
  python play_audio.py file1.wav file2.wav file3.wav
        """
    )
    
    parser.add_argument("files", nargs="+", help="Audio file(s) or directory to play")
    parser.add_argument("--player", default="auto", 
                       choices=["auto", "playsound"],
                       help="Audio player to use (default: auto-detect)")
    parser.add_argument("--volume", type=int, default=100, 
                       help="Volume level (0-100, default: 100)")
    parser.add_argument("--interface", default="dummy",
                       help="Interface for GUI players (default: dummy)")
    parser.add_argument("--no-wait", action="store_true",
                       help="Don't wait for playback to complete")
    parser.add_argument("--pattern", default="*.wav",
                       help="File pattern when playing directory (default: *.wav)")
    parser.add_argument("--recursive", action="store_true",
                       help="Search subdirectories recursively")
    parser.add_argument("--sort-by", default="name",
                       choices=["name", "modified", "size"],
                       help="Sort files by (default: name)")
    parser.add_argument("--pause", type=float, default=1.0,
                       help="Pause between files in seconds (default: 1.0)")
    parser.add_argument("--list", action="store_true",
                       help="List files that would be played without playing them")
    
    args = parser.parse_args()
    
    # Initialize audio player
    player = AudioPlayer(
        player=args.player,
        volume=args.volume,
        interface=args.interface,
        wait_for_completion=not args.no_wait
    )
    
    # Handle single file
    if len(args.files) == 1:
        file_path = Path(args.files[0])
        
        if file_path.is_file():
            # Single file
            if args.list:
                print(f"📁 Would play: {file_path}")
                return
            
            success = player.play_file(str(file_path), f"Playing: {file_path.name}")
            if not success:
                sys.exit(1)
                
        elif file_path.is_dir():
            # Directory
            if args.list:
                print(f"📁 Would play files in directory: {file_path}")
                print(f"   Pattern: {args.pattern}")
                print(f"   Recursive: {args.recursive}")
                print(f"   Sort by: {args.sort_by}")
                return
            
            results = player.play_directory(
                str(file_path),
                pattern=args.pattern,
                recursive=args.recursive,
                sort_by=args.sort_by
            )
            
            if not results:
                print("❌ No files found to play")
                sys.exit(1)
                
        else:
            print(f"❌ File or directory not found: {file_path}")
            sys.exit(1)
    
    else:
        # Multiple files
        if args.list:
            print("📁 Would play files:")
            for file_path in args.files:
                print(f"   {file_path}")
            return
        
        # Check if all files exist
        existing_files = []
        for file_path in args.files:
            path = Path(file_path)
            if path.exists():
                existing_files.append(str(path))
            else:
                print(f"⚠️  File not found: {file_path}")
        
        if not existing_files:
            print("❌ No valid files found")
            sys.exit(1)
        
        # Play multiple files
        labels = [f"File {i+1}: {Path(f).name}" for i, f in enumerate(existing_files)]
        results = player.play_files(existing_files, labels=labels, pause_between=args.pause)
        
        # Check results
        failed_files = [f for f, success in results.items() if not success]
        if failed_files:
            print(f"❌ Failed to play {len(failed_files)} files")
            sys.exit(1)

if __name__ == "__main__":
    main() 