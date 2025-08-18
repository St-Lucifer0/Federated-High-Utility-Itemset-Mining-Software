# Foodmart Sample Datasets

This directory contains three CSV datasets generated for testing the HUI (High Utility Itemset) mining algorithm with different transaction densities.

## Dataset Overview

| Dataset | Transactions | Avg Items/Transaction | Density | File Size |
|---------|-------------|----------------------|---------|-----------|
| Dense | 3,500 | 9.08 | High | 502 KB |
| Medium | 7,000 | 5.76 | Medium | 654 KB |
| Sparse | 10,000 | 3.40 | Low | 555 KB |

## File Descriptions

### 1. `foodmart_dense_3500.csv`
- **Transactions**: 3,500
- **Items per transaction**: 8-15 (average 9.08)
- **Characteristics**: Dense transactions with popular items appearing frequently
- **Use case**: Testing algorithm performance on high-density data

### 2. `foodmart_medium_7000.csv`
- **Transactions**: 7,000
- **Items per transaction**: 4-8 (average 5.76)
- **Characteristics**: Balanced transaction density with moderate item overlap
- **Use case**: Standard testing scenario for typical retail data

### 3. `foodmart_sparse_10000.csv`
- **Transactions**: 10,000
- **Items per transaction**: 2-5 (average 3.40)
- **Characteristics**: Sparse transactions with minimal item overlap
- **Use case**: Testing algorithm efficiency on large, sparse datasets

## Data Format

All datasets follow the CSV format expected by the HUI frontend:

```csv
items,quantities,unit_utilities
item1|item2|item3,qty1|qty2|qty3,util1|util2|util3
```

### Example Transaction
```csv
milk|bread|cheese,2.5|1.0|3.2,4.50|2.25|6.75
```

This represents:
- Items: milk, bread, cheese
- Quantities: 2.5, 1.0, 3.2
- Unit utilities: 4.50, 2.25, 6.75

## Product Categories

The datasets include realistic foodmart items across 10 categories:

- **Dairy**: milk, cheese, yogurt, butter, cream, ice_cream
- **Bakery**: bread, croissant, bagel, muffin, cake, cookies
- **Meat**: chicken, beef, pork, turkey, salmon, tuna
- **Produce**: apple, banana, orange, lettuce, tomato, carrot, potato, onion
- **Beverages**: coffee, tea, soda, juice, water, beer, wine
- **Snacks**: chips, crackers, nuts, candy, chocolate, pretzels
- **Frozen**: pizza, vegetables, berries, dinner, dessert
- **Pantry**: rice, pasta, cereal, oil, vinegar, salt, sugar, flour
- **Household**: detergent, soap, shampoo, toothpaste, paper_towels, toilet_paper
- **Deli**: ham, turkey_slices, salami, hummus, olives

## Utility Ranges

Each category has realistic utility ranges:
- **Meat**: $5.00 - $15.00 (highest utility)
- **Household**: $3.00 - $12.00
- **Beverages**: $1.00 - $12.00
- **Dairy**: $2.00 - $8.00
- **Produce**: $1.00 - $4.00 (lowest utility)

## Usage Instructions

### Frontend Upload
1. Open the HUI frontend
2. Navigate to Store Manager → Register Store tab
3. Register your store with the server
4. Go to Upload Transactions tab
5. Upload any of the three CSV files
6. Start mining with appropriate parameters

### Recommended Mining Parameters

#### Dense Dataset (3,500 transactions)
- **Min Utility**: 50-100
- **Min Support**: 0.05-0.1
- **Max Pattern Length**: 5-8

#### Medium Dataset (7,000 transactions)
- **Min Utility**: 30-80
- **Min Support**: 0.03-0.08
- **Max Pattern Length**: 4-6

#### Sparse Dataset (10,000 transactions)
- **Min Utility**: 20-60
- **Min Support**: 0.01-0.05
- **Max Pattern Length**: 3-5

## Performance Testing

These datasets are designed to test different aspects of the HUI algorithm:

- **Dense**: Tests performance with high item overlap and frequent patterns
- **Medium**: Balanced testing for typical retail scenarios
- **Sparse**: Tests scalability with large transaction counts but low density

## Generation Details

- **Random seed**: 42 (for reproducible results)
- **Unique items**: 63 across all datasets
- **Realistic utilities**: Based on actual grocery item categories
- **Quantity ranges**: 1.0-5.0 per item
- **Format**: Compatible with frontend CSV parser
