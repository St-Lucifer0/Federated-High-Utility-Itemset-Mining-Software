"""
The item class represents the items with its utility value used in the algorithm.
"""

from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class Item:
    """
    It represents an item with its name and utility value
    """
    name: Union[int, str]
    utility: int = 0

    def __post_init__(self):
        """Validate item data after initialization"""
        if not isinstance(self.name, (int, str)):
            raise ValueError("Item name must be an integer or string")
        if not isinstance(self.utility, int):
            raise ValueError("Utility value must be an integer")
        if self.utility < 0:
            raise ValueError("Utility value should be a non-negative integer")

    def get_utility(self) -> int:
        """Get the utility value of this item"""
        return self.utility

    def set_utility(self, utility: int) -> None:
        """Set the utility value of the item"""
        if utility < 0:
            raise ValueError("Utility value must be positive")
        self.utility = utility

    def get_name(self) -> Union[str,int]:
        """Get the name of an item"""
        return self.name

    def __str__(self) -> str:
        """String representation of the item if it is an integer"""
        return f"Item(name={self.name}, utility={self.utility})"

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"Item(name={self.name}, utility={self.utility})"

    def __eq__(self, other) -> bool:
        """Check equality between two items based on their names"""
        if isinstance(other, Item):
            return self.name == other.name
        elif isinstance(other, (int,str)):
            return self.name == other
        else:
            return False

    def __hash__(self) -> int:
        """Hash based on the item name and utility"""
        return hash((self.name, self.utility))
