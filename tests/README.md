# Comprehensive Federated Learning Test Suite

This directory contains a comprehensive test suite for federated learning experiments with the BestEfficientUPGrowth algorithm, covering all requirements from Chapter 4 of your research.

## 📁 Test Files Overview

### Core Test Files

1. **`test_federated_without_laplace.py`** - Tests federated learning WITHOUT Laplace differential privacy
2. **`test_federated_with_laplace.py`** - Tests federated learning WITH Laplace differential privacy  
3. **`run_comprehensive_federated_tests.py`** - Runs all tests and generates unified reports
4. **`test_federated_network_setup.py`** - Network-based federated learning across multiple machines

### What Each Test Covers

#### Chapter 4.3: Pseudo-projection and Incremental Learning
- **File**: `test_federated_without_laplace.py`
- **Tests**:
  - Effectiveness of pseudo-projection optimization
  - Memory usage reduction comparison
  - Runtime improvement analysis
  - HUI quality preservation (95% accuracy target)
  - Incremental learning stability

#### Chapter 4.4: Enhanced FP-Growth Algorithm
- **File**: `test_federated_without_laplace.py`
- **Tests**:
  - Centralized baseline performance
  - Enhanced algorithm efficiency
  - Robustness across different datasets
  - Scalability with varying client numbers
  - Performance comparison with traditional algorithms

#### Chapter 4.5: Federated Learning with Laplace DP
- **File**: `test_federated_with_laplace.py`
- **Tests**:
  - Privacy-utility tradeoff analysis
  - Epsilon impact on HUI quality
  - Cumulative privacy budget tracking
  - Noise impact quantification
  - Fairness across clients
  - Robustness with IID vs Non-IID data

## 🚀 Quick Start Guide

### 1. Run All Tests (Recommended)

```bash
cd tests
python run_comprehensive_federated_tests.py
```

This will:
- Run all federated learning tests
- Generate comprehensive reports
- Create visualization charts
- Save results in `results/chapter_four/comprehensive/`

### 2. Run Individual Test Suites

#### Test Without Laplace DP
```bash
python test_federated_without_laplace.py
```

#### Test With Laplace DP
```bash
python test_federated_with_laplace.py
```

### 3. Network-Based Federated Learning

#### Setup Server (Your Main Laptop)
```bash
python test_federated_network_setup.py server --host 0.0.0.0 --port 8888 --min-utility 100 --rounds 3
```

#### Setup Clients (Other Laptops)
```bash
python test_federated_network_setup.py client --host <SERVER_IP> --port 8888 --client-name laptop1 --dataset chess_data.csv
```

## 🌐 Network Setup Guide: Making Your Laptop a Server

### Prerequisites
- All laptops must be on the same network (WiFi or LAN)
- Python 3.7+ installed on all machines
- Required dependencies installed (see requirements.txt)

### Step-by-Step Network Setup

#### 1. Find Your Server IP Address

**On Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually something like `192.168.1.100`)

**On Mac/Linux:**
```bash
ifconfig
```
Look for `inet` address under your active network interface

#### 2. Configure Firewall (Important!)

**Windows:**
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Click "Change Settings" → "Allow another app"
4. Browse and add Python.exe
5. Check both "Private" and "Public" boxes

**Mac:**
```bash
sudo ufw allow 8888
```

**Alternative: Temporarily disable firewall for testing (not recommended for production)**

#### 3. Start the Server (Main Laptop)

```bash
# Navigate to tests directory
cd C:/Users/User/PycharmProjects/Efiicient_FP_Growth/tests

# Start server (replace with your actual IP)
python test_federated_network_setup.py server --host 0.0.0.0 --port 8888 --min-utility 100 --rounds 3
```

**Server will display:**
```
Federated Learning Server started on 0.0.0.0:8888
Minimum utility threshold: 100
Waiting for clients to connect...
```

#### 4. Connect Clients (Other Laptops)

On each client laptop:

```bash
# Copy the project to client laptop or just the necessary files
# Navigate to tests directory
cd /path/to/tests

# Connect to server (replace SERVER_IP with actual server IP)
python test_federated_network_setup.py client --host 192.168.1.100 --port 8888 --client-name laptop2 --dataset chess_data.csv
```

