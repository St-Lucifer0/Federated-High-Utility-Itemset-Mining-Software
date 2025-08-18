/**
 * Connection status and monitoring routes
 */

import express from 'express';
import { connectionTracker } from '../middleware/connectionTracker.js';

const router = express.Router();

// Get connection statistics
router.get('/stats', (req, res) => {
  const stats = connectionTracker.getConnectionStats();
  res.json({
    ...stats,
    timestamp: new Date().toISOString()
  });
});

// Get all connected clients with details
router.get('/clients', (req, res) => {
  const stats = connectionTracker.getConnectionStats();
  res.json({
    connected_clients: stats.connectedClients,
    active_connections: stats.activeConnections,
    timestamp: new Date().toISOString()
  });
});

export default router;
