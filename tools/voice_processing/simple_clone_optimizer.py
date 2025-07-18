#!/usr/bin/env python3
"""
Simple Clone Optimizer
A practical approach to optimizing voice cloning by:
1. Using existing cloned voices
2. Analyzing their metrics
3. Providing recommendations for improvement
4. Creating a summary report
"""

import os
import json
import csv
from pathlib import Path
import librosa
import numpy as np
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCloneOptimizer:
    def __init__(self):
        """Initialize the clone optimizer."""
        self.output_dir = Path(os.environ.get("COQUI_TTS_OUTPUTS", "output"))
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_voice_metrics(self, wav_path: str) -> Dict[str, float]:
        """Extract voice metrics from audio file"""
        try:
            y, sr = librosa.load(wav_path, sr=None)
            
            duration = float(librosa.get_duration(y=y, sr=sr))
            
            # Pitch (fundamental frequency)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[magnitudes > np.median(magnitudes)]
            pitch = float(np.median(pitch_values)) if len(pitch_values) > 0 else 0.0
            
            # Energy
            energy = float(np.mean(librosa.feature.rms(y=y)))
            
            # Speaking rate (tempo-based estimate)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            speaking_rate = float(tempo[0]) if len(tempo) > 0 else 0.0
            
            # Brightness (spectral centroid)
            brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            
            # Warmth (spectral rolloff)
            warmth = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
            
            return {
                'duration': duration,
                'pitch': pitch,
                'energy': energy,
                'speaking_rate': speaking_rate,
                'brightness': brightness,
                'warmth': warmth
            }
        except Exception as e:
            logger.error(f"Error extracting metrics from {wav_path}: {e}")
            return {
                'duration': 0.0,
                'pitch': 0.0,
                'energy': 0.0,
                'speaking_rate': 0.0,
                'brightness': 0.0,
                'warmth': 0.0
            }
    
    def analyze_cloning_quality(self, original_metrics: Dict, clone_metrics: Dict) -> Dict:
        """Analyze the quality of voice cloning"""
        differences = {}
        quality_score = 0.0
        recommendations = []
        
        # Calculate differences
        for key in original_metrics.keys():
            if original_metrics[key] > 0:
                diff = abs(original_metrics[key] - clone_metrics[key]) / original_metrics[key]
                differences[f"{key}_diff"] = diff
                quality_score += diff
            else:
                differences[f"{key}_diff"] = 1.0
                quality_score += 1.0
        
        # Average quality score (lower is better)
        quality_score = quality_score / len(original_metrics)
        
        # Generate recommendations
        if differences.get('pitch_diff', 1.0) > 0.2:
            recommendations.append("Consider adjusting pitch parameters")
        if differences.get('energy_diff', 1.0) > 0.2:
            recommendations.append("Consider adjusting volume/energy parameters")
        if differences.get('speaking_rate_diff', 1.0) > 0.2:
            recommendations.append("Consider adjusting speed parameters")
        if differences.get('brightness_diff', 1.0) > 0.2:
            recommendations.append("Consider adjusting timbre parameters")
        
        if quality_score < 0.1:
            quality_rating = "Excellent"
        elif quality_score < 0.3:
            quality_rating = "Good"
        elif quality_score < 0.5:
            quality_rating = "Fair"
        else:
            quality_rating = "Poor"
        
        return {
            'quality_score': quality_score,
            'quality_rating': quality_rating,
            'differences': differences,
            'recommendations': recommendations
        }
    
    def find_matching_pairs(self) -> List[Tuple[str, str]]:
        """Find original voice samples and their corresponding clones"""
        pairs = []
        
        # Find all original samples
        originals = list(self.output_dir.glob("clone*_voice_sample.wav"))
        
        # Find all cloned voices
        clones = list(self.output_dir.glob("cloned_voice_*.wav"))
        
        # For now, match by order (this could be improved with better matching logic)
        for i, original in enumerate(originals):
            if i < len(clones):
                pairs.append((str(original), str(clones[i])))
        
        return pairs
    
    def generate_optimization_report(self) -> Dict:
        """Generate a comprehensive optimization report"""
        print("🔍 Analyzing voice cloning quality...")
        
        pairs = self.find_matching_pairs()
        if not pairs:
            print("❌ No voice sample pairs found")
            return {}
        
        report = {
            'summary': {
                'total_pairs': len(pairs),
                'average_quality_score': 0.0,
                'best_clone': None,
                'worst_clone': None
            },
            'detailed_analysis': [],
            'recommendations': []
        }
        
        quality_scores = []
        
        for i, (original_path, clone_path) in enumerate(pairs):
            print(f"📊 Analyzing pair {i+1}/{len(pairs)}")
            print(f"   Original: {Path(original_path).name}")
            print(f"   Clone: {Path(clone_path).name}")
            
            # Extract metrics
            original_metrics = self.extract_voice_metrics(original_path)
            clone_metrics = self.extract_voice_metrics(clone_path)
            
            # Analyze quality
            analysis = self.analyze_cloning_quality(original_metrics, clone_metrics)
            
            # Store detailed analysis
            detailed = {
                'pair_id': i + 1,
                'original_file': Path(original_path).name,
                'clone_file': Path(clone_path).name,
                'original_metrics': original_metrics,
                'clone_metrics': clone_metrics,
                'quality_score': analysis['quality_score'],
                'quality_rating': analysis['quality_rating'],
                'differences': analysis['differences'],
                'recommendations': analysis['recommendations']
            }
            
            report['detailed_analysis'].append(detailed)
            quality_scores.append(analysis['quality_score'])
            
            # Collect recommendations
            report['recommendations'].extend(analysis['recommendations'])
            
            print(f"   Quality: {analysis['quality_rating']} (Score: {analysis['quality_score']:.3f})")
            print()
        
        # Calculate summary statistics
        if quality_scores:
            report['summary']['average_quality_score'] = np.mean(quality_scores)
            
            # Find best and worst clones
            best_idx = np.argmin(quality_scores)
            worst_idx = np.argmax(quality_scores)
            
            report['summary']['best_clone'] = {
                'pair_id': best_idx + 1,
                'quality_score': quality_scores[best_idx],
                'files': {
                    'original': Path(pairs[best_idx][0]).name,
                    'clone': Path(pairs[best_idx][1]).name
                }
            }
            
            report['summary']['worst_clone'] = {
                'pair_id': worst_idx + 1,
                'quality_score': quality_scores[worst_idx],
                'files': {
                    'original': Path(pairs[worst_idx][0]).name,
                    'clone': Path(pairs[worst_idx][1]).name
                }
            }
        
        # Remove duplicate recommendations
        report['recommendations'] = list(set(report['recommendations']))
        
        return report
    
    def save_report(self, report: Dict):
        """Save the optimization report"""
        timestamp = int(time.time())
        
        # Save JSON report
        json_file = self.output_dir / f"clone_optimization_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save CSV summary
        csv_file = self.output_dir / f"clone_optimization_summary_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Pair ID', 'Original File', 'Clone File', 'Quality Score', 
                'Quality Rating', 'Pitch Diff', 'Energy Diff', 'Speaking Rate Diff',
                'Brightness Diff', 'Warmth Diff'
            ])
            
            for analysis in report['detailed_analysis']:
                writer.writerow([
                    analysis['pair_id'],
                    analysis['original_file'],
                    analysis['clone_file'],
                    f"{analysis['quality_score']:.3f}",
                    analysis['quality_rating'],
                    f"{analysis['differences'].get('pitch_diff', 0):.3f}",
                    f"{analysis['differences'].get('energy_diff', 0):.3f}",
                    f"{analysis['differences'].get('speaking_rate_diff', 0):.3f}",
                    f"{analysis['differences'].get('brightness_diff', 0):.3f}",
                    f"{analysis['differences'].get('warmth_diff', 0):.3f}"
                ])
        
        print(f"📄 Reports saved:")
        print(f"   JSON: {json_file}")
        print(f"   CSV: {csv_file}")
        
        return json_file, csv_file

