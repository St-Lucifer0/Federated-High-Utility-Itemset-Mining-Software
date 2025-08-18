"""
Memory monitoring and management for HUI Algorithm.

This script provides real-time memory monitoring and management capabilities
to help optimize the performance of the BestEfficientUPGrowth algorithm.
"""

import psutil
import time
import threading
import gc
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a specific time."""
    timestamp: float
    process_memory_mb: float
    system_available_mb: float
    system_usage_percent: float
    gc_stats: Dict[str, int]
    
    def __str__(self) -> str:
        return (f"Memory Snapshot at {time.strftime('%H:%M:%S', time.localtime(self.timestamp))}: "
                f"Process: {self.process_memory_mb:.1f} MB, "
                f"System Available: {self.system_available_mb:.1f} MB, "
                f"System Usage: {self.system_usage_percent:.1f}%")

class MemoryMonitor:
    """Real-time memory monitoring and management."""
    
    def __init__(self, alert_threshold: float = 0.8, check_interval: float = 1.0):
        """
        Initialize memory monitor.
        
        Args:
            alert_threshold: Memory usage threshold for alerts (0.0 to 1.0)
            check_interval: Interval between memory checks in seconds
        """
        self.alert_threshold = alert_threshold
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        self.snapshots: List[MemorySnapshot] = []
        self.alert_callbacks: List[Callable] = []
        self.max_snapshots = 1000  # Limit memory usage of snapshots
        
    def start_monitoring(self):
        """Start memory monitoring in background thread."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Memory monitoring started...")
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("Memory monitoring stopped.")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._take_snapshot()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Memory monitoring error: {e}")
                time.sleep(self.check_interval)
    
    def _take_snapshot(self):
        """Take a memory usage snapshot."""
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        system_memory = psutil.virtual_memory()
        system_available = system_memory.available / (1024 * 1024)  # MB
        system_usage = system_memory.percent
        
        # Get garbage collection statistics
        gc_stats = {
            'collections': gc.get_stats(),
            'garbage_count': len(gc.garbage)
        }
        
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            process_memory_mb=process_memory,
            system_available_mb=system_available,
            system_usage_percent=system_usage,
            gc_stats=gc_stats
        )
        
        self.snapshots.append(snapshot)
        
        # Limit snapshot history to prevent memory bloat
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots:]
        
        # Check for memory pressure
        if self._is_memory_pressure(snapshot):
            self._trigger_alerts(snapshot)
    
    def _is_memory_pressure(self, snapshot: MemorySnapshot) -> bool:
        """Check if memory pressure is detected."""
        # Check process memory usage relative to system available
        if snapshot.system_available_mb < 1000:  # Less than 1GB available
            return True
        
        # Check if process is using too much of available memory
        if snapshot.process_memory_mb > snapshot.system_available_mb * self.alert_threshold:
            return True
        
        # Check system memory usage
        if snapshot.system_usage_percent > 90:
            return True
        
        return False
    
    def _trigger_alerts(self, snapshot: MemorySnapshot):
        """Trigger memory pressure alerts."""
        for callback in self.alert_callbacks:
            try:
                callback(snapshot)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def add_alert_callback(self, callback: Callable[[MemorySnapshot], None]):
        """Add a callback function for memory pressure alerts."""
        self.alert_callbacks.append(callback)
    
    def get_current_memory_info(self) -> Dict[str, float]:
        """Get current memory information."""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        return {
            'process_memory_mb': latest.process_memory_mb,
            'system_available_mb': latest.system_available_mb,
            'system_usage_percent': latest.system_usage_percent,
            'timestamp': latest.timestamp
        }
    
    def get_memory_trend(self, minutes: int = 5) -> Dict[str, List[float]]:
        """Get memory usage trend over the specified time period."""
        if not self.snapshots:
            return {}
        
        cutoff_time = time.time() - (minutes * 60)
        recent_snapshots = [s for s in self.snapshots if s.timestamp >= cutoff_time]
        
        if not recent_snapshots:
            return {}
        
        return {
            'timestamps': [s.timestamp for s in recent_snapshots],
            'process_memory': [s.process_memory_mb for s in recent_snapshots],
            'system_available': [s.system_available_mb for s in recent_snapshots],
            'system_usage': [s.system_usage_percent for s in recent_snapshots]
        }
    
    def print_memory_status(self):
        """Print current memory status."""
        if not self.snapshots:
            print("No memory data available.")
            return
        
        current = self.snapshots[-1]
        print("=" * 60)
        print("CURRENT MEMORY STATUS")
        print("=" * 60)
        print(f"Process Memory: {current.process_memory_mb:.1f} MB")
        print(f"System Available: {current.system_available_mb:.1f} MB")
        print(f"System Usage: {current.system_usage_percent:.1f}%")
        print(f"Memory Pressure: {'YES' if self._is_memory_pressure(current) else 'NO'}")
        print(f"Snapshots Collected: {len(self.snapshots)}")
        print("=" * 60)
    
    def suggest_optimizations(self) -> List[str]:
        """Suggest memory optimization strategies based on current usage."""
        if not self.snapshots:
            return []
        
        current = self.snapshots[-1]
        suggestions = []
        
        if current.process_memory_mb > 1000:
            suggestions.append("Consider reducing batch sizes")
            suggestions.append("Enable more aggressive pruning")
            suggestions.append("Reduce cache sizes")
        
        if current.system_available_mb < 1000:
            suggestions.append("Close other applications to free memory")
            suggestions.append("Consider using smaller datasets")
            suggestions.append("Enable streaming processing")
        
        if current.system_usage_percent > 85:
            suggestions.append("System memory pressure detected")
            suggestions.append("Consider restarting the application")
            suggestions.append("Monitor for memory leaks")
        
        return suggestions

