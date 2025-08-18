# Federated Learning for High Utility Itemset Mining (HUIM)

## Overview

This repository implements a comprehensive federated learning framework for High Utility Itemset Mining with optional Laplace Differential Privacy. The system allows multiple clients (laptops) to collaboratively mine high utility itemsets while preserving data privacy.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Mathematical Foundation](#mathematical-foundation)
3. [Laplace Differential Privacy](#laplace-differential-privacy)
4. [Setup and Installation](#setup-and-installation)
5. [Running the System](#running-the-system)
6. [Command Line Examples](#command-line-examples)
7. [Configuration Options](#configuration-options)
8. [Code Structure](#code-structure)

## System Architecture

The federated learning system consists of three main components:

### 1. Federated Server (`federated_server.py`)
- Coordinates federated learning rounds
- Aggregates client results
- Manages client connections
- Applies differential privacy mechanisms

### 2. Federated Client (`federated_client.py`)
- Performs local HUIM on private data
- Communicates with the server
- Participates in federated learning rounds

### 3. Federated FP-Growth Algorithm (`federated_fp_growth.py`)
- Implements the core federated learning logic
- Integrates with the OptimizedAlgoUPGrowth algorithm
- Provides Laplace differential privacy mechanisms

## Mathematical Foundation

### High Utility Itemset Mining (HUIM)

#### Basic Definitions

1. **Transaction Weighted Utility (TWU)**:
   ```
   TWU(X) = Σ{T∈D, X⊆T} TU(T)
   ```
   Where:
   - `X` is an itemset
   - `D` is the transaction database
   - `TU(T)` is the utility of transaction `T`

2. **Utility of an Itemset**:
   ```
   u(X,T) = Σ{i∈X} u(i,T)
   ```
   Where:
   - `u(i,T)` is the utility of item `i` in transaction `T`

3. **High Utility Itemset**:
   An itemset `X` is a High Utility Itemset if:
   ```
   u(X) = Σ{T∈D, X⊆T} u(X,T) ≥ min_utility
   ```

### Federated Learning Process

#### 1. Client Selection and Data Distribution

Each client `k` has a local dataset `D_k` where:
```
D = D_1 ∪ D_2 ∪ ... ∪ D_n
```

#### 2. Local Mining Phase

Each client `k` performs local HUIM:
```
HUI_k = HUIM(D_k, min_utility_k)
```

**Code Location**: `federated_client.py`, lines 150-180
```python
def perform_local_mining(self, min_utility: float) -> List[Itemset]:
    """Perform local HUIM on client data."""
    algorithm = OptimizedAlgoUPGrowth()
    # Local mining implementation
    return local_huis
```

#### 3. Aggregation Phase

The server aggregates client results:
```
HUI_global = Aggregate(HUI_1, HUI_2, ..., HUI_n)
```

**Mathematical Aggregation**:
```
For each itemset X:
u_global(X) = Σ{k=1 to n} u_k(X) * weight_k
```

**Code Location**: `federated_server.py`, lines 200-250
```python
def aggregate_client_results(self, client_results: List[Dict]) -> List[Itemset]:
    """Aggregate HUIs from multiple clients."""
    aggregated_huis = {}
    
    for client_result in client_results:
        for hui in client_result['huis']:
            itemset_key = tuple(sorted(hui.get_items()))
            if itemset_key in aggregated_huis:
                # Aggregate utilities
                aggregated_huis[itemset_key].utility += hui.utility
            else:
                aggregated_huis[itemset_key] = copy.deepcopy(hui)
    
    return list(aggregated_huis.values())
```

#### 4. Global Model Update

The global model is updated using FedAvg-style aggregation:
```
θ_global^(t+1) = Σ{k=1 to n} (n_k/n) * θ_k^(t+1)
```

Where:
- `θ_k^(t+1)` represents client `k`'s local model at round `t+1`
- `n_k` is the number of samples at client `k`
- `n` is the total number of samples

## Laplace Differential Privacy

### Mathematical Foundation

#### Differential Privacy Definition

A randomized algorithm `M` satisfies `(ε, δ)`-differential privacy if for all datasets `D1` and `D2` differing by at most one record, and for all possible outputs `S`:

```
Pr[M(D1) ∈ S] ≤ exp(ε) × Pr[M(D2) ∈ S] + δ
```

For pure differential privacy (δ = 0):
```
Pr[M(D1) ∈ S] ≤ exp(ε) × Pr[M(D2) ∈ S]
```

#### Laplace Mechanism

The Laplace mechanism adds noise drawn from the Laplace distribution:

```
Lap(b) = (1/2b) × exp(-|x|/b)
```

Where the scale parameter `b` is:
```
b = Δf / ε
```

- `Δf` is the global sensitivity (maximum change in output when one record changes)
- `ε` is the privacy budget

#### Implementation in Code

**Code Location**: `federated_fp_growth.py`, lines 25-50

```python
@dataclass
class LaplaceDP:
    """Laplace Differential Privacy mechanism for HUIM."""
    
    epsilon: float = 1.0  # Privacy budget
    sensitivity: float = 1.0  # Global sensitivity
    noise_scale: float = field(init=False)
    
    def __post_init__(self):
        """Calculate noise scale based on epsilon and sensitivity."""
        self.noise_scale = self.sensitivity / self.epsilon  # b = Δf / ε
    
    def add_laplace_noise(self, value: float) -> float:
        """Add Laplace noise to a numeric value."""
        noise = np.random.laplace(0, self.noise_scale)  # Sample from Lap(b)
        return max(0, value + noise)  # Ensure non-negative utility values
```

#### Privacy Budget Composition

When multiple queries are made, privacy budgets compose:
```
Total Privacy Cost = Σ{i=1 to k} ε_i
```

**Code Location**: `federated_fp_growth.py`, lines 150-200

```python
def apply_differential_privacy(self, huis: List[Itemset], 
                             total_rounds: int) -> List[Itemset]:
    """Apply differential privacy with budget allocation."""
    # Allocate privacy budget across rounds
    round_epsilon = self.laplace_dp.epsilon / total_rounds
    
    # Create temporary DP mechanism for this round
    round_dp = LaplaceDP(epsilon=round_epsilon, 
                        sensitivity=self.laplace_dp.sensitivity)
    
    # Add noise to each HUI
    private_huis = []
    for hui in huis:
        noisy_hui = round_dp.add_noise_to_itemset(hui)
        if noisy_hui.utility > 0:  # Filter out negative utilities
            private_huis.append(noisy_hui)
    
    return private_huis
```

### Privacy-Utility Tradeoff

The relationship between privacy and utility:

1. **Lower ε (more privacy)** → **Higher noise** → **Lower utility**
2. **Higher ε (less privacy)** → **Lower noise** → **Higher utility**

**Mathematical Relationship**:
```
Noise_scale = Δf / ε
Expected_noise = 0
Variance_noise = 2 × (Δf / ε)²
```

## Setup and Installation

### Prerequisites

```bash
pip install numpy pandas matplotlib seaborn psutil
```

### File Structure

```
HUI_algorithm/
├── federated_server.py          # Main server implementation
├── federated_client.py          # Main client implementation  
├── federated_fp_growth.py       # Core federated algorithm
├── Alogrithm.py                # Base HUIM algorithm
├── datasets/
│   ├── datasets_fedlearn/       # Federated learning datasets
│   │   ├── transactions.txt     # Transaction data
│   │   ├── utilities.txt        # Utility data
│   │   ├── chess_transactions.txt
│   │   └── chess_utilities.txt
│   └── datasets_algo/
│       └── chess_data.csv       # Combined format dataset
└── tests/                       # Test suites
    ├── test_federated_with_laplace.py
    └── test_federated_without_laplace.py
```

## Running the System

### Method 1: Using Separate Server and Client Scripts

#### Step 1: Start the Server

Open a terminal and run:

```bash
# Navigate to the project directory
cd C:/Users/User/PycharmProjects/HUI_algorithm

# Start the federated server
python federated_server.py --port 8888 --min-clients 2 --max-rounds 5
```

**Server Parameters**:
- `--port`: Server port (default: 8888)
- `--min-clients`: Minimum clients required (default: 2)
- `--max-rounds`: Maximum federated rounds (default: 10)
- `--enable-dp`: Enable differential privacy
- `--epsilon`: Privacy budget (default: 1.0)
- `--sensitivity`: Global sensitivity (default: 1.0)

#### Step 2: Start Client(s)

Open another terminal (or multiple terminals for multiple clients):

```bash
# Navigate to the project directory
cd C:/Users/User/PycharmProjects/HUI_algorithm

# Start first client
python federated_client.py --client-id "laptop_1" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/chess_transactions.txt" --utility-file "datasets/datasets_fedlearn/chess_utilities.txt" --min-utility 50
```

**Client Parameters**:
- `--client-id`: Unique client identifier
- `--server-host`: Server IP address (use "localhost" for same machine)
- `--server-port`: Server port (must match server)
- `--data-file`: Path to transaction data
- `--utility-file`: Path to utility data
- `--min-utility`: Minimum utility threshold

#### Step 3: Start Additional Clients (Optional)

```bash
# Start second client with different data
python federated_client.py --client-id "laptop_2" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/transaction_1.txt" --utility-file "datasets/datasets_fedlearn/utility_1.txt" --min-utility 50
```

### Method 2: Using the Test Framework

For testing and experimentation:

```bash
# Run comprehensive federated tests
python tests/run_comprehensive_federated_tests.py

# Run specific tests
python tests/test_federated_without_laplace.py
python tests/test_federated_with_laplace.py
```

## Command Line Examples

### Example 1: Basic Federated Learning (No Privacy)

**Terminal 1 (Server)**:
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_server.py --port 8888 --min-clients 2 --max-rounds 3
```

**Terminal 2 (Client 1)**:
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_client.py --client-id "client_1" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/chess_transactions.txt" --utility-file "datasets/datasets_fedlearn/chess_utilities.txt" --min-utility 100
```

**Terminal 3 (Client 2)**:
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_client.py --client-id "client_2" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/transaction_1.txt" --utility-file "datasets/datasets_fedlearn/utility_1.txt" --min-utility 100
```

### Example 2: Federated Learning with Differential Privacy

**Terminal 1 (Server with DP)**:
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_server.py --port 8888 --min-clients 2 --max-rounds 3 --enable-dp --epsilon 1.0 --sensitivity 1.0
```

**Terminals 2-3 (Clients)**: Same as Example 1

### Example 3: Multi-Client Setup

**Server**:
```bash
python federated_server.py --port 8888 --min-clients 3 --max-rounds 5 --enable-dp --epsilon 2.0
```

**Client 1**:
```bash
python federated_client.py --client-id "laptop_alice" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/chess_transactions.txt" --utility-file "datasets/datasets_fedlearn/chess_utilities.txt" --min-utility 75
```

**Client 2**:
```bash
python federated_client.py --client-id "laptop_bob" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/transaction_1.txt" --utility-file "datasets/datasets_fedlearn/utility_1.txt" --min-utility 75
```

**Client 3**:
```bash
python federated_client.py --client-id "laptop_charlie" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/transactions.txt" --utility-file "datasets/datasets_fedlearn/utilities.txt" --min-utility 75
```

### Example 4: Network Setup (Different Machines)

If running on different machines, replace `localhost` with the server's IP address:

**Server Machine**:
```bash
# Find your IP address first
ipconfig  # On Windows
# or
ifconfig  # On Linux/Mac

# Start server (example IP: 192.168.1.100)
python federated_server.py --port 8888 --min-clients 2 --max-rounds 3
```

**Client Machine**:
```bash
python federated_client.py --client-id "remote_client_1" --server-host 192.168.1.100 --server-port 8888 --data-file "datasets/datasets_fedlearn/chess_transactions.txt" --utility-file "datasets/datasets_fedlearn/chess_utilities.txt" --min-utility 50
```

## Configuration Options

### Server Configuration

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--port` | Server listening port | 8888 | `--port 9999` |
| `--min-clients` | Minimum clients to start | 2 | `--min-clients 3` |
| `--max-rounds` | Maximum federated rounds | 10 | `--max-rounds 5` |
| `--enable-dp` | Enable differential privacy | False | `--enable-dp` |
| `--epsilon` | Privacy budget | 1.0 | `--epsilon 0.5` |
| `--sensitivity` | Global sensitivity | 1.0 | `--sensitivity 2.0` |
| `--aggregation` | Aggregation method | "fedavg" | `--aggregation "weighted"` |

### Client Configuration

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--client-id` | Unique client identifier | Required | `--client-id "laptop_1"` |
| `--server-host` | Server IP address | "localhost" | `--server-host "192.168.1.100"` |
| `--server-port` | Server port | 8888 | `--server-port 9999` |
| `--data-file` | Transaction data file | Required | `--data-file "data.txt"` |
| `--utility-file` | Utility data file | Required | `--utility-file "utilities.txt"` |
| `--min-utility` | Minimum utility threshold | Required | `--min-utility 100` |
| `--max-rounds` | Maximum participation rounds | 10 | `--max-rounds 5` |

## Code Structure

### Key Classes and Methods

#### 1. FederatedServer (`federated_server.py`)

**Main Methods**:
- `start_server()`: Initialize and start the server
- `handle_client_connection()`: Handle individual client connections
- `coordinate_federated_round()`: Coordinate a federated learning round
- `aggregate_client_results()`: Aggregate results from clients

**Key Code Sections**:
```python
# Lines 150-200: Client connection handling
def handle_client_connection(self, client_socket, client_address):
    """Handle communication with a connected client."""
    
# Lines 250-300: Federated round coordination  
def coordinate_federated_round(self, round_num: int):
    """Coordinate a single federated learning round."""
    
# Lines 350-400: Result aggregation
def aggregate_client_results(self, client_results: List[Dict]):
    """Aggregate HUIs from multiple clients."""
```

#### 2. FederatedClient (`federated_client.py`)

**Main Methods**:
- `connect_to_server()`: Establish connection with server
- `perform_local_mining()`: Execute local HUIM
- `participate_in_round()`: Participate in federated round

**Key Code Sections**:
```python
# Lines 100-150: Server connection
def connect_to_server(self):
    """Connect to the federated server."""
    
# Lines 200-250: Local mining
def perform_local_mining(self, min_utility: float):
    """Perform local HUIM on client data."""
    
# Lines 300-350: Round participation
def participate_in_round(self, round_info: Dict):
    """Participate in a federated learning round."""
```

#### 3. LaplaceDP (`federated_fp_growth.py`)

**Differential Privacy Implementation**:
```python
# Lines 25-50: Core DP mechanism
class LaplaceDP:
    def add_laplace_noise(self, value: float) -> float:
        """Add Laplace noise: noise ~ Lap(sensitivity/epsilon)"""
        noise = np.random.laplace(0, self.noise_scale)
        return max(0, value + noise)
    
# Lines 100-150: Privacy budget management
def allocate_privacy_budget(self, total_rounds: int) -> float:
    """Allocate privacy budget across federated rounds."""
    return self.epsilon / total_rounds
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure server is running before starting clients
   - Check firewall settings
   - Verify IP address and port

2. **No HUIs Found**:
   - Lower the minimum utility threshold
   - Check data file format
   - Ensure sufficient data size

3. **Privacy Budget Exhausted**:
   - Increase epsilon value
   - Reduce number of rounds
   - Optimize sensitivity calculation

### Debug Mode

Enable debug logging:
```bash
# Server
python federated_server.py --debug --port 8888

# Client  
python federated_client.py --debug --client-id "debug_client" --server-host localhost
```

## Performance Metrics

The system tracks several metrics:

1. **Communication Cost**: Total bytes transmitted
2. **Round Time**: Time per federated round
3. **Privacy Loss**: Cumulative epsilon consumption
4. **Utility Preservation**: HUI quality with/without DP
5. **Convergence**: Rounds to convergence

These metrics are logged and can be analyzed using the test framework.

## Research Applications

This implementation supports research in:

1. **Federated Learning for Data Mining**
2. **Differential Privacy in Distributed Systems**
3. **Privacy-Preserving Utility Mining**
4. **Heterogeneous Data Distribution Effects**
5. **Communication-Efficient Federated Algorithms**

## Citation

If you use this implementation in your research, please cite:

```bibtex
@software{federated_huim_2024,
  title={Federated Learning Framework for High Utility Itemset Mining with Laplace Differential Privacy},
  author={[Your Name]},
  year={2024},
  url={https://github.com/[your-repo]/HUI_algorithm}
}
```

---

For additional support or questions, please refer to the test files in the `tests/` directory or create an issue in the repository.