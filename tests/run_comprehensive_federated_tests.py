"""
Comprehensive test runner for all federated learning experiments.

This script runs both federated learning tests (with and without Laplace DP)
and generates a unified report covering all Chapter 4 requirements.

Copyright (c) 2024 - Comprehensive Federated Testing
"""

import os
import sys
import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, Any, List
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_federated_without_laplace import FederatedTestWithoutLaplace
from test_federated_with_laplace import FederatedTestWithLaplace


class ComprehensiveFederatedTester:
    """Comprehensive tester that runs all federated learning experiments."""
    
    def __init__(self, results_dir: str = "results/chapter_four/comprehensive"):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize individual testers
        self.tester_no_laplace = FederatedTestWithoutLaplace(
            os.path.join(results_dir, "no_laplace")
        )
        self.tester_with_laplace = FederatedTestWithLaplace(
            os.path.join(results_dir, "with_laplace")
        )
        
        self.comprehensive_results = {}
    
    def run_all_tests(self):
        """Run all comprehensive federated learning tests."""
        print("="*80)
        print("COMPREHENSIVE FEDERATED LEARNING TEST SUITE")
        print("="*80)
        print("This test suite covers all Chapter 4 requirements:")
        print("- 4.3: Pseudo-projection and incremental learning effectiveness")
        print("- 4.4: Enhanced FP-Growth algorithm performance")
        print("- 4.5: Federated learning with and without Laplace DP")
        print("="*80)
        
        # Test datasets with different characteristics
        test_configurations = [
            {
                'dataset': 'chess_data.csv',
                'min_utilities': [50, 100, 200],
                'description': 'Dense, long transactions dataset'
            },
            {
                'dataset': 'mushroom_data.txt',
                'min_utilities': [100, 200, 300],
                'description': 'Dense dataset with categorical features'
            }
        ]
        
        # Add transactional dataset if available
        transactional_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'transactional_data.txt'
        )
        if os.path.exists(transactional_path):
            test_configurations.append({
                'dataset': 'transactional_data.txt',
                'min_utilities': [500, 1000, 1500],
                'description': 'Large sparse transactional dataset'
            })
        
        start_time = time.time()
        
        for config in test_configurations:
            dataset_name = config['dataset']
            dataset_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                dataset_name
            )
            
            if not os.path.exists(dataset_path):
                print(f"Dataset not found: {dataset_path}")
                continue
            
            print(f"\n{'='*60}")
            print(f"TESTING DATASET: {dataset_name}")
            print(f"Description: {config['description']}")
            print(f"{'='*60}")
            
            dataset_results = self.run_dataset_tests(dataset_path, config['min_utilities'])
            self.comprehensive_results[dataset_name] = dataset_results
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_unified_report(total_time)
        
        # Create comprehensive visualizations
        self.create_comprehensive_visualizations()
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TESTING COMPLETE")
        print(f"{'='*80}")
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Results saved in: {self.results_dir}")
    
    def run_dataset_tests(self, dataset_path: str, min_utilities: List[int]) -> Dict[str, Any]:
        """Run all tests for a specific dataset."""
        dataset_results = {}
        
        for min_utility in min_utilities:
            print(f"\n--- Testing with min_utility = {min_utility} ---")
            
            test_key = f"min_util_{min_utility}"
            test_results = {}
            
            try:
                # 1. Run centralized baseline
                print("Running centralized baseline...")
                centralized_result = self.tester_no_laplace.run_centralized_baseline(
                    dataset_path, min_utility
                )
                test_results['centralized'] = centralized_result
                
                # 2. Test pseudo-projection effectiveness
                print("Testing pseudo-projection effectiveness...")
                pp_result = self.tester_no_laplace.test_pseudo_projection_effectiveness(
                    dataset_path, min_utility
                )
                test_results['pseudo_projection'] = pp_result
                
                # 3. Run federated without Laplace DP
                print("Running federated learning without Laplace DP...")
                federated_no_dp = self.tester_no_laplace.run_federated_without_laplace(
                    dataset_path, min_utility, num_clients=5, num_rounds=3, iid=True
                )
                test_results['federated_no_dp'] = federated_no_dp
                
                # 4. Test epsilon impact (with Laplace DP)
                print("Testing epsilon impact...")
                epsilon_impact = self.tester_with_laplace.test_epsilon_impact(
                    dataset_path, min_utility, epsilon_values=[0.1, 0.5, 1.0, 2.0, 5.0]
                )
                test_results['epsilon_impact'] = epsilon_impact
                
                # 5. Compare with/without Laplace DP
                print("Comparing with/without Laplace DP...")
                dp_comparison = self.tester_with_laplace.compare_with_without_laplace(
                    dataset_path, min_utility, epsilon=1.0
                )
                test_results['dp_comparison'] = dp_comparison
                
                # 6. Test robustness (IID vs Non-IID)
                print("Testing robustness with non-IID data...")
                robustness = self.tester_with_laplace.test_robustness_non_iid(
                    dataset_path, min_utility, epsilon=1.0
                )
                test_results['robustness'] = robustness
                
                # 7. Scalability test (only for first min_utility to save time)
                if min_utility == min_utilities[0]:
                    print("Running scalability test...")
                    scalability = self.tester_no_laplace.run_scalability_test(
                        dataset_path, min_utility
                    )
                    test_results['scalability'] = scalability
                
                dataset_results[test_key] = test_results
                
                # Print summary for this configuration
                self.print_test_summary(test_key, test_results)
                
            except Exception as e:
                print(f"Error in test configuration {test_key}: {e}")
                traceback.print_exc()
                dataset_results[test_key] = {'error': str(e)}
        
        return dataset_results
    
    def print_test_summary(self, test_key: str, results: Dict[str, Any]):
        """Print summary of test results."""
        print(f"\n--- SUMMARY FOR {test_key} ---")
        
        # Centralized vs Federated comparison
        if 'centralized' in results and 'federated_no_dp' in results:
            cent_huis = results['centralized'].get('num_huis', 0)
            fed_huis = results['federated_no_dp'].get('num_global_huis', 0)
            cent_time = results['centralized'].get('runtime_seconds', 0)
            fed_time = results['federated_no_dp'].get('runtime_seconds', 0)
            
            print(f"Centralized HUIs: {cent_huis}, Runtime: {cent_time:.2f}s")
            print(f"Federated HUIs: {fed_huis}, Runtime: {fed_time:.2f}s")
            
            if cent_huis > 0:
                accuracy = (fed_huis / cent_huis) * 100
                print(f"Federated Accuracy: {accuracy:.1f}%")
        
        # Privacy impact
        if 'dp_comparison' in results:
            dp_comp = results['dp_comparison']
            if 'privacy_utility_tradeoff' in dp_comp:
                tradeoff = dp_comp['privacy_utility_tradeoff']
                print(f"Privacy Cost - HUI Loss: {tradeoff.get('hui_loss_percent', 0):.1f}%")
                print(f"Privacy Cost - Utility Loss: {tradeoff.get('utility_loss_percent', 0):.1f}%")
        
        # Pseudo-projection effectiveness
        if 'pseudo_projection' in results and 'improvements' in results['pseudo_projection']:
            improvements = results['pseudo_projection']['improvements']
            print(f"Pseudo-projection - Runtime Improvement: {improvements.get('runtime_improvement_percent', 0):.1f}%")
            print(f"Pseudo-projection - Memory Improvement: {improvements.get('memory_improvement_percent', 0):.1f}%")
    
    def generate_unified_report(self, total_execution_time: float):
        """Generate a unified comprehensive report."""
        report = {
            'test_metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_suite': 'Comprehensive Federated FP-Growth Testing',
                'total_execution_time_seconds': total_execution_time,
                'chapter_requirements_covered': [
                    '4.3: Pseudo-projection and incremental learning',
                    '4.4: Enhanced FP-Growth algorithm',
                    '4.5: Federated learning with Laplace DP'
                ]
            },
            'test_results': self.comprehensive_results,
            'summary_statistics': self.calculate_summary_statistics(),
            'key_findings': self.extract_key_findings()
        }
        
        # Save comprehensive report
        report_path = os.path.join(self.results_dir, 'comprehensive_federated_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate CSV summary for easy analysis
        self.generate_csv_summary()
        
        print(f"\nComprehensive report saved to: {report_path}")
        return report
    
    def calculate_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics across all tests."""
        stats = {
            'total_datasets_tested': len(self.comprehensive_results),
            'total_configurations_tested': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'average_federated_accuracy': 0,
            'average_privacy_cost': 0,
            'average_pseudo_projection_improvement': 0
        }
        
        accuracies = []
        privacy_costs = []
        pp_improvements = []
        
        for dataset_results in self.comprehensive_results.values():
            for config_results in dataset_results.values():
                stats['total_configurations_tested'] += 1
                
                if 'error' in config_results:
                    stats['failed_tests'] += 1
                    continue
                
                stats['successful_tests'] += 1
                
                # Calculate federated accuracy
                if ('centralized' in config_results and 
                    'federated_no_dp' in config_results):
                    cent_huis = config_results['centralized'].get('num_huis', 0)
                    fed_huis = config_results['federated_no_dp'].get('num_global_huis', 0)
                    if cent_huis > 0:
                        accuracy = (fed_huis / cent_huis) * 100
                        accuracies.append(accuracy)
                
                # Calculate privacy cost
                if 'dp_comparison' in config_results:
                    dp_comp = config_results['dp_comparison']
                    if 'privacy_utility_tradeoff' in dp_comp:
                        hui_loss = dp_comp['privacy_utility_tradeoff'].get('hui_loss_percent', 0)
                        privacy_costs.append(hui_loss)
                
                # Calculate pseudo-projection improvement
                if 'pseudo_projection' in config_results:
                    pp_result = config_results['pseudo_projection']
                    if 'improvements' in pp_result:
                        runtime_imp = pp_result['improvements'].get('runtime_improvement_percent', 0)
                        pp_improvements.append(runtime_imp)
        
        if accuracies:
            stats['average_federated_accuracy'] = sum(accuracies) / len(accuracies)
        if privacy_costs:
            stats['average_privacy_cost'] = sum(privacy_costs) / len(privacy_costs)
        if pp_improvements:
            stats['average_pseudo_projection_improvement'] = sum(pp_improvements) / len(pp_improvements)
        
        return stats
    
    def extract_key_findings(self) -> List[str]:
        """Extract key findings from all tests."""
        findings = []
        
        # Analyze results and extract insights
        stats = self.calculate_summary_statistics()
        
        findings.append(f"Tested {stats['total_datasets_tested']} datasets with {stats['total_configurations_tested']} configurations")
        findings.append(f"Success rate: {(stats['successful_tests']/max(stats['total_configurations_tested'], 1)*100):.1f}%")
        
        if stats['average_federated_accuracy'] > 0:
            findings.append(f"Average federated accuracy: {stats['average_federated_accuracy']:.1f}%")
        
        if stats['average_privacy_cost'] > 0:
            findings.append(f"Average privacy cost (HUI loss): {stats['average_privacy_cost']:.1f}%")
        
        if stats['average_pseudo_projection_improvement'] > 0:
            findings.append(f"Average pseudo-projection runtime improvement: {stats['average_pseudo_projection_improvement']:.1f}%")
        
        # Add specific insights based on results
        for dataset_name, dataset_results in self.comprehensive_results.items():
            for config_key, config_results in dataset_results.items():
                if 'error' in config_results:
                    continue
                
                # Check for exceptional performance
                if 'pseudo_projection' in config_results:
                    pp_result = config_results['pseudo_projection']
                    if 'improvements' in pp_result:
                        runtime_imp = pp_result['improvements'].get('runtime_improvement_percent', 0)
                        if runtime_imp > 30:
                            findings.append(f"Significant pseudo-projection improvement on {dataset_name}: {runtime_imp:.1f}%")
        
        return findings
    
    def generate_csv_summary(self):
        """Generate CSV summary for easy analysis."""
        summary_data = []
        
        for dataset_name, dataset_results in self.comprehensive_results.items():
            for config_key, config_results in dataset_results.items():
                if 'error' in config_results:
                    continue
                
                row = {
                    'dataset': dataset_name,
                    'configuration': config_key,
                    'centralized_huis': config_results.get('centralized', {}).get('num_huis', 0),
                    'centralized_runtime': config_results.get('centralized', {}).get('runtime_seconds', 0),
                    'federated_huis': config_results.get('federated_no_dp', {}).get('num_global_huis', 0),
                    'federated_runtime': config_results.get('federated_no_dp', {}).get('runtime_seconds', 0),
                    'federated_accuracy': 0,
                    'privacy_hui_loss': 0,
                    'privacy_utility_loss': 0,
                    'pp_runtime_improvement': 0,
                    'pp_memory_improvement': 0
                }
                
                # Calculate derived metrics
                if row['centralized_huis'] > 0:
                    row['federated_accuracy'] = (row['federated_huis'] / row['centralized_huis']) * 100
                
                if 'dp_comparison' in config_results:
                    dp_comp = config_results['dp_comparison']
                    if 'privacy_utility_tradeoff' in dp_comp:
                        tradeoff = dp_comp['privacy_utility_tradeoff']
                        row['privacy_hui_loss'] = tradeoff.get('hui_loss_percent', 0)
                        row['privacy_utility_loss'] = tradeoff.get('utility_loss_percent', 0)
                
                if 'pseudo_projection' in config_results:
                    pp_result = config_results['pseudo_projection']
                    if 'improvements' in pp_result:
                        improvements = pp_result['improvements']
                        row['pp_runtime_improvement'] = improvements.get('runtime_improvement_percent', 0)
                        row['pp_memory_improvement'] = improvements.get('memory_improvement_percent', 0)
                
                summary_data.append(row)
        
        # Save CSV
        if summary_data:
            df = pd.DataFrame(summary_data)
            csv_path = os.path.join(self.results_dir, 'comprehensive_summary.csv')
            df.to_csv(csv_path, index=False)
            print(f"CSV summary saved to: {csv_path}")
    
    def create_comprehensive_visualizations(self):
        """Create comprehensive visualization dashboard."""
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 16))
        
        # Create a 3x3 grid of subplots
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Extract data for visualizations
        datasets = []
        centralized_huis = []
        federated_huis = []
        centralized_times = []
        federated_times = []
        privacy_costs = []
        pp_improvements = []
        
        for dataset_name, dataset_results in self.comprehensive_results.items():
            for config_key, config_results in dataset_results.items():
                if 'error' in config_results:
                    continue
                
                datasets.append(f"{dataset_name}_{config_key}")
                centralized_huis.append(config_results.get('centralized', {}).get('num_huis', 0))
                federated_huis.append(config_results.get('federated_no_dp', {}).get('num_global_huis', 0))
                centralized_times.append(config_results.get('centralized', {}).get('runtime_seconds', 0))
                federated_times.append(config_results.get('federated_no_dp', {}).get('runtime_seconds', 0))
                
                # Privacy cost
                if 'dp_comparison' in config_results:
                    dp_comp = config_results['dp_comparison']
                    if 'privacy_utility_tradeoff' in dp_comp:
                        privacy_costs.append(dp_comp['privacy_utility_tradeoff'].get('hui_loss_percent', 0))
                    else:
                        privacy_costs.append(0)
                else:
                    privacy_costs.append(0)
                
                # Pseudo-projection improvement
                if 'pseudo_projection' in config_results:
                    pp_result = config_results['pseudo_projection']
                    if 'improvements' in pp_result:
                        pp_improvements.append(pp_result['improvements'].get('runtime_improvement_percent', 0))
                    else:
                        pp_improvements.append(0)
                else:
                    pp_improvements.append(0)
        
        if not datasets:
            print("No data available for visualization")
            return
        
        # 1. HUI Count Comparison (Centralized vs Federated)
        ax1 = fig.add_subplot(gs[0, 0])
        x = range(len(datasets))
        width = 0.35
        ax1.bar([i - width/2 for i in x], centralized_huis, width, label='Centralized', alpha=0.8)
        ax1.bar([i + width/2 for i in x], federated_huis, width, label='Federated', alpha=0.8)
        ax1.set_xlabel('Test Configurations')
        ax1.set_ylabel('Number of HUIs')
        ax1.set_title('HUI Count: Centralized vs Federated')
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Runtime Comparison
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.bar([i - width/2 for i in x], centralized_times, width, label='Centralized', alpha=0.8)
        ax2.bar([i + width/2 for i in x], federated_times, width, label='Federated', alpha=0.8)
        ax2.set_xlabel('Test Configurations')
        ax2.set_ylabel('Runtime (seconds)')
        ax2.set_title('Runtime: Centralized vs Federated')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Federated Accuracy
        ax3 = fig.add_subplot(gs[0, 2])
        accuracies = [(f/max(c, 1))*100 for c, f in zip(centralized_huis, federated_huis)]
        ax3.bar(x, accuracies, alpha=0.8, color='green')
        ax3.set_xlabel('Test Configurations')
        ax3.set_ylabel('Accuracy (%)')
        ax3.set_title('Federated Learning Accuracy')
        ax3.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Perfect Accuracy')
        ax3.legend()
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Privacy Cost Analysis
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.bar(x, privacy_costs, alpha=0.8, color='red')
        ax4.set_xlabel('Test Configurations')
        ax4.set_ylabel('HUI Loss (%)')
        ax4.set_title('Privacy Cost (HUI Loss)')
        ax4.tick_params(axis='x', rotation=45)
        
        # 5. Pseudo-Projection Effectiveness
        ax5 = fig.add_subplot(gs[1, 1])
        colors = ['green' if imp > 0 else 'red' for imp in pp_improvements]
        ax5.bar(x, pp_improvements, alpha=0.8, color=colors)
        ax5.set_xlabel('Test Configurations')
        ax5.set_ylabel('Runtime Improvement (%)')
        ax5.set_title('Pseudo-Projection Effectiveness')
        ax5.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax5.tick_params(axis='x', rotation=45)
        
        # 6. Privacy-Utility Tradeoff Scatter
        ax6 = fig.add_subplot(gs[1, 2])
        if privacy_costs and accuracies:
            ax6.scatter(privacy_costs, accuracies, alpha=0.7, s=100)
            ax6.set_xlabel('Privacy Cost (HUI Loss %)')
            ax6.set_ylabel('Federated Accuracy (%)')
            ax6.set_title('Privacy-Utility Tradeoff')
            ax6.grid(True, alpha=0.3)
        
        # 7. Summary Statistics
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('off')
        
        # Calculate and display summary statistics
        stats = self.calculate_summary_statistics()
        summary_text = f"""
        COMPREHENSIVE TEST SUMMARY
        
        Total Datasets Tested: {stats['total_datasets_tested']}
        Total Configurations: {stats['total_configurations_tested']}
        Successful Tests: {stats['successful_tests']}
        Success Rate: {(stats['successful_tests']/max(stats['total_configurations_tested'], 1)*100):.1f}%
        
        Average Federated Accuracy: {stats['average_federated_accuracy']:.1f}%
        Average Privacy Cost: {stats['average_privacy_cost']:.1f}%
        Average Pseudo-Projection Improvement: {stats['average_pseudo_projection_improvement']:.1f}%
        """
        
        ax7.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
        
        # Save comprehensive visualization
        plot_path = os.path.join(self.results_dir, 'comprehensive_federated_analysis.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Comprehensive visualizations saved to: {plot_path}")


def main():
    """Main function to run comprehensive federated learning tests."""
    print("Starting Comprehensive Federated Learning Test Suite...")
    
    # Initialize comprehensive tester
    tester = ComprehensiveFederatedTester()
    
    # Run all tests
    tester.run_all_tests()
    
    print("\nComprehensive testing completed successfully!")
    print(f"All results available in: {tester.results_dir}")


if __name__ == "__main__":
    main()