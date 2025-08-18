"""
UPTree class for High Utility Itemset Mining algorithms.

This class represents the UPTree data structure used by the UPGrowth algorithm.
It provides efficient storage and retrieval of itemsets with utility information.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from .up_node import UPNode
from .item import Item


@dataclass
class UPTree:
    """
    Represents a UPTree for the UPGrowth algorithm.

    Attributes:
        root: The root node of the tree
        header_table: Dictionary mapping item names to their header table entries
        item_to_twu: Dictionary mapping item names to their TWU values
        min_utility: The minimum utility threshold
    """
    root: UPNode = field(default_factory=lambda: UPNode(Item(-1, 0)))  # Root with dummy item
    header_table: Dict[int, List[UPNode]] = field(default_factory=dict)
    item_to_twu: Dict[int, int] = field(default_factory=dict)
    min_utility: int = 0

    def __post_init__(self):
        """Initialize the tree after creation."""
        self.root.set_node_utility(0)
        self.root.set_count(0)

    def add_transaction(self, transaction: List[Item], twu: int) -> None:
        """
        Add a transaction to the tree.

        Args:
            transaction: List of items in the transaction
            twu: Transaction Weighted Utility of the transaction
        """
        if not transaction:
            return

        # Sort items by TWU in descending order
        sorted_items = sorted(transaction,
                              key=lambda item: self.item_to_twu.get(item.get_name(), 0),
                              reverse=True)

        # Filter items that meet minimum utility threshold
        filtered_items = [item for item in sorted_items
                          if self.item_to_twu.get(item.get_name(), 0) >= self.min_utility]

        if not filtered_items:
            return

        # Insert the transaction into the tree
        self._insert_transaction(filtered_items, twu)

    def _insert_transaction(self, items: List[Item], twu: int) -> None:
        """Insert a transaction into the tree."""
        current_node = self.root

        for item in items:
            item_name = item.get_name()
            child = current_node.get_child(item_name)

            if child is None:
                # Create new child node
                child = UPNode(item)
                child.set_node_utility(item.get_utility())
                current_node.add_child(child)

                # Add to header table
                if item_name not in self.header_table:
                    self.header_table[item_name] = []
                self.header_table[item_name].append(child)
            else:
                # Update existing node
                child.set_count(child.get_count() + 1)
                child.set_node_utility(child.get_node_utility() + item.get_utility())

            current_node = child

    def get_header_table(self) -> Dict[int, List[UPNode]]:
        """Get the header table of the tree."""
        return self.header_table

    def get_item_twu(self, item_name: int) -> int:
        """Get the TWU value for a specific item."""
        return self.item_to_twu.get(item_name, 0)

    def set_item_twu(self, item_name: int, twu: int) -> None:
        """Set the TWU value for a specific item."""
        self.item_to_twu[item_name] = twu

    def get_min_utility(self) -> int:
        """Get the minimum utility threshold."""
        return self.min_utility

    def set_min_utility(self, min_utility: int) -> None:
        """Set the minimum utility threshold."""
        if min_utility < 0:
            raise ValueError("Minimum utility cannot be negative")
        self.min_utility = min_utility

    def get_root(self) -> UPNode:
        """Get the root node of the tree."""
        return self.root

    def get_items_by_twu(self) -> List[int]:
        """Get items sorted by TWU in descending order."""
        return sorted(self.item_to_twu.keys(),
                      key=lambda item: self.item_to_twu[item],
                      reverse=True)

    def get_promising_items(self) -> List[int]:
        """Get items that meet the minimum utility threshold."""
        return [item for item, twu in self.item_to_twu.items()
                if twu >= self.min_utility]

    def get_header_nodes(self, item_name: int) -> List[UPNode]:
        """Get all nodes in the header table for a specific item."""
        return self.header_table.get(item_name, [])

    def remove_item_from_header(self, item_name: int) -> None:
        """Remove an item from the header table."""
        if item_name in self.header_table:
            del self.header_table[item_name]

    def clear(self) -> None:
        """Clear the tree and reset to initial state."""
        self.root = UPNode(Item(-1, 0))
        self.root.set_node_utility(0)
        self.root.set_count(0)
        self.header_table.clear()
        self.item_to_twu.clear()

    def get_tree_size(self) -> int:
        """Get the total number of nodes in the tree (excluding root)."""

        def count_nodes(node: UPNode) -> int:
            count = 1  # Count current node
            for child in node.get_children().values():
                count += count_nodes(child)
            return count

        return count_nodes(self.root) - 1  # Exclude root

    def get_depth(self) -> int:
        """Get the maximum depth of the tree."""

        def get_max_depth(node: UPNode, current_depth: int) -> int:
            if not node.has_children():
                return current_depth

            max_child_depth = current_depth
            for child in node.get_children().values():
                child_depth = get_max_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

            return max_child_depth

        return get_max_depth(self.root, 0)

    def __str__(self) -> str:
        """String representation of the tree."""
        return f"UPTree(items={len(self.item_to_twu)}, nodes={self.get_tree_size()})"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"UPTree(items={len(self.item_to_twu)}, nodes={self.get_tree_size()}, "
                f"depth={self.get_depth()}, min_utility={self.min_utility})")