# Client-Server System Setup Guide

## Overview
This guide explains how to set up and test the client-server system for the HUI Federated Learning project.

## Architecture
- **Server (Regional Coordinator)**: Runs on your laptop
- **Client (Store Manager)**: Runs on another machine
- **Communication**: HTTP API with real-time connection tracking

## Setup Instructions

### 1. Server Setup (Your Laptop)

1. **Start the Express Backend**:
   ```bash
   cd backend_node
   npm install
   npm start
   ```
   - Server runs on port 8002
   - Database: SQLite (hui_system.db)

2. **Start the Frontend (Server Dashboard)**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Frontend runs on port 3000
   - Access at: http://localhost:3000
   - Select "Regional Coordinator" role

### 2. Client Setup (Another Machine)

1. **Configure API URL**:
   - Create `.env` file in frontend directory:
   ```
   VITE_API_URL=http://[SERVER_IP]:8002/api
   ```
   - Replace `[SERVER_IP]` with your laptop's IP address

2. **Start Client Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Access at: http://localhost:3000
   - Select "Store Manager" role

### 3. Network Configuration

1. **Find Server IP**:
   ```bash
   # On Windows (Server machine)
   ipconfig
   
   # On Linux/Mac (Server machine)
   ifconfig
   ```

2. **Firewall Settings**:
   - Allow port 8002 (backend) and 3000 (frontend) through firewall
   - For testing on localhost, use: `http://localhost:8002/api`

## Usage Instructions

### Client Registration Process

1. **On Client Machine**:
   - Open Store Manager dashboard
   - Go to "Register Store" tab
   - Enter Store ID (e.g., "STORE001")
   - Enter Store Name (e.g., "Downtown Branch")
   - Click "Register Store"

2. **Verification**:
   - Client should show "Connected to Server" status
   - Heartbeat signals sent every 30 seconds

### Server Monitoring

1. **On Server Machine**:
   - Open Regional Coordinator dashboard
   - Go to "Client Status" tab
   - View registered clients with:
     - Store ID and Name
     - Connection Status (Active/Inactive)
     - IP Address
     - Last Seen timestamp
     - Transaction count

2. **Real-time Updates**:
   - Client list refreshes every 10 seconds
   - Connection status tracked automatically
   - Clients marked inactive after 60 seconds without heartbeat

## API Endpoints

### Client Registration
- **POST** `/api/stores/register`
  ```json
  {
    "store_id": "STORE001",
    "store_name": "Downtown Branch"
  }
  ```

### Heartbeat
- **POST** `/api/stores/{store_id}/heartbeat`

### Get All Stores
- **GET** `/api/stores`

### Connection Stats
- **GET** `/api/connection/stats`

## Database Schema

### Stores Table
```sql
CREATE TABLE stores (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  location TEXT,
  ip_address TEXT,
  connection_status TEXT DEFAULT 'inactive',
  last_seen TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT 1
);
```

## Troubleshooting

### Connection Issues
1. **Client can't connect to server**:
   - Check server IP address in client .env file
   - Verify firewall settings
   - Ensure backend is running on port 8002

2. **Client shows as inactive**:
   - Check network connectivity
   - Verify heartbeat signals are being sent
   - Check server logs for errors

### Testing Locally
For local testing on same machine:
- Server: http://localhost:3000 (Regional Coordinator)
- Client: http://localhost:3001 (Store Manager)
- Backend: http://localhost:8002

### Logs
- Backend logs: Console output and logs/ directory
- Frontend logs: Browser console (F12)
- Connection tracking: Automatic in connectionTracker middleware

## Features

### Real-time Connection Tracking
- Automatic heartbeat every 30 seconds
- Connection timeout after 60 seconds
- Real-time status updates on server dashboard

### Security
- IP address tracking
- CORS protection
- Rate limiting
- Input validation

### Scalability
- Multiple clients can connect simultaneously
- Connection state managed in memory and database
- Automatic cleanup of inactive connections
