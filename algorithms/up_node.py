"""This class represents a node in the UPTree for UPGrowth algorithm"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from .item import Item



@dataclass
class UPNode:
    """
    Represents a node in the UPTree for UPGrowth algorithm

    Attributes:
        item: The item stored in this node
        count: the count of this item in the current path
        node_utility: the utility of this node
        parent: reference to the parent node
        children: a dictionary mapping to the child node
        node_link: link to the next node with the same item
        node_id: unique identifier for this node (for indexing)
    """
    item: Item
    count: int = 1
    node_utility: int = 0
    parent: Optional['UPNode'] = None
    children: Dict[int, 'UPNode'] = field(default_factory=dict)
    node_link: Optional['UPNode'] = None
    node_id: int = field(default_factory=lambda: id(object()))

    def __post_init__(self):
        """Validate the node data after initialization"""
        if not isinstance(self.item, Item):
            raise ValueError("Node item must be an Item in instance")
        if self.count < 0:
            raise ValueError("Count cannot be negative")
        if self.node_utility < 0:
            raise ValueError("Node utility cannot be negative")

    def get_item(self) -> Item:
        """Get the item stored in this node."""
        return self.item

    def get_item_name(self) -> int:
        """Get the name of the item stored in this node."""
        return self.item.get_name()

    def get_node_id(self) -> int:
        """Get the unique identifier of this node."""
        return self.node_id

    def get_count(self) -> int:
        """Get the count of this item in the current path."""
        return self.count

    def set_count(self, count: int) -> None:
        """Set the count of this item in the current path."""
        if count < 0:
            raise ValueError("Count cannot be negative")
        self.count = count

    def get_node_utility(self) -> int:
        """Get the utility of this node."""
        return self.node_utility

    def set_node_utility(self, utility: int) -> None:
        """Set the utility of this node."""
        if utility < 0:
            raise ValueError("Node utility cannot be negative")
        self.node_utility = utility

    def get_parent(self) -> Optional['UPNode']:
        """Get the parent node of this node."""
        return self.parent

    def set_parent(self, parent: Optional['UPNode']) -> None:
        """Set the parent node of this node."""
        self.parent = parent

    def get_children(self) -> Dict[int, 'UPNode']:
        """Get all children of this node."""
        return self.children

    def get_child(self, item_name: int) -> Optional['UPNode']:
        """Get a specific child node by item name."""
        return self.children.get(item_name)

    def add_child(self, child: 'UPNode') -> None:
        """Add a child node to this node."""
        if not isinstance(child, UPNode):
            raise ValueError("Child must be a UPNode instance")
        child.set_parent(self)
        self.children[child.get_item_name()] = child

    def remove_child(self, item_name: int) -> Optional['UPNode']:
        """Remove a child node by item name."""
        child = self.children.pop(item_name, None)
        if child:
            child.set_parent(None)
        return child

    def has_children(self) -> bool:
        """Check if this node has any children."""
        return len(self.children) > 0

    def get_node_link(self) -> Optional['UPNode']:
        """Get the next node with the same item (for header table)."""
        return self.node_link

    def set_node_link(self, node: Optional['UPNode']) -> None:
        """Set the next node with the same item (for header table)."""
        self.node_link = node

    def is_root(self) -> bool:
        """Check if this node is the root node."""
        return self.parent is None

    def is_leaf(self) -> bool:
        """Check if this node is a leaf node (no children)."""
        return len(self.children) == 0

    def get_path_to_root(self) -> List['UPNode']:
        """Get the path from this node to the root."""
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.get_parent()
        return list(reversed(path))

    def get_items_in_path(self) -> List[int]:
        """Get all item names in the path from root to this node."""
        path = self.get_path_to_root()
        return [node.get_item_name() for node in path if not node.is_root()]

    def __str__(self) -> str:
        """String representation of the node."""
        return f"UPNode(item={self.item}, count={self.count}, utility={self.node_utility})"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"UPNode(item={self.item}, count={self.count}, "
                f"utility={self.node_utility}, children={len(self.children)})")