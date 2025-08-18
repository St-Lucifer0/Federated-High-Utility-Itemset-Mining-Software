/**
 * Connection tracking middleware for real-time client status monitoring
 */

import { getDatabase } from '../database/init.js';

class ConnectionTracker {
  constructor() {
    this.connectedClients = new Map();
    this.heartbeatTimeout = 60000; // 60 seconds timeout
    
    // Check for inactive clients every 30 seconds
    setInterval(() => {
      this.checkInactiveClients();
    }, 30000);
  }

  // Mark client as active
  updateClientStatus(storeId, ipAddress) {
    this.connectedClients.set(storeId, {
      lastSeen: new Date(),
      ipAddress: ipAddress
    });
  }

  // Check for clients that haven't sent heartbeat recently
  async checkInactiveClients() {
    const db = getDatabase();
    const now = new Date();
    
    try {
      // Get all active stores from database
      const activeStores = await new Promise((resolve, reject) => {
        db.all(`
          SELECT id FROM stores 
          WHERE connection_status = 'active' AND is_active = 1
        `, (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      // Check each active store for recent heartbeat
      for (const store of activeStores) {
        const clientInfo = this.connectedClients.get(store.id);
        
        if (!clientInfo || (now.getTime() - clientInfo.lastSeen.getTime()) > this.heartbeatTimeout) {
          // Mark as inactive in database
          await new Promise((resolve, reject) => {
            db.run(`
              UPDATE stores 
              SET connection_status = 'inactive'
              WHERE id = ?
            `, [store.id], function(err) {
              if (err) reject(err);
              else resolve();
            });
          });
          
          // Remove from active connections
          this.connectedClients.delete(store.id);
          console.log(`Client ${store.id} marked as inactive due to timeout`);
        }
      }
    } catch (error) {
      console.error('Error checking inactive clients:', error);
    } finally {
      db.close();
    }
  }

  // Get current connection stats
  getConnectionStats() {
    return {
      activeConnections: this.connectedClients.size,
      connectedClients: Array.from(this.connectedClients.keys())
    };
  }
}

// Singleton instance
const connectionTracker = new ConnectionTracker();

// Middleware to track client connections
export const trackConnection = (req, res, next) => {
  // Extract store ID from various possible sources
  const storeId = req.params.store_id || req.body.store_id || req.headers['x-store-id'];
  const clientIp = req.ip || req.connection.remoteAddress || req.socket.remoteAddress || 
                   (req.connection.socket ? req.connection.socket.remoteAddress : null);

  if (storeId) {
    connectionTracker.updateClientStatus(storeId, clientIp);
  }

  next();
};

export { connectionTracker };
export default connectionTracker;
