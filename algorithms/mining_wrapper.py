#!/usr/bin/env python3
"""
Python wrapper script for HUI mining algorithms
Bridges Node.js backend with Python HUI algorithms
"""

import sys
import json
import traceback
from Alogrithm import OptimizedAlgoUPGrowth
from item import Item
from itemset import Itemset

def main():
    try:
        # Read input data from stdin
        input_data = json.loads(sys.stdin.read())
        
        transactions_data = input_data.get('transactions', [])
        min_utility = input_data.get('min_utility', 100)
        min_support = input_data.get('min_support', 0.1)
        
        if not transactions_data:
            raise ValueError("No transactions provided")
        
        # Convert transactions to format expected by HUI algorithm
        transactions = []
        for trans_data in transactions_data:
            items = trans_data.get('items', [])
            quantities = trans_data.get('quantities', [])
            unit_utilities = trans_data.get('unit_utilities', [])
            
            if len(items) != len(quantities) or len(items) != len(unit_utilities):
                raise ValueError("Items, quantities, and utilities arrays must have the same length")
            
            transaction = []
            for i, item_name in enumerate(items):
                try:
                    qty = int(float(quantities[i]))
                    util = int(float(unit_utilities[i]))
                    total_item_utility = qty * util
                    transaction.append(Item(str(item_name), total_item_utility))
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Error processing item {item_name}: {e}")
            
            if transaction:  # Only add non-empty transactions
                transactions.append(transaction)
        
        if not transactions:
            raise ValueError("No valid transactions after processing")
        
        # Run HUI mining algorithm
        algorithm = OptimizedAlgoUPGrowth()
        patterns = algorithm.run_algorithm(transactions, min_utility)
        
        # Convert patterns to JSON-serializable format
        result_patterns = []
        for pattern in patterns:
            pattern_dict = {
                'items': [item.name for item in pattern.items],
                'utility': pattern.utility,
                'support': getattr(pattern, 'support', 0.0),
                'confidence': getattr(pattern, 'confidence', 0.0)
            }
            result_patterns.append(pattern_dict)
        
        # Output results as JSON
        result = {
            'success': True,
            'patterns': result_patterns,
            'total_patterns': len(result_patterns),
            'min_utility_threshold': min_utility
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        # Output error as JSON
        error_result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    main()
