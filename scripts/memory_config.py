"""
Memory optimization configuration for HUI Algorithm.

This file contains configuration settings to optimize memory usage and runtime performance
for the BestEfficientUPGrowth algorithm.
"""

import psutil
import os
from typing import Dict, Any

class MemoryConfig:
    """Configuration class for memory optimization settings."""
    
    def __init__(self):
        """Initialize memory configuration based on system resources."""
        self._setup_memory_limits()
        self._setup_optimization_flags()
    
    def _setup_memory_limits(self):
        """Setup memory limits based on available system memory."""
        # Get system memory information
        total_memory = psutil.virtual_memory().total / (1024 * 1024)  # MB
        available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
        
        # Set memory thresholds based on available memory
        if available_memory < 1000:  # Less than 1GB available
            self.max_cache_size = 500
            self.max_phuis_in_memory = 5000
            self.batch_size = 250
            self.chunk_size = 1000
            self.memory_threshold = 0.6  # More aggressive cleanup
            self.enable_streaming = True
            self.enable_memory_mapping = False
        elif available_memory < 4000:  # Less than 4GB available
            self.max_cache_size = 2000
            self.max_phuis_in_memory = 15000
            self.batch_size = 500
            self.chunk_size = 2500
            self.memory_threshold = 0.7
            self.enable_streaming = True
            self.enable_memory_mapping = True
        else:  # More than 4GB available
            self.max_cache_size = 5000
            self.max_phuis_in_memory = 30000
            self.batch_size = 1000
            self.chunk_size = 5000
            self.memory_threshold = 0.8
            self.enable_streaming = True
            self.enable_memory_mapping = True
        
        # Store memory info for reference
        self.total_memory_mb = total_memory
        self.available_memory_mb = available_memory
        self.memory_usage_percent = (total_memory - available_memory) / total_memory * 100
    
    def _setup_optimization_flags(self):
        """Setup optimization flags based on memory constraints."""
        # Enable/disable features based on memory availability
        if self.available_memory_mb < 2000:
            # Low memory mode
            self.use_smart_caching = False
            self.use_utility_pruning = True
            self.use_support_pruning = True
            self.use_early_termination = True
            self.use_pseudo_projection = True
            self.adaptive_batching = True
            self.enable_garbage_collection = True
        else:
            # Normal mode
            self.use_smart_caching = True
            self.use_utility_pruning = True
            self.use_support_pruning = True
            self.use_early_termination = True
            self.use_pseudo_projection = True
            self.adaptive_batching = True
            self.enable_garbage_collection = True
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for the algorithm."""
        return {
            'max_cache_size': self.max_cache_size,
            'max_phuis_in_memory': self.max_phuis_in_memory,
            'batch_size': self.batch_size,
            'chunk_size': self.chunk_size,
            'memory_threshold': self.memory_threshold,
            'use_smart_caching': self.use_smart_caching,
            'use_utility_pruning': self.use_utility_pruning,
            'use_support_pruning': self.use_support_pruning,
            'use_early_termination': self.use_early_termination,
            'use_pseudo_projection': self.use_pseudo_projection,
            'adaptive_batching': self.adaptive_batching,
            'enable_streaming': self.enable_streaming,
            'enable_memory_mapping': self.enable_memory_mapping,
            'enable_garbage_collection': self.enable_garbage_collection
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory information."""
        current_process = psutil.Process(os.getpid())
        current_memory = current_process.memory_info().rss / (1024 * 1024)  # MB
        
        return {
            'total_system_memory_mb': self.total_memory_mb,
            'available_system_memory_mb': self.available_memory_mb,
            'system_memory_usage_percent': self.memory_usage_percent,
            'current_process_memory_mb': current_memory,
            'memory_pressure_level': self._get_memory_pressure_level()
        }
    
    def _get_memory_pressure_level(self) -> str:
        """Get memory pressure level description."""
        if self.available_memory_mb < 500:
            return "CRITICAL"
        elif self.available_memory_mb < 1000:
            return "HIGH"
        elif self.available_memory_mb < 2000:
            return "MEDIUM"
        else:
            return "LOW"
    
    def should_perform_cleanup(self) -> bool:
        """Check if memory cleanup should be performed."""
        current_process = psutil.Process(os.getpid())
        current_memory = current_process.memory_info().rss / (1024 * 1024)  # MB
        
        # Cleanup if using more than threshold of available memory
        return current_memory > self.available_memory_mb * self.memory_threshold
    
    def get_optimal_batch_size(self, dataset_size: int) -> int:
        """Calculate optimal batch size based on current memory conditions."""
        # Adjust batch size based on available memory
        if self.available_memory_mb < 1000:
            return min(500, dataset_size // 100)
        elif self.available_memory_mb < 4000:
            return min(1000, dataset_size // 50)
        else:
            return min(2000, dataset_size // 25)
    
    def print_memory_status(self):
        """Print current memory status and configuration."""
        print("=" * 60)
        print("MEMORY OPTIMIZATION CONFIGURATION")
        print("=" * 60)
        
        # Memory information
        mem_info = self.get_memory_info()
        print(f"System Memory:")
        print(f"  Total: {mem_info['total_system_memory_mb']:,.0f} MB")
        print(f"  Available: {mem_info['available_system_memory_mb']:,.0f} MB")
        print(f"  Usage: {mem_info['system_memory_usage_percent']:.1f}%")
        print(f"  Pressure Level: {mem_info['memory_pressure_level']}")
        print()
        
        print(f"Current Process Memory: {mem_info['current_process_memory_mb']:.1f} MB")
        print()
        
        # Configuration settings
        config = self.get_algorithm_config()
        print("Algorithm Configuration:")
        print(f"  Max Cache Size: {config['max_cache_size']:,}")
        print(f"  Max PHUIs in Memory: {config['max_phuis_in_memory']:,}")
        print(f"  Batch Size: {config['batch_size']:,}")
        print(f"  Chunk Size: {config['chunk_size']:,}")
        print(f"  Memory Threshold: {config['memory_threshold']:.1%}")
        print()
        
        print("Optimization Features:")
        print(f"  Smart Caching: {'✓' if config['use_smart_caching'] else '✗'}")
        print(f"  Utility Pruning: {'✓' if config['use_utility_pruning'] else '✗'}")
        print(f"  Support Pruning: {'✓' if config['use_support_pruning'] else '✗'}")
        print(f"  Early Termination: {'✓' if config['use_early_termination'] else '✗'}")
        print(f"  Pseudo-Projection: {'✓' if config['use_pseudo_projection'] else '✗'}")
        print(f"  Adaptive Batching: {'✓' if config['adaptive_batching'] else '✗'}")
        print(f"  Streaming: {'✓' if config['enable_streaming'] else '✗'}")
        print(f"  Memory Mapping: {'✓' if config['enable_memory_mapping'] else '✗'}")
        print(f"  Garbage Collection: {'✓' if config['enable_garbage_collection'] else '✗'}")
        print("=" * 60)

# Global configuration instance
memory_config = MemoryConfig()

def get_memory_config() -> MemoryConfig:
    """Get the global memory configuration instance."""
    return memory_config

def update_memory_config():
    """Update memory configuration based on current system state."""
    memory_config._setup_memory_limits()
    memory_config._setup_optimization_flags()

if __name__ == "__main__":
    # Print current memory configuration
    memory_config.print_memory_status()
    
    # Test memory pressure detection
    print(f"\nShould perform cleanup: {memory_config.should_perform_cleanup()}")
    print(f"Optimal batch size for 100k dataset: {memory_config.get_optimal_batch_size(100000):,}")
