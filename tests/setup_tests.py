"""
Setup script for Federated Learning Test Suite.

This script helps set up the testing environment and validates the installation.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def create_directories():
    """Create necessary directories for test results."""
    print("📁 Creating result directories...")
    
    base_dir = Path(__file__).parent.parent
    result_dirs = [
        "results/chapter_four",
        "results/chapter_four/comprehensive",
        "results/chapter_four/federated_no_laplace", 
        "results/chapter_four/federated_with_laplace"
    ]
    
    for dir_path in result_dirs:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {dir_path}")
    
    print("✅ All directories created!")


def check_datasets():
    """Check for available datasets."""
    print("🔍 Checking for datasets...")
    
    base_dir = Path(__file__).parent.parent
    datasets = [
        "chess_data.csv",
        "mushroom_data.txt",
        "transactional_data.txt"
    ]
    
    found_datasets = []
    missing_datasets = []
    
    for dataset in datasets:
        dataset_path = base_dir / dataset
        if dataset_path.exists():
            found_datasets.append(dataset)
            print(f"   ✅ Found: {dataset}")
        else:
            missing_datasets.append(dataset)
            print(f"   ❌ Missing: {dataset}")
    
    if missing_datasets:
        print(f"\n⚠️  Missing {len(missing_datasets)} datasets:")
        for dataset in missing_datasets:
            print(f"   - {dataset}")
        print("\nNote: Tests will automatically skip missing datasets.")
    
    return len(found_datasets) > 0


def check_algorithm_files():
    """Check if required algorithm files exist."""
    print("🔍 Checking algorithm files...")
    
    base_dir = Path(__file__).parent.parent
    required_files = [
        "Alogrithm.py",
        "federated_fp_growth.py",
        "item.py",
        "itemset.py",
        "up_tree.py",
        "up_node.py"
    ]
    
    missing_files = []
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"   ✅ Found: {file_name}")
        else:
            missing_files.append(file_name)
            print(f"   ❌ Missing: {file_name}")
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required algorithm files!")
        print("Please ensure all algorithm files are in the parent directory.")
        return False
    
    print("✅ All algorithm files found!")
    return True


def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        ("numpy", "np"),
        ("pandas", "pd"), 
        ("matplotlib.pyplot", "plt"),
        ("seaborn", "sns"),
        ("psutil", None),
        ("json", None),
        ("socket", None),
        ("threading", None),
        ("pickle", None)
    ]
    
    failed_imports = []
    
    for module_name, alias in modules_to_test:
        try:
            if alias:
                exec(f"import {module_name} as {alias}")
            else:
                exec(f"import {module_name}")
            print(f"   ✅ {module_name}")
        except ImportError as e:
            failed_imports.append(module_name)
            print(f"   ❌ {module_name}: {e}")
    
    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} modules!")
        return False
    
    print("✅ All modules imported successfully!")
    return True


def get_network_info():
    """Get network information for federated setup."""
    print("🌐 Network Information for Federated Setup:")
    
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"   Hostname: {hostname}")
        print(f"   Local IP: {local_ip}")
        
        # Try to get more accurate IP
        try:
            # Connect to a remote server to get the actual local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            actual_ip = s.getsockname()[0]
            s.close()
            
            if actual_ip != local_ip:
                print(f"   Actual IP: {actual_ip}")
                print(f"   Use this IP for federated clients: {actual_ip}")
            else:
                print(f"   Use this IP for federated clients: {local_ip}")
                
        except Exception:
            print(f"   Use this IP for federated clients: {local_ip}")
            
    except Exception as e:
        print(f"   ❌ Could not determine network info: {e}")
    
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Python: {sys.version.split()[0]}")


def create_sample_config():
    """Create a sample configuration file."""
    print("⚙️  Creating sample configuration...")
    
    config_content = """# Sample Configuration for Federated Learning Tests
# Copy this file and modify as needed

# Test Parameters
MIN_UTILITY_VALUES = [50, 100, 200]
NUM_CLIENTS = 5
NUM_ROUNDS = 3
IID_DISTRIBUTION = True

# Privacy Parameters (for Laplace DP tests)
EPSILON_VALUES = [0.1, 0.5, 1.0, 2.0, 5.0]
SENSITIVITY_VALUES = [0.5, 1.0, 2.0, 5.0]

# Network Parameters
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 8888
CLIENT_TIMEOUT = 60

# Dataset Configuration
DATASETS = [
    ("chess_data.csv", [50, 100, 200]),
    ("mushroom_data.txt", [100, 200, 300]),
    ("transactional_data.txt", [500, 1000, 1500])
]

# Performance Settings
ENABLE_PSEUDO_PROJECTION = True
BATCH_SIZE = 1000
ENABLE_CACHING = True
"""
    
    config_path = Path(__file__).parent / "sample_config.py"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"   ✅ Created: {config_path}")


def main():
    """Main setup function."""
    print("="*80)
    print("FEDERATED LEARNING TEST SUITE SETUP")
    print("="*80)
    print("This script will set up your testing environment.\n")
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation.")
        return 1
    
    print()
    
    # Step 2: Create directories
    create_directories()
    print()
    
    # Step 3: Check algorithm files
    if not check_algorithm_files():
        print("❌ Setup failed due to missing algorithm files.")
        return 1
    
    print()
    
    # Step 4: Test imports
    if not test_imports():
        print("❌ Setup failed due to import errors.")
        return 1
    
    print()
    
    # Step 5: Check datasets
    check_datasets()
    print()
    
    # Step 6: Get network info
    get_network_info()
    print()
    
    # Step 7: Create sample config
    create_sample_config()
    print()
    
    # Final instructions
    print("="*80)
    print("✅ SETUP COMPLETE!")
    print("="*80)
    print("Next steps:")
    print("1. Run all tests:")
    print("   python run_all_tests.py")
    print()
    print("2. Run specific test types:")
    print("   python run_all_tests.py --type comprehensive")
    print("   python run_all_tests.py --type no_laplace")
    print("   python run_all_tests.py --type with_laplace")
    print()
    print("3. Set up network federated learning:")
    print("   Server: python test_federated_network_setup.py server")
    print("   Client: python test_federated_network_setup.py client --host <SERVER_IP>")
    print()
    print("4. Check README.md for detailed instructions")
    print("="*80)
    
    return 0


if __name__ == "__main__":
    exit(main())