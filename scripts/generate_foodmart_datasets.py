#!/usr/bin/env python3
"""
Generate three foodmart CSV datasets with different densities for HUI algorithm testing.
Format: items,quantities,unit_utilities (pipe-separated values within each field)
"""

import random
import csv
import os
from typing import List, Tuple

# Foodmart product categories and items
FOODMART_ITEMS = {
    'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice_cream'],
    'bakery': ['bread', 'croissant', 'bagel', 'muffin', 'cake', 'cookies'],
    'meat': ['chicken', 'beef', 'pork', 'turkey', 'salmon', 'tuna'],
    'produce': ['apple', 'banana', 'orange', 'lettuce', 'tomato', 'carrot', 'potato', 'onion'],
    'beverages': ['coffee', 'tea', 'soda', 'juice', 'water', 'beer', 'wine'],
    'snacks': ['chips', 'crackers', 'nuts', 'candy', 'chocolate', 'pretzels'],
    'frozen': ['pizza', 'vegetables', 'berries', 'dinner', 'dessert'],
    'pantry': ['rice', 'pasta', 'cereal', 'oil', 'vinegar', 'salt', 'sugar', 'flour'],
    'household': ['detergent', 'soap', 'shampoo', 'toothpaste', 'paper_towels', 'toilet_paper'],
    'deli': ['ham', 'turkey_slices', 'salami', 'hummus', 'olives']
}

# Flatten all items
ALL_ITEMS = []
for category, items in FOODMART_ITEMS.items():
    ALL_ITEMS.extend(items)

# Utility ranges for different item categories
UTILITY_RANGES = {
    'dairy': (2.0, 8.0),
    'bakery': (1.5, 6.0),
    'meat': (5.0, 15.0),
    'produce': (1.0, 4.0),
    'beverages': (1.0, 12.0),
    'snacks': (2.0, 7.0),
    'frozen': (3.0, 10.0),
    'pantry': (1.5, 8.0),
    'household': (3.0, 12.0),
    'deli': (4.0, 10.0)
}

def get_item_category(item: str) -> str:
    """Get the category of an item."""
    for category, items in FOODMART_ITEMS.items():
        if item in items:
            return category
    return 'pantry'  # default

def get_item_utility(item: str) -> float:
    """Get a realistic utility value for an item."""
    category = get_item_category(item)
    min_util, max_util = UTILITY_RANGES[category]
    return round(random.uniform(min_util, max_util), 2)

def generate_transaction(density: str) -> Tuple[List[str], List[float], List[float]]:
    """Generate a single transaction based on density."""
    
    if density == 'dense':
        # Dense: 8-15 items per transaction, popular items more frequent
        num_items = random.randint(8, 15)
        popular_items = ['milk', 'bread', 'chicken', 'apple', 'cheese', 'coffee', 'rice', 'pasta']
        items = random.choices(popular_items, k=num_items//2) + random.choices(ALL_ITEMS, k=num_items//2)
        
    elif density == 'medium':
        # Medium: 4-8 items per transaction, balanced selection
        num_items = random.randint(4, 8)
        items = random.choices(ALL_ITEMS, k=num_items)
        
    else:  # sparse
        # Sparse: 2-5 items per transaction, more random selection
        num_items = random.randint(2, 5)
        items = random.choices(ALL_ITEMS, k=num_items)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            unique_items.append(item)
            seen.add(item)
    
    items = unique_items
    
    # Generate quantities (1-5 for most items)
    quantities = [round(random.uniform(1.0, 5.0), 1) for _ in items]
    
    # Generate unit utilities based on item categories
    unit_utilities = [get_item_utility(item) for item in items]
    
    return items, quantities, unit_utilities

def generate_dataset(num_transactions: int, density: str, filename: str):
    """Generate a complete dataset and save to CSV."""
    
    print(f"Generating {density} dataset with {num_transactions} transactions...")
    
    transactions = []
    
    for i in range(num_transactions):
        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1}/{num_transactions} transactions...")
            
        items, quantities, unit_utilities = generate_transaction(density)
        
        # Convert to pipe-separated strings
        items_str = '|'.join(items)
        quantities_str = '|'.join(map(str, quantities))
        utilities_str = '|'.join(map(str, unit_utilities))
        
        transactions.append([items_str, quantities_str, utilities_str])
    
    # Save to CSV
    output_path = os.path.join('sample_data', filename)
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['items', 'quantities', 'unit_utilities'])
        writer.writerows(transactions)
    
    print(f"  Saved to: {output_path}")
    
    # Calculate statistics
    total_items = sum(len(t[0].split('|')) for t in transactions)
    avg_items = total_items / len(transactions)
    unique_items = set()
    for t in transactions:
        unique_items.update(t[0].split('|'))
    
    print(f"  Statistics:")
    print(f"    - Total transactions: {len(transactions)}")
    print(f"    - Average items per transaction: {avg_items:.2f}")
    print(f"    - Unique items: {len(unique_items)}")
    print(f"    - Density: {density}")
    print()

def main():
    """Generate all three datasets."""
    print("Generating Foodmart CSV Datasets for HUI Algorithm")
    print("=" * 50)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Generate three datasets
    datasets = [
        (3500, 'dense', 'foodmart_dense_3500.csv'),
        (7000, 'medium', 'foodmart_medium_7000.csv'),
        (10000, 'sparse', 'foodmart_sparse_10000.csv')
    ]
    
    for num_transactions, density, filename in datasets:
        generate_dataset(num_transactions, density, filename)
    
    print("All datasets generated successfully!")
    print("\nDataset Summary:")
    print("- foodmart_dense_3500.csv: 3,500 transactions, 8-15 items each (dense)")
    print("- foodmart_medium_7000.csv: 7,000 transactions, 4-8 items each (medium)")
    print("- foodmart_sparse_10000.csv: 10,000 transactions, 2-5 items each (sparse)")
    print("\nReady for upload to HUI frontend!")

if __name__ == "__main__":
    main()
