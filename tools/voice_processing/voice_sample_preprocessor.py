#!/usr/bin/env python3
"""
Voice Sample Preprocessor
Critical component for high-quality voice cloning:
1. Removes music and background noise from YouTube audio
2. Extracts clean voice-only segments
3. Analyzes voice specifications (pitch, rate, quality)
4. Validates samples before TTS upload
5. Generates voice metadata for optimal cloning
"""

import os
import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VoiceSpecifications:
    """Voice characteristics and specifications"""
    pitch_range: Tuple[float, float]  # (min_pitch, max_pitch) in Hz
    speaking_rate: float  # words per minute
    energy_level: str  # low, medium, high
    language: str  # en, pt-br, etc.
    accent: str  # British, American, etc.
    duration: float  # sample duration in seconds
    quality_score: float  # 0.0 to 1.0
    voice_type: str  # male, female, child
    clarity_score: float  # 0.0 to 1.0
    noise_level: float  # 0.0 to 1.0 (lower is better)

class VoiceSamplePreprocessor:
    def __init__(self, output_dir: str = None):
        """Initialize the voice sample preprocessor."""
        self.output_dir = Path(output_dir) if output_dir else Path(os.environ.get("COQUI_TTS_OUTPUTS", "output"))
        self.output_dir.mkdir(exist_ok=True)
        
    def remove_music_and_noise(self, audio_path: str) -> Optional[str]:
        """
        Remove music and background noise from audio using spectral subtraction
        """
        try:
            logger.info(f"Removing music and noise from: {audio_path}")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            
            # Convert to mono if stereo
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
            
            # Simple noise reduction using spectral gating
            # Calculate noise profile from first 1 second
            noise_duration = min(1.0, len(y) / sr / 4)  # Use 1 second or 1/4 of audio
            noise_samples = int(noise_duration * sr)
            noise_profile = y[:noise_samples]
            
            # Calculate noise spectrum
            noise_spectrum = np.abs(np.fft.fft(noise_profile))
            # Pad or truncate to match full audio length
            full_length = len(y)
            if len(noise_spectrum) < full_length:
                # Pad with zeros
                padded_noise = np.zeros(full_length)
                padded_noise[:len(noise_spectrum)] = noise_spectrum
                noise_spectrum = padded_noise
            else:
                # Truncate
                noise_spectrum = noise_spectrum[:full_length]
            
            # Apply spectral subtraction
            y_fft = np.fft.fft(y)
            y_spectrum = np.abs(y_fft)
            
            # Subtract noise spectrum with scaling factor
            alpha = 1.5  # Noise reduction strength
            cleaned_spectrum = y_spectrum - alpha * noise_spectrum
            cleaned_spectrum = np.maximum(cleaned_spectrum, 0.1 * y_spectrum)
            
            # Reconstruct signal
            cleaned_fft = y_fft * (cleaned_spectrum / y_spectrum)
            cleaned_audio = np.real(np.fft.ifft(cleaned_fft))
            
            # Save cleaned audio
            output_path = audio_path.replace('.wav', '_cleaned.wav')
            sf.write(output_path, cleaned_audio, sr)
            
            logger.info(f"Music/noise removal completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error removing music/noise: {e}")
            # Fallback: return original audio if cleaning fails
            logger.info("Using original audio as fallback")
            return audio_path
    
    def extract_voice_segments(self, audio_path: str, min_duration: float = 60.0) -> List[str]:
        """
        Extract voice-only segments using voice activity detection
        """
        try:
            logger.info(f"Extracting voice segments from: {audio_path}")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            
            # Voice Activity Detection using energy and spectral centroid
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)    # 10ms hop
            
            # Calculate energy
            energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Calculate spectral centroid (voice has higher centroid than music)
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
            
            # Normalize features
            energy_norm = (energy - np.mean(energy)) / np.std(energy)
            centroid_norm = (centroid - np.mean(centroid)) / np.std(centroid)
            
            # Voice activity threshold
            voice_threshold = 0.5
            voice_activity = (energy_norm + centroid_norm) / 2 > voice_threshold
            
            # Find voice segments
            segments = []
            start_frame = None
            
            for i, is_voice in enumerate(voice_activity):
                if is_voice and start_frame is None:
                    start_frame = i
                elif not is_voice and start_frame is not None:
                    end_frame = i
                    duration = (end_frame - start_frame) * hop_length / sr
                    
                    if duration >= min_duration:
                        start_sample = int(start_frame * hop_length)
                        end_sample = int(end_frame * hop_length)
                        segment = y[start_sample:end_sample]
                        
                        # Save segment
                        segment_path = f"{audio_path.replace('.wav', '')}_segment_{len(segments)}.wav"
                        sf.write(segment_path, segment, sr)
                        segments.append(segment_path)
                        
                        logger.info(f"Voice segment {len(segments)}: {duration:.1f}s")
                    
                    start_frame = None
            
            logger.info(f"Extracted {len(segments)} voice segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error extracting voice segments: {e}")
            return []
    
    def analyze_voice_specifications(self, audio_path: str) -> VoiceSpecifications:
        """
        Analyze voice characteristics and generate specifications
        """
        try:
            logger.info(f"Analyzing voice specifications: {audio_path}")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            # Pitch analysis
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[magnitudes > np.median(magnitudes)]
            
            if len(pitch_values) > 0:
                min_pitch = float(np.percentile(pitch_values, 10))
                max_pitch = float(np.percentile(pitch_values, 90))
                median_pitch = float(np.median(pitch_values))
            else:
                min_pitch = max_pitch = median_pitch = 0.0
            
            # Speaking rate (syllable rate estimation)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            speaking_rate = float(tempo[0]) if len(tempo) > 0 else 120.0
            
            # Energy level
            energy = float(np.mean(librosa.feature.rms(y=y)))
            if energy < 0.05:
                energy_level = "low"
            elif energy < 0.15:
                energy_level = "medium"
            else:
                energy_level = "high"
            
            # Voice type classification
            if median_pitch < 150:
                voice_type = "male"
            elif median_pitch < 250:
                voice_type = "female"
            else:
                voice_type = "child"
            
            # Clarity score (spectral contrast)
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            clarity_score = float(np.mean(contrast))
            
            # Noise level (spectral flatness - lower is less noisy)
            flatness = librosa.feature.spectral_flatness(y=y)
            noise_level = float(np.mean(flatness))
            
            # Overall quality score
            quality_score = (clarity_score * 0.4 + (1 - noise_level) * 0.3 + 
                           (1 - abs(speaking_rate - 150) / 150) * 0.3)
            quality_score = max(0.0, min(1.0, quality_score))
            
            # Language detection (simplified)
            language = "en"  # Default, could be enhanced with language detection
            
            # Accent detection (simplified)
            accent = "unknown"  # Could be enhanced with accent detection
            
            specs = VoiceSpecifications(
                pitch_range=(min_pitch, max_pitch),
                speaking_rate=speaking_rate,
                energy_level=energy_level,
                language=language,
                accent=accent,
                duration=duration,
                quality_score=quality_score,
                voice_type=voice_type,
                clarity_score=clarity_score,
                noise_level=noise_level
            )
            
            logger.info(f"Voice analysis completed - Quality: {quality_score:.3f}")
            return specs
            
        except Exception as e:
            logger.error(f"Error analyzing voice specifications: {e}")
            return VoiceSpecifications(
                pitch_range=(0, 0), speaking_rate=0, energy_level="unknown",
                language="unknown", accent="unknown", duration=0,
                quality_score=0, voice_type="unknown", clarity_score=0, noise_level=1
            )
    
    def validate_sample_quality(self, specs: VoiceSpecifications, min_quality: float = 0.6) -> bool:
        """
        Validate if the voice sample meets quality requirements
        """
        quality_checks = []
        
        # Quality score check
        quality_checks.append(specs.quality_score >= min_quality)
        
        # Duration check (minimum 30 seconds)
        quality_checks.append(specs.duration >= 30.0)
        
        # Clarity check
        quality_checks.append(specs.clarity_score > 0.3)
        
        # Noise check
        quality_checks.append(specs.noise_level < 0.7)
        
        # Pitch range check (must have some pitch variation)
        pitch_range = specs.pitch_range[1] - specs.pitch_range[0]
        quality_checks.append(pitch_range > 50.0)
        
        is_valid = all(quality_checks)
        
        logger.info(f"Quality validation: {'PASS' if is_valid else 'FAIL'}")
        logger.info(f"  Quality score: {specs.quality_score:.3f} (min: {min_quality})")
        logger.info(f"  Duration: {specs.duration:.1f}s (min: 30s)")
        logger.info(f"  Clarity: {specs.clarity_score:.3f} (min: 0.3)")
        logger.info(f"  Noise: {specs.noise_level:.3f} (max: 0.7)")
        logger.info(f"  Pitch range: {pitch_range:.1f}Hz (min: 50Hz)")
        
        return is_valid
    
    def process_youtube_audio(self, youtube_audio_path: str, min_quality: float = 0.6) -> Optional[Dict]:
        """
        Complete pipeline: clean audio → extract voice → analyze → validate
        """
        try:
            logger.info(f"Processing YouTube audio: {youtube_audio_path}")
            
            # Step 1: Remove music and noise
            cleaned_audio = self.remove_music_and_noise(youtube_audio_path)
            if not cleaned_audio:
                logger.error("Failed to clean audio")
                return None
            
            # Step 2: Extract voice segments
            voice_segments = self.extract_voice_segments(cleaned_audio, min_duration=60.0)
            if not voice_segments:
                logger.error("No voice segments found")
                return None
            
            # Step 3: Analyze each segment and find the best one
            best_segment = None
            best_specs = None
            best_quality = 0.0
            
            for segment_path in voice_segments:
                specs = self.analyze_voice_specifications(segment_path)
                
                if specs.quality_score > best_quality:
                    best_quality = specs.quality_score
                    best_segment = segment_path
                    best_specs = specs
            
            # Step 4: Validate the best segment
            if not best_segment or not self.validate_sample_quality(best_specs, min_quality):
                logger.error("No high-quality voice segments found")
                return None
            
            # Step 5: Generate metadata
            metadata = {
                'original_file': youtube_audio_path,
                'processed_file': best_segment,
                'specifications': {
                    'pitch_range': best_specs.pitch_range,
                    'speaking_rate': best_specs.speaking_rate,
                    'energy_level': best_specs.energy_level,
                    'language': best_specs.language,
                    'accent': best_specs.accent,
                    'duration': best_specs.duration,
                    'quality_score': best_specs.quality_score,
                    'voice_type': best_specs.voice_type,
                    'clarity_score': best_specs.clarity_score,
                    'noise_level': best_specs.noise_level
                },
                'processing_info': {
                    'cleaned_audio': cleaned_audio,
                    'total_segments': len(voice_segments),
                    'selected_segment': best_segment,
                    'validation_passed': True
                }
            }
            
            # Save metadata
            metadata_path = best_segment.replace('.wav', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Processing completed successfully!")
            logger.info(f"   Best segment: {best_segment}")
            logger.info(f"   Quality score: {best_specs.quality_score:.3f}")
            logger.info(f"   Duration: {best_specs.duration:.1f}s")
            logger.info(f"   Voice type: {best_specs.voice_type}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing YouTube audio: {e}")
            return None

def main():
    """Main function to run the preprocessor."""
    import argparse
    parser = argparse.ArgumentParser(description="Voice Sample Preprocessor")
    parser.add_argument("--input", required=True, help="Input audio file or directory")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--quality", choices=["low", "medium", "high"], default="medium", help="Audio quality")
    parser.add_argument("--normalize", action="store_true", help="Normalize audio")
    parser.add_argument("--trim", action="store_true", help="Trim silence")
    
    args = parser.parse_args()
    
    # Use environment variable for output directory if not specified
    output_dir = args.output or os.environ.get("COQUI_TTS_OUTPUTS", "output")
    output_dir = Path(output_dir)
    
    preprocessor = VoiceSamplePreprocessor(output_dir=output_dir)
    
    # Test with existing YouTube samples
    input_path = args.input
    if input_path.endswith(".wav"):
        print(f"\n🔍 Processing single file: {input_path}")
        result = preprocessor.process_youtube_audio(str(input_path), min_quality=0.5)
    else:
        print(f"\n🔍 Processing directory: {input_path}")
        youtube_samples = list(Path(input_path).glob("*.wav"))
        
        if not youtube_samples:
            print("❌ No .wav files found in the input directory")
            return
        
        print(f"Found {len(youtube_samples)} .wav files to process")
        
        successful_processings = []
        
        for sample_path in youtube_samples:
            if "voice_sample" in sample_path.name:
                print(f"\n🔍 Processing: {sample_path.name}")
                
                result = preprocessor.process_youtube_audio(str(sample_path), min_quality=0.5)
                
                if result:
                    successful_processings.append(result)
                    print(f"✅ Successfully processed: {result['processed_file']}")
                else:
                    print(f"❌ Failed to process: {sample_path.name}")
        
        print(f"\n📊 Processing Summary:")
        print(f"   Total samples: {len(youtube_samples)}")
        print(f"   Successfully processed: {len(successful_processings)}")
        print(f"   Success rate: {len(successful_processings)/len(youtube_samples)*100:.1f}%")
        
        if successful_processings:
            avg_quality = np.mean([r['specifications']['quality_score'] for r in successful_processings])
            print(f"   Average quality score: {avg_quality:.3f}")
            print(f"\n💡 Use these processed samples for voice cloning!")

if __name__ == "__main__":
    main() 