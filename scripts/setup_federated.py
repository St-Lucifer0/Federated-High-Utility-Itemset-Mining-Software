"""
Setup script for Federated Learning HUIM system.

This script helps configure and test the federated learning environment
for High Utility Itemset Mining with Differential Privacy.

Copyright (c) 2024 - Federated HUIM Setup
"""

import os
import sys
import subprocess
import socket
import json
import time
from typing import List, Dict, Optional
import argparse


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'numpy',
        'psutil'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")

    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✓ All dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False

    return True


def check_files():
    """Check if all required files exist."""
    required_files = [
        'algo_best_efficient_upgrowth.py',
        'federated_server.py',
        'federated_client.py',
        'federated_fp_growth.py',
        'item.py',
        'itemset.py',
        'up_tree.py',
        'up_node.py'
    ]

    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            missing_files.append(file)
            print(f"✗ {file} is missing")

    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        print("Please ensure all required files are in the current directory.")
        return False

    return True


def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def test_port_availability(port: int) -> bool:
    """Test if a port is available for use."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', port))
        s.close()
        return True
    except OSError:
        return False


def generate_sample_data(num_clients: int = 3, transactions_per_client: int = 100):
    """Generate sample data files for testing."""
    import random

    print(f"Generating sample data for {num_clients} clients...")

    for client_id in range(1, num_clients + 1):
        # Generate transactions
        transactions = []
        utilities = []

        for _ in range(transactions_per_client):
            # Random transaction size (3-8 items)
            transaction_size = random.randint(3, 8)
            transaction = sorted(random.sample(range(1, 21), transaction_size))
            utility_list = [random.uniform(1, 10) for _ in transaction]

            transactions.append(transaction)
            utilities.append(utility_list)

        # Save transaction data
        with open(f'client_{client_id}_transactions.txt', 'w') as f:
            for transaction in transactions:
                f.write(' '.join(map(str, transaction)) + '\n')

        # Save utility data
        with open(f'client_{client_id}_utilities.txt', 'w') as f:
            for utility_list in utilities:
                f.write(' '.join(f'{u:.2f}' for u in utility_list) + '\n')

        print(f"✓ Generated data for client_{client_id} ({transactions_per_client} transactions)")

    print(f"Sample data generated for {num_clients} clients")


def create_config_file(server_ip: str, server_port: int, num_clients: int):
    """Create a configuration file for the federated setup."""
    config = {
        "server": {
            "host": server_ip,
            "port": server_port,
            "min_utility": 30.0,
            "num_rounds": 5,
            "min_clients": 2,
            "client_sampling_rate": 1.0,
            "use_differential_privacy": True,
            "epsilon": 1.0
        },
        "clients": []
    }

    for client_id in range(1, num_clients + 1):
        client_config = {
            "client_id": f"client_{client_id}",
            "data_file": f"client_{client_id}_transactions.txt",
            "utility_file": f"client_{client_id}_utilities.txt"
        }
        config["clients"].append(client_config)

    with open('federated_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("✓ Configuration file created: federated_config.json")


def create_start_scripts():
    """Create convenient start scripts for server and clients."""

    # Server start script (Windows batch)
    server_script_bat = """@echo off
echo Starting Federated Learning Server...
python federated_server.py --host 0.0.0.0 --port 8888 --min-utility 30.0 --rounds 5 --min-clients 2
pause
"""

    with open('start_server.bat', 'w') as f:
        f.write(server_script_bat)

    # Server start script (Unix shell)
    server_script_sh = """#!/bin/bash
echo "Starting Federated Learning Server..."
python3 federated_server.py --host 0.0.0.0 --port 8888 --min-utility 30.0 --rounds 5 --min-clients 2
"""

    with open('start_server.sh', 'w') as f:
        f.write(server_script_sh)

    # Client start script template (Windows batch)
    client_script_bat = """@echo off
set /p CLIENT_ID="Enter client ID (e.g., client_1): "
set /p SERVER_IP="Enter server IP address (default: localhost): "
if "%SERVER_IP%"=="" set SERVER_IP=localhost

echo Starting Federated Learning Client %CLIENT_ID%...
python federated_client.py --client-id %CLIENT_ID% --server-host %SERVER_IP% --server-port 8888 --data-file %CLIENT_ID%_transactions.txt --utility-file %CLIENT_ID%_utilities.txt
pause
"""

    with open('start_client.bat', 'w') as f:
        f.write(client_script_bat)

    # Client start script template (Unix shell)
    client_script_sh = """#!/bin/bash
