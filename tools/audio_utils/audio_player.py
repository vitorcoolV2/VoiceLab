#!/usr/bin/env python3
"""
Enhanced Audio Player with uniform target output support.
Supports multiple audio players, devices, and output formats.
"""

import os
import subprocess
import time
import glob
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json
import platform

class AudioPlayer:
    """Enhanced audio player with uniform target output support."""
    
    def __init__(self, player: str = "auto", volume: int = 100, 
                 interface: str = "dummy", wait_for_completion: bool = True,
                 output_device: str = None, output_format: str = "wav",
                 target_app: str = None, audio_quality: str = "high"):
        """
        Initialize the enhanced audio player.
        
        Args:
            player: Audio player to use ('vlc', 'mpv', 'ffplay', 'auto')
            volume: Volume level (0-100)
            interface: Interface type for GUI players ('dummy', 'qt', 'gtk')
            wait_for_completion: Whether to wait for playback to complete
            output_device: Specific audio device to use
            output_format: Output format ('wav', 'mp3', 'flac', 'ogg')
            target_app: Target application for output ('browser', 'desktop', 'mobile', 'streaming')
            audio_quality: Audio quality ('low', 'medium', 'high', 'ultra')
        """
        self.player = player
        self.volume = volume
        self.interface = interface
        self.wait_for_completion = wait_for_completion
        self.output_device = output_device
        self.output_format = output_format
        self.target_app = target_app
        self.audio_quality = audio_quality
        
        # Supported formats and quality settings
        self.supported_formats = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac', '.wma'}
        self.quality_settings = {
            'low': {'bitrate': '64k', 'sample_rate': '22050'},
            'medium': {'bitrate': '128k', 'sample_rate': '44100'},
            'high': {'bitrate': '256k', 'sample_rate': '48000'},
            'ultra': {'bitrate': '320k', 'sample_rate': '96000'}
        }
        
        # Target app configurations
        self.target_configs = {
            'browser': {
                'format': 'mp3',
                'quality': 'medium',
                'compatibility': 'web'
            },
            'desktop': {
                'format': 'wav',
                'quality': 'high',
                'compatibility': 'native'
            },
            'mobile': {
                'format': 'm4a',
                'quality': 'medium',
                'compatibility': 'mobile'
            },
            'streaming': {
                'format': 'ogg',
                'quality': 'low',
                'compatibility': 'streaming'
            }
        }
        
        # Auto-detect best available player
        if player == "auto":
            self.player = self._detect_best_player()
            
        # Apply target app settings if specified
        if target_app and target_app in self.target_configs:
            config = self.target_configs[target_app]
            self.output_format = config['format']
            self.audio_quality = config['quality']
    
    def _detect_best_player(self) -> str:
        """Detect the best available audio player."""
        players = [
            ('vlc', ['vlc', '--version']),
            ('mpv', ['mpv', '--version']),
            ('ffplay', ['ffplay', '-version']),
            ('aplay', ['aplay', '--version']),
            ('paplay', ['paplay', '--version'])
        ]
        
        for player_name, test_cmd in players:
            try:
                subprocess.run(test_cmd, capture_output=True, check=True)
                return player_name
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return "vlc"  # Default fallback
    
    def _get_audio_device_args(self) -> List[str]:
        """Get audio device arguments based on platform and player."""
        if not self.output_device:
            return []
            
        if self.player == "vlc":
            return ['--aout', self.output_device]
        elif self.player == "mpv":
            return ['--audio-device', self.output_device]
        elif self.player == "ffplay":
            return ['-af', f'volume={self.volume/100}']
        else:
            return []
    
    def _get_quality_args(self) -> List[str]:
        """Get quality arguments based on audio quality setting."""
        quality = self.quality_settings.get(self.audio_quality, self.quality_settings['high'])
        
        if self.player == "vlc":
            return [
                '--audio-resampler', 'soxr',
                '--audio-channels', '2',
                '--audio-sample-rate', quality['sample_rate']
            ]
        elif self.player == "mpv":
            return [
                '--audio-samplerate', quality['sample_rate'],
                '--audio-channels', '2'
            ]
        elif self.player == "ffplay":
            return [
                '-ar', quality['sample_rate'],
                '-ac', '2'
            ]
        else:
            return []
    
    def _get_player_command(self, audio_file: str, start_time: float = 0, duration: float = None) -> List[str]:
        """Get the command to play an audio file with the selected player."""
        base_cmd = []
        
        if self.player == "vlc":
            base_cmd = [
                'vlc', '--play-and-exit', '--intf', self.interface,
                '--no-video', '--volume', str(self.volume)
            ]
            base_cmd.extend(self._get_audio_device_args())
            base_cmd.extend(self._get_quality_args())
            
            if start_time > 0:
                base_cmd.extend(['--start-time', str(start_time)])
            if duration:
                base_cmd.extend(['--stop-time', str(start_time + duration)])
            base_cmd.append(audio_file)
            
        elif self.player == "mpv":
            base_cmd = [
                'mpv', '--no-video', '--volume', str(self.volume),
                '--really-quiet'
            ]
            base_cmd.extend(self._get_audio_device_args())
            base_cmd.extend(self._get_quality_args())
            
            if start_time > 0:
                base_cmd.extend(['--start', str(start_time)])
            if duration:
                base_cmd.extend(['--length', str(duration)])
            base_cmd.append(audio_file)
            
        elif self.player == "ffplay":
            base_cmd = [
                'ffplay', '-nodisp', '-autoexit', '-volume', str(self.volume),
                '-loglevel', 'error'
            ]
            base_cmd.extend(self._get_quality_args())
            
            if start_time > 0:
                base_cmd.extend(['-ss', str(start_time)])
            if duration:
                base_cmd.extend(['-t', str(duration)])
            base_cmd.append(audio_file)
            
        elif self.player == "aplay":
            # aplay doesn't support start/duration easily, so we'll use sox if available
            try:
                subprocess.run(['sox', '--version'], capture_output=True, check=True)
                base_cmd = ['sox', audio_file, '-t', self.output_format, '-']
                base_cmd.extend(self._get_quality_args())
                
                if start_time > 0:
                    base_cmd.extend(['trim', str(start_time)])
                if duration:
                    base_cmd.extend(['trim', '0', str(duration)])
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to aplay without start/duration
                base_cmd = ['aplay', audio_file]
                
        elif self.player == "paplay":
            # paplay doesn't support start/duration, fallback to sox
            try:
                subprocess.run(['sox', '--version'], capture_output=True, check=True)
                base_cmd = ['sox', audio_file, '-t', self.output_format, '-']
                base_cmd.extend(self._get_quality_args())
                
                if start_time > 0:
                    base_cmd.extend(['trim', str(start_time)])
                if duration:
                    base_cmd.extend(['trim', '0', str(duration)])
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to paplay without start/duration
                base_cmd = ['paplay', audio_file]
        else:
            raise ValueError(f"Unsupported player: {self.player}")
            
        return base_cmd
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system audio information."""
        info = {
            'platform': platform.system(),
            'player': self.player,
            'output_device': self.output_device,
            'output_format': self.output_format,
            'target_app': self.target_app,
            'audio_quality': self.audio_quality,
            'volume': self.volume
        }
        
        # Try to get available audio devices
        try:
            if self.player == "vlc":
                result = subprocess.run(['vlc', '--list'], capture_output=True, text=True)
                info['available_devices'] = result.stdout.split('\n')[:10]  # First 10 lines
            elif self.player == "mpv":
                result = subprocess.run(['mpv', '--audio-device=help'], capture_output=True, text=True)
                info['available_devices'] = result.stdout.split('\n')[:10]
        except:
            info['available_devices'] = ['Could not detect devices']
            
        return info
    
    def play_file(self, audio_file: str, label: str = "", 
                  show_info: bool = True, start_time: float = 0, 
                  duration: float = None, target_app: str = None) -> bool:
        """
        Play a single audio file with target app support.
        
        Args:
            audio_file: Path to the audio file
            label: Display label for the file
            show_info: Whether to show file information
            start_time: Start time in seconds (0 = beginning)
            duration: Duration to play in seconds (None = play until end)
            target_app: Override target app for this playback
            
        Returns:
            True if playback was successful, False otherwise
        """
        if not os.path.exists(audio_file):
            print(f"❌ File not found: {audio_file}")
            return False
        
        # Apply target app settings if specified
        original_target = self.target_app
        if target_app and target_app in self.target_configs:
            self.target_app = target_app
            config = self.target_configs[target_app]
            self.output_format = config['format']
            self.audio_quality = config['quality']
        
        if show_info:
            self._show_file_info(audio_file, label, start_time, duration)
        
        try:
            cmd = self._get_player_command(audio_file, start_time, duration)
            
            # Handle sox pipeline for players that don't support start/duration
            if self.player in ["aplay", "paplay"] and (start_time > 0 or duration):
                try:
                    subprocess.run(['sox', '--version'], capture_output=True, check=True)
                    # Use sox to process audio and pipe to player
                    sox_cmd = cmd
                    player_cmd = [self.player, '-'] if self.player == "aplay" else [self.player, '-']
                    
                    # Create pipeline: sox | player
                    sox_process = subprocess.Popen(sox_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    player_process = subprocess.Popen(player_cmd, stdin=sox_process.stdout, stderr=subprocess.PIPE)
                    sox_process.stdout.close()
                    
                    if self.wait_for_completion:
                        player_process.wait()
                        sox_process.wait()
                    else:
                        time.sleep(0.5)
                    
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Fallback to original player without start/duration
                    print(f"⚠️  sox not available, playing full file with {self.player}")
                    cmd = self._get_player_command(audio_file)
            
            process = subprocess.Popen(cmd)
            
            if self.wait_for_completion:
                process.wait()
            else:
                # Give a small delay to ensure playback starts
                time.sleep(0.5)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error playing {audio_file}: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {self.player} not found. Please install {self.player}.")
            return False
        finally:
            # Restore original target app settings
            if target_app:
                self.target_app = original_target
                if original_target and original_target in self.target_configs:
                    config = self.target_configs[original_target]
                    self.output_format = config['format']
                    self.audio_quality = config['quality']
    
    def play_files(self, audio_files: List[str], labels: Optional[List[str]] = None,
                   pause_between: float = 1.0, show_info: bool = True,
                   target_app: str = None) -> Dict[str, bool]:
        """
        Play multiple audio files in sequence with target app support.
        
        Args:
            audio_files: List of audio file paths
            labels: Optional list of labels for each file
            pause_between: Pause duration between files
            show_info: Whether to show file information
            target_app: Target app for all files
            
        Returns:
            Dictionary mapping file paths to success status
        """
        if labels is None:
            labels = [os.path.basename(f) for f in audio_files]
        
        results = {}
        
        for i, (audio_file, label) in enumerate(zip(audio_files, labels), 1):
            print(f"\n🎵 Playing file {i}/{len(audio_files)}")
            success = self.play_file(audio_file, label, show_info, target_app=target_app)
            results[audio_file] = success
            
            if i < len(audio_files) and pause_between > 0:
                time.sleep(pause_between)
        
        return results
    
    def play_directory(self, directory: str, pattern: str = "*.wav",
                       recursive: bool = False, sort_by: str = "name",
                       show_info: bool = True, target_app: str = None) -> Dict[str, bool]:
        """
        Play all audio files in a directory matching a pattern with target app support.
        
        Args:
            directory: Directory to search for audio files
            pattern: File pattern to match (e.g., "*.wav", "*_cleaned_full.wav")
            recursive: Whether to search subdirectories
            sort_by: Sort method ('name', 'modified', 'size')
            show_info: Whether to show file information
            target_app: Target app for all files
            
        Returns:
            Dictionary mapping file paths to success status
        """
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return {}
        
        # Find matching files
        if recursive:
            search_pattern = os.path.join(directory, "**", pattern)
            audio_files = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(directory, pattern)
            audio_files = glob.glob(search_pattern, recursive=False)
        
        # Filter by supported formats
        audio_files = [f for f in audio_files 
                      if Path(f).suffix.lower() in self.supported_formats]
        
        if not audio_files:
            print(f"❌ No audio files found in {directory} matching pattern: {pattern}")
            return {}
        
        # Sort files
        if sort_by == "name":
            audio_files.sort()
        elif sort_by == "modified":
            audio_files.sort(key=lambda x: os.path.getmtime(x))
        elif sort_by == "size":
            audio_files.sort(key=lambda x: os.path.getsize(x))
        
        print(f"📁 Found {len(audio_files)} audio files in {directory}")
        
        return self.play_files(audio_files, show_info=show_info, target_app=target_app)
    
    def _show_file_info(self, audio_file: str, label: str = "", start_time: float = 0, duration: float = None):
        """Display information about an audio file."""
        try:
            size = os.path.getsize(audio_file)
            modified = time.ctime(os.path.getmtime(audio_file))
            
            if label:
                print(f"🎵 Playing: {label}")
            print(f"📁 File: {audio_file}")
            print(f"📊 Size: {size / 1024:.1f} KB")
            print(f"📅 Modified: {modified}")
            
            # Show target app info
            if self.target_app:
                config = self.target_configs.get(self.target_app, {})
                print(f"🎯 Target: {self.target_app} ({config.get('compatibility', 'unknown')})")
                print(f"🎵 Format: {self.output_format}, Quality: {self.audio_quality}")
            
            if start_time > 0 or duration:
                duration_str = f"{duration:.1f}s" if duration else "until end"
                print(f"⏱️  Playback: {start_time:.1f}s → {duration_str}")
            
        except OSError as e:
            print(f"⚠️  Could not get file info: {e}")
    
    def get_supported_players(self) -> List[str]:
        """Get list of supported audio players."""
        return ["vlc", "mpv", "ffplay", "aplay", "paplay"]
    
    def get_supported_formats(self) -> set:
        """Get set of supported audio formats."""
        return self.supported_formats.copy()
    
    def get_target_apps(self) -> List[str]:
        """Get list of supported target applications."""
        return list(self.target_configs.keys())
    
    def get_audio_qualities(self) -> List[str]:
        """Get list of supported audio qualities."""
        return list(self.quality_settings.keys())

# Convenience functions for common use cases
def play_single_file(audio_file: str, player: str = "auto", target_app: str = None, **kwargs) -> bool:
    """Play a single audio file with target app support."""
    player_instance = AudioPlayer(player=player, target_app=target_app, **kwargs)
    return player_instance.play_file(audio_file, target_app=target_app)

def play_multiple_files(audio_files: List[str], player: str = "auto", target_app: str = None, **kwargs) -> Dict[str, bool]:
    """Play multiple audio files with target app support."""
    player_instance = AudioPlayer(player=player, target_app=target_app, **kwargs)
    return player_instance.play_files(audio_files, target_app=target_app)

def play_directory_files(directory: str, pattern: str = "*.wav", 
                        player: str = "auto", target_app: str = None, **kwargs) -> Dict[str, bool]:
    """Play all audio files in a directory with target app support."""
    player_instance = AudioPlayer(player=player, target_app=target_app, **kwargs)
    return player_instance.play_directory(directory, pattern, target_app=target_app)

def play_wav_python(audio_file: str, volume: int = 100):
    """
    Play a .wav file using pure Python (playsound). Volume control is not supported.
    """
    try:
        from playsound import playsound
        print(f"🔊 Playing (Python): {audio_file}")
        playsound(audio_file)
        return True
    except Exception as e:
        print(f"❌ Error playing audio with Python: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_player.py <audio_file> [player] [target_app]")
        print("Example: python audio_player.py sample.wav vlc browser")
        print("Target apps: browser, desktop, mobile, streaming")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    player = sys.argv[2] if len(sys.argv) > 2 else "auto"
    target_app = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = play_single_file(audio_file, player=player, target_app=target_app)
    if success:
        print("✅ Playback completed successfully")
    else:
        print("❌ Playback failed")
        sys.exit(1) 