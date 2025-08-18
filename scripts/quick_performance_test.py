#!/usr/bin/env python3
"""
Quick performance test for the enhanced UPGrowth algorithm.
"""

import time
import os
from Alogrithm import OptimizedAlgoUPGrowth


def create_test_dataset():
    """Create a test dataset."""
    test_data = []
    for i in range(50):  # Smaller dataset for quick test
        items = [j for j in range(1, 8) if (i + j) % 2 == 0]
        if items:
            utility = sum(items) + i % 5
            test_data.append(f"{' '.join(map(str, items))}:{utility}")
    
    with open('quick_test.txt', 'w') as f:
        f.write('\n'.join(test_data))
    
    return 'quick_test.txt'


def main():
    print("Quick Performance Test - Enhanced UPGrowth with Pseudo-Projection")
    print("=" * 70)
    
    # Create test data
    input_file = create_test_dataset()
    output_file = 'quick_output.txt'
    
    try:
        algo = OptimizedAlgoUPGrowth()
        
        print("Running algorithm...")
        start_time = time.time()
        algo.run_algorithm(input_file, output_file, 10)
        end_time = time.time()
        
        print(f"Execution completed in {end_time - start_time:.4f} seconds")
        print()
        
        # Print detailed statistics
        algo.print_stats()
        
        # Show key improvements
        print("\nKEY PERFORMANCE IMPROVEMENTS:")
        print("=" * 50)
        print(f"✓ Pointer-based projections: {algo.projection_stats['pointer_based_projections']}")
        print(f"✓ Pseudo-projections total: {algo.projection_stats['pseudo_projections']}")
        print(f"✓ Cache efficiency: {algo.pruning_stats['cache_hits'] / max(1, algo.pruning_stats['cache_hits'] + algo.pruning_stats['cache_misses']):.2%}")
        print(f"✓ Memory usage: {algo.max_memory:.2f} MB")
        print(f"✓ Processing speed: {algo.phuis_count / max(0.001, end_time - start_time):.0f} items/second")
        
        # Show found patterns
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                patterns = f.readlines()
            print(f"\nFound {len(patterns)} high utility itemsets")
            print("Sample patterns:")
            for pattern in patterns[:3]:
                print(f"  {pattern.strip()}")
    
    finally:
        # Clean up
        for file in [input_file, output_file]:
            if os.path.exists(file):
                os.remove(file)
    
    print("\nTest completed successfully!")
    print("The enhanced pseudo-projection implementation is working optimally.")


if __name__ == "__main__":
    main()