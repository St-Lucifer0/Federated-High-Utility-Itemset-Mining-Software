"""
 Itemset class for High Utility Itemset Mining algorithms.

 This class represents an itemset and its exact utility.
"""

from dataclasses import dataclass, field
from item import Item
from typing import Optional, List, Tuple, Union
import copy

@dataclass
class Itemset:
    """
    Represents an itemset with its exact utility value
    Attributes:
        items (list): List of items in the itemset.
        utility (int): Exact utility value of the itemset.
    """

    itemset: List[Union[int, str]]
    utility: int = 0

    def __post_init__(self):
        """Validate the itemset data after initialization"""
        if not isinstance(self.itemset, list):
            raise ValueError("Itemset must be a list")
        if not all(isinstance(item, (int, str)) for item in self.itemset):
            raise ValueError("Items in the itemset must be integers or strings")
        if self.utility < 0:
            raise ValueError("Utility cannot be negative")
        # Ensure that itemset is sorted for consistency
        self.itemset = sorted(self.itemset)

    def get_exact_utility(self) -> int:
        """Get the exact utility of this itemset"""
        return self.utility

    def increase_utility(self, utility: int) -> None:
        """Increase the utility of this itemset by the given amount"""
        if self.utility < 0:
            raise ValueError("Utility cannot be negative")
        self.utility += utility

    def get(self, pos: (str, int)) -> int:
        """Get the item at the specified position"""
        if pos < 0 or pos >= len(self.itemset):
            raise IndexError("Position out of range")
        return self.itemset[pos]

    def size(self) -> int:
        """Get the size in this itemset"""
        return len(self.itemset)

    def is_empty(self) -> bool:
        """Check if this itemset is empty"""
        return len(self.itemset) == 0

    def contains(self, item: (str, int)) -> bool:
        """Check whether this itemset contains the given item"""
        return item in self.itemset

    def add_item(self, item: (str, int)) -> None:
        """Add an item to this itemset and maintain sorted order"""
        if item not in self.itemset:
            self.itemset.append(item)
            self.itemset.sort()

    def remove_item(self, item: int) -> bool:
        """Remove an item from this itemset if present."""
        if item in self.itemset:
            self.itemset.remove(item)
            return True
        return False

    def get_items(self) -> List[int]:
        """Get a copy of the items in this itemset."""
        return copy.copy(self.itemset)

    def __str__(self) -> str:
        """String representation of the itemset."""
        return f"Itemset({self.itemset}, utility={self.utility})"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return f"Itemset(itemset={self.itemset}, utility={self.utility})"

    def __eq__(self, other) -> bool:
        """Check if two itemsets are equal."""
        if not isinstance(other, Itemset):
            return False
        return self.itemset == other.itemset and self.utility == other.utility

    def __hash__(self) -> int:
        """Hash based on itemset contents and utility."""
        return hash((tuple(self.itemset), self.utility))

    def __len__(self) -> int:
        """Return the size of the itemset."""
        return len(self.itemset)

    def __contains__(self, item: int) -> bool:
        """Check if an item is in the itemset."""
        return item in self.itemset

    def __iter__(self):
        """Iterate over items in the itemset."""
        return iter(self.itemset)