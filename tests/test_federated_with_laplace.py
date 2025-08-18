"""
Comprehensive test suite for Federated FP-Growth algorithm WITH Laplace Differential Privacy.

This test suite covers Chapter 4.5 requirements:
- Impact of Laplace DP on HUI mining
- Privacy budget analysis
- Noise impact quantification
- Privacy-utility tradeoff evaluation
- Comparison with non-private federated approach

Copyright (c) 2024 - Federated FP-Growth Testing (With Laplace DP)
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
import copy

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from federated_fp_growth import FederatedFPGrowth, FederatedClient, LaplaceDP
from Alogrithm import OptimizedAlgoUPGrowth
from itemset import Itemset
from item import Item


class FederatedTestWithLaplace:
    """Comprehensive tester for federated learning HUIM experiments with Laplace DP."""
    
    def __init__(self, results_dir: str = "results/chapter_four/federated_with_laplace"):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.test_results = {}
        self.privacy_metrics = {}
        
    def load_and_split_dataset(self, dataset_path: str, num_clients: int = 5, 
                              iid: bool = True) -> Tuple[List[List[List[int]]], List[List[List[float]]]]:
        """Load dataset and split among clients (IID or non-IID)."""
        print(f"Loading dataset: {dataset_path}")
        
        transactions = []
        utilities = []
        
        try:
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
                
                # Handle chess dataset format
                if 'class' in df.columns:
                    feature_cols = [col for col in df.columns if col != 'class']
                    for _, row in df.iterrows():
                        transaction = []
                        utility = []
                        for i, col in enumerate(feature_cols):
                            if pd.notna(row[col]) and row[col] != 0:
                                transaction.append(i + 1)
                                utility.append(float(abs(row[col])))
                        if transaction:
                            transactions.append(transaction)
                            utilities.append(utility)
                else:
                    for _, row in df.iterrows():
                        transaction = []
                        utility = []
                        for i, val in enumerate(row):
                            if pd.notna(val) and val != 0:
                                transaction.append(i + 1)
                                utility.append(float(abs(val)))
                        if transaction:
                            transactions.append(transaction)
                            utilities.append(utility)
            else:
                # Handle text format
                with open(dataset_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if ':' in line:
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
                        else:
                            items = [int(x) for x in line.split()]
                            if items:
                                transactions.append(items)
                                utilities.append([1.0] * len(items))
                                
        except Exception as e:
            print(f"Error loading dataset {dataset_path}: {e}")
            return [], []
        
        print(f"Loaded {len(transactions)} transactions")
        
        # Split data among clients
        client_transactions = [[] for _ in range(num_clients)]
        client_utilities = [[] for _ in range(num_clients)]
        
        if iid:
            for i, (trans, util) in enumerate(zip(transactions, utilities)):
                client_idx = i % num_clients
                client_transactions[client_idx].append(trans)
                client_utilities[client_idx].append(util)
        else:
            sorted_data = sorted(zip(transactions, utilities), key=lambda x: len(x[0]))
            chunk_size = len(sorted_data) // num_clients
            
            for i in range(num_clients):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < num_clients - 1 else len(sorted_data)
                
                for j in range(start_idx, end_idx):
                    client_transactions[i].append(sorted_data[j][0])
                    client_utilities[i].append(sorted_data[j][1])
        
        return client_transactions, client_utilities
    
    def run_federated_with_laplace(self, dataset_path: str, min_utility: int, 
                                 epsilon: float = 1.0, sensitivity: float = 1.0,
                                 num_clients: int = 5, num_rounds: int = 3,
                                 iid: bool = True) -> Dict[str, Any]:
        """Run federated FP-Growth with Laplace DP."""
        print(f"\n=== Running Federated FP-Growth (With Laplace DP) ===")
        print(f"Dataset: {dataset_path}")
        print(f"Min Utility: {min_utility}")
        print(f"Epsilon: {epsilon}, Sensitivity: {sensitivity}")
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
        
        # Initialize Laplace DP mechanism
        laplace_dp = LaplaceDP(epsilon=epsilon, sensitivity=sensitivity)
        
        # Initialize federated system with Laplace DP
        federated_system = FederatedFPGrowth(
            min_utility=min_utility,
            use_laplace_dp=True,
            laplace_dp=laplace_dp
        )
        
        # Create clients
        clients = []
        for i in range(num_clients):
            if client_transactions[i]:
                client = FederatedClient(
                    client_id=i,
                    transactions=client_transactions[i],
                    utilities=client_utilities[i],
                    min_utility=min_utility
                )
                clients.append(client)
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Run federated learning with Laplace DP
            global_huis, round_results = federated_system.run_federated_learning(
                clients, num_rounds
            )
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Calculate privacy metrics
            cumulative_epsilon = epsilon * num_rounds  # Simple composition
            privacy_cost_per_round = epsilon
            
            # Calculate communication cost
            total_communication = 0
            for round_result in round_results:
                if 'communication_cost' in round_result:
                    total_communication += round_result['communication_cost']
            
            # Client statistics
            client_stats = []
            total_noise_added = 0
            for i, client in enumerate(clients):
                local_huis = client.get_local_huis()
                
                # Estimate noise impact (simplified)
                original_utility = sum(hui.utility for hui in local_huis) if local_huis else 0
                noise_estimate = len(local_huis) * laplace_dp.noise_scale if local_huis else 0
                total_noise_added += noise_estimate
                
                client_stats.append({
                    'client_id': client.client_id,
                    'num_transactions': len(client.transactions),
                    'num_local_huis': len(local_huis),
                    'local_total_utility': original_utility,
                    'estimated_noise_added': noise_estimate
                })
            
            results = {
                'algorithm': 'Federated FP-Growth (With Laplace DP)',
                'dataset': os.path.basename(dataset_path),
                'min_utility': min_utility,
                'privacy_parameters': {
                    'epsilon': epsilon,
                    'sensitivity': sensitivity,
                    'noise_scale': laplace_dp.noise_scale,
                    'cumulative_epsilon': cumulative_epsilon,
                    'privacy_cost_per_round': privacy_cost_per_round
                },
                'num_clients': len(clients),
                'num_rounds': num_rounds,
                'iid_distribution': iid,
                'num_global_huis': len(global_huis),
                'total_utility': sum(hui.utility for hui in global_huis) if global_huis else 0,
                'avg_utility': sum(hui.utility for hui in global_huis) / len(global_huis) if global_huis else 0,
                'runtime_seconds': end_time - start_time,
                'memory_usage_mb': end_memory - start_memory,
                'communication_cost_mb': total_communication / (1024 * 1024),
                'privacy_metrics': {
                    'total_noise_added': total_noise_added,
                    'noise_to_signal_ratio': total_noise_added / max(sum(hui.utility for hui in global_huis), 1) if global_huis else 0,
                    'privacy_budget_consumed': cumulative_epsilon
                },
                'client_statistics': client_stats,
                'round_results': round_results,
                'hui_details': [{'items': hui.get_items(), 'utility': hui.utility} for hui in global_huis[:10]]
            }
            
            return results
            
        except Exception as e:
            print(f"Error in federated learning with Laplace DP: {e}")
            traceback.print_exc()
            return {
                'algorithm': 'Federated FP-Growth (With Laplace DP)',
                'dataset': os.path.basename(dataset_path),
                'min_utility': min_utility,
                'error': str(e),
                'num_huis': 0,
                'runtime_seconds': 0,
                'memory_usage_mb': 0
            }
    
    def test_epsilon_impact(self, dataset_path: str, min_utility: int, 
                           epsilon_values: List[float] = [0.1, 0.5, 1.0, 2.0, 5.0]) -> Dict[str, Any]:
        """Test impact of different epsilon values on HUI quality."""
        print(f"\n=== Testing Epsilon Impact ===")
        
        epsilon_results = {}
        
        for epsilon in epsilon_values:
            print(f"Testing epsilon = {epsilon}")
            
            result = self.run_federated_with_laplace(
                dataset_path, min_utility, epsilon=epsilon, 
                num_clients=5, num_rounds=3, iid=True
            )
            
            epsilon_results[epsilon] = {
                'num_huis': result.get('num_global_huis', 0),
                'total_utility': result.get('total_utility', 0),
                'avg_utility': result.get('avg_utility', 0),
                'runtime_seconds': result.get('runtime_seconds', 0),
                'noise_to_signal_ratio': result.get('privacy_metrics', {}).get('noise_to_signal_ratio', 0),
                'privacy_budget_consumed': result.get('privacy_metrics', {}).get('privacy_budget_consumed', 0)
            }
        
        return epsilon_results
    
    def compare_with_without_laplace(self, dataset_path: str, min_utility: int, 
                                   epsilon: float = 1.0) -> Dict[str, Any]:
        """Compare federated learning with and without Laplace DP."""
        print(f"\n=== Comparing With/Without Laplace DP ===")
        
        # Run without Laplace DP
        federated_system_no_dp = FederatedFPGrowth(
            num_clients=5,
            min_utility=min_utility,
            use_laplace_dp=False
        )
        
        client_transactions, client_utilities = self.load_and_split_dataset(
            dataset_path, num_clients=5, iid=True
        )
        
        clients = []
        for i in range(5):
            if client_transactions[i]:
                client = FederatedClient(
                    client_id=i,
                    transactions=client_transactions[i],
                    utilities=client_utilities[i],
                    min_utility=min_utility
                )
                clients.append(client)
        
        # Without Laplace DP
        start_time = time.time()
        global_huis_no_dp, _ = federated_system_no_dp.run_federated_learning(clients, 3)
        runtime_no_dp = time.time() - start_time
        
        # With Laplace DP
        result_with_dp = self.run_federated_with_laplace(
            dataset_path, min_utility, epsilon=epsilon, num_clients=5, num_rounds=3
        )
        
        comparison = {
            'without_laplace_dp': {
                'num_huis': len(global_huis_no_dp),
                'total_utility': sum(hui.utility for hui in global_huis_no_dp) if global_huis_no_dp else 0,
                'avg_utility': sum(hui.utility for hui in global_huis_no_dp) / len(global_huis_no_dp) if global_huis_no_dp else 0,
                'runtime_seconds': runtime_no_dp
            },
            'with_laplace_dp': {
                'num_huis': result_with_dp.get('num_global_huis', 0),
                'total_utility': result_with_dp.get('total_utility', 0),
                'avg_utility': result_with_dp.get('avg_utility', 0),
                'runtime_seconds': result_with_dp.get('runtime_seconds', 0),
                'privacy_cost': result_with_dp.get('privacy_metrics', {}).get('privacy_budget_consumed', 0)
            }
        }
        
        # Calculate privacy-utility tradeoff metrics
        if comparison['without_laplace_dp']['num_huis'] > 0:
            hui_loss_percent = (
                (comparison['without_laplace_dp']['num_huis'] - comparison['with_laplace_dp']['num_huis']) /
                comparison['without_laplace_dp']['num_huis'] * 100
            )
        else:
            hui_loss_percent = 0
            
        if comparison['without_laplace_dp']['total_utility'] > 0:
            utility_loss_percent = (
                (comparison['without_laplace_dp']['total_utility'] - comparison['with_laplace_dp']['total_utility']) /
                comparison['without_laplace_dp']['total_utility'] * 100
            )
        else:
            utility_loss_percent = 0
        
        comparison['privacy_utility_tradeoff'] = {
            'hui_loss_percent': hui_loss_percent,
            'utility_loss_percent': utility_loss_percent,
            'privacy_gain': epsilon,  # Privacy budget used
            'runtime_overhead_percent': (
                (comparison['with_laplace_dp']['runtime_seconds'] - comparison['without_laplace_dp']['runtime_seconds']) /
                max(comparison['without_laplace_dp']['runtime_seconds'], 0.001) * 100
            )
        }
        
        return comparison
    
    def test_sensitivity_analysis(self, dataset_path: str, min_utility: int, 
                                epsilon: float = 1.0, 
                                sensitivity_values: List[float] = [0.5, 1.0, 2.0, 5.0]) -> Dict[str, Any]:
        """Test impact of different sensitivity values."""
        print(f"\n=== Testing Sensitivity Analysis ===")
        
        sensitivity_results = {}
        
        for sensitivity in sensitivity_values:
            print(f"Testing sensitivity = {sensitivity}")
            
            result = self.run_federated_with_laplace(
                dataset_path, min_utility, epsilon=epsilon, sensitivity=sensitivity,
                num_clients=5, num_rounds=3, iid=True
            )
            
            sensitivity_results[sensitivity] = {
                'num_huis': result.get('num_global_huis', 0),
                'total_utility': result.get('total_utility', 0),
                'noise_scale': result.get('privacy_parameters', {}).get('noise_scale', 0),
                'noise_to_signal_ratio': result.get('privacy_metrics', {}).get('noise_to_signal_ratio', 0)
            }
        
        return sensitivity_results
    
    def test_robustness_non_iid(self, dataset_path: str, min_utility: int, 
                               epsilon: float = 1.0) -> Dict[str, Any]:
        """Test robustness with non-IID data distribution."""
        print(f"\n=== Testing Robustness with Non-IID Data ===")
        
        # Test IID distribution
        iid_result = self.run_federated_with_laplace(
            dataset_path, min_utility, epsilon=epsilon, 
            num_clients=5, num_rounds=3, iid=True
        )
        
        # Test non-IID distribution
        non_iid_result = self.run_federated_with_laplace(
            dataset_path, min_utility, epsilon=epsilon, 
            num_clients=5, num_rounds=3, iid=False
        )
        
        robustness_comparison = {
            'iid_distribution': {
                'num_huis': iid_result.get('num_global_huis', 0),
                'total_utility': iid_result.get('total_utility', 0),
                'avg_utility': iid_result.get('avg_utility', 0),
                'client_fairness': self._calculate_client_fairness(iid_result.get('client_statistics', []))
            },
            'non_iid_distribution': {
                'num_huis': non_iid_result.get('num_global_huis', 0),
                'total_utility': non_iid_result.get('total_utility', 0),
                'avg_utility': non_iid_result.get('avg_utility', 0),
                'client_fairness': self._calculate_client_fairness(non_iid_result.get('client_statistics', []))
            }
        }
        
        return robustness_comparison
    
    def _calculate_client_fairness(self, client_stats: List[Dict]) -> Dict[str, float]:
        """Calculate fairness metrics across clients."""
        if not client_stats:
            return {'gini_coefficient': 0, 'std_deviation': 0, 'coefficient_of_variation': 0}
        
        hui_counts = [client['num_local_huis'] for client in client_stats]
        utilities = [client['local_total_utility'] for client in client_stats]
        
        # Gini coefficient for HUI distribution
        def gini_coefficient(values):
            if not values or all(v == 0 for v in values):
                return 0
            sorted_values = sorted(values)
            n = len(values)
            cumsum = np.cumsum(sorted_values)
            return (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(cumsum))) / (n * sum(sorted_values))
        
        return {
            'hui_gini_coefficient': gini_coefficient(hui_counts),
            'utility_gini_coefficient': gini_coefficient(utilities),
            'hui_std_deviation': np.std(hui_counts),
            'utility_std_deviation': np.std(utilities),
            'hui_coefficient_of_variation': np.std(hui_counts) / max(np.mean(hui_counts), 1),
            'utility_coefficient_of_variation': np.std(utilities) / max(np.mean(utilities), 1)
        }
    
    def generate_comprehensive_report(self, test_results: Dict[str, Any], 
                                    output_file: str = "federated_with_laplace_report.json"):
        """Generate comprehensive test report."""
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_type': 'Federated FP-Growth with Laplace DP',
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
    
    def create_privacy_visualizations(self, test_results: Dict[str, Any]):
        """Create privacy-specific visualization charts."""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Epsilon impact analysis
        epsilon_data = None
        for result in test_results.values():
            if isinstance(result, dict) and 'epsilon_impact' in result:
                epsilon_data = result['epsilon_impact']
                break
        
        if epsilon_data:
            epsilons = list(epsilon_data.keys())
            hui_counts = [epsilon_data[e]['num_huis'] for e in epsilons]
            noise_ratios = [epsilon_data[e]['noise_to_signal_ratio'] for e in epsilons]
            
            # HUI count vs epsilon
            axes[0, 0].plot(epsilons, hui_counts, marker='o', linewidth=2, markersize=8, color='blue')
            axes[0, 0].set_xlabel('Privacy Budget (ε)')
            axes[0, 0].set_ylabel('Number of HUIs')
            axes[0, 0].set_title('Privacy-Utility Tradeoff: HUIs vs Epsilon')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Noise-to-signal ratio vs epsilon
            axes[0, 1].plot(epsilons, noise_ratios, marker='s', linewidth=2, markersize=8, color='red')
            axes[0, 1].set_xlabel('Privacy Budget (ε)')
            axes[0, 1].set_ylabel('Noise-to-Signal Ratio')
            axes[0, 1].set_title('Noise Impact vs Epsilon')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Privacy-utility comparison
        comparison_data = None
        for result in test_results.values():
            if isinstance(result, dict) and 'comparison' in result:
                comparison_data = result['comparison']
                break
        
        if comparison_data and 'privacy_utility_tradeoff' in comparison_data:
            tradeoff = comparison_data['privacy_utility_tradeoff']
            
            categories = ['HUI Loss', 'Utility Loss', 'Runtime Overhead']
            values = [
                tradeoff.get('hui_loss_percent', 0),
                tradeoff.get('utility_loss_percent', 0),
                tradeoff.get('runtime_overhead_percent', 0)
            ]
            
            colors = ['red', 'orange', 'yellow']
            bars = axes[1, 0].bar(categories, values, color=colors, alpha=0.7)
            axes[1, 0].set_ylabel('Loss/Overhead (%)')
            axes[1, 0].set_title('Privacy Cost Analysis')
            axes[1, 0].set_ylim(0, max(values) * 1.2 if values else 100)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                               f'{value:.1f}%', ha='center', va='bottom')
        
        # Robustness analysis (IID vs Non-IID)
        robustness_data = None
        for result in test_results.values():
            if isinstance(result, dict) and 'robustness' in result:
                robustness_data = result['robustness']
                break
        
        if robustness_data:
            distributions = ['IID', 'Non-IID']
            hui_counts = [
                robustness_data['iid_distribution']['num_huis'],
                robustness_data['non_iid_distribution']['num_huis']
            ]
            fairness_scores = [
                1 - robustness_data['iid_distribution']['client_fairness'].get('hui_gini_coefficient', 0),
                1 - robustness_data['non_iid_distribution']['client_fairness'].get('hui_gini_coefficient', 0)
            ]
            
            x = np.arange(len(distributions))
            width = 0.35
            
            axes[1, 1].bar(x - width/2, hui_counts, width, label='HUI Count', alpha=0.8)
            ax2 = axes[1, 1].twinx()
            ax2.bar(x + width/2, fairness_scores, width, label='Fairness Score', alpha=0.8, color='orange')
            
            axes[1, 1].set_xlabel('Data Distribution')
            axes[1, 1].set_ylabel('Number of HUIs', color='blue')
            ax2.set_ylabel('Fairness Score', color='orange')
            axes[1, 1].set_title('Robustness: IID vs Non-IID')
            axes[1, 1].set_xticks(x)
            axes[1, 1].set_xticklabels(distributions)
            
            # Add legends
            axes[1, 1].legend(loc='upper left')
            ax2.legend(loc='upper right')
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.results_dir, 'federated_with_laplace_privacy_analysis.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Privacy analysis visualizations saved to: {plot_path}")


def main():
    """Main function to run all federated learning tests with Laplace DP."""
    print("=== Federated FP-Growth Testing Suite (With Laplace DP) ===")
    print("Testing based on Chapter 4 structure requirements")
    
    # Initialize tester
    tester = FederatedTestWithLaplace()
    
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
                # Test epsilon impact
                epsilon_impact = tester.test_epsilon_impact(dataset_path, min_utility)
                
                # Compare with/without Laplace DP
                comparison = tester.compare_with_without_laplace(dataset_path, min_utility, epsilon=1.0)
                
                # Test sensitivity analysis (only for first min_utility)
                sensitivity_analysis = None
                if min_utility == min_utilities[0]:
                    sensitivity_analysis = tester.test_sensitivity_analysis(dataset_path, min_utility)
                
                # Test robustness with non-IID data
                robustness = tester.test_robustness_non_iid(dataset_path, min_utility, epsilon=1.0)
                
                all_results[test_key] = {
                    'epsilon_impact': epsilon_impact,
                    'comparison': comparison,
                    'sensitivity_analysis': sensitivity_analysis,
                    'robustness': robustness
                }
                
                # Print summary
                print(f"\n--- Results Summary for {test_key} ---")
                print(f"Without DP HUIs: {comparison['without_laplace_dp']['num_huis']}")
                print(f"With DP HUIs: {comparison['with_laplace_dp']['num_huis']}")
                print(f"HUI Loss: {comparison['privacy_utility_tradeoff']['hui_loss_percent']:.1f}%")
                print(f"Utility Loss: {comparison['privacy_utility_tradeoff']['utility_loss_percent']:.1f}%")
                print(f"Privacy Budget Used: {comparison['with_laplace_dp']['privacy_cost']:.2f}")
                
            except Exception as e:
                print(f"Error testing {test_key}: {e}")
                traceback.print_exc()
                all_results[test_key] = {'error': str(e)}
    
    # Generate comprehensive report
    report = tester.generate_comprehensive_report(all_results)
    
    # Create privacy-specific visualizations
    tester.create_privacy_visualizations(all_results)
    
    print(f"\n{'='*60}")
    print("FEDERATED LEARNING TESTING COMPLETE (WITH LAPLACE DP)")
    print(f"{'='*60}")
    print(f"Results saved in: {tester.results_dir}")
    print(f"Total tests completed: {len(all_results)}")
    print(f"Successful tests: {len([r for r in all_results.values() if 'error' not in r])}")


if __name__ == "__main__":
    main()