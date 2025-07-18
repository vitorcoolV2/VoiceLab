#!/usr/bin/env python3
"""
Enhanced Voice Processor with Comprehensive Data Storage
Focuses on the most critical aspects for voice cloning:
1. Basic audio cleaning
2. Voice segment extraction with detailed analysis
3. Quality analysis and validation
4. Comprehensive metadata generation for TTS optimization
5. Detailed process data storage in JSON files
"""

import os
import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedVoiceProcessor:
    def __init__(self, output_dir: str = None):
        """Initialize the voice processor."""
        self.output_dir = Path(output_dir) if output_dir else Path(os.environ.get("COQUI_TTS_OUTPUTS", "output"))
        self.output_dir.mkdir(exist_ok=True)
        self.process_id = int(time.time())
    
    def clean_audio_basic(self, audio_path: str) -> Tuple[str, Dict]:
        """
        Basic audio cleaning: normalize, remove DC offset, basic filtering
        Returns: (cleaned_audio_path, cleaning_info)
        """
        try:
            logger.info(f"Basic cleaning: {audio_path}")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            original_shape = y.shape
            original_duration = len(y) / sr
            
            # Convert to mono if stereo
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
                channels_converted = True
            else:
                channels_converted = False
            
            # Remove DC offset
            dc_offset = np.mean(y)
            y = y - dc_offset
            
            # Normalize audio
            max_amplitude = np.max(np.abs(y))
            normalization_factor = 0.95 / max_amplitude if max_amplitude > 0 else 1.0
            y = y * normalization_factor
            
            # Basic high-pass filter to remove low-frequency noise
            y = librosa.effects.preemphasis(y, coef=0.97)
            
            # Save cleaned audio
            output_path = audio_path.replace('.wav', '_cleaned.wav')
            sf.write(output_path, y, sr)
            
            # Calculate cleaning statistics
            cleaning_info = {
                'original_shape': original_shape,
                'original_duration': float(original_duration),
                'channels_converted': channels_converted,
                'dc_offset_removed': float(dc_offset),
                'normalization_factor': float(normalization_factor),
                'max_amplitude_before': float(max_amplitude),
                'max_amplitude_after': float(np.max(np.abs(y))),
                'sample_rate': int(sr),
                'cleaned_duration': float(len(y) / sr),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Basic cleaning completed: {output_path}")
            return output_path, cleaning_info
            
        except Exception as e:
            logger.error(f"Error in basic cleaning: {e}")
            return audio_path, {'error': str(e)}
    
    def extract_voice_segments_detailed(self, audio_path: str, min_duration: float = 30.0) -> Tuple[List[str], Dict]:
        """
        Detailed voice segment extraction using energy-based detection
        Returns: (segment_paths, detection_info)
        """
        try:
            logger.info(f"Extracting voice segments: {audio_path}")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            # Calculate energy over time
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)    # 10ms hop
            
            energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Calculate energy statistics
            energy_mean = float(np.mean(energy))
            energy_std = float(np.std(energy))
            energy_min = float(np.min(energy))
            energy_max = float(np.max(energy))
            
            # Multiple threshold levels for analysis
            thresholds = {
                '10th_percentile': float(np.percentile(energy, 10)),
                '20th_percentile': float(np.percentile(energy, 20)),
                '30th_percentile': float(np.percentile(energy, 30)),
                '40th_percentile': float(np.percentile(energy, 40)),
                '50th_percentile': float(np.percentile(energy, 50))
            }
            
            # Use 30th percentile as primary threshold
            energy_threshold = thresholds['30th_percentile']
            voice_activity = energy > energy_threshold
            
            # Find voice segments
            segments = []
            segment_info = []
            start_frame = None
            
            for i, is_voice in enumerate(voice_activity):
                if is_voice and start_frame is None:
                    start_frame = i
                elif not is_voice and start_frame is not None:
                    end_frame = i
                    segment_duration = (end_frame - start_frame) * hop_length / sr
                    
                    if segment_duration >= min_duration:
                        start_sample = int(start_frame * hop_length)
                        end_sample = int(end_frame * hop_length)
                        segment = y[start_sample:end_sample]
                        
                        # Calculate segment statistics
                        segment_energy = float(np.mean(librosa.feature.rms(y=segment, frame_length=frame_length, hop_length=hop_length)[0]))
                        
                        # Save segment
                        segment_path = f"{audio_path.replace('.wav', '')}_segment_{len(segments)}.wav"
                        sf.write(segment_path, segment, sr)
                        segments.append(segment_path)
                        
                        segment_info.append({
                            'segment_index': len(segments) - 1,
                            'start_frame': int(start_frame),
                            'end_frame': int(end_frame),
                            'start_time': float(start_frame * hop_length / sr),
                            'end_time': float(end_frame * hop_length / sr),
                            'duration': float(segment_duration),
                            'mean_energy': segment_energy,
                            'file_path': segment_path
                        })
                        
                        logger.info(f"Voice segment {len(segments)}: {segment_duration:.1f}s")
                    
                    start_frame = None
            
            # If no segments found, use the entire audio
            if not segments:
                logger.info("No voice segments found, using entire audio")
                segment_path = f"{audio_path.replace('.wav', '')}_full.wav"
                sf.write(segment_path, y, sr)
                segments.append(segment_path)
                
                segment_info.append({
                    'segment_index': 0,
                    'start_frame': 0,
                    'end_frame': len(energy),
                    'start_time': 0.0,
                    'end_time': float(duration),
                    'duration': float(duration),
                    'mean_energy': energy_mean,
                    'file_path': segment_path,
                    'note': 'entire_audio_used'
                })
            
            # Compile detection information
            detection_info = {
                'audio_duration': float(duration),
                'sample_rate': int(sr),
                'frame_length_ms': 25,
                'hop_length_ms': 10,
                'total_frames': int(len(energy)),
                'energy_statistics': {
                    'mean': energy_mean,
                    'std': energy_std,
                    'min': energy_min,
                    'max': energy_max
                },
                'thresholds': thresholds,
                'primary_threshold': float(energy_threshold),
                'voice_activity_percentage': float(np.sum(voice_activity) / len(voice_activity) * 100),
                'total_segments_found': int(len(segments)),
                'min_duration_requirement': float(min_duration),
                'segments': segment_info,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Extracted {len(segments)} voice segments")
            return segments, detection_info
            
        except Exception as e:
            logger.error(f"Error extracting voice segments: {e}")
            return [], {'error': str(e)}
    
    def analyze_voice_quality_detailed(self, audio_path: str) -> Dict:
        """
        Detailed voice quality and characteristics analysis
        """
        try:
            logger.info(f"Analyzing voice quality: {audio_path}")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            # Basic metrics
            energy = float(np.mean(librosa.feature.rms(y=y)))
            
            # Spectral analysis
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # Pitch analysis
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[magnitudes > np.median(magnitudes)]
            
            if len(pitch_values) > 0:
                median_pitch = float(np.median(pitch_values))
                pitch_std = float(np.std(pitch_values))
                pitch_min = float(np.min(pitch_values))
                pitch_max = float(np.max(pitch_values))
                pitch_range = pitch_max - pitch_min
            else:
                median_pitch = 0.0
                pitch_std = 0.0
                pitch_min = 0.0
                pitch_max = 0.0
                pitch_range = 0.0
            
            # Voice type classification with confidence
            if median_pitch < 150:
                voice_type = "male"
                voice_confidence = 0.8
            elif median_pitch < 250:
                voice_type = "female"
                voice_confidence = 0.7
            else:
                voice_type = "child"
                voice_confidence = 0.6
            
            # MFCC features for voice characteristics
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = [float(x) for x in np.mean(mfccs, axis=1)]
            mfcc_std = [float(x) for x in np.std(mfccs, axis=1)]
            
            # Quality score based on multiple factors
            quality_factors = []
            
            # Duration factor (prefer longer samples)
            duration_factor = min(1.0, duration / 60.0)
            quality_factors.append(duration_factor)
            
            # Energy factor (prefer medium energy)
            energy_factor = 1.0 - abs(energy - 0.1) / 0.1  # Optimal around 0.1
            energy_factor = max(0.0, min(1.0, energy_factor))
            quality_factors.append(energy_factor)
            
            # Pitch stability factor
            pitch_stability = 1.0 - min(1.0, pitch_std / 50.0)  # Lower std = more stable
            quality_factors.append(pitch_stability)
            
            # Spectral consistency factor
            spectral_consistency = 1.0 - min(1.0, np.std(spectral_centroids) / 1000.0)
            quality_factors.append(spectral_consistency)
            
            # Overall quality score
            quality_score = np.mean(quality_factors)
            
            # Compile detailed analysis
            analysis = {
                'basic_metrics': {
                    'duration': float(duration),
                    'sample_rate': int(sr),
                    'total_samples': int(len(y)),
                    'energy': float(energy)
                },
                'spectral_analysis': {
                    'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                    'spectral_centroid_std': float(np.std(spectral_centroids)),
                    'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                    'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth))
                },
                'pitch_analysis': {
                    'median_pitch': float(median_pitch),
                    'pitch_std': float(pitch_std),
                    'pitch_min': float(pitch_min),
                    'pitch_max': float(pitch_max),
                    'pitch_range': float(pitch_range),
                    'pitch_frames_analyzed': int(len(pitch_values))
                },
                'voice_classification': {
                    'voice_type': str(voice_type),
                    'confidence': float(voice_confidence),
                    'pitch_thresholds': {
                        'male_threshold': 150,
                        'female_threshold': 250
                    }
                },
                'mfcc_features': {
                    'mfcc_mean': mfcc_mean,
                    'mfcc_std': mfcc_std
                },
                'quality_assessment': {
                    'quality_score': float(quality_score),
                    'quality_factors': {
                        'duration_factor': float(duration_factor),
                        'energy_factor': float(energy_factor),
                        'pitch_stability': float(pitch_stability),
                        'spectral_consistency': float(spectral_consistency)
                    },
                    'quality_thresholds': {
                        'excellent': 0.8,
                        'good': 0.6,
                        'acceptable': 0.4,
                        'poor': 0.2
                    }
                },
                'processing_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Voice analysis completed - Quality: {quality_score:.3f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing voice quality: {e}")
            return {
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def process_audio_comprehensive(self, audio_path: str, min_quality: float = 0.3) -> Optional[Dict]:
        """
        Complete processing pipeline with comprehensive data storage
        """
        try:
            logger.info(f"Processing audio: {audio_path}")
            start_time = time.time()
            
            # Step 1: Basic cleaning
            cleaned_audio, cleaning_info = self.clean_audio_basic(audio_path)
            
            # Step 2: Extract voice segments with detailed analysis
            voice_segments, detection_info = self.extract_voice_segments_detailed(cleaned_audio, min_duration=30.0)
            
            if not voice_segments:
                logger.error("No voice segments found")
                return None
            
            # Step 3: Analyze each segment and find the best one
            segment_analyses = []
            best_segment = None
            best_analysis = None
            best_quality = 0.0
            
            for segment_path in voice_segments:
                analysis = self.analyze_voice_quality_detailed(segment_path)
                segment_analyses.append({
                    'segment_path': segment_path,
                    'analysis': analysis
                })
                
                if analysis.get('quality_assessment', {}).get('quality_score', 0) > best_quality:
                    best_quality = analysis.get('quality_assessment', {}).get('quality_score', 0)
                    best_segment = segment_path
                    best_analysis = analysis
            
            # Step 4: Check if quality meets minimum threshold
            quality_met = best_quality >= min_quality
            if not quality_met:
                logger.warning(f"Best quality {best_quality:.3f} below threshold {min_quality}")
            
            # Step 5: Generate comprehensive metadata
            processing_time = time.time() - start_time
            
            comprehensive_metadata = {
                'process_id': self.process_id,
                'processing_summary': {
                    'original_file': audio_path,
                    'processed_file': best_segment,
                    'processing_time_seconds': float(processing_time),
                    'quality_threshold': float(min_quality),
                    'quality_met': bool(quality_met),
                    'total_segments_analyzed': int(len(voice_segments)),
                    'best_segment_index': int(voice_segments.index(best_segment)) if best_segment in voice_segments else 0
                },
                'cleaning_stage': cleaning_info,
                'voice_detection_stage': detection_info,
                'segment_analyses': segment_analyses,
                'best_segment_analysis': best_analysis,
                'file_information': {
                    'original_file_size_bytes': os.path.getsize(audio_path) if os.path.exists(audio_path) else 0,
                    'cleaned_file_size_bytes': os.path.getsize(cleaned_audio) if os.path.exists(cleaned_audio) else 0,
                    'best_segment_size_bytes': os.path.getsize(best_segment) if os.path.exists(best_segment) else 0,
                    'processing_timestamp': datetime.now().isoformat()
                },
                'recommendations': {
                    'suitable_for_tts': bool(quality_met),
                    'suggested_improvements': self._generate_improvement_suggestions(best_analysis, quality_met),
                    'voice_cloning_compatibility': self._assess_tts_compatibility(best_analysis)
                }
            }
            
            # Save comprehensive metadata
            metadata_path = best_segment.replace('.wav', '_comprehensive_info.json')
            with open(metadata_path, 'w') as f:
                json.dump(comprehensive_metadata, f, indent=2)
            
            # Also save a simplified version for backward compatibility
            simple_metadata = {
                'original_file': audio_path,
                'processed_file': best_segment,
                'quality_analysis': {
                    'duration': float(best_analysis.get('basic_metrics', {}).get('duration', 0)),
                    'energy': float(best_analysis.get('basic_metrics', {}).get('energy', 0)),
                    'median_pitch': float(best_analysis.get('pitch_analysis', {}).get('median_pitch', 0)),
                    'pitch_std': float(best_analysis.get('pitch_analysis', {}).get('pitch_std', 0)),
                    'voice_type': str(best_analysis.get('voice_classification', {}).get('voice_type', 'unknown')),
                    'quality_score': float(best_analysis.get('quality_assessment', {}).get('quality_score', 0)),
                    'quality_factors': best_analysis.get('quality_assessment', {}).get('quality_factors', {})
                },
                'processing_info': {
                    'cleaned_audio': cleaned_audio,
                    'total_segments': int(len(voice_segments)),
                    'selected_segment': best_segment,
                    'quality_threshold': float(min_quality),
                    'quality_met': bool(quality_met)
                }
            }
            
            simple_metadata_path = best_segment.replace('.wav', '_metadata.json')
            with open(simple_metadata_path, 'w') as f:
                json.dump(simple_metadata, f, indent=2)
            
            logger.info(f"✅ Processing completed!")
            logger.info(f"   Best segment: {best_segment}")
            logger.info(f"   Quality score: {best_analysis.get('quality_assessment', {}).get('quality_score', 0):.3f}")
            logger.info(f"   Duration: {best_analysis.get('basic_metrics', {}).get('duration', 0):.1f}s")
            logger.info(f"   Voice type: {best_analysis.get('voice_classification', {}).get('voice_type', 'unknown')}")
            logger.info(f"   Comprehensive data saved to: {metadata_path}")
            
            return comprehensive_metadata
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None
    
    def _generate_improvement_suggestions(self, analysis: Dict, quality_met: bool) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        if not quality_met:
            suggestions.append("Quality below threshold - consider longer audio samples")
        
        duration = analysis.get('basic_metrics', {}).get('duration', 0)
        if duration < 30:
            suggestions.append("Sample duration is short - longer samples work better for TTS")
        
        energy = analysis.get('basic_metrics', {}).get('energy', 0)
        if energy < 0.05:
            suggestions.append("Low energy detected - audio may be too quiet")
        elif energy > 0.2:
            suggestions.append("High energy detected - audio may be too loud")
        
        pitch_std = analysis.get('pitch_analysis', {}).get('pitch_std', 0)
        if pitch_std > 100:
            suggestions.append("High pitch variation - consider more stable voice samples")
        
        if not suggestions:
            suggestions.append("Audio quality is good for voice cloning")
        
        return suggestions
    
    def _assess_tts_compatibility(self, analysis: Dict) -> Dict:
        """Assess compatibility with TTS voice cloning"""
        quality_score = analysis.get('quality_assessment', {}).get('quality_score', 0)
        duration = analysis.get('basic_metrics', {}).get('duration', 0)
        voice_type = analysis.get('voice_classification', {}).get('voice_type', 'unknown')
        
        compatibility = {
            'overall_score': quality_score,
            'duration_suitable': duration >= 30,
            'voice_type_suitable': voice_type in ['male', 'female', 'child'],
            'recommended_use': 'excellent' if quality_score > 0.7 else 'good' if quality_score > 0.5 else 'acceptable' if quality_score > 0.3 else 'poor'
        }
        
        return compatibility

# Backward compatibility - keep the old class name
SimpleVoiceProcessor = EnhancedVoiceProcessor

def main():
    """Test the enhanced voice processor"""
    print("🎤 Enhanced Voice Processor with Comprehensive Data Storage")
    print("=" * 70)
    
    processor = EnhancedVoiceProcessor()
    
    # Process the existing voice samples
    downloads_dir = Path("downloads")
    voice_samples = list(downloads_dir.glob("*.wav"))
    
    if not voice_samples:
        print("❌ No voice samples found in downloads directory")
        return
    
    print(f"Found {len(voice_samples)} voice samples to process")
    
    successful_processings = []
    
    for sample_path in voice_samples:
        print(f"\n🔍 Processing: {sample_path.name}")
        
        result = processor.process_audio_comprehensive(str(sample_path), min_quality=0.2)
        
        if result:
            successful_processings.append(result)
            print(f"✅ Successfully processed: {result['processing_summary']['processed_file']}")
        else:
            print(f"❌ Failed to process: {sample_path.name}")
    
    print(f"\n📊 Processing Summary:")
    print(f"   Total samples: {len(voice_samples)}")
    print(f"   Successfully processed: {len(successful_processings)}")
    print(f"   Success rate: {len(successful_processings)/len(voice_samples)*100:.1f}%")
    
    if successful_processings:
        avg_quality = np.mean([r['best_segment_analysis']['quality_assessment']['quality_score'] for r in successful_processings])
        print(f"   Average quality score: {avg_quality:.3f}")
        
        # Show best processed sample
        best_result = max(successful_processings, key=lambda x: x['best_segment_analysis']['quality_assessment']['quality_score'])
        print(f"\n🏆 Best processed sample:")
        print(f"   File: {best_result['processing_summary']['processed_file']}")
        print(f"   Quality: {best_result['best_segment_analysis']['quality_assessment']['quality_score']:.3f}")
        print(f"   Voice type: {best_result['best_segment_analysis']['voice_classification']['voice_type']}")
        print(f"   Duration: {best_result['best_segment_analysis']['basic_metrics']['duration']:.1f}s")
        print(f"   TTS Compatibility: {best_result['recommendations']['voice_cloning_compatibility']['recommended_use']}")
        
        print(f"\n💡 Use these processed samples for voice cloning!")
        print(f"📄 Comprehensive data stored in *_comprehensive_info.json files")

if __name__ == "__main__":
    main() 