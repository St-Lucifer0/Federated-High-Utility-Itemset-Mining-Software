"""
Network-based Federated Learning Test Suite.

This test suite demonstrates how to set up federated learning across multiple machines
using IP addresses, making one laptop a server and others as clients.

Copyright (c) 2024 - Network Federated Testing
"""

import socket
import threading
import time
import json
import pickle
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
import argparse
from datetime import datetime
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Alogrithm import OptimizedAlgoUPGrowth
from itemset import Itemset
from item import Item


class NetworkFederatedServer:
    """Federated learning server that coordinates multiple network clients."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8888, min_utility: int = 100):
        self.host = host
        self.port = port
        self.min_utility = min_utility
        self.clients = {}
        self.global_huis = []
        self.round_results = []
        self.server_socket = None
        self.running = False
        
    def start_server(self):
        """Start the federated learning server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"Federated Learning Server started on {self.host}:{self.port}")
            print(f"Minimum utility threshold: {self.min_utility}")
            print("Waiting for clients to connect...")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"Client connected from {client_address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Error starting server: {e}")
            traceback.print_exc()
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """Handle communication with a connected client."""
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        try:
            while self.running:
                # Receive message from client
                message = self.receive_message(client_socket)
                if not message:
                    break
                
                response = self.process_client_message(client_id, message)
                
                # Send response back to client
                self.send_message(client_socket, response)
                
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            client_socket.close()
            if client_id in self.clients:
                del self.clients[client_id]
            print(f"Client {client_id} disconnected")
    
    def process_client_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process message from client and return response."""
        msg_type = message.get('type')
        
        if msg_type == 'register':
            # Register new client
            self.clients[client_id] = {
                'status': 'registered',
                'last_seen': time.time(),
                'data_info': message.get('data_info', {})
            }
            
            return {
                'type': 'registration_ack',
                'client_id': client_id,
                'min_utility': self.min_utility,
                'status': 'success'
            }
        
        elif msg_type == 'local_huis':
            # Receive local HUIs from client
            local_huis_data = message.get('huis', [])
            
            # Convert received data back to Itemset objects
            local_huis = []
            for hui_data in local_huis_data:
                itemset = Itemset()
                for item_id in hui_data['items']:
                    itemset.add_item(Item(item_id, 1))  # Default utility
                itemset.utility = hui_data['utility']
                local_huis.append(itemset)
            
            # Store client's local HUIs
            if client_id in self.clients:
                self.clients[client_id]['local_huis'] = local_huis
                self.clients[client_id]['last_seen'] = time.time()
            
            return {
                'type': 'huis_received',
                'status': 'success',
                'num_huis_received': len(local_huis)
            }
        
        elif msg_type == 'request_global_model':
            # Send current global model to client
            global_huis_data = []
            for hui in self.global_huis:
                global_huis_data.append({
                    'items': hui.get_items(),
                    'utility': hui.utility
                })
            
            return {
                'type': 'global_model',
                'global_huis': global_huis_data,
                'num_global_huis': len(self.global_huis)
            }
        
        else:
            return {
                'type': 'error',
                'message': f'Unknown message type: {msg_type}'
            }
    
    def run_federated_round(self, round_num: int) -> Dict[str, Any]:
        """Run one round of federated learning."""
        print(f"\n=== Starting Federated Round {round_num} ===")
        
        round_start_time = time.time()
        
        # Wait for all clients to send their local HUIs
        print("Waiting for clients to compute local HUIs...")
        self.wait_for_client_updates()
        
        # Aggregate local HUIs into global model
        print("Aggregating local HUIs into global model...")
        self.aggregate_local_huis()
        
        round_end_time = time.time()
        
        round_result = {
            'round': round_num,
            'num_clients': len(self.clients),
            'num_global_huis': len(self.global_huis),
            'round_time': round_end_time - round_start_time,
            'client_stats': {}
        }
        
        # Collect client statistics
        for client_id, client_info in self.clients.items():
            if 'local_huis' in client_info:
                round_result['client_stats'][client_id] = {
                    'num_local_huis': len(client_info['local_huis']),
                    'total_utility': sum(hui.utility for hui in client_info['local_huis'])
                }
        
        self.round_results.append(round_result)
        
        print(f"Round {round_num} completed:")
        print(f"  - Clients participated: {len(self.clients)}")
        print(f"  - Global HUIs: {len(self.global_huis)}")
        print(f"  - Round time: {round_end_time - round_start_time:.2f}s")
        
        return round_result
    
    def wait_for_client_updates(self, timeout: int = 60):
        """Wait for all clients to send their local HUIs."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_updated = True
            for client_id, client_info in self.clients.items():
                if 'local_huis' not in client_info:
                    all_updated = False
                    break
            
            if all_updated:
                print("All clients have sent their local HUIs")
                return
            
            time.sleep(1)
        
        print(f"Timeout waiting for client updates. Proceeding with available clients.")
    
    def aggregate_local_huis(self):
        """Aggregate local HUIs from all clients into global model."""
        # Simple aggregation: union of all local HUIs above threshold
        hui_map = {}
        
        for client_id, client_info in self.clients.items():
            if 'local_huis' not in client_info:
                continue
            
            for hui in client_info['local_huis']:
                items_key = tuple(sorted(hui.get_items()))
                
                if items_key in hui_map:
                    # Average the utilities
                    hui_map[items_key]['utility'] = (
                        hui_map[items_key]['utility'] + hui.utility
                    ) / 2
                    hui_map[items_key]['count'] += 1
                else:
                    hui_map[items_key] = {
                        'items': hui.get_items(),
                        'utility': hui.utility,
                        'count': 1
                    }
        
        # Create global HUIs from aggregated results
        self.global_huis = []
        for items_key, hui_info in hui_map.items():
            if hui_info['utility'] >= self.min_utility:
                itemset = Itemset()
                for item_id in hui_info['items']:
                    itemset.add_item(Item(item_id, 1))
                itemset.utility = hui_info['utility']
                self.global_huis.append(itemset)
        
        print(f"Aggregated {len(self.global_huis)} global HUIs from {len(hui_map)} candidates")
    
    def send_message(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Send message to client."""
        try:
            serialized = pickle.dumps(message)
            message_length = len(serialized)
            
            # Send message length first
            client_socket.sendall(message_length.to_bytes(4, byteorder='big'))
            # Send message
            client_socket.sendall(serialized)
            
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def receive_message(self, client_socket: socket.socket) -> Optional[Dict[str, Any]]:
        """Receive message from client."""
        try:
            # Receive message length
            length_bytes = client_socket.recv(4)
            if not length_bytes:
                return None
            
            message_length = int.from_bytes(length_bytes, byteorder='big')
            
            # Receive message
            message_data = b''
            while len(message_data) < message_length:
                chunk = client_socket.recv(min(message_length - len(message_data), 4096))
                if not chunk:
                    return None
                message_data += chunk
            
            return pickle.loads(message_data)
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def stop_server(self):
        """Stop the federated learning server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("Server stopped")
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary of federated learning results."""
        return {
            'num_rounds': len(self.round_results),
            'num_clients': len(self.clients),
            'num_global_huis': len(self.global_huis),
            'total_global_utility': sum(hui.utility for hui in self.global_huis),
            'round_results': self.round_results,
            'client_info': {
                client_id: {
                    'data_info': info.get('data_info', {}),
                    'num_local_huis': len(info.get('local_huis', []))
                }
                for client_id, info in self.clients.items()
            }
        }


class NetworkFederatedClient:
    """Federated learning client that connects to a network server."""
    
    def __init__(self, server_host: str, server_port: int = 8888, 
                 client_name: str = "client", dataset_path: str = ""):
        self.server_host = server_host
        self.server_port = server_port
        self.client_name = client_name
        self.dataset_path = dataset_path
        self.client_socket = None
        self.min_utility = 100
        self.local_huis = []
        
    def connect_to_server(self) -> bool:
        """Connect to the federated learning server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_host, self.server_port))
            
            print(f"Connected to server at {self.server_host}:{self.server_port}")
            
            # Register with server
            registration_msg = {
                'type': 'register',
                'client_name': self.client_name,
                'data_info': {
                    'dataset_path': self.dataset_path,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            self.send_message(registration_msg)
            response = self.receive_message()
            
            if response and response.get('status') == 'success':
                self.min_utility = response.get('min_utility', 100)
                print(f"Successfully registered with server. Min utility: {self.min_utility}")
                return True
            else:
                print(f"Registration failed: {response}")
                return False
                
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def load_local_data(self) -> bool:
        """Load local dataset for training."""
        if not os.path.exists(self.dataset_path):
            print(f"Dataset not found: {self.dataset_path}")
            return False
        
        print(f"Loading local dataset: {self.dataset_path}")
        
        # Load dataset (simplified version)
        transactions = []
        utilities = []
        
        try:
            if self.dataset_path.endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(self.dataset_path)
                
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
                # Handle text format
                with open(self.dataset_path, 'r') as f:
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
            
            self.transactions = transactions
            self.utilities = utilities
            print(f"Loaded {len(transactions)} transactions")
            return True
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return False
    
    def compute_local_huis(self) -> bool:
        """Compute local HUIs using BestEfficientUPGrowth algorithm."""
        if not hasattr(self, 'transactions') or not self.transactions:
            print("No local data available")
            return False
        
        print("Computing local HUIs...")
        
        try:
            # Create temporary dataset file
            temp_file = f"temp_client_data_{self.client_name}.txt"
            with open(temp_file, 'w') as f:
                for trans, utils in zip(self.transactions, self.utilities):
                    line_parts = []
                    for item, util in zip(trans, utils):
                        line_parts.append(f"{item}:{util}")
                    f.write(" ".join(line_parts) + "\n")
            
            # Run BestEfficientUPGrowth algorithm
            algorithm = BestEfficientUPGrowth()
            temp_output = f"temp_output_{self.client_name}.txt"
            
            algorithm.run_algorithm(temp_file, temp_output, self.min_utility)
            
            # Get local HUIs
            self.local_huis = algorithm.phuis if hasattr(algorithm, 'phuis') else []
            
            print(f"Computed {len(self.local_huis)} local HUIs")
            
            # Clean up temporary files
            for temp in [temp_file, temp_output]:
                if os.path.exists(temp):
                    os.remove(temp)
            
            return True
            
        except Exception as e:
            print(f"Error computing local HUIs: {e}")
            traceback.print_exc()
            return False
    
    def send_local_huis(self) -> bool:
        """Send local HUIs to the server."""
        if not self.local_huis:
            print("No local HUIs to send")
            return False
        
        print(f"Sending {len(self.local_huis)} local HUIs to server...")
        
        # Convert HUIs to serializable format
        huis_data = []
        for hui in self.local_huis:
            huis_data.append({
                'items': hui.get_items(),
                'utility': hui.utility
            })
        
        message = {
            'type': 'local_huis',
            'huis': huis_data,
            'client_name': self.client_name
        }
        
        try:
            self.send_message(message)
            response = self.receive_message()
            
            if response and response.get('status') == 'success':
                print(f"Successfully sent local HUIs. Server received {response.get('num_huis_received', 0)} HUIs")
                return True
            else:
                print(f"Failed to send local HUIs: {response}")
                return False
                
        except Exception as e:
            print(f"Error sending local HUIs: {e}")
            return False
    
    def request_global_model(self) -> List[Itemset]:
        """Request global model from server."""
        print("Requesting global model from server...")
        
        message = {
            'type': 'request_global_model',
            'client_name': self.client_name
        }
        
        try:
            self.send_message(message)
            response = self.receive_message()
            
            if response and response.get('type') == 'global_model':
                global_huis_data = response.get('global_huis', [])
                
                # Convert back to Itemset objects
                global_huis = []
                for hui_data in global_huis_data:
                    itemset = Itemset()
                    for item_id in hui_data['items']:
                        itemset.add_item(Item(item_id, 1))
                    itemset.utility = hui_data['utility']
                    global_huis.append(itemset)
                
                print(f"Received global model with {len(global_huis)} HUIs")
                return global_huis
            else:
                print(f"Failed to get global model: {response}")
                return []
                
        except Exception as e:
            print(f"Error requesting global model: {e}")
            return []
    
    def send_message(self, message: Dict[str, Any]):
        """Send message to server."""
        try:
            serialized = pickle.dumps(message)
            message_length = len(serialized)
            
            # Send message length first
            self.client_socket.sendall(message_length.to_bytes(4, byteorder='big'))
            # Send message
            self.client_socket.sendall(serialized)
            
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive message from server."""
        try:
            # Receive message length
            length_bytes = self.client_socket.recv(4)
            if not length_bytes:
                return None
            
            message_length = int.from_bytes(length_bytes, byteorder='big')
            
            # Receive message
            message_data = b''
            while len(message_data) < message_length:
                chunk = self.client_socket.recv(min(message_length - len(message_data), 4096))
                if not chunk:
                    return None
                message_data += chunk
            
            return pickle.loads(message_data)
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from server."""
        if self.client_socket:
            self.client_socket.close()
        print("Disconnected from server")
    
    def run_client_session(self) -> bool:
        """Run complete client session."""
        print(f"Starting client session: {self.client_name}")
        
        # Connect to server
        if not self.connect_to_server():
            return False
        
        # Load local data
        if not self.load_local_data():
            self.disconnect()
            return False
        
        # Compute local HUIs
        if not self.compute_local_huis():
            self.disconnect()
            return False
        
        # Send local HUIs to server
        if not self.send_local_huis():
            self.disconnect()
            return False
        
        # Wait a bit for server to aggregate
        time.sleep(2)
        
        # Request global model
        global_huis = self.request_global_model()
        
        print(f"Client session completed. Local HUIs: {len(self.local_huis)}, Global HUIs: {len(global_huis)}")
        
        self.disconnect()
        return True


def run_server(host: str = '0.0.0.0', port: int = 8888, min_utility: int = 100, 
               num_rounds: int = 3):
    """Run federated learning server."""
    print("="*60)
    print("FEDERATED LEARNING SERVER")
    print("="*60)
    
    server = NetworkFederatedServer(host, port, min_utility)
    
    try:
        # Start server in separate thread
        server_thread = threading.Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for clients to connect
        print("Press Enter to start federated learning rounds (after clients connect)...")
        input()
        
        # Run federated learning rounds
        for round_num in range(1, num_rounds + 1):
            server.run_federated_round(round_num)
            
            if round_num < num_rounds:
                print(f"Waiting 10 seconds before next round...")
                time.sleep(10)
        
        # Print final results
        results = server.get_results_summary()
        print("\n" + "="*60)
        print("FEDERATED LEARNING RESULTS")
        print("="*60)
        print(f"Total rounds: {results['num_rounds']}")
        print(f"Total clients: {results['num_clients']}")
        print(f"Global HUIs: {results['num_global_huis']}")
        print(f"Total global utility: {results['total_global_utility']:.2f}")
        
        # Save results
        results_file = f"federated_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {results_file}")
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.stop_server()


def run_client(server_host: str, server_port: int = 8888, 
               client_name: str = "client", dataset_path: str = ""):
    """Run federated learning client."""
    print("="*60)
    print(f"FEDERATED LEARNING CLIENT: {client_name}")
    print("="*60)
    
    client = NetworkFederatedClient(server_host, server_port, client_name, dataset_path)
    
    try:
        success = client.run_client_session()
        if success:
            print("Client session completed successfully!")
        else:
            print("Client session failed!")
            
    except KeyboardInterrupt:
        print("\nClient interrupted by user")
        client.disconnect()


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Network Federated Learning Test')
    parser.add_argument('mode', choices=['server', 'client'], 
                       help='Run as server or client')
    parser.add_argument('--host', default='localhost', 
                       help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888, 
                       help='Server port (default: 8888)')
    parser.add_argument('--min-utility', type=int, default=100, 
                       help='Minimum utility threshold (default: 100)')
    parser.add_argument('--rounds', type=int, default=3, 
                       help='Number of federated rounds (server only, default: 3)')
    parser.add_argument('--client-name', default='client', 
                       help='Client name (client only)')
    parser.add_argument('--dataset', default='chess_data.csv', 
                       help='Dataset path (client only)')
    
    args = parser.parse_args()
    
    if args.mode == 'server':
        run_server(args.host, args.port, args.min_utility, args.rounds)
    else:
        # For client mode, resolve dataset path
        dataset_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            args.dataset
        )
        run_client(args.host, args.port, args.client_name, dataset_path)


if __name__ == "__main__":
    main()