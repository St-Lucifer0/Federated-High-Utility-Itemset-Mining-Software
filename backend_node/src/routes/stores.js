/**
 * Store management routes
 */

import express from 'express';
import { body, param, validationResult } from 'express-validator';
import { getDatabase } from '../database/init.js';
import { ValidationError, NotFoundError, ConflictError } from '../middleware/errorHandler.js';
import { trackConnection } from '../middleware/connectionTracker.js';

const router = express.Router();

// Validation middleware
const validateStore = [
  body('store_id').isString().notEmpty().withMessage('Store ID is required'),
  body('name').isString().notEmpty().withMessage('Store name is required'),
  body('location').optional().isString().withMessage('Store location must be a string'),
  body('manager_name').optional().isString().withMessage('Manager name must be a string')
];

const validateStoreRegistration = [
  body('store_id').isString().notEmpty().withMessage('Store ID is required'),
  body('store_name').isString().notEmpty().withMessage('Store name is required')
];

function handleValidationErrors(req, res, next) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw new ValidationError('Validation failed', { errors: errors.array() });
  }
  next();
}

// Register a new store (client registration)
router.post('/register',
  validateStoreRegistration,
  handleValidationErrors,
  trackConnection,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id, store_name } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress || req.socket.remoteAddress || 
                     (req.connection.socket ? req.connection.socket.remoteAddress : null);

    try {
      await new Promise((resolve, reject) => {
        db.run(`
          INSERT OR REPLACE INTO stores (id, name, ip_address, connection_status, last_seen, is_active)
          VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP, 1)
        `, [store_id, store_name, clientIp], function(err) {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        });
      });

      res.status(201).json({
        message: 'Store registered successfully',
        store_id: store_id,
        store_name: store_name,
        status: 'active'
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Create a new store (admin function)
router.post('/',
  validateStore,
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id, name, location, manager_name } = req.body;

    try {
      await new Promise((resolve, reject) => {
        db.run(`
          INSERT INTO stores (id, name, location, is_active)
          VALUES (?, ?, ?, 1)
        `, [store_id, name, location || ''], function(err) {
          if (err) {
            if (err.code === 'SQLITE_CONSTRAINT_UNIQUE') {
              reject(new ConflictError('Store ID already exists'));
            } else {
              reject(err);
            }
          } else {
            resolve();
          }
        });
      });

      res.status(201).json({
        message: 'Store created successfully',
        store_id: store_id
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get all stores with connection status
router.get('/', async (req, res, next) => {
  const db = getDatabase();

  try {
    const stores = await new Promise((resolve, reject) => {
      db.all(`
        SELECT s.id, s.name, s.location, s.is_active, s.ip_address, 
               s.connection_status, s.last_seen, s.created_at,
               COUNT(t.id) as transaction_count,
               COALESCE(SUM(t.total_utility), 0) as total_utility,
               COUNT(DISTINCT mj.id) as mining_jobs_count
        FROM stores s
        LEFT JOIN transactions t ON s.id = t.store_id
        LEFT JOIN mining_jobs mj ON s.id = mj.store_id
        WHERE s.is_active = 1
        GROUP BY s.id, s.name, s.location, s.is_active, s.ip_address, 
                 s.connection_status, s.last_seen, s.created_at
        ORDER BY s.connection_status DESC, s.last_seen DESC, s.name
      `, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });

    res.json({ stores });

  } catch (error) {
    next(error);
  } finally {
    db.close();
  }
});

// Update store connection status (heartbeat)
router.post('/:store_id/heartbeat',
  param('store_id').isString().notEmpty().withMessage('Store ID is required'),
  handleValidationErrors,
  trackConnection,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;
    const clientIp = req.ip || req.connection.remoteAddress || req.socket.remoteAddress || 
                     (req.connection.socket ? req.connection.socket.remoteAddress : null);

    try {
      await new Promise((resolve, reject) => {
        db.run(`
          UPDATE stores 
          SET connection_status = 'active', 
              last_seen = CURRENT_TIMESTAMP,
              ip_address = ?
          WHERE id = ?
        `, [clientIp, store_id], function(err) {
          if (err) reject(err);
          else resolve();
        });
      });

      res.json({
        message: 'Heartbeat updated',
        store_id: store_id,
        status: 'active',
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get store by ID
router.get('/:store_id',
  param('store_id').isString().notEmpty().withMessage('Store ID is required'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;

    try {
      const store = await new Promise((resolve, reject) => {
        db.get(`
          SELECT s.id, s.name, s.location, s.is_active, s.created_at,
                 COUNT(t.id) as transaction_count,
                 COALESCE(SUM(t.total_utility), 0) as total_utility,
                 COUNT(DISTINCT mj.id) as mining_jobs_count
          FROM stores s
          LEFT JOIN transactions t ON s.id = t.store_id
          LEFT JOIN mining_jobs mj ON s.id = mj.store_id
          WHERE s.id = ?
          GROUP BY s.id, s.name, s.location, s.is_active, s.created_at
        `, [store_id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      if (!store) {
        throw new NotFoundError('Store not found');
      }

      res.json(store);

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Update store
router.put('/:store_id',
  param('store_id').isString().notEmpty().withMessage('Store ID is required'),
  body('name').optional().isString().notEmpty().withMessage('Store name cannot be empty'),
  body('location').optional().isString().notEmpty().withMessage('Store location cannot be empty'),
  body('is_active').optional().isBoolean().withMessage('is_active must be a boolean'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;
    const updates = req.body;

    try {
      // Check if store exists
      const existingStore = await new Promise((resolve, reject) => {
        db.get('SELECT id FROM stores WHERE id = ?', [store_id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      if (!existingStore) {
        throw new NotFoundError('Store not found');
      }

      // Build dynamic update query
      const updateFields = [];
      const updateValues = [];

      if (updates.name !== undefined) {
        updateFields.push('name = ?');
        updateValues.push(updates.name);
      }
      if (updates.location !== undefined) {
        updateFields.push('location = ?');
        updateValues.push(updates.location);
      }
      if (updates.is_active !== undefined) {
        updateFields.push('is_active = ?');
        updateValues.push(updates.is_active);
      }

      if (updateFields.length === 0) {
        return res.json({ message: 'No updates provided' });
      }

      updateValues.push(store_id);

      await new Promise((resolve, reject) => {
        db.run(`
          UPDATE stores 
          SET ${updateFields.join(', ')}
          WHERE id = ?
        `, updateValues, function(err) {
          if (err) reject(err);
          else resolve();
        });
      });

      res.json({
        message: 'Store updated successfully',
        store_id: store_id
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Delete store (soft delete)
router.delete('/:store_id',
  param('store_id').isString().notEmpty().withMessage('Store ID is required'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;

    try {
      const result = await new Promise((resolve, reject) => {
        db.run(`
          UPDATE stores 
          SET is_active = 0
          WHERE id = ?
        `, [store_id], function(err) {
          if (err) reject(err);
          else resolve(this.changes);
        });
      });

      if (result === 0) {
        throw new NotFoundError('Store not found');
      }

      res.json({
        message: 'Store deactivated successfully',
        store_id: store_id
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get store analytics
router.get('/:store_id/analytics',
  param('store_id').isString().notEmpty().withMessage('Store ID is required'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;

    try {
      // Get transaction analytics
      const transactionStats = await new Promise((resolve, reject) => {
        db.get(`
          SELECT 
            COUNT(*) as total_transactions,
            AVG(total_utility) as avg_utility,
            MAX(total_utility) as max_utility,
            MIN(total_utility) as min_utility,
            SUM(total_utility) as total_utility_sum,
            DATE(MIN(transaction_date)) as first_transaction,
            DATE(MAX(transaction_date)) as last_transaction
          FROM transactions 
          WHERE store_id = ?
        `, [store_id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      // Get mining job analytics
      const miningStats = await new Promise((resolve, reject) => {
        db.get(`
          SELECT 
            COUNT(*) as total_jobs,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
            AVG(CASE WHEN status = 'completed' THEN execution_time_seconds END) as avg_execution_time,
            SUM(CASE WHEN status = 'completed' THEN patterns_found ELSE 0 END) as total_patterns_found
          FROM mining_jobs 
          WHERE store_id = ?
        `, [store_id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      // Get recent activity
      const recentActivity = await new Promise((resolve, reject) => {
        db.all(`
          SELECT 'transaction' as type, transaction_date as date, total_utility as value
          FROM transactions 
          WHERE store_id = ?
          UNION ALL
          SELECT 'mining_job' as type, started_at as date, patterns_found as value
          FROM mining_jobs 
          WHERE store_id = ? AND status = 'completed'
          ORDER BY date DESC
          LIMIT 10
        `, [store_id, store_id], (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      res.json({
        store_id,
        transaction_analytics: transactionStats,
        mining_analytics: miningStats,
        recent_activity: recentActivity
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

export default router;
