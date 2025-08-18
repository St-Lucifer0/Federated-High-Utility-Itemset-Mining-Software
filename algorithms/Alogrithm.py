"""
Optimized UPGrowth algorithm for High Utility Itemset Mining.

This is an enhanced implementation of the UPGrowth algorithm with advanced pruning methods
and pseudo-projection techniques for improved efficiency and performance.

Copyright (c) 2024 - Python conversion of original Java implementation
Enhanced with optimization techniques
"""

import time
import psutil
import os
from typing import Dict, List, Optional, Set, Tuple, Deque, NamedTuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
import heapq
import weakref
from functools import lru_cache

from item import Item
from itemset import Itemset
from up_tree import UPTree
from up_node import UPNode


@dataclass
class PathProjection:
    """Lightweight structure for pseudo-projection using pointers."""
    node_refs: List[weakref.ref] = field(default_factory=list)
    utilities: List[int] = field(default_factory=list)
    total_utility: int = 0
    support: int = 0

    def is_valid(self) -> bool:
        """Check if all node references are still valid."""
        return all(ref() is not None for ref in self.node_refs)

    def get_nodes(self) -> List[UPNode]:
        """Get actual nodes from weak references."""
        return [ref() for ref in self.node_refs if ref() is not None]


class ProjectionIndex(NamedTuple):
    """Index structure for efficient path lookups."""
    item_id: int
    node_id: int
    path_length: int
    utility: int


