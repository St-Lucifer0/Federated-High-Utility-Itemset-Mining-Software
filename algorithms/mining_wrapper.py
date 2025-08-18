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
        
        # Convert transactions to format expected by algorithm
        formatted_transactions = []
        formatted_utilities = []
        
        for trans_data in transactions_data:
            items = trans_data.get('items', [])
            quantities = trans_data.get('quantities', [])
            unit_utilities = trans_data.get('unit_utilities', [])
            
            if len(items) != len(quantities) or len(items) != len(unit_utilities):
                raise ValueError("Items, quantities, and utilities arrays must have the same length")
            
            if len(items) > 0:  # Only process non-empty transactions
                # Convert items to integers (hash them for algorithm)
                item_ids = [abs(hash(str(item))) % 100000 for item in items]
                # Calculate actual utilities (quantity * unit_utility)
                utilities = [int(float(q) * float(u)) for q, u in zip(quantities, unit_utilities)]
                
                formatted_transactions.append(item_ids)
                formatted_utilities.append(utilities)
        
        if not formatted_transactions:
            raise ValueError("No valid transactions after processing")
        
        # Run HUI mining algorithm
        algorithm = OptimizedAlgoUPGrowth()
        patterns = algorithm.run_algorithm_memory(formatted_transactions, formatted_utilities, float(min_utility))
        
        # Convert patterns to JSON-serializable format
        result_patterns = []
        for pattern in patterns:
            pattern_dict = {
                'items': pattern.itemset,
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
