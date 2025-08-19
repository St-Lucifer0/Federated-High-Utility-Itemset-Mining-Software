/**
 * Transaction management routes
 */

import express from 'express';
import { body, param, query, validationResult } from 'express-validator';
import { v4 as uuidv4 } from 'uuid';
import { getDatabase } from '../database/init.js';
import { ValidationError, NotFoundError } from '../middleware/errorHandler.js';

const router = express.Router();

// Validation middleware
const validateTransaction = [
  body('*.items').isArray().withMessage('Items must be an array'),
  body('*.quantities').isArray().withMessage('Quantities must be an array'),
  body('*.unit_utilities').isArray().withMessage('Unit utilities must be an array'),
  body('*.items.*').isString().withMessage('Each item must be a string'),
  body('*.quantities.*').isNumeric().withMessage('Each quantity must be a number'),
  body('*.unit_utilities.*').isNumeric().withMessage('Each utility must be a number')
];

const validateStoreId = [
  param('store_id').isString().notEmpty().withMessage('Store ID is required')
];

const validateLimit = [
  query('limit').optional().isInt({ min: 1, max: 50000 }).withMessage('Limit must be between 1 and 50000')
];

function handleValidationErrors(req, res, next) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw new ValidationError('Validation failed', { errors: errors.array() });
  }
  next();
}

// Upload transactions for a store
router.post('/upload/:store_id', 
  validateStoreId,
  validateTransaction,
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;
    const transactions = req.body;

    try {
      // Start transaction
      await new Promise((resolve, reject) => {
        db.run('BEGIN TRANSACTION', (err) => {
          if (err) reject(err);
          else resolve();
        });
      });

      const insertPromises = transactions.map(transaction => {
        return new Promise((resolve, reject) => {
          // Calculate total utility if not provided
          const totalUtility = transaction.total_utility || 
            transaction.quantities.reduce((sum, qty, idx) => 
              sum + (qty * transaction.unit_utilities[idx]), 0);

          const transactionId = uuidv4();
          
          db.run(`
            INSERT INTO transactions 
            (id, store_id, items, quantities, unit_utilities, total_utility)
            VALUES (?, ?, ?, ?, ?, ?)
          `, [
            transactionId,
            store_id,
            JSON.stringify(transaction.items),
            JSON.stringify(transaction.quantities),
            JSON.stringify(transaction.unit_utilities),
            totalUtility
          ], function(err) {
            if (err) reject(err);
            else resolve(this.lastID);
          });
        });
      });

      await Promise.all(insertPromises);

      // Commit transaction
      await new Promise((resolve, reject) => {
        db.run('COMMIT', (err) => {
          if (err) reject(err);
          else resolve();
        });
      });

      res.json({
        message: `Uploaded ${transactions.length} transactions`,
        store_id: store_id
      });

    } catch (error) {
      // Rollback on error
      await new Promise((resolve) => {
        db.run('ROLLBACK', () => resolve());
      });
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get transactions for a store
router.get('/:store_id',
  validateStoreId,
  validateLimit,
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;
    const limit = parseInt(req.query.limit) || 10000;

    try {
      const transactions = await new Promise((resolve, reject) => {
        db.all(`
          SELECT id, items, quantities, unit_utilities, total_utility, transaction_date
          FROM transactions 
          WHERE store_id = ? 
          ORDER BY transaction_date DESC 
          LIMIT ?
        `, [store_id, limit], (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      const formattedTransactions = transactions.map(row => ({
        id: row.id,
        items: JSON.parse(row.items),
        quantities: JSON.parse(row.quantities),
        unit_utilities: JSON.parse(row.unit_utilities),
        total_utility: row.total_utility,
        transaction_date: row.transaction_date
      }));

      res.json({
        transactions: formattedTransactions,
        count: formattedTransactions.length
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get transaction statistics for a store
router.get('/:store_id/stats',
  validateStoreId,
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;

    try {
      const stats = await new Promise((resolve, reject) => {
        db.get(`
          SELECT 
            COUNT(*) as total_transactions,
            AVG(total_utility) as avg_utility,
            MAX(total_utility) as max_utility,
            MIN(total_utility) as min_utility,
            SUM(total_utility) as total_utility_sum
          FROM transactions 
          WHERE store_id = ?
        `, [store_id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      res.json(stats);

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

export default router;