#### 5. Example Multi-Client Setup

**Server (Main Laptop - IP: 192.168.1.100):**
```bash
python test_federated_network_setup.py server --host 0.0.0.0 --port 8888 --min-utility 100 --rounds 3
```

**Client 1 (Laptop 2):**
```bash
python test_federated_network_setup.py client --host 192.168.1.100 --port 8888 --client-name laptop2 --dataset chess_data.csv
```

**Client 2 (Laptop 3):**
```bash
python test_federated_network_setup.py client --host 192.168.1.100 --port 8888 --client-name laptop3 --dataset mushroom_data.txt
```

**Client 3 (Laptop 4):**
```bash
python test_federated_network_setup.py client --host 192.168.1.100 --port 8888 --client-name laptop4 --dataset transactional_data.txt
```

### Network Troubleshooting

#### Common Issues and Solutions

1. **Connection Refused Error**
   - Check if server is running
   - Verify IP address and port
   - Check firewall settings
   - Ensure all devices are on same network

2. **Timeout Errors**
   - Increase timeout in client code
   - Check network stability
   - Verify server is not overloaded

3. **Dataset Not Found**
   - Ensure dataset files exist on client machines
   - Use absolute paths for datasets
   - Copy datasets to all client machines

4. **Permission Errors**
   - Run with administrator privileges if needed
   - Check file permissions
   - Ensure write access to results directory

## 📊 Test Results and Reports

### Generated Files

After running tests, you'll find:

```
results/chapter_four/
├── comprehensive/
│   ├── comprehensive_federated_report.json
│   ├── comprehensive_summary.csv
│   ├── comprehensive_federated_analysis.png
│   ├── no_laplace/
│   │   ├── federated_no_laplace_report.json
│   │   └── federated_no_laplace_performance.png
│   └── with_laplace/
│       ├── federated_with_laplace_report.json
│       └── federated_with_laplace_privacy_analysis.png
```

### Report Contents

#### Comprehensive Report (`comprehensive_federated_report.json`)
- Complete test metadata and execution times
- All test results organized by dataset and configuration
- Summary statistics across all tests
- Key findings and insights

#### CSV Summary (`comprehensive_summary.csv`)
- Tabular data for easy analysis in Excel/R/Python
- Columns: dataset, configuration, centralized_huis, federated_huis, accuracy, privacy_cost, etc.
- Perfect for statistical analysis and plotting

#### Visualization Charts
- **Performance Analysis**: Runtime and HUI count comparisons
- **Privacy Analysis**: Epsilon impact, noise-to-signal ratios
- **Scalability Charts**: Performance vs number of clients
- **Effectiveness Plots**: Pseudo-projection improvements

## 🔧 Configuration Options

### Test Parameters

You can customize tests by modifying these parameters:

```python
# In test files
datasets = [
    ("chess_data.csv", [50, 100, 200]),           # Dense, long transactions
    ("mushroom_data.txt", [100, 200, 300]),       # Dense categorical data
    ("transactional_data.txt", [500, 1000, 1500]) # Large sparse data
]

# Federated learning parameters
num_clients = 5          # Number of federated clients
num_rounds = 3           # Federated learning rounds
iid_distribution = True  # IID vs Non-IID data distribution

# Privacy parameters (for Laplace DP tests)
epsilon_values = [0.1, 0.5, 1.0, 2.0, 5.0]  # Privacy budget values
sensitivity_values = [0.5, 1.0, 2.0, 5.0]   # Sensitivity values
```

### Network Parameters

```python
# Server configuration
host = '0.0.0.0'        # Listen on all interfaces
port = 8888             # Server port
min_utility = 100       # Minimum utility threshold

# Client configuration
server_host = '192.168.1.100'  # Server IP address
client_name = 'laptop1'        # Unique client identifier
dataset_path = 'chess_data.csv' # Local dataset path
```

## 📈 Performance Metrics Tracked

### Chapter 4.3 Metrics (Pseudo-projection & Incremental Learning)
- **Memory Usage**: Before/after pseudo-projection
- **Runtime Improvement**: Percentage reduction in execution time
- **HUI Accuracy**: Percentage of HUIs preserved (target: 95%)
- **Cache Efficiency**: Hit/miss ratios for optimization caches

