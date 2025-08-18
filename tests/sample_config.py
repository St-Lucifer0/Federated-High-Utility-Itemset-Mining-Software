# Sample Configuration for Federated Learning Tests
# Copy this file and modify as needed

# Test Parameters
MIN_UTILITY_VALUES = [50, 100, 200]
NUM_CLIENTS = 5
NUM_ROUNDS = 3
IID_DISTRIBUTION = True

# Privacy Parameters (for Laplace DP tests)
EPSILON_VALUES = [0.1, 0.5, 1.0, 2.0, 5.0]
SENSITIVITY_VALUES = [0.5, 1.0, 2.0, 5.0]

# Network Parameters
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 8888
CLIENT_TIMEOUT = 60

# Dataset Configuration
DATASETS = [
    ("chess_data.csv", [50, 100, 200]),
    ("mushroom_data.txt", [100, 200, 300]),
    ("transactional_data.txt", [500, 1000, 1500])
]

# Performance Settings
ENABLE_PSEUDO_PROJECTION = True
BATCH_SIZE = 1000
ENABLE_CACHING = True
