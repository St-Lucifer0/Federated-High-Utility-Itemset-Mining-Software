"""
Debug script to understand why no HUIs are found.
"""

import os
from Alogrithm import OptimizedAlgoUPGrowth

def debug_hui_mining():
    """Debug the HUI mining process step by step."""
    
    # Use the chess dataset
    input_file = "datasets/datasets_algo/chess_data.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    print("=== DEBUG: HUI Mining Process ===")
    print(f"Dataset: {input_file}")
    
    # Check dataset content
    print("\n1. Dataset Analysis:")
    with open(input_file, 'r') as f:
        lines = f.readlines()
        print(f"   Total lines: {len(lines)}")
        print("   Sample transactions:")
        for i, line in enumerate(lines[:5]):
            print(f"     {i+1}: {line.strip()}")
    
    # Test with different minimum utility values
    test_utilities = [10, 20, 30, 50, 100]
    
    for min_util in test_utilities:
        print(f"\n2. Testing with min_utility = {min_util}")
        
        # Create algorithm instance
        algo = OptimizedAlgoUPGrowth()
        algo.debug = True
        
        # Calculate item statistics manually
        print("   Calculating item statistics...")
        item_stats = algo._calculate_item_statistics(input_file)
        
        print(f"   Items found: {len(item_stats)}")
        if item_stats:
            # Show top 10 items by TWU
            sorted_items = sorted(item_stats.items(), key=lambda x: x[1]['twu'], reverse=True)
            print("   Top 10 items by TWU:")
            for i, (item, stats) in enumerate(sorted_items[:10]):
                print(f"     Item {item}: TWU={stats['twu']}, Support={stats['support']}")
        
        # Create tree
        print("   Creating UPTree...")
        tree = algo._create_optimized_tree(item_stats, min_util)
        promising_items = tree.get_promising_items()
        
        print(f"   Promising items (TWU >= {min_util}): {len(promising_items)}")
        if promising_items:
            print(f"   Promising items: {promising_items[:10]}...")  # Show first 10
        
        # Check if any items pass the threshold
        items_above_threshold = [(item, stats['twu']) for item, stats in item_stats.items() 
                               if stats['twu'] >= min_util]
        print(f"   Items with TWU >= {min_util}: {len(items_above_threshold)}")
        
        if items_above_threshold:
            print("   Items above threshold:")
            for item, twu in items_above_threshold[:10]:
                print(f"     Item {item}: TWU={twu}")
        
        print(f"   Result: {'PASS' if promising_items else 'FAIL - No promising items'}")
        
        if promising_items:
            print("   This threshold should find HUIs!")
            break
        else:
            print("   This threshold is too high - no items pass TWU filter")
    
    # Find the maximum TWU to suggest a good threshold
    if item_stats:
        max_twu = max(stats['twu'] for stats in item_stats.values())
        avg_twu = sum(stats['twu'] for stats in item_stats.values()) / len(item_stats)
        print(f"\n3. TWU Statistics:")
        print(f"   Maximum TWU: {max_twu}")
        print(f"   Average TWU: {avg_twu:.2f}")
        print(f"   Suggested min_utility: {int(avg_twu * 0.1)} to {int(avg_twu * 0.5)}")

if __name__ == "__main__":
    debug_hui_mining()