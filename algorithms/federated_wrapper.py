#!/usr/bin/env python3
"""
Python wrapper script for federated learning aggregation
Bridges Node.js backend with Python federated learning algorithms
"""

import sys
import json
import traceback
import numpy as np
from collections import defaultdict
from federated_server import FederatedServer
from federated_client import FederatedClient

def aggregate_patterns_with_privacy(local_patterns, privacy_budget=1.0, min_clients=2):
    """
    Aggregate local patterns from multiple clients with privacy preservation
    """
    # Group patterns by item sets
    pattern_groups = defaultdict(list)
    
    for pattern in local_patterns:
        items_key = tuple(sorted(pattern['items']))
        pattern_groups[items_key].append(pattern)
    
    global_patterns = []
    
    for items_key, patterns in pattern_groups.items():
        # Only consider patterns that appear in at least min_clients stores
        contributing_stores = len(set(p['store_id'] for p in patterns))
        
        if contributing_stores >= min_clients:
            # Aggregate utilities with differential privacy noise
            utilities = [p['utility'] for p in patterns]
            supports = [p['support'] for p in patterns]
            
            # Simple aggregation (can be enhanced with more sophisticated methods)
            aggregated_utility = np.mean(utilities)
            global_support = np.mean(supports)
            
            # Add differential privacy noise (simplified Laplace mechanism)
            if privacy_budget > 0:
                sensitivity = max(utilities) - min(utilities) if len(utilities) > 1 else 0
                if sensitivity > 0:
                    noise_scale = sensitivity / privacy_budget
                    noise = np.random.laplace(0, noise_scale)
                    aggregated_utility = max(0, aggregated_utility + noise)
            
            global_patterns.append({
                'items': list(items_key),
                'aggregated_utility': float(aggregated_utility),
                'global_support': float(global_support),
                'contributing_stores': contributing_stores,
                'original_patterns_count': len(patterns)
            })
    
    # Sort by aggregated utility
    global_patterns.sort(key=lambda x: x['aggregated_utility'], reverse=True)
    
    return global_patterns

def main():
    try:
        # Read input data from stdin
        input_data = json.loads(sys.stdin.read())
        
        local_patterns = input_data.get('local_patterns', [])
        privacy_budget = input_data.get('privacy_budget', 1.0)
        min_clients = input_data.get('min_clients', 2)
        
        if not local_patterns:
            raise ValueError("No local patterns provided")
        
        # Validate input data
        for pattern in local_patterns:
            required_fields = ['store_id', 'items', 'utility', 'support']
            for field in required_fields:
                if field not in pattern:
                    raise ValueError(f"Missing required field: {field}")
        
        # Aggregate patterns with privacy preservation
        global_patterns = aggregate_patterns_with_privacy(
            local_patterns, privacy_budget, min_clients
        )
        
        # Calculate aggregation statistics
        total_stores = len(set(p['store_id'] for p in local_patterns))
        total_local_patterns = len(local_patterns)
        
        # Output results as JSON
        result = {
            'success': True,
            'global_patterns': global_patterns,
            'statistics': {
                'total_global_patterns': len(global_patterns),
                'total_local_patterns': total_local_patterns,
                'participating_stores': total_stores,
                'privacy_budget_used': privacy_budget,
                'min_clients_threshold': min_clients
            }
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
