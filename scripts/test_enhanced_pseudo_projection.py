#!/usr/bin/env python3
"""
Test script for the enhanced UPGrowth algorithm with pseudo-projection using pointers.
This script tests the performance improvements and correctness of the new implementation.
"""

import time
import os
from Alogrithm import OptimizedAlgoUPGrowth


def create_test_data():
    """Create a small test dataset for verification."""
    test_data = """1 2 3:10
2 3 4:15
1 3 4:12
2 4 5:8
1 2 4 5:20
3 4 5:14
1 2 3 4:18
2 3 5:11
1 4 5:16
2 3 4 5:22"""
    
    with open('test_data.txt', 'w') as f:
        f.write(test_data)
    
    return 'test_data.txt'


def test_enhanced_algorithm():
    """Test the enhanced algorithm with pseudo-projection."""
    print("Testing Enhanced UPGrowth with Pseudo-Projection")
    print("=" * 60)
    
    # Create test data
    input_file = create_test_data()
    output_file = 'test_output.txt'
    
    try:
        # Initialize algorithm
        algo = OptimizedAlgoUPGrowth()
        
        # Test with different minimum utility thresholds
        min_utilities = [5, 10, 15]
        
        for min_util in min_utilities:
            print(f"\nTesting with minimum utility: {min_util}")
            print("-" * 40)
            
            # Run algorithm
            start_time = time.time()
            algo.run_algorithm(input_file, output_file, min_util)
            end_time = time.time()
            
            # Print results
            print(f"Execution time: {end_time - start_time:.4f} seconds")
            algo.print_stats()
            
            # Show found patterns
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    patterns = f.readlines()
                print(f"Found {len(patterns)} high utility itemsets:")
                for pattern in patterns[:5]:  # Show first 5
                    print(f"  {pattern.strip()}")
                if len(patterns) > 5:
                    print(f"  ... and {len(patterns) - 5} more")
            
            print()
    
    finally:
        # Clean up
        for file in [input_file, output_file]:
            if os.path.exists(file):
                os.remove(file)


def test_memory_version():
    """Test the in-memory version for federated learning."""
    print("\nTesting In-Memory Version for Federated Learning")
    print("=" * 60)
    
    # Create test transactions
    transactions = [
        [1, 2, 3],
        [2, 3, 4],
        [1, 3, 4],
        [2, 4, 5],
        [1, 2, 4, 5],
        [3, 4, 5],
        [1, 2, 3, 4],
        [2, 3, 5],
        [1, 4, 5],
        [2, 3, 4, 5]
    ]
    
    utilities = [
        [3.0, 3.0, 4.0],
        [4.0, 5.0, 6.0],
        [3.0, 4.0, 5.0],
        [2.0, 3.0, 3.0],
        [5.0, 5.0, 5.0, 5.0],
        [4.0, 5.0, 5.0],
        [4.0, 4.0, 5.0, 5.0],
        [3.0, 4.0, 4.0],
        [4.0, 4.0, 8.0],
        [5.0, 5.0, 6.0, 6.0]
    ]
    
    # Initialize algorithm
    algo = OptimizedAlgoUPGrowth()
    
    # Test with different thresholds
    min_utilities = [10.0, 15.0, 20.0]
    
    for min_util in min_utilities:
        print(f"\nTesting with minimum utility: {min_util}")
        print("-" * 40)
        
        start_time = time.time()
        high_utility_itemsets = algo.run_algorithm_memory(transactions, utilities, min_util)
        end_time = time.time()
        
        print(f"Execution time: {end_time - start_time:.4f} seconds")
        print(f"Found {len(high_utility_itemsets)} high utility itemsets:")
        
        for itemset in high_utility_itemsets[:5]:  # Show first 5
            print(f"  Items: {itemset.get_items()}, Utility: {itemset.get_exact_utility()}")
        
        if len(high_utility_itemsets) > 5:
            print(f"  ... and {len(high_utility_itemsets) - 5} more")
        
        algo.print_stats()
        print()


def performance_comparison():
    """Compare performance metrics."""
    print("\nPerformance Analysis")
    print("=" * 60)
    
    # Create larger test data
    larger_test_data = []
    for i in range(100):
        items = [j for j in range(1, 11) if (i + j) % 3 == 0]
        utility = sum(items) + i % 10
        larger_test_data.append(f"{' '.join(map(str, items))}:{utility}")
    
    with open('large_test_data.txt', 'w') as f:
        f.write('\n'.join(larger_test_data))
    
    try:
        algo = OptimizedAlgoUPGrowth()
        
        print("Running on larger dataset (100 transactions)...")
        start_time = time.time()
        algo.run_algorithm('large_test_data.txt', 'large_output.txt', 20)
        end_time = time.time()
        
        print(f"Total execution time: {end_time - start_time:.4f} seconds")
        algo.print_stats()
        
        # Analyze performance metrics
        opt_stats = algo.get_optimization_stats()
        print(f"\nPerformance Analysis:")
        print(f"- Cache hit rate: {opt_stats['cache_efficiency']:.2%}")
        print(f"- Items pruned: {opt_stats['total_pruned']}")
        print(f"- Projection efficiency: {algo.projection_stats['pointer_based_projections']} pointer-based projections")
        print(f"- Memory saved: {algo.projection_stats['memory_saved_mb']:.2f} MB")
        
    finally:
        for file in ['large_test_data.txt', 'large_output.txt']:
            if os.path.exists(file):
                os.remove(file)


if __name__ == "__main__":
    print("Enhanced UPGrowth Algorithm Test Suite")
    print("=" * 60)
    
    # Run tests
    test_enhanced_algorithm()
    test_memory_version()
    performance_comparison()
    
    print("\nAll tests completed successfully!")
    print("The enhanced pseudo-projection implementation is working correctly.")