### Chapter 4.4 Metrics (Enhanced FP-Growth)
- **HUI Quality**: Count, average utility, precision/recall
- **Efficiency**: Runtime, memory usage, scalability
- **Robustness**: Performance across diverse datasets
- **Comparison**: vs traditional algorithms

### Chapter 4.5 Metrics (Federated Learning with DP)
- **Privacy Metrics**: Cumulative epsilon, privacy budget consumption
- **Utility Loss**: HUI count/utility reduction due to noise
- **Noise Analysis**: Noise-to-signal ratios, sensitivity impact
- **Fairness**: Client contribution balance, Gini coefficients
- **Communication Cost**: Data transferred per round
- **Scalability**: Performance vs number of clients

## 🎯 Expected Results (Based on Chapter 4 Requirements)

### Pseudo-projection Effectiveness
- **Memory Reduction**: 30-50% improvement
- **Runtime Improvement**: 25-50% faster execution
- **HUI Accuracy**: 95%+ preservation rate

### Federated Learning Performance
- **Accuracy**: 90-95% of centralized performance
- **Communication Efficiency**: Minimal data transfer
- **Scalability**: Linear scaling with client count

### Privacy-Utility Tradeoff
- **Low Privacy (ε=5.0)**: <10% utility loss
- **Medium Privacy (ε=1.0)**: 10-25% utility loss  
- **High Privacy (ε=0.1)**: 25-50% utility loss

## 🛠️ Troubleshooting

### Common Test Issues

1. **Memory Errors**
   - Reduce batch sizes in algorithm configuration
   - Use smaller datasets for initial testing
   - Increase system virtual memory

2. **Dataset Loading Errors**
   - Verify dataset file formats
   - Check file paths and permissions
   - Ensure datasets contain valid transaction data

3. **Algorithm Convergence Issues**
   - Adjust minimum utility thresholds
   - Check for empty or invalid transactions
   - Verify item and utility value ranges

4. **Network Connection Issues**
   - Check firewall settings
   - Verify IP addresses and ports
   - Ensure all machines are on same network
   - Test with simple ping/telnet first

### Performance Optimization

1. **For Large Datasets**
   - Enable pseudo-projection optimization
   - Increase batch sizes
   - Use incremental processing

2. **For Network Tests**
   - Use wired connections when possible
   - Minimize network traffic during tests
   - Consider local network setup

3. **For Privacy Tests**
   - Start with higher epsilon values
   - Gradually decrease for privacy analysis
   - Monitor noise impact on results

## 📚 Additional Resources

### Research Papers Referenced
1. **UP-Growth**: Tseng, V. S., et al. "UP-Growth: an efficient algorithm for high utility itemset mining." KDD 2010
2. **Differential Privacy**: Dwork, C. "Differential Privacy." ICALP 2006
3. **Federated Learning**: McMahan, B., et al. "Communication-Efficient Learning of Deep Networks from Decentralized Data." AISTATS 2017

### Code Documentation
- See `../OVERVIEW.md` for algorithm implementation details
- Check individual algorithm files for specific optimizations
- Review `../federated_fp_growth.py` for federated learning implementation

### Support
- Check GitHub issues for common problems
- Review test output logs for detailed error information
- Modify test parameters based on your specific requirements

---

**Note**: This test suite is designed to comprehensively evaluate your BestEfficientUPGrowth algorithm in federated learning scenarios, covering all aspects required for Chapter 4 of your research. The tests generate detailed reports and visualizations suitable for academic publication.

## 🎉 Quick Test Commands Summary

```bash
# Run everything (recommended)
python run_comprehensive_federated_tests.py

# Individual tests
python test_federated_without_laplace.py
python test_federated_with_laplace.py

# Network federated learning
# Server:
python test_federated_network_setup.py server --host 0.0.0.0 --port 8888

# Client:
python test_federated_network_setup.py client --host <SERVER_IP> --client-name laptop1 --dataset chess_data.csv
```

Good luck with your federated learning experiments! 🚀