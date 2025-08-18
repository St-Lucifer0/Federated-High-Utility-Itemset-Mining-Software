"""
Federated Learning Server for High Utility Itemset Mining with Differential Privacy.

This server coordinates federated learning across multiple client laptops,
aggregates results, and applies differential privacy mechanisms.

Copyright (c) 2024 - Federated HUIM Server
"""

import socket
import threading
import json
import time
import pickle
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np

from .federated_fp_growth import FederatedFPGrowth, LaplaceDP
from .itemset import Itemset
from .item import Item

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('federated_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ClientConnection:
    """Represents a connected client."""
    client_id: str
    socket: socket.socket
    address: Tuple[str, int]
    last_seen: float = field(default_factory=time.time)
    data_size: int = 0
    min_utility: float = 0.0  # Client-specific minimum utility
    is_active: bool = True


class FederatedServer:
    """
    Federated Learning Server for HUIM with Differential Privacy.

    Manages client connections, coordinates federated learning rounds,
    and aggregates results with privacy guarantees.
    """

    def __init__(self,
                 host: str = "0.0.0.0",
                 port: int = 8888,
                 min_utility: float = 30.0,
                 num_rounds: int = 5,
                 min_clients: int = 2,
                 client_sampling_rate: float = 1.0,
                 use_differential_privacy: bool = True,
                 epsilon: float = 1.0):

        self.host = host
        self.port = port
        self.min_utility = min_utility
        self.num_rounds = num_rounds
        self.min_clients = min_clients
        self.client_sampling_rate = client_sampling_rate
        self.use_differential_privacy = use_differential_privacy

        # Server state
        self.clients: Dict[str, ClientConnection] = {}
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.current_round = 0

        # Federated learning components
        self.federated_algorithm = FederatedFPGrowth(
            min_utility=min_utility,
            num_rounds=num_rounds,
            client_sampling_rate=client_sampling_rate,
            use_laplace_dp=use_differential_privacy
        )

        if use_differential_privacy:
            self.federated_algorithm.laplace_dp = LaplaceDP(epsilon=epsilon)

        # Results storage
        self.global_results: List[Itemset] = []
        self.round_results: List[Dict] = []
        self.performance_metrics: Dict = {}

        # Threading
        self.client_threads: List[threading.Thread] = []
        self.lock = threading.Lock()

    def start_server(self):
        """Start the federated learning server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)

            self.is_running = True
            logger.info(f"Federated Server started on {self.host}:{self.port}")
            logger.info(f"Waiting for at least {self.min_clients} clients to connect...")

            # Start accepting client connections
            accept_thread = threading.Thread(target=self._accept_clients)
            accept_thread.daemon = True
            accept_thread.start()

            # Wait for minimum clients and start federated learning
            self._wait_for_clients_and_start()

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.stop_server()

    def _accept_clients(self):
        """Accept incoming client connections."""
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"New client connection from {address}")

                # Handle client registration
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                self.client_threads.append(client_thread)

            except Exception as e:
                if self.is_running:
                    logger.error(f"Error accepting client: {e}")

    def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle individual client communication."""
        client_id = None
        try:
            # Receive client registration
            data = self._receive_message(client_socket)
            if data and data.get('type') == 'register':
                client_id = data['client_id']
                data_size = data.get('data_size', 0)
                min_utility = data.get('min_utility', 0.0)  # Extract client-specific minimum utility

                # Register client
                with self.lock:
                    self.clients[client_id] = ClientConnection(
                        client_id=client_id,
                        socket=client_socket,
                        address=address,
                        data_size=data_size,
                        min_utility=min_utility
                    )

                logger.info(
                    f"Client {client_id} registered with {data_size} transactions and min utility {min_utility}")

                # Send acknowledgment
                self._send_message(client_socket, {
                    'type': 'registration_ack',
                    'status': 'success',
                    'server_config': {
                        'min_utility': self.min_utility,
                        'num_rounds': self.num_rounds,
                        'use_dp': self.use_differential_privacy
                    }
                })

                # Keep connection alive and handle requests
                self._maintain_client_connection(client_socket, client_id)

        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id and client_id in self.clients:
                with self.lock:
                    self.clients[client_id].is_active = False
                logger.info(f"Client {client_id} disconnected")
            client_socket.close()

    def _maintain_client_connection(self, client_socket: socket.socket, client_id: str):
        """Maintain connection with client and handle requests."""
        while self.is_running and client_id in self.clients:
            try:
                # Set timeout for socket operations
                client_socket.settimeout(30.0)

                data = self._receive_message(client_socket)
                if not data:
                    break

                if data.get('type') == 'heartbeat':
                    with self.lock:
                        if client_id in self.clients:
                            self.clients[client_id].last_seen = time.time()

                    self._send_message(client_socket, {'type': 'heartbeat_ack'})

                elif data.get('type') == 'training_results':
                    self._handle_training_results(client_id, data)

            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Error maintaining connection with {client_id}: {e}")
                break

    def _wait_for_clients_and_start(self):
        """Wait for minimum clients and start federated learning."""
        while len(self.clients) < self.min_clients:
            logger.info(f"Waiting for clients... ({len(self.clients)}/{self.min_clients})")
            time.sleep(5)

        logger.info(f"Minimum clients connected. Starting federated learning...")
        self.run_federated_learning()

    def run_federated_learning(self):
        """Run the federated learning process."""
        logger.info("Starting federated learning process...")
        start_time = time.time()

        for round_num in range(self.num_rounds):
            self.current_round = round_num + 1
            logger.info(f"Starting round {self.current_round}/{self.num_rounds}")

            # Select participating clients
            participating_clients = self._select_clients()
            logger.info(f"Selected {len(participating_clients)} clients for round {self.current_round}")

            # Send training request to clients
            round_results = self._coordinate_training_round(participating_clients)

            # Aggregate results
            if round_results:
                aggregated_huis = self._aggregate_results(round_results)

                # Apply differential privacy if enabled
                if self.use_differential_privacy:
                    aggregated_huis = self.federated_algorithm.apply_differential_privacy(aggregated_huis)

                self.global_results = aggregated_huis

                # Store round metrics
                round_metrics = {
                    'round': self.current_round,
                    'participating_clients': len(participating_clients),
                    'total_huis': len(aggregated_huis),
                    'timestamp': time.time()
                }
                self.round_results.append(round_metrics)

                logger.info(f"Round {self.current_round} completed. Found {len(aggregated_huis)} HUIs")
            else:
                logger.warning(f"No results received in round {self.current_round}")

        # Calculate final performance metrics
        total_time = time.time() - start_time
        self.performance_metrics = self._calculate_performance_metrics(total_time)

        logger.info("Federated learning completed!")
        self._save_results()

    def _select_clients(self) -> List[str]:
        """Select clients for the current round."""
        active_clients = [
            client_id for client_id, client in self.clients.items()
            if client.is_active and (time.time() - client.last_seen) < 60
        ]

        num_selected = max(1, int(len(active_clients) * self.client_sampling_rate))
        return np.random.choice(active_clients, size=min(num_selected, len(active_clients)), replace=False).tolist()

    def _coordinate_training_round(self, participating_clients: List[str]) -> List[Dict]:
        """Coordinate a training round with selected clients."""
        results = []

        # Send training requests
        for client_id in participating_clients:
            if client_id in self.clients:
                try:
                    client = self.clients[client_id]
                    request = {
                        'type': 'training_request',
                        'round': self.current_round,
                        'min_utility': client.min_utility,  # Use client's specific minimum utility
                        'timeout': 300  # 5 minutes timeout
                    }

                    self._send_message(client.socket, request)
                    logger.info(f"Training request sent to client {client_id}")

                except Exception as e:
                    logger.error(f"Failed to send training request to {client_id}: {e}")

        # Wait for results (with timeout)
        timeout = 300  # 5 minutes
        start_time = time.time()
        received_results = {}

        while len(received_results) < len(participating_clients) and (time.time() - start_time) < timeout:
            time.sleep(1)

            # Check for received results
            with self.lock:
                for client_id in participating_clients:
                    if hasattr(self, '_pending_results') and client_id in self._pending_results:
                        received_results[client_id] = self._pending_results.pop(client_id)

        logger.info(f"Received results from {len(received_results)}/{len(participating_clients)} clients")
        return list(received_results.values())

    def _handle_training_results(self, client_id: str, data: Dict):
        """Handle training results from a client."""
        try:
            if not hasattr(self, '_pending_results'):
                self._pending_results = {}

            with self.lock:
                self._pending_results[client_id] = data

            logger.info(f"Received training results from client {client_id}")

        except Exception as e:
            logger.error(f"Error handling training results from {client_id}: {e}")

    def _aggregate_results(self, round_results: List[Dict]) -> List[Itemset]:
        """Aggregate HUI results from multiple clients."""
        all_huis = []

        for result in round_results:
            if 'huis' in result:
                client_huis = []
                for hui_data in result['huis']:
                    # Reconstruct Itemset from serialized data
                    itemset = Itemset(hui_data['items'])  # Directly use the integer list
                    itemset.utility = hui_data['utility']
                    client_huis.append(itemset)

                all_huis.extend(client_huis)

        # Remove duplicates and filter by minimum utility
        unique_huis = {}
        for hui in all_huis:
            key = tuple(sorted(hui.itemset))
            if key not in unique_huis or hui.utility > unique_huis[key].utility:
                unique_huis[key] = hui

        # Filter by minimum utility
        filtered_huis = [hui for hui in unique_huis.values() if hui.utility >= self.min_utility]

        return sorted(filtered_huis, key=lambda x: x.utility, reverse=True)

    def _calculate_performance_metrics(self, total_time: float) -> Dict:
        """Calculate comprehensive performance metrics."""
        total_clients = len(self.clients)
        total_data_size = sum(client.data_size for client in self.clients.values())

        return {
            'total_runtime': total_time,
            'total_rounds': self.num_rounds,
            'total_clients': total_clients,
            'total_data_size': total_data_size,
            'total_huis_found': len(self.global_results),
            'average_huis_per_round': len(self.global_results) / self.num_rounds if self.num_rounds > 0 else 0,
            'privacy_enabled': self.use_differential_privacy,
            'epsilon': self.federated_algorithm.laplace_dp.epsilon if self.use_differential_privacy else None
        }

    def _save_results(self):
        """Save federated learning results to files."""
        import os

        # Ensure fedlearn_results directory exists
        os.makedirs('fedlearn_results', exist_ok=True)

        timestamp = int(time.time())

        # Save global HUIs
        with open(f'fedlearn_results/federated_results_{timestamp}.json', 'w') as f:
            results_data = []
            for hui in self.global_results:
                results_data.append({
                    'items': hui.itemset,
                    'utility': hui.utility
                })
            json.dump(results_data, f, indent=2)

        # Save performance metrics
        with open(f'fedlearn_results/federated_metrics_{timestamp}.json', 'w') as f:
            json.dump(self.performance_metrics, f, indent=2)

        logger.info(f"Results saved to fedlearn_results/federated_results_{timestamp}.json")
        logger.info(f"Metrics saved to fedlearn_results/federated_metrics_{timestamp}.json")

    def _send_message(self, client_socket: socket.socket, message: Dict):
        """Send a message to a client."""
        try:
            serialized = json.dumps(message).encode('utf-8')
            length = len(serialized)
            client_socket.sendall(length.to_bytes(4, byteorder='big'))
            client_socket.sendall(serialized)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    def _receive_message(self, client_socket: socket.socket) -> Optional[Dict]:
        """Receive a message from a client."""
        try:
            # Receive message length
            length_bytes = client_socket.recv(4)
            if not length_bytes:
                return None

            length = int.from_bytes(length_bytes, byteorder='big')

            # Receive message data
            data = b''
            while len(data) < length:
                chunk = client_socket.recv(min(length - len(data), 4096))
                if not chunk:
                    return None
                data += chunk

            return json.loads(data.decode('utf-8'))

        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None

    def stop_server(self):
        """Stop the federated learning server."""
        logger.info("Stopping federated server...")
        self.is_running = False

        # Close client connections
        for client in self.clients.values():
            try:
                client.socket.close()
            except:
                pass

        # Close server socket
        if self.server_socket:
            self.server_socket.close()

        logger.info("Federated server stopped")

    def get_status(self) -> Dict:
        """Get current server status."""
        active_clients = sum(1 for client in self.clients.values() if client.is_active)

        return {
            'is_running': self.is_running,
            'current_round': self.current_round,
            'total_clients': len(self.clients),
            'active_clients': active_clients,
            'global_huis_count': len(self.global_results),
            'use_differential_privacy': self.use_differential_privacy
        }


def main():
    """Main function to start the federated server."""
    import argparse

    parser = argparse.ArgumentParser(description='Federated Learning Server for HUIM')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=8888, help='Server port')
    parser.add_argument('--min-utility', type=float, default=30.0, help='Minimum utility threshold')
    parser.add_argument('--rounds', type=int, default=5, help='Number of federated rounds')
    parser.add_argument('--min-clients', type=int, default=2, help='Minimum clients required')
    parser.add_argument('--sampling-rate', type=float, default=1.0, help='Client sampling rate')
    parser.add_argument('--no-dp', action='store_true', help='Disable differential privacy')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Privacy budget (epsilon)')

    args = parser.parse_args()

    server = FederatedServer(
        host=args.host,
        port=args.port,
        min_utility=args.min_utility,
        num_rounds=args.rounds,
        min_clients=args.min_clients,
        client_sampling_rate=args.sampling_rate,
        use_differential_privacy=not args.no_dp,
        epsilon=args.epsilon
    )

    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        server.stop_server()


if __name__ == "__main__":
    main()
