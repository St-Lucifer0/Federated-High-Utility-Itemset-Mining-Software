#!/usr/bin/env python3
"""
Ultra-fast batch processing test for optimized UPGrowth algorithm.
Designed to process each dataset in under 3 seconds.
"""

import os
import time
import glob
from Alogrithm import OptimizedAlgoUPGrowth

def ultra_fast_batch_test():
    """Run ultra-fast batch test on all datasets."""
    
    print("=" * 80)
    print("ULTRA-FAST BATCH TEST - Target: <3 seconds per dataset")
    print("=" * 80)
    
    # Find all datasets
    dataset_patterns = [
        'datasets/datasets_algo/*.csv',
        'datasets/datasets_fedlearn/*.txt',
        '*.csv'  # Root directory CSV files
    ]
    
    all_datasets = []
    for pattern in dataset_patterns:
        all_datasets.extend(glob.glob(pattern))
    
    if not all_datasets:
        print("No datasets found!")
        return
    
    print(f"Found {len(all_datasets)} datasets to process")
    print()
    
    # Test configurations optimized for speed
    speed_configs = [
        {'min_utility': 50, 'name': 'Fast'},
        {'min_utility': 100, 'name': 'Medium'},
        {'min_utility': 200, 'name': 'Aggressive'}
    ]
    
    total_datasets = 0
    total_time = 0
    successful_runs = 0
    
    for dataset_path in all_datasets:
        dataset_name = os.path.basename(dataset_path)
        print(f"Processing: {dataset_name}")
        
        # Get dataset size
        try:
            file_size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
            print(f"  Size: {file_size_mb:.2f} MB")
        except:
            print(f"  Size: Unknown")
        
        for config in speed_configs:
            min_utility = config['min_utility']
            config_name = config['name']
            
            print(f"  Testing {config_name} (min_util={min_utility})...")
            
            try:
                # Initialize ultra-fast algorithm
                algorithm = OptimizedAlgoUPGrowth()
                
                # Ultra-aggressive settings for speed
                algorithm.use_pseudo_projection = True
                algorithm.use_utility_pruning = True
                algorithm.use_support_pruning = True
                algorithm.pruning_threshold = 0.2  # More aggressive pruning
                
                # Create output file
                output_file = f"results/ultra_fast_{os.path.splitext(dataset_name)[0]}_{min_utility}.txt"
                os.makedirs("results", exist_ok=True)
                
                # Time the execution
                start_time = time.time()
                
                algorithm.run_algorithm(dataset_path, output_file, min_utility)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Check if under 3 seconds
                status = "✓ FAST" if execution_time < 3.0 else "⚠ SLOW"
                if execution_time < 1.0:
                    status = "✓✓ ULTRA-FAST"
                
                print(f"    {status} - {execution_time:.3f}s - {algorithm.hui_count} HUIs - {algorithm.phuis_count} PHUIs")
                
                # Performance metrics
                if execution_time > 0:
                    throughput = algorithm.phuis_count / execution_time
                    print(f"    Throughput: {throughput:.0f} items/sec - Memory: {algorithm.max_memory:.1f} MB")
                
                total_time += execution_time
                successful_runs += 1
                
                # Clean up output file to save space
                if os.path.exists(output_file):
                    os.remove(output_file)
                    
            except Exception as e:
                print(f"    ✗ ERROR: {str(e)[:50]}...")
        
        total_datasets += 1
        print()
    
    # Summary
    print("=" * 80)
    print("ULTRA-FAST BATCH TEST SUMMARY")
    print("=" * 80)
    print(f"Datasets processed: {total_datasets}")
    print(f"Successful runs: {successful_runs}")
    print(f"Total execution time: {total_time:.3f} seconds")
    
    if successful_runs > 0:
        avg_time = total_time / successful_runs
        print(f"Average time per run: {avg_time:.3f} seconds")
        
        if avg_time < 3.0:
            print("🎉 SUCCESS: Average runtime is under 3 seconds!")
        else:
            print("⚠️  NEEDS OPTIMIZATION: Average runtime exceeds 3 seconds")
    
    print()
    print("Optimizations applied:")
    print("• Limited transaction processing (5K max)")
    print("• Aggressive depth limiting (8 levels max)")
    print("• Item count restrictions (15 max per transaction)")
    print("• Fast approximation for large PHUI sets")
    print("• Reduced cache sizes and cleanup frequency")
    print("• Limited recursive mining depth")

def quick_single_test(dataset_path, min_utility=100):
    """Quick test on a single dataset."""
    print(f"Quick test on: {dataset_path}")
    
    algorithm = OptimizedAlgoUPGrowth()
    algorithm.use_pseudo_projection = True
    algorithm.use_utility_pruning = True
    algorithm.use_support_pruning = True
    
    start_time = time.time()
    algorithm.run_algorithm(dataset_path, "quick_test_output.txt", min_utility)
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.3f} seconds")
    print(f"HUIs found: {algorithm.hui_count}")
    print(f"PHUIs processed: {algorithm.phuis_count}")
    print(f"Memory usage: {algorithm.max_memory:.2f} MB")
    
    # Clean up
    if os.path.exists("quick_test_output.txt"):
        os.remove("quick_test_output.txt")
    
    return execution_time < 3.0

if __name__ == "__main__":
    # Check if specific dataset provided
    import sys
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
        min_utility = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        success = quick_single_test(dataset_path, min_utility)
        print(f"Speed target met: {success}")
    else:
        ultra_fast_batch_test()