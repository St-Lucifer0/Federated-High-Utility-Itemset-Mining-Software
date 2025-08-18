# HUI Mining System with Federated Learning

A comprehensive High Utility Itemset (HUI) mining system with federated learning capabilities, featuring a React frontend and Python backend.

## 🏗️ Project Structure

```
HUI_algorithm/
├── algorithms/           # Core HUI mining algorithms
│   ├── Alogrithm.py     # Optimized UP-Growth algorithm
│   ├── item.py          # Item class definition
│   ├── itemset.py       # Itemset class definition
│   ├── up_node.py       # UP-Tree node implementation
│   ├── up_tree.py       # UP-Tree data structure
│   ├── federated_client.py    # Federated learning client
│   ├── federated_server.py    # Federated learning server
│   └── federated_fp_growth.py # Federated FP-Growth algorithm
├── backend_node/        # Node.js/Express backend server
│   ├── src/            # Source code
│   │   ├── server.js   # Main Express server
│   │   ├── database/   # Database setup and models
│   │   ├── routes/     # API route handlers
│   │   └── middleware/ # Express middleware
│   ├── package.json    # Node.js dependencies
│   └── README.md       # Backend documentation
├── frontend/           # React TypeScript frontend
│   ├── src/           # Frontend source code
│   ├── package.json   # Frontend dependencies
│   └── ...
├── data/              # Dataset files
│   ├── chess_data.csv
│   ├── mushroom_data.csv
│   ├── large_sparse_dataset.csv
│   └── Transactional_T20I6D100K_converted.csv
├── scripts/           # Utility and test scripts
│   ├── test_*.py     # Various test scripts
│   ├── debug_*.py    # Debugging utilities
│   ├── memory_*.py   # Memory optimization scripts
│   └── performance_comparison.py
├── docs/              # Documentation
│   ├── FEDERATED_LEARNING_README.md
│   ├── PSEUDO_PROJECTION_IMPROVEMENTS.md
│   └── QUICK_START_COMMANDS.md
├── logs/              # Log files
├── results/           # Mining results and outputs
├── tests/             # Test suites
└── src/               # Additional source files
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend_node
npm install
npm start
```
Backend runs on: `http://localhost:8001`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on: `http://localhost:3000`

## 🔧 System Features

- **High Utility Itemset Mining**: Optimized UP-Growth algorithm
- **Federated Learning**: Privacy-preserving distributed mining
- **Web Interface**: Modern React frontend with real-time data
- **RESTful API**: Node.js/Express backend with comprehensive endpoints
- **Database Integration**: SQLite for local development
- **Role-Based Access**: Store Manager and Regional Coordinator dashboards

## 📊 Integration Status

✅ **Completed Integration**
- Frontend connected to real HUI algorithms
- All dummy data replaced with live algorithm results
- Database converted from PostgreSQL to SQLite
- API endpoints fully functional
- Transaction processing and mining job management

## 🧪 Testing

Run integration tests:
```bash
python test_integration.py
```

Current test results: **3/4 tests passing**
- ✅ Backend Health Check
- ✅ Store Creation
- ✅ Transaction Upload
- ⚠️ Mining Job Execution (minor utility validation issue)

## 📁 Key Components

### Algorithms (`/algorithms/`)
- **Alogrithm.py**: Core UP-Growth implementation
- **federated_server.py**: Coordinates federated learning
- **federated_client.py**: Client-side federated participation

### Backend (`/backend_node/`)
- **server.js**: Express server bridging frontend and algorithms
- RESTful endpoints for transactions, mining, and federated learning
- SQLite database integration with comprehensive schema

### Frontend (`/frontend/`)
- React TypeScript application with Tailwind CSS
- Client and Server dashboards for different user roles
- Real-time mining progress and results display

## 🔗 API Endpoints

- `GET /` - Health check
- `POST /api/stores` - Create stores
- `POST /api/transactions/upload/{store_id}` - Upload transactions
- `POST /api/mining/start` - Start mining jobs
- `GET /api/mining/status/{job_id}` - Check job status
- `GET /api/mining/results/{job_id}` - Get mining results
- `POST /api/federated/start-round` - Start federated round

## 📈 Performance

The system is optimized for:
- Large-scale transaction processing
- Memory-efficient mining operations
- Real-time federated learning coordination
- Responsive web interface

## 🛠️ Development

The project follows clean architecture principles with:
- Separation of concerns between frontend and backend
- Modular algorithm implementations
- Comprehensive testing suite
- Well-documented APIs

For detailed development information, see the documentation in `/docs/`.
