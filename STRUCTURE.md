# Project Structure Overview

## 📁 Organized Directory Layout

Your HUI algorithm project has been reorganized into a clean, professional structure:

```
HUI_algorithm/
├── 📂 algorithms/           # Core HUI mining algorithms
│   ├── Alogrithm.py        # Optimized UP-Growth algorithm
│   ├── item.py             # Item class definition
│   ├── itemset.py          # Itemset class definition
│   ├── up_node.py          # UP-Tree node implementation
│   ├── up_tree.py          # UP-Tree data structure
│   ├── federated_client.py # Federated learning client
│   ├── federated_server.py # Federated learning server
│   ├── federated_fp_growth.py # Federated FP-Growth
│   └── __init__.py         # Package initialization
│
├── 📂 backend_node/        # Node.js/Express backend server
│   ├── src/               # Source code
│   │   ├── server.js      # Main Express server
│   │   ├── database/      # Database setup and models
│   │   ├── routes/        # API route handlers
│   │   └── middleware/    # Express middleware
│   ├── package.json       # Node.js dependencies
│   └── README.md          # Backend documentation
│
├── 📂 frontend/           # React TypeScript frontend
│   ├── src/              # Frontend source code
│   ├── package.json      # Frontend dependencies
│   └── ...               # Other frontend files
│
├── 📂 data/              # Dataset files
│   ├── chess_data.csv
│   ├── mushroom_data.csv
│   ├── large_sparse_dataset.csv
│   └── Transactional_T20I6D100K_converted.csv
│
├── 📂 scripts/           # Utility and test scripts
│   ├── test_integration.py      # Integration tests
│   ├── test_*.py               # Various test scripts
│   ├── debug_*.py              # Debugging utilities
│   ├── memory_*.py             # Memory optimization
│   ├── performance_comparison.py # Performance tests
│   └── README.md               # Scripts documentation
│
├── 📂 docs/              # Documentation
│   ├── FEDERATED_LEARNING_README.md
│   ├── PSEUDO_PROJECTION_IMPROVEMENTS.md
│   └── QUICK_START_COMMANDS.md
│
├── 📂 logs/              # Log files
│   ├── federated_client.log
│   └── federated_server.log
│
├── 📂 results/           # Mining results and outputs
├── 📂 tests/             # Test suites
├── 📂 src/               # Additional source files
├── 📂 config/            # Configuration files
├── 📂 datasets/          # Original dataset directory
├── 📂 fedlearn_results/  # Federated learning results
│
├── 📄 README.md          # Main project documentation
├── 📄 .gitignore         # Git ignore rules
└── 📄 STRUCTURE.md       # This file
```

## 🎯 Benefits of This Organization

### **Clear Separation of Concerns**
- **algorithms/**: Core mining logic isolated
- **backend_node/**: Node.js/Express API server and database
- **frontend/**: User interface components
- **scripts/**: Development and testing utilities
- **data/**: Raw datasets organized

### **Improved Maintainability**
- Related files grouped together
- Easy to locate specific functionality
- Clear import paths and dependencies
- Proper package structure with `__init__.py`

### **Professional Structure**
- Follows Python project best practices
- Scalable for future development
- Easy for new developers to understand
- Clean separation between production and development code

## 🔧 Updated Import Paths

The reorganization required updating import statements:

**Before:**
```python
from Alogrithm import OptimizedAlgoUPGrowth
from item import Item
```

**After:**
```python
from algorithms.Alogrithm import OptimizedAlgoUPGrowth
from algorithms.item import Item
```

## 🚀 Running the System

All commands should be run from the project root:

```bash
# Backend
cd backend_node && npm start

# Frontend  
cd frontend && npm run dev

# Tests
python scripts/test_integration.py
```

## 📊 Integration Status

✅ **File Organization Complete**
- All files moved to appropriate directories
- Package structure created with `__init__.py`
- Import paths updated in backend
- Documentation and README files created
- Git ignore file added for clean version control

The project now has a professional, maintainable structure that supports the integrated HUI mining system with federated learning capabilities.
