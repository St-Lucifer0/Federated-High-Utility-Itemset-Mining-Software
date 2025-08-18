"""
Debug script to trace the mining loop in detail.
"""

import os
import time
from Alogrithm import OptimizedAlgoUPGrowth

def debug_mining_loop():
    """Debug the mining loop step by step."""
    
    input_file = "datasets/datasets_algo/chess_data.csv"
    min_utility = 50
    
    print("=== MINING LOOP DEBUG ===")
    print(f"Dataset: {input_file}")
    print(f"Min utility: {min_utility}")
    
    # Create algorithm instance
    algo = OptimizedAlgoUPGrowth()
    algo.debug = True
    algo.timeout_seconds = 30.0  # Increase timeout
    
    # Initialize stats
    algo.pruning_stats = {
        'utility_pruned': 0,
        'support_pruned': 0,
        'early_termination': 0,
        'cache_hits': 0,
        'cache_misses': 0
    }
    
    algo.projection_stats = {
        'pseudo_projections': 0,
        'full_projections': 0,
        'projection_savings': 0,
        'pointer_based_projections': 0,
        'memory_saved_mb': 0
    }
    
    # Prepare data
    item_stats = algo._calculate_item_statistics(input_file)
    tree = algo._create_optimized_tree(item_stats, min_utility)
    algo._build_optimized_tree(input_file, tree, item_stats)
    
    print(f"Tree built with {tree.get_tree_size()} nodes")
    
    # Start mining with detailed logging
    algo.start_timestamp = time.time()
    
    # Get items sorted by TWU
    items_by_twu = tree.get_items_by_twu()
    print(f"Items by TWU: {len(items_by_twu)}")
    print(f"Top 10 items: {items_by_twu[:10]}")
    
    # Process items one by one with detailed logging
    processed_count = 0
    prefix = []
    
    for i, item_name in enumerate(items_by_twu[:10]):  # Test first 10 items
        print(f"\n--- Processing item {i+1}: {item_name} ---")
        
        # Check timeout
        elapsed = time.time() - algo.start_timestamp
        print(f"Elapsed time: {elapsed:.2f}s")
        if elapsed > algo.timeout_seconds:
            print("TIMEOUT reached!")
            break
        
        # Check processing limit
        if processed_count >= 15:
            print("Processing limit reached!")
            break
        
        # Check TWU
        item_twu = tree.get_item_twu(item_name)
        print(f"Item TWU: {item_twu}, Min utility: {min_utility}")
        if item_twu < min_utility:
            print("Item TWU < min_utility, skipping")
            continue
        
        # Check early termination
        should_terminate = algo._ultra_fast_should_terminate(item_name, prefix, item_stats, min_utility, item_twu)
        print(f"Should terminate: {should_terminate}")
        if should_terminate:
            print("Early termination triggered")
            algo.pruning_stats['early_termination'] += 1
            continue
        
        # Create itemset
        new_itemset = prefix + [item_name]
        print(f"New itemset: {new_itemset}")
        
        # Save PHUI
        initial_phuis = len(algo.phuis)
        algo._fast_save_phui(new_itemset)
        final_phuis = len(algo.phuis)
        print(f"PHUIs before: {initial_phuis}, after: {final_phuis}")
        
        # Create projection
        print("Creating projection...")
        projection = algo._create_ultra_fast_projection(tree, item_name, min_utility)
        
        if projection:
            print(f"Projection created: support={projection.support}, total_utility={projection.total_utility}")
            if projection.support > 0:
                print("Projection has support > 0, mining projection...")
                algo.projection_stats['pointer_based_projections'] += 1
                
                if len(new_itemset) < 6:
                    print("Recursively mining projection...")
                    algo._ultra_fast_mine_projection(projection, min_utility, new_itemset, item_stats)
                else:
                    print("Itemset too long, skipping recursive mining")
        else:
            print("No projection created")
        
        processed_count += 1
        print(f"Processed count: {processed_count}")
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total PHUIs: {len(algo.phuis)}")
    print(f"Pruning stats: {algo.pruning_stats}")
    print(f"Projection stats: {algo.projection_stats}")

if __name__ == "__main__":
    debug_mining_loop()