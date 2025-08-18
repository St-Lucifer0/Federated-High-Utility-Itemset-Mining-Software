"""
Main script to run high utility itemset mining algorithms on user-selected datasets.
"""

import os
import time
from Alogrithm import OptimizedAlgoUPGrowth


def get_available_datasets():
    """Get list of available CSV datasets in the datasets/datasets_algo directory."""
    csv_files = []
    datasets_dir = 'datasets/datasets_algo'
    if os.path.exists(datasets_dir):
        for file in os.listdir(datasets_dir):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(datasets_dir, file))
    return sorted(csv_files)


def test_datasets():
    """Test the selected dataset with all algorithms."""

    # Get available datasets
    available_datasets = get_available_datasets()

    if not available_datasets:
        print("Error: No CSV datasets found!")
        print("Please make sure you have CSV dataset files in the datasets/datasets_algo directory.")
        return

    # Let user select dataset
    print("Available datasets:")
    for i, dataset in enumerate(available_datasets, 1):
        print(f"  {i}. {os.path.basename(dataset)}")

    while True:
        try:
            choice = int(input(f"\nSelect a dataset (1-{len(available_datasets)}): "))
            if 1 <= choice <= len(available_datasets):
                selected_file = available_datasets[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(available_datasets)}")
        except ValueError:
            print("Please enter a valid number")

    # Check if selected dataset exists
    if not os.path.exists(selected_file):
        print(f"Error: {selected_file} not found!")
        print("Please make sure the dataset file is in the current directory.")
        return

    print("=" * 80)
    print("Testing Dataset with High Utility Itemset Mining")
    print("=" * 80)
    print(f"Dataset: {selected_file}")

    # Check dataset size
    with open(selected_file, 'r') as f:
        transaction_count = sum(1 for line in f)
    print(f"Total transactions: {transaction_count}")

    # Show sample transactions
    print("\nSample transactions:")
    with open(selected_file, 'r') as f:
        for i, line in enumerate(f):
            if i < 5:
                print(f"  {line.strip()}")
            else:
                break

    # Set minimum utility threshold
    min_utility = int(input("Enter a minimum utility: "))  # Adjust based on your dataset characteristics
    print(f"\nMinimum utility threshold: {min_utility}")

    # Test algorithms
    algorithms = [
        ("Best Efficient UPGrowth", OptimizedAlgoUPGrowth())
    ]

    results = []

    for name, algorithm in algorithms:
        print(f"\n{'-' * 60}")
        print(f"Testing {name} Algorithm")
        print(f"{'-' * 60}")

        # Configure optimization settings for efficient algorithm
        if name == "Efficient UPGrowth":
            algorithm.use_utility_pruning = True
            algorithm.use_support_pruning = True
            algorithm.use_early_termination = True
            algorithm.use_smart_caching = True

        # Configure settings for best efficient algorithm
        if name == "Best Efficient UPGrowth":
            algorithm.use_pseudo_projection = True
            algorithm.adaptive_batching = True

        print("Configuration:")
        if hasattr(algorithm, 'use_utility_pruning'):
            print(f"  Utility pruning: {algorithm.use_utility_pruning}")
        if hasattr(algorithm, 'use_support_pruning'):
            print(f"  Support pruning: {algorithm.use_support_pruning}")
        if hasattr(algorithm, 'use_early_termination'):
            print(f"  Early termination: {algorithm.use_early_termination}")
        if hasattr(algorithm, 'use_smart_caching'):
            print(f"  Smart caching: {algorithm.use_smart_caching}")
        if hasattr(algorithm, 'use_pseudo_projection'):
            print(f"  Pseudo-projection: {algorithm.use_pseudo_projection}")
        if hasattr(algorithm, 'adaptive_batching'):
            print(f"  Adaptive batching: {algorithm.adaptive_batching}")

        # Create output file
        dataset_name = os.path.splitext(os.path.basename(selected_file))[0]
        output_file = f"results/{dataset_name}_results_{name.lower().replace(' ', '_')}.txt"
        
        # Ensure results directory exists
        os.makedirs("results", exist_ok=True)

        try:
            # Run algorithm
            start_time = time.time()
            print(f"\nRunning {name} algorithm...")

            algorithm.run_algorithm(selected_file, output_file, min_utility)

            end_time = time.time()
            execution_time = end_time - start_time

            # Get statistics
            algorithm.print_stats()

            # Get optimization statistics if available
            opt_stats = {}
            if hasattr(algorithm, 'get_optimization_stats'):
                opt_stats = algorithm.get_optimization_stats()

            print(f"\n--- Performance Results ---")
            print(f"Execution time: {execution_time:.4f} seconds")
            print(f"High utility itemsets found: {algorithm.hui_count}")
            print(f"Memory usage: {algorithm.max_memory:.2f} MB")

            if opt_stats:
                print(f"Cache efficiency: {opt_stats.get('cache_efficiency', 0):.2%}")
                print(f"Total items pruned: {opt_stats.get('total_pruned', 0)}")
                if opt_stats.get('paths_processed', 0) > 0:
                    print(f"Paths processed: {opt_stats.get('paths_processed', 0):,}")
                if opt_stats.get('batches_created', 0) > 0:
                    print(f"Batches created: {opt_stats.get('batches_created', 0):,}")

            # Show some results
            print(f"\nResults saved to: {output_file}")
            if os.path.exists(output_file):
                print("Sample high utility itemsets found:")
                with open(output_file, 'r') as f:
                    count = 0
                    for line in f:
                        if count < 10:  # Show first 10 itemsets
                            print(f"  {line.strip()}")
                            count += 1
                        else:
                            break
                    if count == 0:
                        print("  No high utility itemsets found with current threshold.")

            results.append({
                'name': name,
                'execution_time': execution_time,
                'hui_count': algorithm.hui_count,
                'memory_usage': algorithm.max_memory,
                'opt_stats': opt_stats
            })

        except Exception as e:
            print(f"Error running {name}: {e}")
            results.append({
                'name': name,
                'execution_time': float('inf'),
                'hui_count': 0,
                'memory_usage': 0,
                'opt_stats': {}
            })

    # Print summary comparison
    print(f"\n{'=' * 80}")
    print("ALGORITHM COMPARISON SUMMARY")
    print(f"{'=' * 80}")
    print(f"{'Algorithm':<25} {'Time (s)':<12} {'HUIs Found':<12} {'Memory (MB)':<12} {'Cache Eff.':<12}")
    print(f"{'-' * 80}")

    for result in results:
        cache_eff = result['opt_stats'].get('cache_efficiency', 0)
        print(f"{result['name']:<25} {result['execution_time']:<12.4f} "
              f"{result['hui_count']:<12} {result['memory_usage']:<12.2f} "
              f"{cache_eff:<12.2%}")

    # Find best performing algorithm
    valid_results = [r for r in results if r['execution_time'] != float('inf')]
    if valid_results:
        fastest = min(valid_results, key=lambda x: x['execution_time'])
        most_itemsets = max(valid_results, key=lambda x: x['hui_count'])

        print(f"\n--- Performance Highlights ---")
        print(f"Fastest algorithm: {fastest['name']} ({fastest['execution_time']:.4f}s)")
        print(f"Most itemsets found: {most_itemsets['name']} ({most_itemsets['hui_count']} itemsets)")

    print(f"\n{'=' * 80}")
    print("Dataset testing completed!")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    test_datasets()