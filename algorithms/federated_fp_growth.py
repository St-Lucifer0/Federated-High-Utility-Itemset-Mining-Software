"""
Federated FP-Growth algorithm for High Utility Itemset Mining with Laplace Differential Privacy.

This implementation provides a federated learning framework for HUIM that integrates
with the BestEfficientUPGrowth algorithm and supports Laplace differential privacy.

Copyright (c) 2024 - Federated FP-Growth with Laplace DP
"""

import time
import numpy as np
import psutil
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import copy
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from .Alogrithm import OptimizedAlgoUPGrowth
from .itemset import Itemset
from .item import Item


@dataclass
class LaplaceDP:
    """Laplace Differential Privacy mechanism for HUIM."""

    epsilon: float = 1.0  # Privacy budget
    sensitivity: float = 1.0  # Global sensitivity
    noise_scale: float = field(init=False)

    def __post_init__(self):
        """Calculate noise scale based on epsilon and sensitivity."""
        self.noise_scale = self.sensitivity / self.epsilon

    def add_laplace_noise(self, value: float) -> float:
        """Add Laplace noise to a numeric value."""
        noise = np.random.laplace(0, self.noise_scale)
        return max(0, value + noise)  # Ensure non-negative utility values

    def add_noise_to_itemset(self, itemset: Itemset) -> Itemset:
        """Add Laplace noise to an itemset's utility."""
        noisy_itemset = copy.deepcopy(itemset)
        noisy_itemset.utility = self.add_laplace_noise(itemset.utility)
        return noisy_itemset

    def add_noise_to_hui_list(self, huis: List[Itemset]) -> List[Itemset]:
        """Add Laplace noise to a list of HUIs."""
        return [self.add_noise_to_itemset(hui) for hui in huis]


@dataclass
class FederatedClient:
    """Represents a client in the federated learning setup."""

    client_id: int
    transactions: List[List[int]]
    utilities: List[List[float]]
    min_utility: float
    local_algorithm: OptimizedAlgoUPGrowth = field(default_factory=OptimizedAlgoUPGrowth)
    local_huis: List[Itemset] = field(default_factory=list)
    participation_rate: float = 1.0
    data_size: int = 0

    def __post_init__(self):
        """Initialize client data size."""
        self.data_size = len(self.transactions)

    def mine_local_huis(self, use_pseudo_projection: bool = True) -> List[Itemset]:
        """Mine HUIs locally using the efficient algorithm."""
        self.local_algorithm.use_pseudo_projection = use_pseudo_projection
        self.local_huis = self.local_algorithm.run_algorithm_memory(
            self.transactions, self.utilities, self.min_utility
        )
        return self.local_huis

    def get_local_statistics(self) -> Dict[str, Any]:
        """Get local mining statistics."""
        return {
            'client_id': self.client_id,
            'data_size': self.data_size,
            'hui_count': len(self.local_huis),
            'total_utility': sum(hui.utility for hui in self.local_huis),
            'avg_utility': sum(hui.utility for hui in self.local_huis) / max(1, len(self.local_huis)),
            'memory_usage': self.local_algorithm.max_memory,
            'runtime': self.local_algorithm.end_timestamp - self.local_algorithm.start_timestamp
        }