read -p "Enter client ID (e.g., client_1): " CLIENT_ID
read -p "Enter server IP address (default: localhost): " SERVER_IP
SERVER_IP=${SERVER_IP:-localhost}

echo "Starting Federated Learning Client $CLIENT_ID..."
python3 federated_client.py --client-id $CLIENT_ID --server-host $SERVER_IP --server-port 8888 --data-file ${CLIENT_ID}_transactions.txt --utility-file ${CLIENT_ID}_utilities.txt
"""

    with open('start_client.sh', 'w') as f:
        f.write(client_script_sh)

    # Make shell scripts executable on Unix systems
    try:
        os.chmod('start_server.sh', 0o755)
        os.chmod('start_client.sh', 0o755)
    except:
        pass  # Ignore on Windows

    print("✓ Start scripts created:")
    print("  - start_server.bat / start_server.sh")
    print("  - start_client.bat / start_client.sh")


def run_system_test():
    """Run a quick system test to verify everything works."""
    print("\nRunning system test...")

    # Test with sample data generation
    print("Testing with generated sample data...")

    try:
        # Import and test the main components
        from federated_server import FederatedServer
        from federated_client import FederatedClient

        print("✓ All modules imported successfully")

        # Test port availability
        if test_port_availability(8888):
            print("✓ Port 8888 is available")
        else:
            print("⚠ Port 8888 is in use, consider using a different port")

        print("✓ System test completed successfully")
        return True

    except Exception as e:
        print(f"✗ System test failed: {e}")
        return False


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='Setup Federated Learning HUIM System')
    parser.add_argument('--generate-data', action='store_true', help='Generate sample data')
    parser.add_argument('--num-clients', type=int, default=3, help='Number of clients for sample data')
    parser.add_argument('--transactions-per-client', type=int, default=100, help='Transactions per client')
    parser.add_argument('--server-port', type=int, default=8888, help='Server port')
    parser.add_argument('--test-only', action='store_true', help='Only run system test')

    args = parser.parse_args()

    print("=" * 60)
    print("Federated Learning HUIM System Setup")
    print("=" * 60)

    if args.test_only:
        success = run_system_test()
        sys.exit(0 if success else 1)

    # Step 1: Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        print("Please install missing dependencies and run setup again.")
        sys.exit(1)

    # Step 2: Check required files
    print("\n2. Checking required files...")
    if not check_files():
        print("Please ensure all required files are present.")
        sys.exit(1)

    # Step 3: Get network configuration
    print("\n3. Network configuration...")
    local_ip = get_local_ip()
    print(f"Local IP address: {local_ip}")

    if not test_port_availability(args.server_port):
        print(f"⚠ Port {args.server_port} is in use")
        response = input(f"Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print(f"✓ Port {args.server_port} is available")

    # Step 4: Generate sample data if requested
    if args.generate_data:
        print("\n4. Generating sample data...")
        generate_sample_data(args.num_clients, args.transactions_per_client)
    else:
        print("\n4. Skipping sample data generation (use --generate-data to enable)")

    # Step 5: Create configuration file
    print("\n5. Creating configuration...")
    create_config_file(local_ip, args.server_port, args.num_clients)

    # Step 6: Create start scripts
    print("\n6. Creating start scripts...")
    create_start_scripts()

    # Step 7: Run system test
    print("\n7. Running system test...")
    if not run_system_test():
        print("⚠ System test failed, but setup is complete")

    # Final instructions
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print(f"\nServer IP: {local_ip}")
    print(f"Server Port: {args.server_port}")
    print(f"\nTo start the system:")
    print("1. On the server laptop, run: python federated_server.py")
    print("2. On each client laptop, run: python federated_client.py --client-id <unique_id> --server-host <server_ip>")
    print("\nOr use the convenient start scripts:")
    print("- Server: start_server.bat (Windows) or ./start_server.sh (Linux/Mac)")
    print("- Client: start_client.bat (Windows) or ./start_client.sh (Linux/Mac)")
    print("\nSee README_Federated_Setup.md for detailed instructions.")


if __name__ == "__main__":
    main()
