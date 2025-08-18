#!/usr/bin/env python3
"""
Quick memory status checker for HUI Algorithm.

Run this script to get an immediate overview of your system's memory status
and receive optimization recommendations.
"""

import psutil
import os
import gc

def check_memory_status():
    """Check and display current memory status."""
    print("=" * 60)
    print("QUICK MEMORY STATUS CHECK")
    print("=" * 60)
    
    # Get system memory information
    system_memory = psutil.virtual_memory()
    total_mb = system_memory.total / (1024 * 1024)
    available_mb = system_memory.available / (1024 * 1024)
    used_mb = total_mb - available_mb
    usage_percent = system_memory.percent
    
    # Get current process memory
    process = psutil.Process(os.getpid())
    process_memory_mb = process.memory_info().rss / (1024 * 1024)
    
    print(f"System Memory:")
    print(f"  Total: {total_mb:,.0f} MB")
    print(f"  Used: {used_mb:,.0f} MB")
    print(f"  Available: {available_mb:,.0f} MB")
    print(f"  Usage: {usage_percent:.1f}%")
    
    print(f"\nCurrent Process:")
    print(f"  Memory Usage: {process_memory_mb:.1f} MB")
    print(f"  % of System Total: {(process_memory_mb/total_mb)*100:.2f}%")
    
    # Memory pressure assessment
    print(f"\nMemory Pressure Assessment:")
    if available_mb < 500:
        pressure_level = "🔴 CRITICAL"
        recommendation = "Immediate action required - close applications or restart"
    elif available_mb < 1000:
        pressure_level = "🟠 HIGH"
        recommendation = "Close unnecessary applications to free memory"
    elif available_mb < 2000:
        pressure_level = "🟡 MEDIUM"
        recommendation = "Monitor memory usage, consider optimization"
    else:
        pressure_level = "🟢 LOW"
        recommendation = "Memory usage is healthy"
    
    print(f"  Level: {pressure_level}")
    print(f"  Recommendation: {recommendation}")
    
    # Optimization suggestions
    print(f"\nOptimization Suggestions:")
    suggestions = []
    
    if usage_percent > 90:
        suggestions.append("🔴 System memory usage is very high - restart applications")
    
    if available_mb < 1000:
        suggestions.append("🟠 Enable streaming processing for large datasets")
        suggestions.append("🟠 Reduce batch sizes in algorithm configuration")
        suggestions.append("🟠 Close other memory-intensive applications")
    
    if process_memory_mb > 1000:
        suggestions.append("🟡 Current process using significant memory")
        suggestions.append("🟡 Consider running garbage collection")
        suggestions.append("🟡 Check for memory leaks in algorithm")
    
    if not suggestions:
        suggestions.append("✅ No immediate optimizations needed")
    
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    print("=" * 60)

def quick_optimize():
    """Perform quick memory optimization."""
    print("\nPerforming quick memory optimization...")
    
    # Force garbage collection
    collected = gc.collect()
    print(f"  Garbage collection: {collected} objects collected")
    
    # Get memory before and after
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / (1024 * 1024)
    
    # Force another collection
    gc.collect()
    
    memory_after = process.memory_info().rss / (1024 * 1024)
    memory_freed = memory_before - memory_after
    
    print(f"  Memory freed: {memory_freed:.1f} MB")
    print("  Quick optimization completed!")

def show_algorithm_recommendations():
    """Show algorithm-specific optimization recommendations."""
    print(f"\nAlgorithm-Specific Recommendations:")
    
    # Check if memory config is available
    try:
        from memory_config import get_memory_config
        memory_config = get_memory_config()
        config = memory_config.get_algorithm_config()
        
        print(f"  📊 Current Configuration:")
        print(f"    - Max Cache Size: {config['max_cache_size']:,}")
        print(f"    - Max PHUIs in Memory: {config['max_phuis_in_memory']:,}")
        print(f"    - Batch Size: {config['batch_size']:,}")
        print(f"    - Memory Threshold: {config['memory_threshold']:.1%}")
        
        # Check if optimizations are enabled
        optimizations = []
        if config['use_smart_caching']:
            optimizations.append("Smart Caching")
        if config['use_utility_pruning']:
            optimizations.append("Utility Pruning")
        if config['use_support_pruning']:
            optimizations.append("Support Pruning")
        if config['use_early_termination']:
            optimizations.append("Early Termination")
        if config['use_pseudo_projection']:
            optimizations.append("Pseudo-Projection")
        if config['adaptive_batching']:
            optimizations.append("Adaptive Batching")
        
        print(f"  🚀 Active Optimizations: {', '.join(optimizations)}")
        
    except ImportError:
        print(f"  ℹ️  Memory configuration not available - using default settings")
        print(f"  💡 Run 'python memory_config.py' to set up memory optimization")

if __name__ == "__main__":
    # Check current memory status
    check_memory_status()
    
    # Show algorithm recommendations
    show_algorithm_recommendations()
    
    # Ask if user wants to optimize
    print(f"\nOptions:")
    print(f"  1. Run quick memory optimization")
    print(f"  2. Exit")
    
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            quick_optimize()
            print(f"\nUpdated memory status:")
            check_memory_status()
    except KeyboardInterrupt:
        print(f"\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
    
    print(f"\nFor detailed memory monitoring, run: python memory_monitor.py")
    print(f"For memory-optimized testing, run: python test_memory_optimized.py")
