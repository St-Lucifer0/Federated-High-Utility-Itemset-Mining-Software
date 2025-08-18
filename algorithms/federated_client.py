"""
Federated Learning Client for High Utility Itemset Mining.

This client connects to a federated server, performs local HUIM,
and participates in federated learning rounds.

Copyright (c) 2024 - Federated HUIM Client
"""

import socket
import json
import time
import threading
import logging
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse

from .Alogrithm import OptimizedAlgoUPGrowth
from .itemset import Itemset
from .item import Item

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('federated_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FederatedClient:
    """
    Federated Learning Client for HUIM.

    Connects to a federated server and participates in distributed
    high utility itemset mining with differential privacy.
    """

    def __init__(self,
                 client_id: str,
                 server_host: str = "localhost",
                 server_port: int = 8888,
                 data_file: Optional[str] = None,
                 utility_file: Optional[str] = None,
                 min_utility: float = 30.0):

        self.client_id = client_id
        self.server_host = server_host
        self.server_port = server_port
        self.data_file = data_file
        self.utility_file = utility_file
        self.min_utility = min_utility

        # Client state
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.is_running = False

        # Data and algorithm
        self.transactions: List[List[int]] = []
        self.utilities: List[List[float]] = []
        self.local_algorithm = OptimizedAlgoUPGrowth()
        self.local_huis: List[Itemset] = []

        # Server configuration
        self.server_config: Dict = {}

        # Threading
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.message_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

    def load_data(self, data_file: str, utility_file: str):
        """Load transaction data and utilities from files."""
        try:
            logger.info(f"Loading data from {data_file} and {utility_file}")

            # Load transactions
            with open(data_file, 'r') as f:
                for line in f:
                    if line.strip():
                        transaction = [int(x) for x in line.strip().split()]
                        self.transactions.append(transaction)

            # Load utilities
            with open(utility_file, 'r') as f:
                for line in f:
                    if line.strip():
                        utilities = [float(x) for x in line.strip().split()]
                        self.utilities.append(utilities)

            logger.info(f"Loaded {len(self.transactions)} transactions")

            if len(self.transactions) != len(self.utilities):
                raise ValueError("Number of transactions and utility lists must match")

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def generate_sample_data(self, num_transactions: int = 100, num_items: int = 20):
        """Generate sample transaction data for testing."""
        import random

        logger.info(f"Generating {num_transactions} sample transactions with {num_items} items")

        self.transactions = []
        self.utilities = []

        for _ in range(num_transactions):
            # Random transaction size (3-8 items)
            transaction_size = random.randint(3, 8)
            transaction = sorted(random.sample(range(1, num_items + 1), transaction_size))
            # Generate higher utilities to ensure some itemsets meet minimum utility threshold
            utilities = [random.uniform(10, 50) for _ in transaction]

            self.transactions.append(transaction)
            self.utilities.append(utilities)

        # Calculate data statistics for debugging
        total_utilities = [sum(util_list) for util_list in self.utilities]
        max_transaction_utility = max(total_utilities) if total_utilities else 0
        avg_transaction_utility = sum(total_utilities) / len(total_utilities) if total_utilities else 0

        logger.info(f"Generated {len(self.transactions)} sample transactions")
        logger.info(f"Max transaction utility: {max_transaction_utility:.2f}")
        logger.info(f"Average transaction utility: {avg_transaction_utility:.2f}")
        logger.info(
            f"Recommended min_utility range: {avg_transaction_utility * 0.1:.2f} - {avg_transaction_utility * 0.5:.2f}")

    def connect_to_server(self) -> bool:
        """Connect to the federated server."""
        try:
            logger.info(f"Connecting to server at {self.server_host}:{self.server_port}")

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))

            # Send registration message
            registration = {
                'type': 'register',
                'client_id': self.client_id,
                'data_size': len(self.transactions),
                'min_utility': self.min_utility,
                'timestamp': time.time()
            }

            self._send_message(registration)

            # Wait for acknowledgment
            response = self._receive_message()
            if response and response.get('type') == 'registration_ack':
                if response.get('status') == 'success':
                    self.server_config = response.get('server_config', {})
                    self.is_connected = True
                    logger.info("Successfully registered with server")
                    return True
                else:
                    logger.error("Server rejected registration")
                    return False
            else:
                logger.error("No valid registration response from server")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            return False

    def start_client(self):
        """Start the federated client."""
        if not self.is_connected:
            logger.error("Not connected to server")
            return

        self.is_running = True
        logger.info("Starting federated client...")

        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

        # Start message handling thread
        self.message_thread = threading.Thread(target=self._message_loop)
        self.message_thread.daemon = True
        self.message_thread.start()

        logger.info("Client started. Waiting for training requests...")

        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Client interrupted by user")
        finally:
            self.stop_client()

    def _heartbeat_loop(self):
        """Send periodic heartbeat messages to server."""
        while self.is_running and self.is_connected:
            try:
                heartbeat = {
                    'type': 'heartbeat',
                    'client_id': self.client_id,
                    'timestamp': time.time()
                }

                self._send_message(heartbeat)

                # Wait for heartbeat response
                time.sleep(30)  # Send heartbeat every 30 seconds

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                self.is_connected = False
                break

    def _message_loop(self):
        """Handle incoming messages from server."""
        while self.is_running and self.is_connected:
            try:
                message = self._receive_message()
                if not message:
                    continue

                message_type = message.get('type')

                if message_type == 'heartbeat_ack':
                    # Heartbeat acknowledged
                    continue

                elif message_type == 'training_request':
                    self._handle_training_request(message)

                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except Exception as e:
                logger.error(f"Message handling error: {e}")
                self.is_connected = False
                break

    def _handle_training_request(self, request: Dict):
        """Handle a training request from the server."""
        try:
            round_num = request.get('round', 0)
            min_utility = request.get('min_utility', self.min_utility)
            timeout = request.get('timeout', 300)

            logger.info(f"Received training request for round {round_num}")

            # Perform local training
            start_time = time.time()
            local_huis = self._perform_local_training(min_utility)
            training_time = time.time() - start_time

            # Prepare results
            results = {
                'type': 'training_results',
                'client_id': self.client_id,
                'round': round_num,
                'training_time': training_time,
                'huis': [],
                'statistics': {
                    'total_huis': len(local_huis),
                    'data_size': len(self.transactions),
                    'timestamp': time.time()
                }
            }

            # Serialize HUIs
            for hui in local_huis:
                hui_data = {
                    'items': hui.itemset,
                    'utility': hui.utility
                }
                results['huis'].append(hui_data)

            # Send results to server
            self._send_message(results)
            logger.info(f"Sent {len(local_huis)} HUIs to server for round {round_num}")

        except Exception as e:
            logger.error(f"Error handling training request: {e}")

    def _perform_local_training(self, min_utility: float) -> List[Itemset]:
        """Perform local HUIM training."""
        try:
            logger.info(f"Starting local HUIM training with min_utility: {min_utility}")

            # Debug: Check data statistics
            if self.transactions and self.utilities:
                total_utilities = [sum(util_list) for util_list in self.utilities]
                max_transaction_utility = max(total_utilities) if total_utilities else 0
                avg_transaction_utility = sum(total_utilities) / len(total_utilities) if total_utilities else 0

                logger.info(
                    f"Data stats - Transactions: {len(self.transactions)}, Max utility: {max_transaction_utility:.2f}, Avg utility: {avg_transaction_utility:.2f}")

                # Suggest better minimum utility if current one is too high
                if min_utility > max_transaction_utility:
                    suggested_min_utility = max_transaction_utility * 0.3
                    logger.warning(
                        f"Min utility {min_utility} is higher than max transaction utility {max_transaction_utility:.2f}")
                    logger.warning(f"Consider using min_utility around {suggested_min_utility:.2f}")

            # Configure algorithm
            self.local_algorithm.debug = True  # Enable debug for troubleshooting

            # Run the algorithm with in-memory data
            self.local_huis = self.local_algorithm.run_algorithm_memory(
                transactions=self.transactions,
                utilities=self.utilities,
                min_utility=min_utility
            )

            # Debug: Check potential HUIs before filtering
            logger.info(f"Algorithm found {self.local_algorithm.phuis_count} potential HUIs")
            logger.info(f"After filtering: {len(self.local_huis)} HUIs meet min_utility {min_utility}")

            # Debug: Show some potential HUIs and their utilities
            if self.local_algorithm.phuis:
                logger.info("Sample potential HUIs:")
                for i, phui in enumerate(self.local_algorithm.phuis[:5]):  # Show first 5
                    logger.info(f"  PHUI {i + 1}: items={phui.get_items()}, utility={phui.utility}")

            logger.info(f"Local training completed. Found {len(self.local_huis)} HUIs")
            return self.local_huis

        except Exception as e:
            logger.error(f"Error in local training: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _send_message(self, message: Dict):
        """Send a message to the server."""
        try:
            with self.lock:
                if self.socket:
                    serialized = json.dumps(message).encode('utf-8')
                    length = len(serialized)
                    self.socket.sendall(length.to_bytes(4, byteorder='big'))
                    self.socket.sendall(serialized)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.is_connected = False
            raise

    def _receive_message(self) -> Optional[Dict]:
        """Receive a message from the server."""
        try:
            if not self.socket:
                return None

            # Set timeout for socket operations
            self.socket.settimeout(30.0)

            # Receive message length
            length_bytes = self.socket.recv(4)
            if not length_bytes:
                return None

            length = int.from_bytes(length_bytes, byteorder='big')

            # Receive message data
            data = b''
            while len(data) < length:
                chunk = self.socket.recv(min(length - len(data), 4096))
                if not chunk:
                    return None
                data += chunk

            return json.loads(data.decode('utf-8'))

        except socket.timeout:
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            self.is_connected = False
            return None

    def stop_client(self):
        """Stop the federated client."""
        logger.info("Stopping federated client...")
        self.is_running = False
        self.is_connected = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        logger.info("Federated client stopped")

    def get_status(self) -> Dict:
        """Get current client status."""
        return {
            'client_id': self.client_id,
            'is_connected': self.is_connected,
            'is_running': self.is_running,
            'data_size': len(self.transactions),
            'local_huis_count': len(self.local_huis),
            'server_host': self.server_host,
            'server_port': self.server_port
        }


def main():
    """Main function to start the federated client."""
    parser = argparse.ArgumentParser(description='Federated Learning Client for HUIM')
    parser.add_argument('--client-id', required=True, help='Unique client identifier')
    parser.add_argument('--server-host', default='localhost', help='Server host address')
    parser.add_argument('--server-port', type=int, default=8888, help='Server port')
    parser.add_argument('--data-file', help='Path to transaction data file')
    parser.add_argument('--utility-file', help='Path to utility data file')
    parser.add_argument('--generate-data', action='store_true', help='Generate sample data')
    parser.add_argument('--num-transactions', type=int, default=100, help='Number of sample transactions')
    parser.add_argument('--num-items', type=int, default=20, help='Number of items in sample data')

    args = parser.parse_args()

    # Get minimum utility interactively from user
    print(f"\n🎯 Setting up federated client '{args.client_id}'")
    print("💡 Minimum utility suggestions:")
    print("   • 10.0-25.0: Low threshold (finds many itemsets)")
    print("   • 30.0-50.0: Medium threshold (balanced approach)")
    print("   • 60.0+: High threshold (finds fewer, high-value itemsets)")

    while True:
        try:
            min_utility = float(input("Enter minimum utility threshold for this client: "))
            if min_utility > 0:
                if min_utility < 25:
                    level = "Low (will find many itemsets)"
                elif min_utility < 60:
                    level = "Medium (balanced approach)"
                else:
                    level = "High (will find fewer, high-value itemsets)"

                print(f"✅ Using minimum utility: {min_utility} ({level})")
                break
            else:
                print("❌ Minimum utility must be positive. Please try again.")
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")

    # Create client
    client = FederatedClient(
        client_id=args.client_id,
        server_host=args.server_host,
        server_port=args.server_port,
        data_file=args.data_file,
        utility_file=args.utility_file,
        min_utility=min_utility
    )

    try:
        # Load or generate data
        if args.generate_data:
            client.generate_sample_data(args.num_transactions, args.num_items)
        elif args.data_file and args.utility_file:
            client.load_data(args.data_file, args.utility_file)
        else:
            logger.error("Either provide data files or use --generate-data")
            sys.exit(1)

        # Connect to server
        if client.connect_to_server():
            client.start_client()
        else:
            logger.error("Failed to connect to server")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Client interrupted by user")
    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        client.stop_client()


if __name__ == "__main__":
    main()
