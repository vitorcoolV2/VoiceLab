#!/usr/bin/env python3
"""
System Monitor for Coqui TTS Server
Provides real-time monitoring, diagnostics, and performance metrics.
"""

import os
import sys
import time
import psutil
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tools.audio_utils.audio_player import AudioPlayer

class SystemMonitor:
    """System monitor for Coqui TTS server."""
    
    def __init__(self, server_url: str = "http://localhost:8000", 
                 log_file: str = "system_monitor.log"):
        self.server_url = server_url
        self.log_file = log_file
        self.start_time = time.time()
        self.metrics_history = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 5.0,  # seconds
            'error_rate': 0.1  # 10%
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics (find TTS server process)
            tts_process = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'tts_server' in ' '.join(proc.info['cmdline'] or []):
                        tts_process = proc
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_gb': memory.used / (1024**3),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'tts_process': {
                    'pid': tts_process.pid if tts_process else None,
                    'cpu_percent': tts_process.cpu_percent() if tts_process else None,
                    'memory_mb': tts_process.memory_info().rss / (1024**2) if tts_process else None,
                    'status': tts_process.status() if tts_process else None
                }
            }
            
            return metrics
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_server_health(self) -> Dict[str, Any]:
        """Get server health status."""
        try:
            start_time = time.time()
            response = requests.get(f"{self.server_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health = response.json()
                health['response_time'] = response_time
                health['status_code'] = response.status_code
                return health
            else:
                return {
                    'status': 'unhealthy',
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'response_time': 10.0,
                'error': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'connection_error',
                'error': 'Cannot connect to server'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_alerts(self, metrics: Dict[str, Any], health: Dict[str, Any]) -> List[str]:
        """Check for system alerts based on thresholds."""
        alerts = []
        
        # CPU alerts
        if metrics.get('cpu', {}).get('percent', 0) > self.alert_thresholds['cpu_percent']:
            alerts.append(f"🚨 High CPU usage: {metrics['cpu']['percent']:.1f}%")
        
        # Memory alerts
        if metrics.get('memory', {}).get('percent', 0) > self.alert_thresholds['memory_percent']:
            alerts.append(f"🚨 High memory usage: {metrics['memory']['percent']:.1f}%")
        
        # Disk alerts
        if metrics.get('disk', {}).get('percent', 0) > self.alert_thresholds['disk_percent']:
            alerts.append(f"🚨 High disk usage: {metrics['disk']['percent']:.1f}%")
        
        # Response time alerts
        if health.get('response_time', 0) > self.alert_thresholds['response_time']:
            alerts.append(f"🚨 Slow server response: {health['response_time']:.2f}s")
        
        # Server status alerts
        if health.get('status') != 'healthy':
            alerts.append(f"🚨 Server unhealthy: {health.get('status', 'unknown')}")
        
        return alerts
    
    def log_metrics(self, metrics: Dict[str, Any], health: Dict[str, Any], alerts: List[str]):
        """Log metrics to file."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'health': health,
            'alerts': alerts
        }
        
        self.metrics_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Write to log file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"⚠️  Could not write to log file: {e}")
    
    def print_status(self, metrics: Dict[str, Any], health: Dict[str, Any], alerts: List[str]):
        """Print current system status."""
        print(f"\n📊 System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # System metrics
        print("🖥️  System Metrics:")
        if 'cpu' in metrics:
            cpu = metrics['cpu']
            print(f"   CPU: {cpu['percent']:.1f}% ({cpu['count']} cores, {cpu['frequency_mhz']:.0f} MHz)")
        
        if 'memory' in metrics:
            mem = metrics['memory']
            print(f"   Memory: {mem['percent']:.1f}% ({mem['used_gb']:.1f}GB / {mem['total_gb']:.1f}GB)")
        
        if 'disk' in metrics:
            disk = metrics['disk']
            print(f"   Disk: {disk['percent']:.1f}% ({disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB)")
        
        # TTS Process metrics
        if 'tts_process' in metrics and metrics['tts_process']['pid']:
            proc = metrics['tts_process']
            print(f"   TTS Process: PID {proc['pid']}, CPU {proc['cpu_percent']:.1f}%, Memory {proc['memory_mb']:.1f}MB")
        
        # Server health
        print("\n🎤 Server Health:")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Response Time: {health.get('response_time', 0):.3f}s")
        print(f"   TTS Initialized: {'✅' if health.get('tts_initialized') else '❌'}")
        print(f"   Whisper Initialized: {'✅' if health.get('whisper_initialized') else '❌'}")
        print(f"   GPU Available: {'✅' if health.get('gpu_available') else '❌'}")
        
        # Alerts
        if alerts:
            print(f"\n🚨 Alerts ({len(alerts)}):")
            for alert in alerts:
                print(f"   {alert}")
        else:
            print(f"\n✅ No alerts - System healthy")
    
    def get_performance_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_metrics = [
            entry for entry in self.metrics_history
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': 'No recent metrics available'}
        
        # Calculate averages
        cpu_values = [m['metrics'].get('cpu', {}).get('percent', 0) for m in recent_metrics]
        memory_values = [m['metrics'].get('memory', {}).get('percent', 0) for m in recent_metrics]
        response_times = [m['health'].get('response_time', 0) for m in recent_metrics]
        
        summary = {
            'period_minutes': minutes,
            'samples': len(recent_metrics),
            'cpu_avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            'cpu_max': max(cpu_values) if cpu_values else 0,
            'memory_avg': sum(memory_values) / len(memory_values) if memory_values else 0,
            'memory_max': max(memory_values) if memory_values else 0,
            'response_time_avg': sum(response_times) / len(response_times) if response_times else 0,
            'response_time_max': max(response_times) if response_times else 0,
            'alerts_count': sum(len(m['alerts']) for m in recent_metrics)
        }
        
        return summary
    
    def monitor_continuous(self, interval: int = 30, duration: Optional[int] = None):
        """Monitor system continuously."""
        print(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        if duration:
            print(f"⏱️  Duration: {duration} seconds")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                # Check if duration exceeded
                if duration and (time.time() - start_time) > duration:
                    print(f"\n⏰ Monitoring duration completed ({duration}s)")
                    break
                
                # Get metrics
                metrics = self.get_system_metrics()
                health = self.get_server_health()
                alerts = self.check_alerts(metrics, health)
                
                # Log and display
                self.log_metrics(metrics, health, alerts)
                self.print_status(metrics, health, alerts)
                
                # Show iteration info
                elapsed = time.time() - start_time
                print(f"   Iteration: {iteration}, Elapsed: {elapsed:.0f}s")
                
                # Wait for next iteration
                if duration and (time.time() - start_time + interval) > duration:
                    break
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n⏹️  Monitoring stopped by user")
        
        # Print final summary
        summary = self.get_performance_summary()
        print(f"\n📈 Performance Summary:")
        print(f"   CPU Avg: {summary.get('cpu_avg', 0):.1f}% (Max: {summary.get('cpu_max', 0):.1f}%)")
        print(f"   Memory Avg: {summary.get('memory_avg', 0):.1f}% (Max: {summary.get('memory_max', 0):.1f}%)")
        print(f"   Response Time Avg: {summary.get('response_time_avg', 0):.3f}s (Max: {summary.get('response_time_max', 0):.3f}s)")
        print(f"   Total Alerts: {summary.get('alerts_count', 0)}")

def main():
    parser = argparse.ArgumentParser(description="System Monitor for Coqui TTS Server")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    parser.add_argument("--log", default="system_monitor.log", help="Log file path")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    parser.add_argument("--duration", type=int, help="Monitoring duration in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--summary", type=int, metavar="MINUTES", help="Show performance summary for last N minutes")
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(args.server, args.log)
    
    if args.summary:
        # Show performance summary
        summary = monitor.get_performance_summary(args.summary)
        print(f"📊 Performance Summary (Last {args.summary} minutes)")
        print("=" * 50)
        for key, value in summary.items():
            print(f"   {key}: {value}")
    
    elif args.once:
        # Run once
        metrics = monitor.get_system_metrics()
        health = monitor.get_server_health()
        alerts = monitor.check_alerts(metrics, health)
        monitor.print_status(metrics, health, alerts)
    
    else:
        # Continuous monitoring
        monitor.monitor_continuous(args.interval, args.duration)

if __name__ == "__main__":
    main() 