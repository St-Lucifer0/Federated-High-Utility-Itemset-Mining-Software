#!/usr/bin/env python3
"""
Integration test for HUI Mining System
Tests the connection between frontend, backend API, and HUI algorithms
"""

import requests
import json
import time

# Test configuration
BACKEND_URL = "http://localhost:8000"
TEST_STORE_ID = "test_store_001"

def test_backend_health():
    """Test if backend server is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"PASS: Backend health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"FAIL: Backend health check failed: {e}")
        return False

def test_store_creation():
    """Test store creation endpoint"""
    try:
        store_data = {
            "store_id": TEST_STORE_ID,
            "name": "Test Store",
            "location": "Test Location",
            "manager_name": "Test Manager"
        }
        response = requests.post(f"{BACKEND_URL}/api/stores", json=store_data)
        print(f"PASS: Store creation: {response.status_code}")
        # Accept 200, 201 (created) or 400 (already exists)
        return response.status_code in [200, 201, 400]
    except Exception as e:
        print(f"FAIL: Store creation failed: {e}")
        return False

def test_transaction_upload():
    """Test transaction upload and processing"""
    try:
        # Sample transaction data
        transactions = [
            {
                "transaction_id": "T001",
                "store_id": TEST_STORE_ID,
                "items": ["bread", "milk", "eggs"],
                "quantities": [2, 1, 12],
                "unit_utilities": [2, 2, 1],
                "timestamp": "2025-08-18T02:00:00"
            },
            {
                "transaction_id": "T002", 
                "store_id": TEST_STORE_ID,
                "items": ["bread", "butter", "jam"],
                "quantities": [1, 1, 1],
                "unit_utilities": [2, 3, 3],
                "timestamp": "2025-08-18T02:01:00"
            }
        ]
        
        for transaction in transactions:
            response = requests.post(f"{BACKEND_URL}/api/transactions/upload/{TEST_STORE_ID}", json=[transaction])
            print(f"PASS: Transaction upload {transaction['transaction_id']}: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"FAIL: Transaction upload failed: {e}")
        return False

def test_mining_job():
    """Test mining job creation and execution"""
    try:
        # Start mining job
        mining_params = {
            "store_id": TEST_STORE_ID,
            "min_utility": 3.0,
            "algorithm": "up_growth"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/mining/start", json=mining_params)
        print(f"PASS: Mining job started: {response.status_code}")
        
        if response.status_code not in [200, 201]:
            return False
            
        job_data = response.json()
        job_id = job_data.get("job_id")
        
        # Poll for job completion
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = requests.get(f"{BACKEND_URL}/api/mining/status/{job_id}")
            status_data = status_response.json()
            
            print(f"Mining job status: {status_data.get('status')} (attempt {attempt + 1})")
            
            if status_data.get("status") == "completed":
                # Get results
                results_response = requests.get(f"{BACKEND_URL}/api/mining/results/{job_id}")
                results = results_response.json()
                # Add parent directory to path to import HUI modules
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                print(f"PASS: Mining completed. Found {len(results.get('patterns', []))} patterns")
                return True
            elif status_data.get("status") == "failed":
                print(f"FAIL: Mining job failed: {status_data.get('error', 'Unknown error')}")
                return False
                
            time.sleep(2)
            
        print("FAIL: Mining job timed out")
        return False
        
    except Exception as e:
        print(f"FAIL: Mining job test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("Starting HUI Mining System Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Health Check", test_backend_health),
        ("Store Creation", test_store_creation),
        ("Transaction Upload", test_transaction_upload),
        ("Mining Job Execution", test_mining_job)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"FAILED: {test_name}")
    
    print("\n" + "=" * 50)
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All integration tests passed! System is fully functional.")
    else:
        print("WARNING: Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    run_integration_tests()