@contextmanager
def memory_monitoring(alert_threshold: float = 0.8, check_interval: float = 1.0):
    """
    Context manager for automatic memory monitoring.
    
    Args:
        alert_threshold: Memory usage threshold for alerts
        check_interval: Interval between memory checks in seconds
    
    Usage:
        with memory_monitoring() as monitor:
            # Your algorithm code here
            monitor.print_memory_status()
    """
    monitor = MemoryMonitor(alert_threshold, check_interval)
    
    try:
        monitor.start_monitoring()
        yield monitor
    finally:
        monitor.stop_monitoring()

def optimize_memory_usage():
    """Perform immediate memory optimization."""
    print("Performing memory optimization...")
    
    # Force garbage collection
    collected = gc.collect()
    print(f"Garbage collection: {collected} objects collected")
    
    # Clear Python's internal caches
    import sys
    if hasattr(sys, 'intern'):
        sys.intern.clear()
    
    # Get current memory usage
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / (1024 * 1024)
    
    # Force another garbage collection
    gc.collect()
    
    memory_after = process.memory_info().rss / (1024 * 1024)
    memory_freed = memory_before - memory_after
    
    print(f"Memory freed: {memory_freed:.1f} MB")
    print("Memory optimization completed.")

def get_memory_efficiency_score() -> float:
    """Calculate a memory efficiency score (0.0 to 1.0)."""
    try:
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        system_memory = psutil.virtual_memory()
        system_total = system_memory.total / (1024 * 1024)  # MB
        
        # Score based on process memory usage relative to system total
        # Lower usage = higher score
        efficiency = max(0.0, 1.0 - (process_memory / system_total))
        
        return efficiency
    except Exception:
        return 0.0

if __name__ == "__main__":
    # Test memory monitoring
    print("Testing memory monitoring...")
    
    with memory_monitoring() as monitor:
        # Simulate some work
        print("Simulating algorithm execution...")
        time.sleep(3)
        
        # Print memory status
        monitor.print_memory_status()
        
        # Get suggestions
        suggestions = monitor.suggest_optimizations()
        if suggestions:
            print("\nOptimization suggestions:")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        
        # Get efficiency score
        efficiency = get_memory_efficiency_score()
        print(f"\nMemory efficiency score: {efficiency:.2%}")
        
        # Simulate more work
        print("\nSimulating more work...")
        time.sleep(2)
        
        # Print final status
        monitor.print_memory_status()
    
    print("\nMemory monitoring test completed.")
