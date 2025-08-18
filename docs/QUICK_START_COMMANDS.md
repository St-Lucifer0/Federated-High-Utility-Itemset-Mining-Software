# Quick Start Commands for Federated Learning

## 🚀 Fastest Way to Test (Automated Demo)

```bash
# Navigate to project directory
cd C:/Users/User/PycharmProjects/HUI_algorithm

# Run automated demo (starts server + 2 clients automatically)
python start_federated_demo.py --mode demo --min-utility 50

# Run demo with differential privacy
python start_federated_demo.py --mode demo --enable-dp --epsilon 1.0 --min-utility 50
```

## 📋 Manual Setup (Recommended for Learning)

### Step 1: Start Server

**Terminal 1 (Server without DP):**
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_server.py --port 8888 --min-clients 2 --max-rounds 3
```

**Terminal 1 (Server with DP):**
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_server.py --port 8888 --min-clients 2 --max-rounds 3 --enable-dp --epsilon 1.0 --sensitivity 1.0
```

### Step 2: Start Clients

**Terminal 2 (Client 1):**
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_client.py --client-id "laptop_1" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/chess_transactions.txt" --utility-file "datasets/datasets_fedlearn/chess_utilities.txt" --min-utility 50
```

**Terminal 3 (Client 2):**
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python federated_client.py --client-id "laptop_2" --server-host localhost --server-port 8888 --data-file "datasets/datasets_fedlearn/transactions.txt" --utility-file "datasets/datasets_fedlearn/utilities.txt" --min-utility 50
```

## 🔧 Testing Commands

### Test Basic Algorithm (Fixed Version)
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python main.py
# Select dataset and enter minimum utility (try 50 or 100)
```

### Test Federated Components
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python test_federated_quick.py
```

### Run Comprehensive Tests
```bash
cd C:/Users/User/PycharmProjects/HUI_algorithm
python tests/run_comprehensive_federated_tests.py --quick-test
```

## 🌐 Network Setup (Different Machines)

### Server Machine
```bash
# Find your IP address
ipconfig

# Start server (replace with your actual IP)
python federated_server.py --port 8888 --min-clients 2 --max-rounds 3
```

### Client Machine
```bash
# Connect to server (replace 192.168.1.100 with server's IP)
python federated_client.py --client-id "remote_laptop" --server-host 192.168.1.100 --server-port 8888 --data-file "datasets/datasets_fedlearn/chess_transactions.txt" --utility-file "datasets/datasets_fedlearn/chess_utilities.txt" --min-utility 50
```

## 📊 Parameter Recommendations

### For Quick Testing
- **min-utility**: 50-100 (lower values find more itemsets)
- **max-rounds**: 3-5 (fewer rounds for quick results)
- **epsilon**: 1.0-2.0 (moderate privacy)

### For Research/Production
- **min-utility**: 100-500 (depends on your data)
- **max-rounds**: 10-20 (more rounds for convergence)
- **epsilon**: 0.1-1.0 (stronger privacy)

## 🐛 Troubleshooting

### If Server Won't Start
```bash
# Check if port is in use
netstat -an | findstr :8888

# Use different port
python federated_server.py --port 9999
```

### If Client Can't Connect
```bash
# Test server connectivity
telnet localhost 8888

# Check firewall settings
# Ensure server is running first
```

### If No HUIs Found
```bash
# Lower the minimum utility threshold
python federated_client.py --min-utility 25

# Check data files exist
dir datasets\datasets_fedlearn\
```

## 📈 What to Expect

### Successful Run Output:
```
=== Server Output ===
Server started on port 8888
Waiting for 2 clients...
Client laptop_1 connected
Client laptop_2 connected
Starting federated round 1/3
Round 1 completed: 150 HUIs aggregated
Round 2 completed: 200 HUIs aggregated
Round 3 completed: 180 HUIs aggregated
Federated learning completed!

=== Client Output ===
Connected to server at localhost:8888
Participating in round 1/3
Local mining found 75 HUIs
Sent results to server
Round completed
```

### With Differential Privacy:
```
=== Server Output (with DP) ===
Differential Privacy enabled (ε=1.0)
Round 1 completed: 145 HUIs aggregated (noise added)
Round 2 completed: 195 HUIs aggregated (noise added)
Privacy budget remaining: 0.33
```

## 🎯 Success Indicators

✅ **Server starts without errors**
✅ **Clients connect successfully** 
✅ **Federated rounds complete**
✅ **HUIs are found and aggregated**
✅ **Privacy noise is applied (if DP enabled)**

## 📚 Next Steps

1. **Read the full README**: `FEDERATED_LEARNING_README.md`
2. **Experiment with parameters**: Try different epsilon values, minimum utilities
3. **Test with your own data**: Replace the dataset files
4. **Run comprehensive tests**: Use the test suite for detailed analysis
5. **Analyze results**: Check the output files and logs

---

**Need Help?** Check the logs in `federated_server.log` and `federated_client.log` for detailed debugging information.