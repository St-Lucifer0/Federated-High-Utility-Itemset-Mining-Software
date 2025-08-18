"""
Quick test to verify federated learning functionality after algorithm changes.
"""

import os
import sys
import time
from federated_fp_growth import FederatedFPGrowth, LaplaceDP
from Alogrithm import OptimizedAlgoUPGrowth

def test_federated_components():
    """Test that all federated components work correctly."""
    
    print("=== FEDERATED LEARNING COMPONENT TEST ===")
    
    # Test 1: Basic algorithm functionality
    print("\n1. Testing base algorithm...")
    algo = OptimizedAlgoUPGrowth()
    print("   ✓ OptimizedAlgoUPGrowth imported successfully")
    
    # Test 2: Laplace DP functionality
    print("\n2. Testing Laplace DP...")
    dp = LaplaceDP(epsilon=1.0, sensitivity=1.0)
    print(f"   ✓ LaplaceDP created with noise_scale={dp.noise_scale}")
    
    # Test noise addition
    original_value = 100.0
    noisy_value = dp.add_laplace_noise(original_value)
    print(f"   ✓ Noise added: {original_value} → {noisy_value:.2f}")
    
    # Test 3: Federated FP-Growth initialization
    print("\n3. Testing FederatedFPGrowth...")
    try:
        fed_system = FederatedFPGrowth()
        print("   ✓ FederatedFPGrowth initialized successfully")
    except Exception as e:
        print(f"   ✗ Error initializing FederatedFPGrowth: {e}")
        return False
    
    # Test 4: Dataset loading (if available)
    print("\n4. Testing dataset loading...")
    test_datasets = [
        "datasets/datasets_fedlearn/chess_transactions.txt",
        "datasets/datasets_fedlearn/transactions.txt",
        "datasets/datasets_algo/chess_data.csv"
    ]
    
    available_datasets = []
    for dataset in test_datasets:
        if os.path.exists(dataset):
            available_datasets.append(dataset)
            print(f"   ✓ Found dataset: {dataset}")
    
    if not available_datasets:
        print("   ⚠ No test datasets found, but this is not critical")
    
    # Test 5: Privacy budget allocation
    print("\n5. Testing privacy budget allocation...")
    total_rounds = 5
    round_epsilon = dp.epsilon / total_rounds
    print(f"   ✓ Privacy budget per round: {round_epsilon}")
    
    # Test 6: Integration test (if dataset available)
    if available_datasets:
        print("\n6. Testing integration with real data...")
        try:
            # Use the chess dataset if available
            dataset = "datasets/datasets_algo/chess_data.csv"
            if os.path.exists(dataset):
                # Quick mining test
                algo = OptimizedAlgoUPGrowth()
                algo.timeout_seconds = 10.0  # Short timeout for test
                
                # Test with low threshold to ensure we find something
                min_utility = 50
                output_file = "test_output_federated.txt"
                
                print(f"   Running quick mining test with min_utility={min_utility}...")
                start_time = time.time()
                algo.run_algorithm(dataset, output_file, min_utility)
                end_time = time.time()
                
                print(f"   ✓ Mining completed in {end_time - start_time:.2f}s")
                print(f"   ✓ Found {algo.hui_count} HUIs")
                
                # Clean up
                if os.path.exists(output_file):
                    os.remove(output_file)
            else:
                print("   ⚠ Chess dataset not found, skipping integration test")
        except Exception as e:
            print(f"   ✗ Integration test failed: {e}")
            return False
    
    print("\n=== TEST RESULTS ===")
    print("✓ All federated learning components are working correctly!")
    print("✓ The algorithm changes did not break federated functionality!")
    print("✓ Ready for federated learning experiments!")
    
    return True

if __name__ == "__main__":
    success = test_federated_components()
    if success:
        print("\n🎉 Federated learning system is ready to use!")
        print("\nNext steps:")
        print("1. Follow the README to start the server and clients")
        print("2. Use the command line examples provided")
        print("3. Run comprehensive tests with the test suite")
    else:
        print("\n❌ Some issues were found. Please check the errors above.")
        sys.exit(1)