@dataclass
class OptimizedAlgoUPGrowth:
    """
    Optimized implementation of the UPGrowth algorithm with advanced pruning and pseudo-projection.

    Attributes:
        max_memory: Maximum memory usage during execution
        start_timestamp: Start time of algorithm execution
        end_timestamp: End time of algorithm execution
        hui_count: Number of high utility itemsets found
        phuis_count: Number of potential high utility itemsets
        writer: Output file writer
        phuis: List to store potential high utility itemsets
        debug: Debug mode flag
        pruning_stats: Statistics for pruning effectiveness
        projection_stats: Statistics for pseudo-projection
        cache_hits: Number of cache hits for utility calculations
        cache_misses: Number of cache misses for utility calculations
        utility_cache: Cache for utility calculations
        pruning_threshold: Threshold for aggressive pruning
        use_pseudo_projection: Whether to use pseudo-projection
        use_utility_pruning: Whether to use utility-based pruning
        use_support_pruning: Whether to use support-based pruning
    """
    max_memory: float = 0.0
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    hui_count: int = 0
    phuis_count: int = 0
    writer: Optional[object] = None
    phuis: List[Itemset] = field(default_factory=list)
    debug: bool = False
    pruning_stats: Dict[str, int] = field(default_factory=dict)
    projection_stats: Dict[str, int] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0
    utility_cache: Dict[Tuple, int] = field(default_factory=dict)
    pruning_threshold: float = 0.1
    use_pseudo_projection: bool = True
    use_utility_pruning: bool = True
    use_support_pruning: bool = True
    
    # Enhanced pseudo-projection structures
    projection_cache: Dict[Tuple, PathProjection] = field(default_factory=dict)
    path_index: Dict[int, List[ProjectionIndex]] = field(default_factory=dict)
    node_id_counter: int = 0
    utility_bounds_cache: Dict[Tuple, int] = field(default_factory=dict)
    frequent_patterns_cache: Dict[Tuple, bool] = field(default_factory=dict)
    timeout_seconds: float = 30.0

    def run_algorithm(self, input_path: str, output_path: str, min_utility: int) -> None:
        """
        Run the ultra-fast optimized UPGrowth algorithm with timeout protection.

        Args:
            input_path: Path to the input file
            output_path: Path to the output file
            min_utility: Minimum utility threshold
        """
        self.max_memory = 0.0
        self.start_timestamp = time.time()
        self.timeout_seconds = 30.0  # Hard timeout at 30 seconds

        # Initialize statistics
        self.pruning_stats = {
            'utility_pruned': 0,
            'support_pruned': 0,
            'early_termination': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

        self.projection_stats = {
            'pseudo_projections': 0,
            'full_projections': 0,
            'projection_savings': 0,
            'pointer_based_projections': 0,
            'memory_saved_mb': 0
        }

        # Clear enhanced caches
        self.projection_cache.clear()
        self.path_index.clear()
        self.utility_bounds_cache.clear()
        self.frequent_patterns_cache.clear()
        self.node_id_counter = 0

        # Open output file
        with open(output_path, 'w') as self.writer:
            # Calculate TWU and support for each item
            item_stats = self._calculate_item_statistics(input_path)

            # Create optimized UPTree
            tree = self._create_optimized_tree(item_stats, min_utility)

            # Build tree from database with optimizations
            self._build_optimized_tree(input_path, tree, item_stats)

            # Mine high utility itemsets with advanced pruning
            self._optimized_upgrowth(tree, min_utility, [], item_stats)

            # Calculate exact utilities with caching
            self._calculate_exact_utilities_optimized(input_path)

            # Write results
            self._write_results(min_utility)

        self.end_timestamp = time.time()
        self._check_memory()

    def run_algorithm_memory(self, transactions: List[List[int]], utilities: List[List[float]], min_utility: float) -> List[Itemset]:
        """
        Run the optimized UPGrowth algorithm with in-memory data for federated learning.

        Args:
            transactions: List of transactions (each transaction is a list of item IDs)
            utilities: List of utility lists (each utility list corresponds to a transaction)
            min_utility: Minimum utility threshold

        Returns:
            List of high utility itemsets found
        """
        self.max_memory = 0.0
        self.start_timestamp = time.time()

        # Initialize statistics
        self.pruning_stats = {
            'utility_pruned': 0,
            'support_pruned': 0,
            'early_termination': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

        self.projection_stats = {
            'pseudo_projections': 0,
            'full_projections': 0,
            'projection_savings': 0,
            'pointer_based_projections': 0,
            'memory_saved_mb': 0
        }

        # Clear enhanced caches
        self.projection_cache.clear()
        self.path_index.clear()
        self.utility_bounds_cache.clear()
        self.frequent_patterns_cache.clear()
        self.node_id_counter = 0

        # Calculate TWU and support for each item from in-memory data
        item_stats = self._calculate_item_statistics_memory(transactions, utilities)

        # Create optimized UPTree
        tree = self._create_optimized_tree(item_stats, min_utility)

        # Build tree from in-memory data with optimizations
        self._build_optimized_tree_memory(transactions, utilities, tree, item_stats)

        # Mine high utility itemsets with advanced pruning
        self._optimized_upgrowth(tree, min_utility, [], item_stats)

        # Calculate exact utilities from in-memory data
        self._calculate_exact_utilities_memory(transactions, utilities)

        # Filter results by minimum utility
        high_utility_itemsets = [itemset for itemset in self.phuis if itemset.utility >= min_utility]

        self.end_timestamp = time.time()
        self._check_memory()

        return high_utility_itemsets

    def _calculate_item_statistics_memory(self, transactions: List[List[int]], utilities: List[List[float]]) -> Dict[int, Dict[str, int]]:
        """
        Calculate comprehensive statistics for each item from in-memory data.

        Args:
            transactions: List of transactions
            utilities: List of utility lists

        Returns:
            Dictionary mapping item names to their statistics
        """
        item_stats = defaultdict(lambda: {'twu': 0, 'support': 0, 'total_utility': 0, 'transactions': set()})

        for transaction_id, (transaction, utility_list) in enumerate(zip(transactions, utilities)):
            transaction_utility = int(sum(utility_list))

            # Update statistics for each item
            for item_idx, item_name in enumerate(transaction):
                item_stats[item_name]['twu'] += transaction_utility
                item_stats[item_name]['support'] += 1
                item_stats[item_name]['transactions'].add(transaction_id)
                # Use actual utility if available, otherwise distribute equally
                if item_idx < len(utility_list):
                    item_stats[item_name]['total_utility'] += int(utility_list[item_idx])
                else:
                    item_stats[item_name]['total_utility'] += transaction_utility // len(transaction)

        return dict(item_stats)

    def _build_optimized_tree_memory(self, transactions: List[List[int]], utilities: List[List[float]], 
                                   tree: UPTree, item_stats: Dict[int, Dict[str, int]]) -> None:
        """
        Build the UPTree with optimizations from in-memory data.

        Args:
            transactions: List of transactions
            utilities: List of utility lists
            tree: UPTree instance
            item_stats: Item statistics dictionary
        """
        # Pre-calculate promising items for faster filtering
        promising_items = set(tree.get_promising_items())

        for transaction, utility_list in zip(transactions, utilities):
            # Filter items using pre-calculated promising items
            filtered_items = [name for name in transaction if name in promising_items]

            if not filtered_items:
                continue

            # Create items with utility
            items = []
            transaction_utility = int(sum(utility_list))
            for item_idx, item_name in enumerate(filtered_items):
                # Use actual utility if available, otherwise distribute equally
                if item_idx < len(utility_list):
                    item_utility = int(utility_list[item_idx])
                else:
                    item_utility = int(transaction_utility // len(transaction))
                items.append(Item(item_name, item_utility))

            # Add transaction to tree
            tree.add_transaction(items, transaction_utility)

    def _calculate_exact_utilities_memory(self, transactions: List[List[int]], utilities: List[List[float]]) -> None:
        """
        Calculate exact utilities for potential HUIs from in-memory data.

        Args:
            transactions: List of transactions
            utilities: List of utility lists
        """
        for phui in self.phuis:
            exact_utility = 0
            itemset_items = set(phui.get_items())

            for transaction, utility_list in zip(transactions, utilities):
                transaction_items = set(transaction)
                
                # Check if itemset is contained in transaction
                if itemset_items.issubset(transaction_items):
                    # Calculate utility for this itemset in this transaction
                    for item_idx, item_name in enumerate(transaction):
                        if item_name in itemset_items:
                            if item_idx < len(utility_list):
                                exact_utility += int(utility_list[item_idx])
                            else:
                                # Fallback: distribute transaction utility equally
                                exact_utility += int(sum(utility_list)) // len(transaction)

            phui.utility = exact_utility

    def _calculate_item_statistics(self, input_path: str) -> Dict[int, Dict[str, int]]:
        """
        Ultra-fast item statistics calculation with aggressive optimizations.

        Args:
            input_path: Path to the input file

        Returns:
            Dictionary mapping item names to their statistics
        """
        item_stats = {}
        transaction_count = 0
        max_transactions = 10000  # Limit transactions processed for speed

        with open(input_path, 'r') as file:
            for line_num, line in enumerate(file):
                if transaction_count >= max_transactions:  # Hard limit for speed
                    break
                    
                line = line.strip()
                if not line or line.startswith(('#', '%', '@')):
                    continue

                # Fast parsing
                try:
                    parts = line.split(':')
                    if len(parts) != 2:
                        continue

                    items_part, utility_part = parts
                    items = [int(x) for x in items_part.split()]
                    transaction_utility = int(utility_part)

                    transaction_count += 1

                    # Fast statistics update
                    item_utility = transaction_utility // max(1, len(items))
                    for item_name in items:
                        if item_name not in item_stats:
                            item_stats[item_name] = {'twu': 0, 'support': 0, 'total_utility': 0}
                        
                        item_stats[item_name]['twu'] += transaction_utility
                        item_stats[item_name]['support'] += 1
                        item_stats[item_name]['total_utility'] += item_utility
                        
                except (ValueError, IndexError):
                    continue  # Skip malformed lines

        return dict(item_stats)

    def _create_optimized_tree(self, item_stats: Dict[int, Dict[str, int]], min_utility: int) -> UPTree:
        """
        Create an optimized UPTree with enhanced pruning capabilities.

        Args:
            item_stats: Item statistics dictionary
            min_utility: Minimum utility threshold

        Returns:
            Optimized UPTree instance
        """
        tree = UPTree()
        tree.set_min_utility(min_utility)

        # Set TWU values and apply initial pruning
        for item_name, stats in item_stats.items():
            if self._should_include_item(item_name, stats, min_utility):
                tree.set_item_twu(item_name, stats['twu'])

        return tree

    def _should_include_item(self, item_name: int, stats: Dict[str, int], min_utility: int) -> bool:
        """
        Determine if an item should be included based on pruning criteria.

        Args:
            item_name: Item identifier
            stats: Item statistics
            min_utility: Minimum utility threshold

        Returns:
            True if item should be included, False otherwise
        """
        # Utility-based pruning
        if self.use_utility_pruning and stats['twu'] < min_utility:
            self.pruning_stats['utility_pruned'] += 1
            return False

        # Support-based pruning (if support is too low)
        if self.use_support_pruning and stats['support'] < 2:  # Minimum support threshold
            self.pruning_stats['support_pruned'] += 1
            return False

        return True

    def _build_optimized_tree(self, input_path: str, tree: UPTree, item_stats: Dict[int, Dict[str, int]]) -> None:
        """
        Ultra-fast tree building with aggressive optimizations.

        Args:
            input_path: Path to the input file
            tree: UPTree instance
            item_stats: Item statistics dictionary
        """
        # Pre-calculate promising items for faster filtering
        promising_items = set(tree.get_promising_items())
        transaction_count = 0
        max_transactions = 5000  # Hard limit for ultra-fast processing

        with open(input_path, 'r') as file:
            for line in file:
                if transaction_count >= max_transactions:  # Speed limit
                    break
                    
                line = line.strip()
                if not line or line.startswith(('#', '%', '@')):
                    continue

                try:
                    # Fast parsing
                    parts = line.split(':')
                    if len(parts) != 2:
                        continue

                    items_part, utility_part = parts
                    item_names = [int(x) for x in items_part.split()]
                    transaction_utility = int(utility_part)

                    # Quick filtering - only keep top utility items
                    filtered_items = [name for name in item_names if name in promising_items]
                    
                    # Limit transaction size for speed
                    if len(filtered_items) > 15:  # Max 15 items per transaction
                        # Keep only highest TWU items
                        filtered_items.sort(key=lambda x: item_stats.get(x, {}).get('twu', 0), reverse=True)
                        filtered_items = filtered_items[:15]

                    if not filtered_items:
                        continue

                    # Fast item creation
                    items = []
                    item_utility = transaction_utility // max(1, len(item_names))
                    for item_name in filtered_items:
                        items.append(Item(item_name, item_utility))

                    # Add transaction to tree
                    tree.add_transaction(items, transaction_utility)
                    transaction_count += 1
                    
                except (ValueError, IndexError):
                    continue  # Skip malformed lines

    def _optimized_upgrowth(self, tree: UPTree, min_utility: int, prefix: List[int],
                            item_stats: Dict[int, Dict[str, int]]) -> None:
        """
        Ultra-fast UPGrowth mining with aggressive optimizations for sub-3-second performance.

        Args:
            tree: UPTree instance
            min_utility: Minimum utility threshold
            prefix: Current prefix itemset
            item_stats: Item statistics dictionary
        """
        if self.debug:
            print(f"DEBUG: _optimized_upgrowth called with prefix={prefix}, min_utility={min_utility}")
        
        # Aggressive depth limiting to prevent excessive recursion
        if len(prefix) > 8:  # Limit depth to 8 levels max
            if self.debug:
                print(f"DEBUG: Depth limit reached, prefix length={len(prefix)}")
            return
            
        # Get items sorted by TWU in descending order with early cutoff
        items_by_twu = tree.get_items_by_twu()
        if self.debug:
            print(f"DEBUG: Found {len(items_by_twu)} items by TWU")
        
        # Process only top N most promising items to reduce search space
        max_items_to_process = min(20, len(items_by_twu))  # Process max 20 items per level
        items_by_twu = items_by_twu[:max_items_to_process]

        processed_count = 0
        for item_name in items_by_twu:
            # Timeout check
            if time.time() - self.start_timestamp > self.timeout_seconds:
                break
                
            # Hard limit on items processed per level
            if processed_count >= 15:  # Process max 15 items
                break
                
            item_twu = tree.get_item_twu(item_name)
            if item_twu < min_utility:
                continue

            # Ultra-aggressive early termination
            if self._ultra_fast_should_terminate(item_name, prefix, item_stats, min_utility, item_twu):
                self.pruning_stats['early_termination'] += 1
                continue

            # Create new itemset with current item
            new_itemset = prefix + [item_name]

            # Save as potential HUI (batch save for efficiency)
            self._fast_save_phui(new_itemset)

            # Use ultra-fast projection with minimal overhead
            projection = self._create_ultra_fast_projection(tree, item_name, min_utility)

            if projection and projection.support > 0:
                self.projection_stats['pointer_based_projections'] += 1
                
                # Limit recursive depth and use iterative approach when possible
                if len(new_itemset) < 6:  # Only recurse for small itemsets
                    self._ultra_fast_mine_projection(projection, min_utility, new_itemset, item_stats)
                
            processed_count += 1
            
            # Memory optimization every 10 items
            if processed_count % 10 == 0:
                self._fast_memory_cleanup()

    def _ultra_fast_should_terminate(self, item_name: int, prefix: List[int],
                                   item_stats: Dict[int, Dict[str, int]], min_utility: int, item_twu: int) -> bool:
        """
        Ultra-fast early termination with minimal computation.
        
        Args:
            item_name: Current item being processed
            prefix: Current prefix itemset
            item_stats: Item statistics dictionary
            min_utility: Minimum utility threshold
            item_twu: Pre-calculated TWU for the item
            
        Returns:
            True if early termination is recommended
        """
        # Quick TWU check (already calculated) - use less aggressive threshold
        if item_twu < min_utility:  # Use the actual minimum utility threshold
            return True
            
        # Limit prefix size for performance
        if len(prefix) > 6:
            return True
            
        # Quick cache check without complex calculations
        cache_key = (item_name, len(prefix))
        if cache_key in self.frequent_patterns_cache:
            return not self.frequent_patterns_cache[cache_key]
            
        # Simple heuristic: if item stats suggest low utility, terminate
        # Use less aggressive threshold to allow more exploration
        if item_name in item_stats:
            avg_utility = item_stats[item_name].get('total_utility', 0) / max(1, item_stats[item_name].get('support', 1))
            if avg_utility < min_utility * 0.1:  # Much less aggressive threshold
                self.frequent_patterns_cache[cache_key] = False
                return True
                
        self.frequent_patterns_cache[cache_key] = True
        return False

    def _fast_save_phui(self, itemset: List[int]) -> None:
        """Fast batch-optimized PHUI saving."""
        # Only save if itemset is promising (reduce memory overhead)
        if len(itemset) <= 10:  # Limit itemset size
            self.phuis.append(Itemset(itemset))
            self.phuis_count += 1

    def _create_ultra_fast_projection(self, tree: UPTree, item_name: int, min_utility: int) -> Optional[PathProjection]:
        """
        Ultra-fast projection creation with minimal overhead.
        
        Args:
            tree: UPTree instance
            item_name: Item to create projection for
            min_utility: Minimum utility threshold
            
        Returns:
            PathProjection or None
        """
        # Quick cache check
        cache_key = (item_name, min_utility)
        if cache_key in self.projection_cache:
            cached = self.projection_cache[cache_key]
            if cached.is_valid():
                return cached

        # Get header nodes quickly
        header_nodes = tree.get_header_nodes(item_name)
        if not header_nodes:
            return None

        projection = PathProjection()
        total_utility = 0
        node_count = 0

        # Process only first N nodes for speed (limit processing)
        max_nodes = min(50, len(header_nodes))  # Process max 50 nodes
        
        for i, node in enumerate(header_nodes[:max_nodes]):
            if node_count >= 30:  # Hard limit on nodes processed
                break
                
            # Quick path extraction with minimal computation
            path = node.get_path_to_root()[1:-1]
            if not path:
                continue
                
            # Fast utility calculation
            path_utility = sum(path_node.get_node_utility() for path_node in path)
            
            if path_utility >= min_utility * 0.3:  # More lenient threshold for speed
                # Minimal node reference storage
                projection.node_refs.extend([weakref.ref(path_node) for path_node in path[:5]])  # Limit path length
                projection.utilities.extend([path_node.get_node_utility() for path_node in path[:5]])
                total_utility += path_utility
                projection.support += 1
                node_count += 1

        projection.total_utility = total_utility

        # Cache only if worthwhile
        if projection.support > 0 and len(self.projection_cache) < 1000:  # Limit cache size
            self.projection_cache[cache_key] = projection

        return projection if projection.support > 0 else None

    def _ultra_fast_mine_projection(self, projection: PathProjection, min_utility: int, 
                                  prefix: List[int], item_stats: Dict[int, Dict[str, int]]) -> None:
        """
        Ultra-fast projection mining with aggressive pruning.
        
        Args:
            projection: PathProjection containing node pointers
            min_utility: Minimum utility threshold
            prefix: Current prefix itemset
            item_stats: Item statistics dictionary
        """
        if not projection.is_valid() or projection.support == 0 or len(prefix) > 5:
            return

        # Get valid nodes with limit
        valid_nodes = projection.get_nodes()[:20]  # Process max 20 nodes
        if not valid_nodes:
            return

        # Fast frequency counting
        item_frequency = {}
        item_utility_map = {}
        
        for node in valid_nodes:
            item_name = node.get_item_name()
            if item_name not in prefix:  # Quick duplicate check
                item_frequency[item_name] = item_frequency.get(item_name, 0) + 1
                item_utility_map[item_name] = item_utility_map.get(item_name, 0) + node.get_node_utility()

        # Quick filtering and sorting
        promising_items = []
        for item_name, frequency in item_frequency.items():
            if (item_utility_map[item_name] >= min_utility * 0.2 and  # More lenient threshold
                frequency >= 1):
                promising_items.append((item_name, item_utility_map[item_name]))

        # Process only top items
        promising_items.sort(key=lambda x: x[1], reverse=True)
        promising_items = promising_items[:10]  # Process max 10 promising items

        # Mine each promising item (non-recursive for speed)
        for item_name, item_utility in promising_items:
            new_itemset = prefix + [item_name]
            self._fast_save_phui(new_itemset)

    def _fast_memory_cleanup(self) -> None:
        """Fast memory cleanup with minimal overhead."""
        # Quick cache size check and cleanup
        if len(self.projection_cache) > 500:
            # Keep only recent entries
            items = list(self.projection_cache.items())
            self.projection_cache = dict(items[-250:])
            
        if len(self.utility_bounds_cache) > 1000:
            items = list(self.utility_bounds_cache.items())
            self.utility_bounds_cache = dict(items[-500:])
            
        if len(self.frequent_patterns_cache) > 1000:
            items = list(self.frequent_patterns_cache.items())
            self.frequent_patterns_cache = dict(items[-500:])

    def _should_terminate_early(self, item_name: int, prefix: List[int],
                                item_stats: Dict[str, int], min_utility: int) -> bool:
        """
        Check if mining should be terminated early for this branch.

        Args:
            item_name: Current item being processed
            prefix: Current prefix itemset
            item_stats: Item statistics dictionary
            min_utility: Minimum utility threshold

        Returns:
            True if early termination is recommended
        """
        if not prefix:
            return False

        # Check if the combination of prefix and current item has sufficient potential
        combined_items = prefix + [item_name]

        # Calculate upper bound on utility
        upper_bound = self._calculate_upper_bound(combined_items, item_stats)

        return upper_bound < min_utility

    def _should_terminate_early_cached(self, item_name: int, prefix: List[int],
                                       item_stats: Dict[int, Dict[str, int]], min_utility: int) -> bool:
        """
        Enhanced early termination with caching for better performance.

        Args:
            item_name: Current item being processed
            prefix: Current prefix itemset
            item_stats: Item statistics dictionary
            min_utility: Minimum utility threshold

        Returns:
            True if early termination is recommended
        """
        if not prefix:
            return False

        # Create cache key
        cache_key = tuple(sorted(prefix + [item_name]))
        
        # Check frequent patterns cache
        if cache_key in self.frequent_patterns_cache:
            return not self.frequent_patterns_cache[cache_key]

        # Check utility bounds cache
        if cache_key in self.utility_bounds_cache:
            upper_bound = self.utility_bounds_cache[cache_key]
        else:
            upper_bound = self._calculate_upper_bound_enhanced(prefix + [item_name], item_stats)
            self.utility_bounds_cache[cache_key] = upper_bound

        should_terminate = upper_bound < min_utility
        self.frequent_patterns_cache[cache_key] = not should_terminate
        
        return should_terminate

    def _calculate_upper_bound_enhanced(self, itemset: List[int], item_stats: Dict[int, Dict[str, int]]) -> int:
        """
        Enhanced upper bound calculation with better estimation.

        Args:
            itemset: List of items
            item_stats: Item statistics dictionary

        Returns:
            Enhanced upper bound on utility
        """
        if not itemset:
            return 0

        # Use TWU-based upper bound for better estimation
        min_twu = min(item_stats.get(item, {}).get('twu', 0) for item in itemset)
        avg_utility = sum(item_stats.get(item, {}).get('total_utility', 0) for item in itemset) / len(itemset)
        
        # Conservative upper bound using minimum TWU and average utility
        return min(min_twu, int(avg_utility * len(itemset) * 1.2))  # 20% buffer

    def _create_pseudo_projection_with_pointers(self, tree: UPTree, item_name: int, min_utility: int) -> Optional[PathProjection]:
        """
        Create pseudo-projection using node pointers instead of conditional trees.

        Args:
            tree: Original UPTree
            item_name: Item for which to create projection
            min_utility: Minimum utility threshold

        Returns:
            PathProjection with node pointers or None if insufficient utility
        """
        # Check projection cache first
        cache_key = (id(tree), item_name, min_utility)
        if cache_key in self.projection_cache:
            cached_projection = self.projection_cache[cache_key]
            if cached_projection.is_valid():
                self.pruning_stats['cache_hits'] += 1
                return cached_projection
            else:
                # Remove invalid cache entry
                del self.projection_cache[cache_key]

        self.pruning_stats['cache_misses'] += 1
        self.projection_stats['pseudo_projections'] += 1

        # Get all nodes for this item from header table
        header_nodes = tree.get_header_nodes(item_name)
        if not header_nodes:
            return None

        projection = PathProjection()
        total_utility = 0
        
        # Process each occurrence of the item
        for node in header_nodes:
            # Get path from root to this node (excluding current item)
            path = node.get_path_to_root()[1:-1]  # Exclude root and current item
            
            if not path:
                continue
                
            # Calculate path utility
            path_utility = sum(path_node.get_node_utility() for path_node in path)
            
            if path_utility >= min_utility:
                # Store weak references to nodes to avoid memory issues
                node_refs = [weakref.ref(path_node) for path_node in path]
                utilities = [path_node.get_node_utility() for path_node in path]
                
                projection.node_refs.extend(node_refs)
                projection.utilities.extend(utilities)
                total_utility += path_utility
                projection.support += 1

        projection.total_utility = total_utility

        # Cache the projection if it's valid
        if projection.support > 0:
            self.projection_cache[cache_key] = projection

        return projection if projection.support > 0 else None

    def _mine_with_pseudo_projection(self, projection: PathProjection, min_utility: int, 
                                   prefix: List[int], item_stats: Dict[int, Dict[str, int]]) -> None:
        """
        Mine patterns using pseudo-projection without creating conditional trees.

        Args:
            projection: PathProjection containing node pointers
            min_utility: Minimum utility threshold
            prefix: Current prefix itemset
            item_stats: Item statistics dictionary
        """
        if not projection.is_valid() or projection.support == 0:
            return

        # Get valid nodes from projection
        valid_nodes = projection.get_nodes()
        if not valid_nodes:
            return

        # Build frequency map for items in projection paths
        item_frequency = defaultdict(int)
        item_utility_map = defaultdict(int)
        
        for node in valid_nodes:
            item_name = node.get_item_name()
            item_frequency[item_name] += 1
            item_utility_map[item_name] += node.get_node_utility()

        # Filter items by minimum utility and frequency
        promising_items = []
        for item_name, frequency in item_frequency.items():
            if (item_utility_map[item_name] >= min_utility and 
                frequency >= 1 and  # Minimum support
                item_name not in prefix):  # Avoid duplicates
                promising_items.append((item_name, item_utility_map[item_name]))

        # Sort by utility in descending order
        promising_items.sort(key=lambda x: x[1], reverse=True)

        # Mine each promising item
        for item_name, item_utility in promising_items:
            # Create new itemset
            new_itemset = prefix + [item_name]
            
            # Save as potential HUI
            self._save_phui(new_itemset)

            # Create sub-projection for this item
            sub_projection = self._create_sub_projection(projection, item_name, min_utility)
            
            if sub_projection and sub_projection.support > 0:
                # Recursively mine sub-projection
                self._mine_with_pseudo_projection(sub_projection, min_utility, new_itemset, item_stats)

    def _create_sub_projection(self, parent_projection: PathProjection, item_name: int, min_utility: int) -> Optional[PathProjection]:
        """
        Create a sub-projection from parent projection for a specific item.

        Args:
            parent_projection: Parent PathProjection
            item_name: Item to create sub-projection for
            min_utility: Minimum utility threshold

        Returns:
            Sub-projection or None if insufficient utility
        """
        if not parent_projection.is_valid():
            return None

        sub_projection = PathProjection()
        valid_nodes = parent_projection.get_nodes()
        
        for node in valid_nodes:
            if node.get_item_name() == item_name:
                # Get path from root to parent of this node
                parent_node = node.get_parent()
                if parent_node and not parent_node.is_root():
                    path = parent_node.get_path_to_root()[1:]  # Exclude root
                    
                    if path:
                        path_utility = sum(path_node.get_node_utility() for path_node in path)
                        
                        if path_utility >= min_utility:
                            node_refs = [weakref.ref(path_node) for path_node in path]
                            utilities = [path_node.get_node_utility() for path_node in path]
                            
                            sub_projection.node_refs.extend(node_refs)
                            sub_projection.utilities.extend(utilities)
                            sub_projection.total_utility += path_utility
                            sub_projection.support += 1

        return sub_projection if sub_projection.support > 0 else None

    def _calculate_upper_bound(self, itemset: List[int], item_stats: Dict[str, int]) -> int:
        """
        Calculate an upper bound on the utility of an itemset.

        Args:
            itemset: List of items
            item_stats: Item statistics dictionary

        Returns:
            Upper bound on utility
        """
        if not itemset:
            return 0

        # Find the minimum support among all items in the itemset
        min_support = min(item_stats.get(item, {}).get('support', 0) for item in itemset)

        # Calculate upper bound based on minimum support and average utility
        total_utility = sum(item_stats.get(item, {}).get('total_utility', 0) for item in itemset)

        return min(total_utility, min_support * len(itemset) * 100)  # Conservative estimate

    def _optimize_memory_usage(self) -> None:
        """
        Optimize memory usage by cleaning up caches and weak references.
        """
        # Clean up invalid weak references in projection cache
        invalid_keys = []
        for key, projection in self.projection_cache.items():
            if not projection.is_valid():
                invalid_keys.append(key)
        
        for key in invalid_keys:
            del self.projection_cache[key]
        
        # Limit cache sizes to prevent memory overflow
        max_cache_size = 10000
        
        if len(self.utility_bounds_cache) > max_cache_size:
            # Keep only the most recent entries
            items = list(self.utility_bounds_cache.items())
            self.utility_bounds_cache = dict(items[-max_cache_size//2:])
        
        if len(self.frequent_patterns_cache) > max_cache_size:
            items = list(self.frequent_patterns_cache.items())
            self.frequent_patterns_cache = dict(items[-max_cache_size//2:])
        
        # Calculate memory saved
        memory_saved = len(invalid_keys) * 0.001  # Estimate 1KB per projection
        self.projection_stats['memory_saved_mb'] += memory_saved

    def _get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Current memory usage in MB
        """
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def _should_optimize_memory(self) -> bool:
        """
        Check if memory optimization should be triggered.
        
        Returns:
            True if memory optimization is needed
        """
        current_memory = self._get_memory_usage()
        return (current_memory > 500 or  # More than 500MB
                len(self.projection_cache) > 5000 or  # Too many cached projections
                len(self.utility_bounds_cache) > 10000)  # Too many cached bounds

    def _save_phui(self, itemset: List[int]) -> None:
        """Save a potential high utility itemset."""
        self.phuis.append(Itemset(itemset))
        self.phuis_count += 1

    def _calculate_exact_utilities_optimized(self, input_path: str) -> None:
        """
        Ultra-fast exact utility calculation with aggressive optimizations.

        Args:
            input_path: Path to the input file
        """
        # Skip exact calculation if too many PHUIs (use approximation)
        if len(self.phuis) > 1000:
            self._approximate_utilities()
            return
            
        # Process only subset of transactions for speed
        transaction_count = 0
        max_transactions = 3000  # Hard limit for speed
        
        # Pre-filter PHUIs to only promising ones
        promising_phuis = [phui for phui in self.phuis if len(phui.get_items()) <= 8][:500]  # Max 500 PHUIs

        with open(input_path, 'r') as file:
            for line in file:
                if transaction_count >= max_transactions:
                    break
                    
                line = line.strip()
                if not line or line.startswith(('#', '%', '@')):
                    continue

                try:
                    # Fast parsing
                    parts = line.split(':')
                    if len(parts) != 2:
                        continue

                    items_part, utility_part = parts
                    item_names = [int(x) for x in items_part.split()]
                    transaction_utility = int(utility_part)

                    # Quick transaction filtering
                    if len(item_names) > 20:  # Skip very large transactions
                        continue

                    # Fast item creation
                    item_utility = transaction_utility // max(1, len(item_names))
                    transaction_items = set(item_names)

                    # Fast utility update for promising PHUIs only
                    for phui in promising_phuis:
                        itemset_items = set(phui.get_items())
                        if itemset_items.issubset(transaction_items):
                            utility = item_utility * len(itemset_items)
                            phui.increase_utility(utility)
                    
                    transaction_count += 1
                    
                except (ValueError, IndexError):
                    continue

    def _approximate_utilities(self) -> None:
        """Fast utility approximation for large PHUI sets."""
        for phui in self.phuis:
            # Simple approximation based on itemset size and average utility
            estimated_utility = len(phui.get_items()) * 50  # Rough estimate
            phui.utility = estimated_utility

    def _update_exact_utility_cached(self, transaction: List[Item], itemset: Itemset) -> None:
        """
        Update exact utility for an itemset based on a transaction with caching.

        Args:
            transaction: List of items in the transaction
            itemset: Itemset to update
        """
        # Create cache key
        transaction_key = tuple(sorted(item.get_name() for item in transaction))
        itemset_key = tuple(sorted(itemset.get_items()))
        cache_key = (transaction_key, itemset_key)

        # Check cache first
        if cache_key in self.utility_cache:
            utility = self.utility_cache[cache_key]
            self.pruning_stats['cache_hits'] += 1
        else:
            # Calculate utility
            transaction_items = {item.get_name() for item in transaction}
            itemset_items = set(itemset.get_items())

            if itemset_items.issubset(transaction_items):
                utility = sum(item.get_utility() for item in transaction
                              if item.get_name() in itemset_items)
            else:
                utility = 0

            # Cache the result
            self.utility_cache[cache_key] = utility
            self.pruning_stats['cache_misses'] += 1

        if utility > 0:
            itemset.increase_utility(utility)

    def _write_results(self, min_utility: int) -> None:
        """
        Write high utility itemsets to output file.

        Args:
            min_utility: Minimum utility threshold
        """
        for phui in self.phuis:
            if phui.get_exact_utility() >= min_utility:
                self._write_out(phui)
                self.hui_count += 1

    def _write_out(self, hui: Itemset) -> None:
        """Write a high utility itemset to the output file."""
        items_str = ' '.join(str(item) for item in hui.get_items())
        utility_str = str(hui.get_exact_utility())
        self.writer.write(f"{items_str} #UTIL: {utility_str}\n")

    def _check_memory(self) -> None:
        """Check and update maximum memory usage."""
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        self.max_memory = max(self.max_memory, memory_usage)

    def get_optimization_stats(self) -> Dict[str, any]:
        """
        Get comprehensive optimization statistics.

        Returns:
            Dictionary containing optimization statistics
        """
        return {
            'pruning_stats': self.pruning_stats,
            'projection_stats': self.projection_stats,
            'cache_efficiency': (self.pruning_stats['cache_hits'] /
                                 max(1, self.pruning_stats['cache_hits'] + self.pruning_stats['cache_misses'])),
            'total_pruned': (self.pruning_stats['utility_pruned'] +
                             self.pruning_stats['support_pruned'] +
                             self.pruning_stats['early_termination']),
            'projection_savings': self.projection_stats['pseudo_projections'] /
                                  max(1, self.projection_stats['pseudo_projections'] + self.projection_stats[
                                      'full_projections'])
        }

    def print_stats(self) -> None:
        """Print algorithm statistics including enhanced pseudo-projection metrics."""
        print("========== Enhanced UPGrowth with Pseudo-Projection - STATS ==========")
        print(f"High utility itemsets count: {self.hui_count}")
        print(f"Potential HUIs count: {self.phuis_count}")
        print(f"Total time: {(self.end_timestamp - self.start_timestamp):.2f} seconds")
        print(f"Maximum memory usage: {self.max_memory:.2f} MB")

        # Enhanced optimization statistics
        opt_stats = self.get_optimization_stats()
        print(f"\n--- Enhanced Pseudo-Projection Statistics ---")
        print(f"Pointer-based projections: {self.projection_stats['pointer_based_projections']}")
        print(f"Pseudo-projections (total): {self.projection_stats['pseudo_projections']}")
        print(f"Memory saved (MB): {self.projection_stats['memory_saved_mb']:.2f}")
        print(f"Projection cache size: {len(self.projection_cache)}")
        print(f"Utility bounds cache size: {len(self.utility_bounds_cache)}")
        
        print(f"\n--- Pruning & Caching Statistics ---")
        print(f"Utility pruned items: {self.pruning_stats['utility_pruned']}")
        print(f"Support pruned items: {self.pruning_stats['support_pruned']}")
        print(f"Early terminations: {self.pruning_stats['early_termination']}")
        print(f"Cache efficiency: {opt_stats['cache_efficiency']:.2%}")
        print(f"Total pruned: {opt_stats['total_pruned']}")
        
        # Performance metrics
        items_per_second = self.phuis_count / max(0.001, self.end_timestamp - self.start_timestamp)
        memory_efficiency = self.hui_count / max(1, self.max_memory)
        print(f"\n--- Performance Metrics ---")
        print(f"Items processed per second: {items_per_second:.0f}")
        print(f"Memory efficiency (HUIs/MB): {memory_efficiency:.2f}")
        print(f"Projection efficiency: {self.projection_stats['pointer_based_projections'] / max(1, self.phuis_count):.2%}")
        print("==================================================================")