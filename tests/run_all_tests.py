"""
Simple test runner for all federated learning experiments.

This script provides an easy way to run all tests with different configurations.
"""

import os
import sys
import time
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test_suite(test_type: str = "all", quick: bool = False):
    """Run specified test suite."""
    
    print("="*80)
    print("FEDERATED LEARNING TEST SUITE RUNNER")
    print("="*80)
    print(f"Test Type: {test_type}")
    print(f"Quick Mode: {quick}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    start_time = time.time()
    
    if test_type in ["all", "comprehensive"]:
        print("\n🚀 Running Comprehensive Test Suite...")
        try:
            from run_comprehensive_federated_tests import main as run_comprehensive
            run_comprehensive()
            print("✅ Comprehensive tests completed successfully!")
        except Exception as e:
            print(f"❌ Comprehensive tests failed: {e}")
    
    elif test_type in ["all", "no_laplace"]:
        print("\n🔓 Running Tests WITHOUT Laplace DP...")
        try:
            from test_federated_without_laplace import main as run_no_laplace
            run_no_laplace()
            print("✅ No-Laplace tests completed successfully!")
        except Exception as e:
            print(f"❌ No-Laplace tests failed: {e}")
    
    elif test_type in ["all", "with_laplace"]:
        print("\n🔒 Running Tests WITH Laplace DP...")
        try:
            from test_federated_with_laplace import main as run_with_laplace
            run_with_laplace()
            print("✅ Laplace DP tests completed successfully!")
        except Exception as e:
            print(f"❌ Laplace DP tests failed: {e}")
    
    elif test_type == "network":
        print("\n🌐 Network Test Setup Instructions:")
        print("1. Start server on main laptop:")
        print("   python test_federated_network_setup.py server --host 0.0.0.0 --port 8888")
        print("2. Connect clients from other laptops:")
        print("   python test_federated_network_setup.py client --host <SERVER_IP> --client-name laptop1")
        print("3. See README.md for detailed network setup instructions")
        return
    
    total_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("TEST SUITE EXECUTION COMPLETE")
    print("="*80)
    print(f"Total Execution Time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 Results Location:")
    print("   - Comprehensive: results/chapter_four/comprehensive/")
    print("   - No Laplace: results/chapter_four/federated_no_laplace/")
    print("   - With Laplace: results/chapter_four/federated_with_laplace/")
    print("\n📈 Key Files to Check:")
    print("   - comprehensive_federated_report.json (main results)")
    print("   - comprehensive_summary.csv (for analysis)")
    print("   - *.png files (visualizations)")
    print("="*80)


def check_requirements():
    """Check if required dependencies are available."""
    required_modules = [
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'psutil'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required modules:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nInstall missing modules with:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    return True


def check_datasets():
    """Check if required datasets are available."""
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    datasets = [
        'chess_data.csv',
        'mushroom_data.txt'
    ]
    
    available_datasets = []
    missing_datasets = []
    
    for dataset in datasets:
        dataset_path = os.path.join(parent_dir, dataset)
        if os.path.exists(dataset_path):
            available_datasets.append(dataset)
        else:
            missing_datasets.append(dataset)
    
    print(f"📁 Available datasets: {len(available_datasets)}")
    for dataset in available_datasets:
        print(f"   ✅ {dataset}")
    
    if missing_datasets:
        print(f"📁 Missing datasets: {len(missing_datasets)}")
        for dataset in missing_datasets:
            print(f"   ❌ {dataset}")
        print("\nNote: Tests will skip missing datasets automatically.")
    
    return len(available_datasets) > 0


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Federated Learning Test Suite Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                    # Run all tests
  python run_all_tests.py --type comprehensive  # Run comprehensive tests only
  python run_all_tests.py --type no_laplace     # Run tests without Laplace DP
  python run_all_tests.py --type with_laplace   # Run tests with Laplace DP
  python run_all_tests.py --type network        # Show network setup instructions
  python run_all_tests.py --quick               # Run with reduced test cases
        """
    )
    
    parser.add_argument(
        '--type', 
        choices=['all', 'comprehensive', 'no_laplace', 'with_laplace', 'network'],
        default='all',
        help='Type of tests to run (default: all)'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run tests with reduced configurations for faster execution'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check requirements and datasets, do not run tests'
    )
    
    args = parser.parse_args()
    
    # Check requirements
    print("🔍 Checking Requirements...")
    if not check_requirements():
        print("❌ Requirements check failed. Please install missing dependencies.")
        return 1
    
    print("✅ All required modules are available.")
    
    # Check datasets
    print("\n🔍 Checking Datasets...")
    if not check_datasets():
        print("❌ No datasets found. Please ensure datasets are in the parent directory.")
        return 1
    
    if args.check_only:
        print("\n✅ All checks passed. Ready to run tests!")
        return 0
    
    # Run tests
    try:
        run_test_suite(args.type, args.quick)
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())