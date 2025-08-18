"""
Demo script to easily start federated learning for testing.
This script helps you quickly test the federated learning system.
"""

import os
import sys
import subprocess
import time
import threading
import argparse

def start_server(port=8888, min_clients=2, max_rounds=3, enable_dp=False, epsilon=1.0):
    """Start the federated server."""
    cmd = [
        sys.executable, "federated_server.py",
        "--port", str(port),
        "--min-clients", str(min_clients),
        "--max-rounds", str(max_rounds)
    ]
    
    if enable_dp:
        cmd.extend(["--enable-dp", "--epsilon", str(epsilon)])
    
    print(f"Starting server with command: {' '.join(cmd)}")
    return subprocess.Popen(cmd)

def start_client(client_id, server_host="localhost", server_port=8888, 
                data_file=None, utility_file=None, min_utility=50):
    """Start a federated client."""
    
    # Default data files if not specified
    if data_file is None:
        data_file = "datasets/datasets_fedlearn/chess_transactions.txt"
    if utility_file is None:
        utility_file = "datasets/datasets_fedlearn/chess_utilities.txt"
    
    cmd = [
        sys.executable, "federated_client.py",
        "--client-id", client_id,
        "--server-host", server_host,
        "--server-port", str(server_port),
        "--data-file", data_file,
        "--utility-file", utility_file,
        "--min-utility", str(min_utility)
    ]
    
    print(f"Starting client {client_id} with command: {' '.join(cmd)}")
    return subprocess.Popen(cmd)

def main():
    parser = argparse.ArgumentParser(description="Start federated learning demo")
    parser.add_argument("--mode", choices=["server", "client", "demo"], default="demo",
                       help="Mode to run: server, client, or demo (both)")
    parser.add_argument("--port", type=int, default=8888, help="Server port")
    parser.add_argument("--min-clients", type=int, default=2, help="Minimum clients")
    parser.add_argument("--max-rounds", type=int, default=3, help="Maximum rounds")
    parser.add_argument("--enable-dp", action="store_true", help="Enable differential privacy")
    parser.add_argument("--epsilon", type=float, default=1.0, help="Privacy budget")
    parser.add_argument("--client-id", default="demo_client", help="Client ID")
    parser.add_argument("--server-host", default="localhost", help="Server host")
    parser.add_argument("--min-utility", type=int, default=50, help="Minimum utility threshold")
    
    args = parser.parse_args()
    
    print("=== FEDERATED LEARNING DEMO ===")
    print(f"Mode: {args.mode}")
    print(f"Privacy: {'Enabled' if args.enable_dp else 'Disabled'}")
    if args.enable_dp:
        print(f"Epsilon: {args.epsilon}")
    print()
    
    if args.mode == "server":
        print("Starting server only...")
        server_process = start_server(
            port=args.port,
            min_clients=args.min_clients,
            max_rounds=args.max_rounds,
            enable_dp=args.enable_dp,
            epsilon=args.epsilon
        )
        
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server_process.terminate()
    
    elif args.mode == "client":
        print("Starting client only...")
        client_process = start_client(
            client_id=args.client_id,
            server_host=args.server_host,
            server_port=args.port,
            min_utility=args.min_utility
        )
        
        try:
            client_process.wait()
        except KeyboardInterrupt:
            print(f"\nShutting down client {args.client_id}...")
            client_process.terminate()
    
    elif args.mode == "demo":
        print("Starting full demo (server + 2 clients)...")
        print("This will start a server and 2 clients automatically.")
        print("Press Ctrl+C to stop all processes.")
        print()
        
        processes = []
        
        try:
            # Start server
            print("1. Starting server...")
            server_process = start_server(
                port=args.port,
                min_clients=args.min_clients,
                max_rounds=args.max_rounds,
                enable_dp=args.enable_dp,
                epsilon=args.epsilon
            )
            processes.append(server_process)
            time.sleep(2)  # Give server time to start
            
            # Start first client
            print("2. Starting first client...")
            client1_process = start_client(
                client_id="demo_client_1",
                server_port=args.port,
                data_file="datasets/datasets_fedlearn/chess_transactions.txt",
                utility_file="datasets/datasets_fedlearn/chess_utilities.txt",
                min_utility=args.min_utility
            )
            processes.append(client1_process)
            time.sleep(1)
            
            # Start second client
            print("3. Starting second client...")
            client2_process = start_client(
                client_id="demo_client_2",
                server_port=args.port,
                data_file="datasets/datasets_fedlearn/transactions.txt",
                utility_file="datasets/datasets_fedlearn/utilities.txt",
                min_utility=args.min_utility
            )
            processes.append(client2_process)
            
            print("\n=== DEMO RUNNING ===")
            print("Server and clients are now running.")
            print("Watch the output to see federated learning in action!")
            print("Press Ctrl+C to stop all processes.")
            
            # Wait for all processes
            for process in processes:
                process.wait()
                
        except KeyboardInterrupt:
            print("\n\nShutting down all processes...")
            for process in processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
            print("All processes stopped.")

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("federated_server.py"):
        print("Error: Please run this script from the HUI_algorithm directory")
        print("Current directory:", os.getcwd())
        print("Expected files: federated_server.py, federated_client.py")
        sys.exit(1)
    
    main()