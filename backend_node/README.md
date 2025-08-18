# HUI Federated Learning - Node.js/Express Backend

This is the Node.js/Express backend for the HUI (High Utility Itemset) Federated Learning System, replacing the previous FastAPI implementation.

## Features

- **RESTful API** for transaction management, mining operations, and federated learning
- **SQLite Database** for data persistence
- **Python Integration** for HUI algorithms via subprocess calls
- **Express.js Framework** with modern middleware stack
- **Comprehensive Error Handling** and validation
- **Rate Limiting** and security features
- **Structured Logging** with Winston

## Architecture

```
backend_node/
├── src/
│   ├── server.js              # Main Express server
│   ├── database/
│   │   └── init.js           # Database initialization
│   ├── middleware/
│   │   └── errorHandler.js   # Error handling middleware
│   └── routes/
│       ├── transactions.js   # Transaction management
│       ├── mining.js         # Mining operations
│       ├── federated.js      # Federated learning
│       └── stores.js         # Store management
├── logs/                     # Application logs
├── package.json
└── README.md
```

## Prerequisites

- Node.js 18+ 
- Python 3.8+ (for HUI algorithms)
- SQLite3

## Installation

1. **Install dependencies:**
   ```bash
   cd backend_node
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Ensure Python dependencies are available:**
   ```bash
   # The backend calls Python scripts in ../algorithms/
   # Make sure the HUI algorithm modules are accessible
   ```

## Running the Server

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

The server will start on port 8001 by default.

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health status

### Transactions
- `POST /api/transactions/upload/:store_id` - Upload transactions
- `GET /api/transactions/:store_id` - Get store transactions
- `GET /api/transactions/:store_id/stats` - Get transaction statistics

### Mining Operations
- `POST /api/mining/start` - Start mining job
- `GET /api/mining/status/:job_id` - Get job status
- `GET /api/mining/results/:job_id` - Get mining results
- `GET /api/mining/jobs/:store_id` - Get all jobs for store

### Federated Learning
- `POST /api/federated/start-round` - Start federated round
- `GET /api/federated/rounds` - Get all rounds
- `GET /api/federated/rounds/:round_id/patterns` - Get round patterns
- `GET /api/federated/rounds/:round_id/status` - Get round status
- `GET /api/federated/global-patterns` - Get all global patterns

### Store Management
- `POST /api/stores` - Create store
- `GET /api/stores` - Get all stores
- `GET /api/stores/:store_id` - Get store details
- `PUT /api/stores/:store_id` - Update store
- `DELETE /api/stores/:store_id` - Deactivate store
- `GET /api/stores/:store_id/analytics` - Get store analytics

## Database Schema

The system uses SQLite with the following main tables:
- `users` - User accounts and roles
- `stores` - Store information
- `transactions` - Transaction data
- `mining_jobs` - Mining job tracking
- `local_patterns` - Store-specific patterns
- `federated_rounds` - Federated learning rounds
- `global_patterns` - Aggregated global patterns

## Python Integration

The backend integrates with Python HUI algorithms through wrapper scripts:
- `algorithms/mining_wrapper.py` - HUI mining interface
- `algorithms/federated_wrapper.py` - Federated aggregation interface

These scripts communicate via JSON over stdin/stdout.

## Security Features

- **CORS** protection with configurable origins
- **Rate limiting** to prevent abuse
- **Input validation** using express-validator
- **Helmet** for security headers
- **Error sanitization** in production

## Logging

Logs are written to:
- `logs/combined.log` - All logs
- `logs/error.log` - Error logs only
- Console output in development

## Environment Variables

Key configuration options in `.env`:
- `PORT` - Server port (default: 8001)
- `NODE_ENV` - Environment (development/production)
- `DATABASE_PATH` - SQLite database path
- `LOG_LEVEL` - Logging level
- `CORS_ORIGINS` - Allowed CORS origins

## Migration from FastAPI

This backend provides full compatibility with the existing React frontend. All API endpoints maintain the same request/response formats as the original FastAPI implementation.

Key improvements over FastAPI:
- **Better Performance** - Node.js event loop efficiency
- **Simpler Deployment** - Single runtime environment
- **Enhanced Error Handling** - Structured error responses
- **Improved Logging** - Comprehensive request/response logging
- **Better Integration** - Native JavaScript/JSON handling

## Development

### Adding New Routes
1. Create route file in `src/routes/`
2. Add validation middleware
3. Implement route handlers
4. Register routes in `src/server.js`

### Database Changes
1. Update schema in `src/database/init.js`
2. Handle migrations carefully
3. Test with existing data

### Python Integration
1. Create wrapper scripts in `algorithms/`
2. Use JSON for data exchange
3. Handle errors gracefully
4. Test subprocess communication

## Testing

```bash
npm test
```

## Troubleshooting

### Common Issues

1. **Python script errors**
   - Check Python path in environment
   - Verify algorithm dependencies
   - Check wrapper script permissions

2. **Database errors**
   - Ensure SQLite is installed
   - Check file permissions
   - Verify database path

3. **Port conflicts**
   - Change PORT in .env
   - Check for running processes

### Debug Mode

Set `LOG_LEVEL=debug` in `.env` for verbose logging.
