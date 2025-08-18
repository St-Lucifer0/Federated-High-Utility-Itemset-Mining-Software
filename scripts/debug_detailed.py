"""
Detailed debug script to trace the HUI mining process step by step.
"""

import os
from Alogrithm import OptimizedAlgoUPGrowth

def debug_detailed_mining():
    """Debug the HUI mining process in detail."""
    
    input_file = "datasets/datasets_algo/chess_data.csv"
    output_file = "debug_output.txt"
    min_utility = 50  # Start with a reasonable threshold
    
    print("=== DETAILED DEBUG: HUI Mining Process ===")
    print(f"Dataset: {input_file}")
    print(f"Min utility: {min_utility}")
    
    # Create algorithm instance with debug enabled
    algo = OptimizedAlgoUPGrowth()
    algo.debug = True
    
    # Step 1: Calculate item statistics
    print("\n1. Calculating item statistics...")
    item_stats = algo._calculate_item_statistics(input_file)
    print(f"   Items found: {len(item_stats)}")
    
    # Show items that pass utility threshold
    items_above_threshold = [(item, stats) for item, stats in item_stats.items() 
                           if stats['twu'] >= min_utility]
    print(f"   Items with TWU >= {min_utility}: {len(items_above_threshold)}")
    
    if not items_above_threshold:
        print("   ERROR: No items pass the TWU threshold!")
        return
    
    # Step 2: Create tree
    print("\n2. Creating UPTree...")
    tree = algo._create_optimized_tree(item_stats, min_utility)
    promising_items = tree.get_promising_items()
    print(f"   Promising items: {len(promising_items)}")
    
    if not promising_items:
        print("   ERROR: No promising items in tree!")
        return
    
    # Step 3: Build tree
    print("\n3. Building tree from transactions...")
    algo._build_optimized_tree(input_file, tree, item_stats)
    print(f"   Tree built successfully")
    print(f"   Tree size: {tree.get_tree_size()} nodes")
    print(f"   Tree depth: {tree.get_depth()}")
    
    # Step 4: Mine itemsets
    print("\n4. Mining itemsets...")
    initial_phuis_count = len(algo.phuis)
    algo._optimized_upgrowth(tree, min_utility, [], item_stats)
    final_phuis_count = len(algo.phuis)
    
    print(f"   PHUIs found: {final_phuis_count}")
    print(f"   PHUIs added during mining: {final_phuis_count - initial_phuis_count}")
    
    if final_phuis_count == 0:
        print("   ERROR: No PHUIs generated during mining!")
        return
    
    # Show some PHUIs
    print("   Sample PHUIs:")
    for i, phui in enumerate(algo.phuis[:10]):
        print(f"     PHUI {i+1}: {phui.get_items()} (initial utility: {phui.utility})")
    
    # Step 5: Calculate exact utilities
    print("\n5. Calculating exact utilities...")
    algo._calculate_exact_utilities_optimized(input_file)
    
    # Show PHUIs with exact utilities
    print("   PHUIs with exact utilities:")
    hui_count = 0
    for i, phui in enumerate(algo.phuis[:10]):
        exact_utility = phui.get_exact_utility()
        is_hui = exact_utility >= min_utility
        if is_hui:
            hui_count += 1
        print(f"     PHUI {i+1}: {phui.get_items()} -> Utility: {exact_utility} {'(HUI)' if is_hui else '(not HUI)'}")
    
    print(f"\n   Total HUIs with utility >= {min_utility}: {hui_count}")
    
    # Step 6: Write results
    print("\n6. Writing results...")
    with open(output_file, 'w') as writer:
        algo.writer = writer
        algo._write_results(min_utility)
    
    print(f"   HUIs written: {algo.hui_count}")
    print(f"   Results saved to: {output_file}")
    
    # Show final results
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            content = f.read().strip()
            if content:
                print("   Sample results:")
                lines = content.split('\n')
                for i, line in enumerate(lines[:5]):
                    print(f"     {line}")
                if len(lines) > 5:
                    print(f"     ... and {len(lines) - 5} more")
            else:
                print("   ERROR: Output file is empty!")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Items in dataset: {len(item_stats)}")
    print(f"Items passing TWU threshold: {len(items_above_threshold)}")
    print(f"Promising items in tree: {len(promising_items)}")
    print(f"PHUIs generated: {final_phuis_count}")
    print(f"Final HUIs: {algo.hui_count}")

if __name__ == "__main__":
    debug_detailed_mining()