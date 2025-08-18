#!/usr/bin/env python3
"""
Mining wrapper script for HUI algorithm integration
Reads JSON input from stdin and outputs results to stdout
"""

import json
import sys
import os

# Add the algorithms directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'algorithms'))

try:
    from Alogrithm import OptimizedAlgoUPGrowth
    from item import Item
    from itemset import Itemset
except ImportError as e:
    print(f"Error importing HUI algorithms: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        transactions = input_data.get('transactions', [])
        min_utility = input_data.get('min_utility', 10)
        min_support = input_data.get('min_support', 0.1)
        
        if not transactions:
            print(json.dumps({"patterns": [], "error": "No transactions provided"}))
            return
        
        # Convert transactions to the format expected by the algorithm
        formatted_transactions = []
        for txn in transactions:
            items = txn.get('items', [])
            quantities = txn.get('quantities', [])
            unit_utilities = txn.get('unit_utilities', [])
            
            if len(items) == len(quantities) == len(unit_utilities):
                formatted_transactions.append({
                    'items': items,
                    'quantities': quantities,
                    'unit_utilities': unit_utilities
                })
        
        if not formatted_transactions:
            print(json.dumps({"patterns": [], "error": "No valid transactions found"}))
            return
        
        # Initialize and run the UP-Growth algorithm
        algo = OptimizedAlgoUPGrowth()
        
        # Run mining
        patterns = algo.run_algorithm(
            transactions=formatted_transactions,
            min_utility=min_utility,
            min_support=min_support
        )
        
        # Format results for JSON output
        result_patterns = []
        for pattern in patterns:
            result_patterns.append({
                'items': pattern.get('items', []),
                'utility': pattern.get('utility', 0),
                'support': pattern.get('support', 0),
                'confidence': pattern.get('confidence', 0)
            })
        
        # Output results as JSON
        print(json.dumps({
            "patterns": result_patterns,
            "total_patterns": len(result_patterns),
            "min_utility": min_utility,
            "min_support": min_support
        }))
        
    except json.JSONDecodeError as e:
        print(json.dumps({"patterns": [], "error": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"patterns": [], "error": f"Mining failed: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
