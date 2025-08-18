"""
Comprehensive test suite for Federated FP-Growth algorithm WITHOUT Laplace Differential Privacy.

This test suite covers Chapter 4.3 and 4.4 requirements:
- Performance of HUI Mining without Laplace DP
- Efficiency and Scalability
- Comparison with centralized approach
- Pseudo-projection and incremental learning effectiveness

Copyright (c) 2024 - Federated FP-Growth Testing (No DP)
"""

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Tuple, Optional
import os
import json
from datetime import datetime
import psutil
import sys
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from federated_fp_growth import FederatedFPGrowth, FederatedClient
from Alogrithm import OptimizedAlgoUPGrowth
from itemset import Itemset
from item import Item


class FederatedTestWithoutLaplace:
    """Comprehensive tester for federated learning HUIM experiments without Laplace DP."""
    
    def __init__(self, results_dir: str = "results/chapter_four/federated_no_laplace"):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.test_results = {}
        self.performance_metrics = {}
        
    def load_and_split_dataset(self, dataset_path: str, num_clients: int = 5, 
                              iid: bool = True) -> Tuple[List[List[List[int]]], List[List[List[float]]]]:
        """Load dataset and split among clients (IID or non-IID)."""
        print(f"Loading dataset: {dataset_path}")
        
        transactions = []
        utilities = []
        
        try:
            if dataset_path.endswith('.csv'):
                # Handle chess dataset format: "item1 item2 item3:utility"
                with open(dataset_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if ':' in line:
                            # Split by colon to separate items and utility
                            items_part, utility_part = line.rsplit(':', 1)
                            items = [int(x) for x in items_part.split()]
                            total_utility = float(utility_part)
                            
                            if items:
                                transactions.append(items)
                                # Distribute utility equally among items
                                item_utility = total_utility / len(items)
                                utilities.append([item_utility] * len(items))
                        else:
                            # No utility specified, use default
                            items = [int(x) for x in line.split()]
                            if items:
                                transactions.append(items)
                                utilities.append([1.0] * len(items))
            else:
                # Handle text format (mushroom, transactional)
                with open(dataset_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if ':' in line:  # Format: item1:utility1 item2:utility2
                            parts = line.split()
                            transaction = []
                            utility = []
                            for part in parts:
                                if ':' in part:
                                    item, util = part.split(':')
                                    transaction.append(int(item))
                                    utility.append(float(util))
                            if transaction:
                                transactions.append(transaction)
                                utilities.append(utility)
                        else:  # Simple format: item1 item2 item3
                            items = [int(x) for x in line.split()]
                            if items:
                                transactions.append(items)
                                utilities.append([1.0] * len(items))  # Default utility
                                
        except Exception as e:
            print(f"Error loading dataset {dataset_path}: {e}")
            return [], []
        
        print(f"Loaded {len(transactions)} transactions")
        
        # Split data among clients
        client_transactions = [[] for _ in range(num_clients)]
        client_utilities = [[] for _ in range(num_clients)]
        
        if iid:
            # IID distribution - random assignment
            for i, (trans, util) in enumerate(zip(transactions, utilities)):
                client_idx = i % num_clients
                client_transactions[client_idx].append(trans)
                client_utilities[client_idx].append(util)
        else:
            # Non-IID distribution - sort by transaction length and distribute
            sorted_data = sorted(zip(transactions, utilities), key=lambda x: len(x[0]))
            chunk_size = len(sorted_data) // num_clients
            
            for i in range(num_clients):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < num_clients - 1 else len(sorted_data)
                
                for j in range(start_idx, end_idx):
                    client_transactions[i].append(sorted_data[j][0])
                    client_utilities[i].append(sorted_data[j][1])
        
        return client_transactions, client_utilities
    
    def run_centralized_baseline(self, dataset_path: str, min_utility: int) -> Dict[str, Any]:
        """Run centralized BestEfficientUPGrowth as baseline."""
        print(f"\n=== Running Centralized Baseline ===")
        print(f"Dataset: {dataset_path}")
        print(f"Min Utility: {min_utility}")
        
        algorithm = OptimizedAlgoUPGrowth()
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Create temporary output file
            temp_output = os.path.join(self.results_dir, "temp_centralized_output.txt")
            algorithm.run_algorithm(dataset_path, temp_output, min_utility)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Get results
            huis = algorithm.phuis if hasattr(algorithm, 'phuis') else []
            
            results = {
                'algorithm': 'Centralized BestEfficientUPGrowth',
                'dataset': os.path.basename(dataset_path),
                'min_utility': min_utility,
                'num_huis': len(huis),
                'total_utility': sum(hui.utility for hui in huis) if huis else 0,
                'avg_utility': sum(hui.utility for hui in huis) / len(huis) if huis else 0,
                'runtime_seconds': end_time - start_time,
                'memory_usage_mb': end_memory - start_memory,
                'max_memory_mb': algorithm.max_memory if hasattr(algorithm, 'max_memory') else 0,
                'hui_details': [{'items': hui.get_items(), 'utility': hui.utility} for hui in huis[:10]]  # First 10 HUIs
            }
            
            # Clean up
            if os.path.exists(temp_output):
                os.remove(temp_output)
                
            return results
            
        except Exception as e:
            print(f"Error in centralized baseline: {e}")
            traceback.print_exc()
            return {
                'algorithm': 'Centralized BestEfficientUPGrowth',
                'dataset': os.path.basename(dataset_path),
                'min_utility': min_utility,
                'error': str(e),
                'num_huis': 0,
                'runtime_seconds': 0,
                'memory_usage_mb': 0
            }
    
    def run_federated_without_laplace(self, dataset_path: str, min_utility: int, 
                                    num_clients: int = 5, num_rounds: int = 3,
                                    iid: bool = True) -> Dict[str, Any]:
        """Run federated FP-Growth without Laplace DP."""
        print(f"\n=== Running Federated FP-Growth (No Laplace DP) ===")
        print(f"Dataset: {dataset_path}")
        print(f"Min Utility: {min_utility}")
        print(f"Clients: {num_clients}, Rounds: {num_rounds}, IID: {iid}")
        
        # Load and split dataset
        client_transactions, client_utilities = self.load_and_split_dataset(
            dataset_path, num_clients, iid
        )
        
        if not client_transactions or not any(client_transactions):
            return {
                'error': 'Failed to load or split dataset',
                'num_huis': 0,
                'runtime_seconds': 0
            }
        
        # Initialize federated system
        federated_system = FederatedFPGrowth(
            min_utility=min_utility,
            use_laplace_dp=False  # No Laplace DP
        )
        
        # Create clients and add them to the federated system
        for i in range(num_clients):
            if client_transactions[i]:  # Only create client if it has data
                client = FederatedClient(
                    client_id=i,
                    transactions=client_transactions[i],
                    utilities=client_utilities[i],
                    min_utility=min_utility
                )
                federated_system.add_client(client)
        
        # Set number of rounds
        federated_system.num_rounds = num_rounds
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Run federated learning
            global_huis = federated_system.run_federated_learning()
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Get performance metrics
            performance_metrics = federated_system.get_performance_metrics()
            
            # Calculate communication cost
            total_communication = sum(federated_system.communication_costs)
            
            # Client statistics
            client_stats = []
            for client in federated_system.clients:
                client_stats.append({
                    'client_id': client.client_id,
                    'num_transactions': len(client.transactions),
                    'num_local_huis': len(client.local_huis),
                    'local_total_utility': sum(hui.utility for hui in client.local_huis) if client.local_huis else 0
                })
            
            results = {
                'algorithm': 'Federated FP-Growth (No Laplace DP)',
                'dataset': os.path.basename(dataset_path),
                'min_utility': min_utility,
                'num_clients': len(federated_system.clients),
                'num_rounds': num_rounds,
                'iid_distribution': iid,
                'num_global_huis': len(global_huis),
                'total_utility': sum(hui.utility for hui in global_huis) if global_huis else 0,
                'avg_utility': sum(hui.utility for hui in global_huis) / len(global_huis) if global_huis else 0,
                'runtime_seconds': end_time - start_time,
                'memory_usage_mb': end_memory - start_memory,
                'communication_cost_mb': total_communication / (1024 * 1024),  # Convert to MB
                'client_statistics': client_stats,
                'round_results': federated_system.round_times,
                'hui_details': [{'items': hui.items, 'utility': hui.utility} for hui in global_huis[:10]]
            }
            
            return results
            
        except Exception as e:
            print(f"Error in federated learning: {e}")
            traceback.print_exc()
            return {
                'algorithm': 'Federated FP-Growth (No Laplace DP)',
                'dataset': os.path.basename(dataset_path),
                'min_utility': min_utility,
                'error': str(e),
                'num_huis': 0,
                'runtime_seconds': 0,
                'memory_usage_mb': 0
            }
    
    def test_pseudo_projection_effectiveness(self, dataset_path: str, min_utility: int) -> Dict[str, Any]:
        """Test effectiveness of pseudo-projection optimization."""
        print(f"\n=== Testing Pseudo-Projection Effectiveness ===")
        
        results = {}
        
        # Test with pseudo-projection enabled
        algorithm_with_pp = OptimizedAlgoUPGrowth()
        algorithm_with_pp.use_pseudo_projection = True
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        temp_output_pp = os.path.join(self.results_dir, "temp_pp_output.txt")
        algorithm_with_pp.run_algorithm(dataset_path, temp_output_pp, min_utility)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        results['with_pseudo_projection'] = {
            'num_huis': len(algorithm_with_pp.phuis) if hasattr(algorithm_with_pp, 'phuis') else 0,
            'runtime_seconds': end_time - start_time,
            'memory_usage_mb': end_memory - start_memory,
            'cache_hits': algorithm_with_pp.cache_hits if hasattr(algorithm_with_pp, 'cache_hits') else 0,
            'cache_misses': algorithm_with_pp.cache_misses if hasattr(algorithm_with_pp, 'cache_misses') else 0
        }
        
        # Test without pseudo-projection
        algorithm_without_pp = OptimizedAlgoUPGrowth()
        algorithm_without_pp.use_pseudo_projection = False
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        temp_output_no_pp = os.path.join(self.results_dir, "temp_no_pp_output.txt")
        algorithm_without_pp.run_algorithm(dataset_path, temp_output_no_pp, min_utility)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        results['without_pseudo_projection'] = {
            'num_huis': len(algorithm_without_pp.phuis) if hasattr(algorithm_without_pp, 'phuis') else 0,
            'runtime_seconds': end_time - start_time,
            'memory_usage_mb': end_memory - start_memory
        }
        
        # Calculate improvements
        if results['without_pseudo_projection']['runtime_seconds'] > 0:
            runtime_improvement = (
                (results['without_pseudo_projection']['runtime_seconds'] - 
                 results['with_pseudo_projection']['runtime_seconds']) /
                results['without_pseudo_projection']['runtime_seconds'] * 100
            )
        else:
            runtime_improvement = 0
            
        if results['without_pseudo_projection']['memory_usage_mb'] > 0:
            memory_improvement = (
                (results['without_pseudo_projection']['memory_usage_mb'] - 
                 results['with_pseudo_projection']['memory_usage_mb']) /
                results['without_pseudo_projection']['memory_usage_mb'] * 100
            )
        else:
            memory_improvement = 0
        
        results['improvements'] = {
            'runtime_improvement_percent': runtime_improvement,
            'memory_improvement_percent': memory_improvement,
            'hui_accuracy_percent': (
                results['with_pseudo_projection']['num_huis'] /
                max(results['without_pseudo_projection']['num_huis'], 1) * 100
            )
        }
        
        # Clean up
        for temp_file in [temp_output_pp, temp_output_no_pp]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return results
    
    def run_scalability_test(self, dataset_path: str, min_utility: int) -> Dict[str, Any]:
        """Test scalability with different numbers of clients."""
        print(f"\n=== Running Scalability Test ===")
        
        client_counts = [2, 3, 5, 8, 10]
        scalability_results = {}
        
        for num_clients in client_counts:
            print(f"Testing with {num_clients} clients...")
            
            result = self.run_federated_without_laplace(
                dataset_path, min_utility, num_clients, num_rounds=2, iid=True
            )
            
            scalability_results[num_clients] = {
                'num_huis': result.get('num_global_huis', 0),
                'runtime_seconds': result.get('runtime_seconds', 0),
                'memory_usage_mb': result.get('memory_usage_mb', 0),
                'communication_cost_mb': result.get('communication_cost_mb', 0),
                'avg_client_huis': np.mean([
                    client['num_local_huis'] for client in result.get('client_statistics', [])
                ]) if result.get('client_statistics') else 0
            }
        
        return scalability_results
    
    def generate_comprehensive_report(self, test_results: Dict[str, Any], 
                                    output_file: str = "federated_no_laplace_report.json"):
        """Generate comprehensive test report."""
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_type': 'Federated FP-Growth without Laplace DP',
            'results': test_results,
            'summary': {
                'total_tests': len(test_results),
                'successful_tests': len([r for r in test_results.values() if 'error' not in r])
            }
        }
        
        # Save report
        report_path = os.path.join(self.results_dir, output_file)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nReport saved to: {report_path}")
        return report
    
    def create_performance_visualizations(self, test_results: Dict[str, Any]):
        """Create performance visualization charts."""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Extract data for visualization
        datasets = []
        centralized_times = []
        federated_times = []
        centralized_huis = []
        federated_huis = []
        
        for test_name, result in test_results.items():
            if isinstance(result, dict) and 'centralized' in result and 'federated' in result:
                datasets.append(result['centralized'].get('dataset', test_name))
                centralized_times.append(result['centralized'].get('runtime_seconds', 0))
                federated_times.append(result['federated'].get('runtime_seconds', 0))
                centralized_huis.append(result['centralized'].get('num_huis', 0))
                federated_huis.append(result['federated'].get('num_global_huis', 0))
        
        if datasets:
            # Runtime comparison
            x = np.arange(len(datasets))
            width = 0.35
            
            axes[0, 0].bar(x - width/2, centralized_times, width, label='Centralized', alpha=0.8)
            axes[0, 0].bar(x + width/2, federated_times, width, label='Federated', alpha=0.8)
            axes[0, 0].set_xlabel('Datasets')
            axes[0, 0].set_ylabel('Runtime (seconds)')
            axes[0, 0].set_title('Runtime Comparison: Centralized vs Federated')
            axes[0, 0].set_xticks(x)
            axes[0, 0].set_xticklabels(datasets, rotation=45)
            axes[0, 0].legend()
            
            # HUI count comparison
            axes[0, 1].bar(x - width/2, centralized_huis, width, label='Centralized', alpha=0.8)
            axes[0, 1].bar(x + width/2, federated_huis, width, label='Federated', alpha=0.8)
            axes[0, 1].set_xlabel('Datasets')
            axes[0, 1].set_ylabel('Number of HUIs')
            axes[0, 1].set_title('HUI Count Comparison: Centralized vs Federated')
            axes[0, 1].set_xticks(x)
            axes[0, 1].set_xticklabels(datasets, rotation=45)
            axes[0, 1].legend()
        
        # Scalability plot (if available)
        scalability_data = None
        for result in test_results.values():
            if isinstance(result, dict) and 'scalability' in result:
                scalability_data = result['scalability']
                break
        
        if scalability_data:
            clients = list(scalability_data.keys())
            runtimes = [scalability_data[c]['runtime_seconds'] for c in clients]
            
            axes[1, 0].plot(clients, runtimes, marker='o', linewidth=2, markersize=8)
            axes[1, 0].set_xlabel('Number of Clients')
            axes[1, 0].set_ylabel('Runtime (seconds)')
            axes[1, 0].set_title('Scalability: Runtime vs Number of Clients')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Pseudo-projection effectiveness (if available)
        pp_data = None
        for result in test_results.values():
            if isinstance(result, dict) and 'pseudo_projection' in result:
                pp_data = result['pseudo_projection']
                break
        
        if pp_data and 'improvements' in pp_data:
            improvements = pp_data['improvements']
            metrics = ['Runtime', 'Memory', 'HUI Accuracy']
            values = [
                improvements.get('runtime_improvement_percent', 0),
                improvements.get('memory_improvement_percent', 0),
                improvements.get('hui_accuracy_percent', 100) - 100  # Show as improvement from 100%
            ]
            
            colors = ['green' if v > 0 else 'red' for v in values]
            axes[1, 1].bar(metrics, values, color=colors, alpha=0.7)
            axes[1, 1].set_ylabel('Improvement (%)')
            axes[1, 1].set_title('Pseudo-Projection Effectiveness')
            axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.results_dir, 'federated_no_laplace_performance.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Performance visualizations saved to: {plot_path}")


def main():
    """Main function to run all federated learning tests without Laplace DP."""
    print("=== Federated FP-Growth Testing Suite (No Laplace DP) ===")
    print("Testing based on Chapter 4 structure requirements")
    
    # Initialize tester
    tester = FederatedTestWithoutLaplace()
    
    # Test datasets
    datasets = [
        ("chess_data.csv", [50, 100, 200]),
        ("mushroom_data.txt", [100, 200, 300]),
        ("transactional_data.txt", [500, 1000, 1500])
    ]
    
    all_results = {}
    
    for dataset_name, min_utilities in datasets:
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dataset_name)
        
        if not os.path.exists(dataset_path):
            print(f"Dataset not found: {dataset_path}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Testing Dataset: {dataset_name}")
        print(f"{'='*60}")
        
        for min_utility in min_utilities:
            test_key = f"{dataset_name}_{min_utility}"
            
            try:
                # Run centralized baseline
                centralized_result = tester.run_centralized_baseline(dataset_path, min_utility)
                
                # Run federated without Laplace DP
                federated_result = tester.run_federated_without_laplace(
                    dataset_path, min_utility, num_clients=5, num_rounds=3, iid=True
                )
                
                # Test pseudo-projection effectiveness
                pp_result = tester.test_pseudo_projection_effectiveness(dataset_path, min_utility)
                
                # Run scalability test (only for first min_utility to save time)
                scalability_result = None
                if min_utility == min_utilities[0]:
                    scalability_result = tester.run_scalability_test(dataset_path, min_utility)
                
                all_results[test_key] = {
                    'centralized': centralized_result,
                    'federated': federated_result,
                    'pseudo_projection': pp_result,
                    'scalability': scalability_result
                }
                
                # Print summary
                print(f"\n--- Results Summary for {test_key} ---")
                print(f"Centralized HUIs: {centralized_result.get('num_huis', 0)}")
                print(f"Federated HUIs: {federated_result.get('num_global_huis', 0)}")
                print(f"Centralized Runtime: {centralized_result.get('runtime_seconds', 0):.2f}s")
                print(f"Federated Runtime: {federated_result.get('runtime_seconds', 0):.2f}s")
                
                if pp_result and 'improvements' in pp_result:
                    improvements = pp_result['improvements']
                    print(f"Pseudo-projection Runtime Improvement: {improvements.get('runtime_improvement_percent', 0):.1f}%")
                    print(f"Pseudo-projection Memory Improvement: {improvements.get('memory_improvement_percent', 0):.1f}%")
                
            except Exception as e:
                print(f"Error testing {test_key}: {e}")
                traceback.print_exc()
                all_results[test_key] = {'error': str(e)}
    
    # Generate comprehensive report
    report = tester.generate_comprehensive_report(all_results)
    
    # Create visualizations
    tester.create_performance_visualizations(all_results)
    
    print(f"\n{'='*60}")
    print("FEDERATED LEARNING TESTING COMPLETE (NO LAPLACE DP)")
    print(f"{'='*60}")
    print(f"Results saved in: {tester.results_dir}")
    print(f"Total tests completed: {len(all_results)}")
    print(f"Successful tests: {len([r for r in all_results.values() if 'error' not in r])}")


if __name__ == "__main__":
    main()