@dataclass
class FederatedFPGrowth:
    """Federated FP-Growth algorithm for HUIM with Laplace DP."""

    clients: List[FederatedClient] = field(default_factory=list)
    global_huis: List[Itemset] = field(default_factory=list)
    min_utility: float = 0.0
    num_rounds: int = 5
    client_sampling_rate: float = 1.0
    use_laplace_dp: bool = False
    laplace_dp: Optional[LaplaceDP] = None

    # Performance metrics
    communication_costs: List[float] = field(default_factory=list)
    round_times: List[float] = field(default_factory=list)
    privacy_budget_consumed: float = 0.0
    total_runtime: float = 0.0

    # Fairness and robustness metrics
    client_contributions: Dict[int, int] = field(default_factory=dict)
    data_heterogeneity: float = 0.0

    def __post_init__(self):
        """Initialize Laplace DP if enabled."""
        if self.use_laplace_dp and self.laplace_dp is None:
            self.laplace_dp = LaplaceDP()

    def add_client(self, client: FederatedClient):
        """Add a client to the federation."""
        self.clients.append(client)
        self.client_contributions[client.client_id] = 0

    def sample_clients(self) -> List[FederatedClient]:
        """Sample clients for participation in current round."""
        num_clients = max(1, int(len(self.clients) * self.client_sampling_rate))
        return random.sample(self.clients, num_clients)

    def aggregate_huis(self, client_huis_list: List[List[Itemset]]) -> List[Itemset]:
        """Aggregate HUIs from multiple clients."""
        hui_dict = defaultdict(float)
        hui_items_dict = defaultdict(set)

        # Aggregate utilities for identical itemsets
        for client_huis in client_huis_list:
            for hui in client_huis:
                key = tuple(sorted(hui.itemset))
                hui_dict[key] += hui.utility
                hui_items_dict[key] = set(hui.itemset)

        # Create aggregated HUIs
        aggregated_huis = []
        for key, total_utility in hui_dict.items():
            if total_utility >= self.min_utility:
                hui = Itemset(itemset=list(hui_items_dict[key]), utility=int(total_utility))
                aggregated_huis.append(hui)

        return aggregated_huis

    def apply_differential_privacy(self, huis: List[Itemset]) -> List[Itemset]:
        """Apply Laplace differential privacy to HUIs."""
        if not self.use_laplace_dp or self.laplace_dp is None:
            return huis

        noisy_huis = self.laplace_dp.add_noise_to_hui_list(huis)
        # Filter out HUIs that fall below minimum utility after noise
        filtered_huis = [hui for hui in noisy_huis if hui.utility >= self.min_utility]

        # Update privacy budget
        self.privacy_budget_consumed += self.laplace_dp.epsilon

        return filtered_huis

    def calculate_communication_cost(self, client_huis_list: List[List[Itemset]]) -> float:
        """Calculate communication cost for the current round."""
        total_cost = 0.0
        for client_huis in client_huis_list:
            # Estimate cost as number of itemsets * average itemset size * 8 bytes
            for hui in client_huis:
                total_cost += len(hui.itemset) * 8 + 8  # items + utility
        return total_cost

    def calculate_data_heterogeneity(self) -> float:
        """Calculate data heterogeneity across clients (coefficient of variation)."""
        if len(self.clients) <= 1:
            return 0.0

        data_sizes = [client.data_size for client in self.clients]
        mean_size = np.mean(data_sizes)
        std_size = np.std(data_sizes)

        return std_size / mean_size if mean_size > 0 else 0.0

    def run_federated_learning(self) -> List[Itemset]:
        """Run the federated learning process."""
        start_time = time.time()
        self.data_heterogeneity = self.calculate_data_heterogeneity()

        print(f"Starting federated learning with {len(self.clients)} clients")
        print(f"Privacy enabled: {self.use_laplace_dp}")
        print(f"Data heterogeneity: {self.data_heterogeneity:.3f}")

        for round_num in range(self.num_rounds):
            round_start = time.time()
            print(f"\n--- Round {round_num + 1}/{self.num_rounds} ---")

            # Sample clients for this round
            selected_clients = self.sample_clients()
            print(f"Selected {len(selected_clients)} clients")

            # Parallel local mining
            client_huis_list = []
            with ThreadPoolExecutor(max_workers=min(4, len(selected_clients))) as executor:
                future_to_client = {
                    executor.submit(client.mine_local_huis): client
                    for client in selected_clients
                }

                for future in as_completed(future_to_client):
                    client = future_to_client[future]
                    try:
                        local_huis = future.result()
                        client_huis_list.append(local_huis)
                        self.client_contributions[client.client_id] += len(local_huis)
                        print(f"Client {client.client_id}: {len(local_huis)} HUIs")
                    except Exception as e:
                        print(f"Client {client.client_id} failed: {e}")

            # Aggregate HUIs
            round_huis = self.aggregate_huis(client_huis_list)
            print(f"Aggregated HUIs: {len(round_huis)}")

            # Apply differential privacy
            if self.use_laplace_dp:
                round_huis = self.apply_differential_privacy(round_huis)
                print(f"HUIs after DP: {len(round_huis)}")

            # Update global HUIs
            self.global_huis = round_huis

            # Calculate metrics
            comm_cost = self.calculate_communication_cost(client_huis_list)
            self.communication_costs.append(comm_cost)

            round_time = time.time() - round_start
            self.round_times.append(round_time)

            print(f"Round time: {round_time:.2f}s, Comm cost: {comm_cost:.0f} bytes")

        self.total_runtime = time.time() - start_time
        print(f"\nFederated learning completed in {self.total_runtime:.2f}s")
        print(f"Final global HUIs: {len(self.global_huis)}")

        if self.use_laplace_dp:
            print(f"Total privacy budget consumed: {self.privacy_budget_consumed:.3f}")

        return self.global_huis

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            'total_runtime': self.total_runtime,
            'num_clients': len(self.clients),
            'num_rounds': self.num_rounds,
            'global_hui_count': len(self.global_huis),
            'total_utility': sum(hui.utility for hui in self.global_huis),
            'avg_utility': sum(hui.utility for hui in self.global_huis) / max(1, len(self.global_huis)),
            'communication_costs': self.communication_costs,
            'total_communication_cost': sum(self.communication_costs),
            'avg_round_time': np.mean(self.round_times) if self.round_times else 0,
            'data_heterogeneity': self.data_heterogeneity,
            'client_contributions': dict(self.client_contributions),
            'privacy_budget_consumed': self.privacy_budget_consumed,
            'privacy_enabled': self.use_laplace_dp
        }

    def get_fairness_metrics(self) -> Dict[str, Any]:
        """Calculate fairness metrics across clients."""
        contributions = list(self.client_contributions.values())
        if not contributions:
            return {}

        return {
            'contribution_mean': np.mean(contributions),
            'contribution_std': np.std(contributions),
            'contribution_cv': np.std(contributions) / np.mean(contributions) if np.mean(contributions) > 0 else 0,
            'min_contribution': min(contributions),
            'max_contribution': max(contributions),
            'contribution_distribution': contributions
        }