def main():
    """Main function to run simple clone optimization"""
    print("🎯 Simple Clone Optimizer")
    print("=" * 50)
    
    optimizer = SimpleCloneOptimizer()
    
    # Generate optimization report
    report = optimizer.generate_optimization_report()
    
    if not report:
        print("❌ No analysis performed")
        return
    
    # Print summary
    print("\n📊 Optimization Summary:")
    print("=" * 50)
    
    summary = report['summary']
    print(f"📈 Total pairs analyzed: {summary['total_pairs']}")
    print(f"📊 Average quality score: {summary['average_quality_score']:.3f}")
    
    if summary['best_clone']:
        print(f"🏆 Best clone: Pair {summary['best_clone']['pair_id']}")
        print(f"   Score: {summary['best_clone']['quality_score']:.3f}")
        print(f"   Files: {summary['best_clone']['files']['original']} → {summary['best_clone']['files']['clone']}")
    
    if summary['worst_clone']:
        print(f"⚠️  Worst clone: Pair {summary['worst_clone']['pair_id']}")
        print(f"   Score: {summary['worst_clone']['quality_score']:.3f}")
        print(f"   Files: {summary['worst_clone']['files']['original']} → {summary['worst_clone']['files']['clone']}")
    
    # Print recommendations
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Save reports
    optimizer.save_report(report)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    import time
    main() 