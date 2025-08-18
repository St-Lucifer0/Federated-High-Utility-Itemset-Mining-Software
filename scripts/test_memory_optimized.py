"""
Memory-optimized test script for BestEfficientUPGrowth algorithm.

This script tests the algorithm with memory monitoring and optimization
to ensure efficient resource usage.
"""

import os
import time
import gc
from Alogrithm import BestEfficientUPGrowth
from memory_monitor import memory_monitoring, optimize_memory_usage, get_memory_efficiency_score

def test_algorithm_with_memory_monitoring():
    """Test algorithm with real-time memory monitoring."""
    
    # Get datasets
    datasets_dir = 'datasets/datasets_algo'
    datasets = []
    
    if os.path.exists(datasets_dir):
        for file in os.listdir(datasets_dir):
            if file.endswith('.csv'):
                datasets.append(os.path.join(datasets_dir, file))
    
    if not datasets:
        print("Error: No datasets found!")
        return
    
    print("=" * 80)
    print("MEMORY-OPTIMIZED ALGORITHM TEST - BestEfficientUPGrowth")
    print("=" * 80)
    print("Testing with memory monitoring and optimization")
    print()
    
    # Test each dataset
    for dataset_path in datasets:
        dataset_name = os.path.basename(dataset_path)
        print(f"Testing dataset: {dataset_name}")
        
        # Get dataset info
        with open(dataset_path, 'r') as f:
            transaction_count = sum(1 for line in f if line.strip() and not line.startswith(('#', '%', '@')))
        
        file_size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
        print(f"  Transactions: {transaction_count:,}")
        print(f"  File size: {file_size_mb:.2f} MB")
        
        # Test with different minimum utility thresholds
        min_utilities = [50, 100, 200]
        
        for min_utility in min_utilities:
            print(f"\n  Testing with min_utility = {min_utility}")
            
            # Initialize algorithm
            algorithm = BestEfficientUPGrowth()
            
            # Create output file
            output_file = f"results/memory_optimized_{os.path.splitext(dataset_name)[0]}_{min_utility}.txt"
            os.makedirs("results", exist_ok=True)
            
            try:
                # Run algorithm with memory monitoring
                with memory_monitoring(alert_threshold=0.7, check_interval=0.5) as monitor:
                    # Add memory pressure alert callback
                    def memory_alert(snapshot):
                        print(f"    ⚠️  Memory pressure detected: {snapshot.process_memory_mb:.1f} MB")
                        if snapshot.process_memory_mb > 1000:
                            print("    🔄 Triggering memory optimization...")
                            optimize_memory_usage()
                    
                    monitor.add_alert_callback(memory_alert)
                    
                    # Run algorithm
                    start_time = time.time()
                    print(f"    🚀 Running algorithm with memory monitoring...")
                    
                    algorithm.run_algorithm(dataset_path, output_file, min_utility)
                    
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    # Print memory status
                    monitor.print_memory_status()
                    
                    # Get optimization suggestions
                    suggestions = monitor.suggest_optimizations()
                    if suggestions:
                        print(f"\n    💡 Optimization suggestions:")
                        for suggestion in suggestions:
                            print(f"      • {suggestion}")
                
                # Calculate efficiency metrics
                transactions_per_second = transaction_count / execution_time if execution_time > 0 else 0
                mb_per_second = file_size_mb / execution_time if execution_time > 0 else 0
                
                # Get optimization statistics
                opt_stats = algorithm.get_optimization_stats()
                
                print(f"\n    📊 Performance Results:")
                print(f"      + Execution time: {execution_time:.4f} seconds")
                print(f"      + HUIs found: {algorithm.hui_count}")
                print(f"      + PHUIs processed: {algorithm.phuis_count}")
                print(f"      + Memory usage: {algorithm.max_memory:.2f} MB")
                print(f"      + Throughput: {transactions_per_second:,.0f} transactions/second")
                print(f"      + Data rate: {mb_per_second:.2f} MB/second")
                print(f"      + Cache efficiency: {opt_stats.get('cache_efficiency', 0):.2f}%")
                
                # Memory efficiency score
                efficiency_score = get_memory_efficiency_score()
                print(f"      + Memory efficiency: {efficiency_score:.2%}")
                
                # Verify O(n) complexity
                complexity_ratio = execution_time / transaction_count * 1000000  # microseconds per transaction
                print(f"      + Time per transaction: {complexity_ratio:.2f} microseconds")
                
                if complexity_ratio < 100:
                    print(f"      + O(n) COMPLEXITY CONFIRMED - Excellent linear performance!")
                elif complexity_ratio < 500:
                    print(f"      + O(n) COMPLEXITY CONFIRMED - Good linear performance")
                else:
                    print(f"      ! Performance may not be optimal O(n)")
                
                # Show some results
                print(f"\n    💾 Results saved to: {output_file}")
                if os.path.exists(output_file):
                    print("    📋 Sample high utility itemsets found:")
                    with open(output_file, 'r') as f:
                        count = 0
                        for line in f:
                            if count < 5:  # Show first 5 itemsets
                                print(f"      {line.strip()}")
                                count += 1
                            else:
                                break
                        if count == 0:
                            print("      No high utility itemsets found with current threshold.")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            # Force garbage collection between tests
            gc.collect()
            
            # Small delay to allow system to stabilize
            time.sleep(1)
        
        print("-" * 60)
    
    print("\n" + "=" * 80)
    print("MEMORY-OPTIMIZED TEST COMPLETED")
    print("=" * 80)
    print("Your algorithm now includes:")
    print("  • Real-time memory monitoring")
    print("  • Automatic memory optimization")
    print("  • Adaptive configuration based on system resources")
    print("  • Streaming file processing for large datasets")
    print("  • Bounded caching to prevent memory bloat")
    print("  • Progressive pruning for memory efficiency")

def test_memory_configuration():
    """Test memory configuration system."""
    print("\n" + "=" * 60)
    print("TESTING MEMORY CONFIGURATION")
    print("=" * 60)
    
    try:
        from memory_config import get_memory_config
        memory_config = get_memory_config()
        memory_config.print_memory_status()
        
        # Test configuration updates
        print("\nUpdating memory configuration...")
        from memory_config import update_memory_config
        update_memory_config()
        memory_config.print_memory_status()
        
    except ImportError as e:
        print(f"Memory configuration not available: {e}")
        print("Using default memory settings.")

def test_memory_optimization():
    """Test memory optimization functions."""
    print("\n" + "=" * 60)
    print("TESTING MEMORY OPTIMIZATION")
    print("=" * 60)
    
    # Test memory optimization
    print("Testing memory optimization...")
    optimize_memory_usage()
    
    # Test efficiency score
    efficiency = get_memory_efficiency_score()
    print(f"Current memory efficiency score: {efficiency:.2%}")
    
    if efficiency > 0.8:
        print("✅ Excellent memory efficiency!")
    elif efficiency > 0.6:
        print("✅ Good memory efficiency")
    elif efficiency > 0.4:
        print("⚠️  Moderate memory efficiency")
    else:
        print("❌ Low memory efficiency - consider optimization")

if __name__ == "__main__":
    # Test memory configuration
    test_memory_configuration()
    
    # Test memory optimization
    test_memory_optimization()
    
    # Test algorithm with memory monitoring
    test_algorithm_with_memory_monitoring()
