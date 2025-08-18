/**
 * Federated learning routes
 */

import express from 'express';
import { body, param, validationResult } from 'express-validator';
import { v4 as uuidv4 } from 'uuid';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getDatabase } from '../database/init.js';
import { ValidationError, NotFoundError } from '../middleware/errorHandler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const router = express.Router();

// Validation middleware
const validateFederatedRequest = [
  body('min_clients').optional().isInt({ min: 1 }).withMessage('Min clients must be a positive integer'),
  body('privacy_budget').optional().isFloat({ min: 0 }).withMessage('Privacy budget must be a positive number')
];

function handleValidationErrors(req, res, next) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw new ValidationError('Validation failed', { errors: errors.array() });
  }
  next();
}

// Function to run federated learning round
async function runFederatedRound(roundId, minClients = 2, privacyBudget = 1.0) {
  const db = getDatabase();
  
  try {
    // Update round status to running
    await new Promise((resolve, reject) => {
      db.run(`
        UPDATE federated_rounds 
        SET status = 'running', started_at = CURRENT_TIMESTAMP 
        WHERE id = ?
      `, [roundId], function(err) {
        if (err) reject(err);
        else resolve();
      });
    });

    // Get available local patterns from different stores
    const localPatterns = await new Promise((resolve, reject) => {
      db.all(`
        SELECT lp.store_id, lp.pattern_items, lp.utility, lp.support, lp.confidence
        FROM local_patterns lp
        JOIN mining_jobs mj ON lp.mining_job_id = mj.id
        WHERE mj.status = 'completed'
        GROUP BY lp.store_id, lp.pattern_items
        HAVING COUNT(DISTINCT lp.store_id) >= ?
        ORDER BY lp.utility DESC
      `, [minClients], (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });

    if (localPatterns.length === 0) {
      throw new Error(`Insufficient patterns from ${minClients} or more stores`);
    }

    // Create Python script path for federated aggregation
    const pythonScriptPath = path.join(__dirname, '..', '..', '..', 'algorithms', 'federated_wrapper.py');
    
    // Prepare input data for federated aggregation
    const inputData = {
      local_patterns: localPatterns.map(row => ({
        store_id: row.store_id,
        items: JSON.parse(row.pattern_items),
        utility: row.utility,
        support: row.support,
        confidence: row.confidence
      })),
      privacy_budget: privacyBudget,
      min_clients: minClients
    };

    const startTime = Date.now();

    // Run federated aggregation
    const globalPatterns = await new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [pythonScriptPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Federated aggregation failed: ${stderr}`));
        } else {
          try {
            const result = JSON.parse(stdout);
            resolve(result.global_patterns || []);
          } catch (parseError) {
            reject(new Error(`Failed to parse federated output: ${parseError.message}`));
          }
        }
      });

      // Send input data to Python script
      pythonProcess.stdin.write(JSON.stringify(inputData));
      pythonProcess.stdin.end();
    });

    // Store global patterns in database
    let patternsCount = 0;
    const uniqueStores = new Set(localPatterns.map(p => p.store_id));
    
    for (const pattern of globalPatterns) {
      const patternId = uuidv4();
      
      await new Promise((resolve, reject) => {
        db.run(`
          INSERT INTO global_patterns 
          (id, round_id, pattern_items, aggregated_utility, global_support, contributing_stores)
          VALUES (?, ?, ?, ?, ?, ?)
        `, [
          patternId,
          roundId,
          JSON.stringify(pattern.items),
          pattern.aggregated_utility,
          pattern.global_support,
          pattern.contributing_stores || uniqueStores.size
        ], function(err) {
          if (err) reject(err);
          else resolve();
        });
      });
      patternsCount++;
    }

    // Update round completion
    await new Promise((resolve, reject) => {
      db.run(`
        UPDATE federated_rounds 
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
            participating_clients = ?, patterns_aggregated = ?
        WHERE id = ?
      `, [uniqueStores.size, patternsCount, roundId], function(err) {
        if (err) reject(err);
        else resolve();
      });
    });

    console.log(`Federated round ${roundId} completed. Aggregated ${patternsCount} patterns from ${uniqueStores.size} stores`);

  } catch (error) {
    console.error(`Federated round ${roundId} failed:`, error.message);
    
    await new Promise((resolve) => {
      db.run(`
        UPDATE federated_rounds 
        SET status = 'failed', completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `, [roundId], () => resolve());
    });
  } finally {
    db.close();
  }
}

// Start a federated learning round
router.post('/start-round',
  validateFederatedRequest,
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const roundId = uuidv4();
    const { min_clients = 2, privacy_budget = 1.0 } = req.body;

    try {
      // Get the next round number
      const lastRound = await new Promise((resolve, reject) => {
        db.get(`
          SELECT MAX(round_number) as max_round
          FROM federated_rounds
        `, (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      const roundNumber = (lastRound?.max_round || 0) + 1;

      // Insert federated round record
      await new Promise((resolve, reject) => {
        db.run(`
          INSERT INTO federated_rounds 
          (id, round_number, min_clients_required, started_at)
          VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        `, [roundId, roundNumber, min_clients], function(err) {
          if (err) reject(err);
          else resolve();
        });
      });

      // Start federated round in background
      setImmediate(() => {
        runFederatedRound(roundId, min_clients, privacy_budget);
      });

      res.json({
        round_id: roundId,
        round_number: roundNumber,
        status: 'started'
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get federated learning rounds
router.get('/rounds', async (req, res, next) => {
  const db = getDatabase();

  try {
    const rounds = await new Promise((resolve, reject) => {
      db.all(`
        SELECT id, round_number, status, participating_clients, 
               started_at, completed_at, patterns_aggregated
        FROM federated_rounds 
        ORDER BY started_at DESC
      `, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });

    res.json({ rounds });

  } catch (error) {
    next(error);
  } finally {
    db.close();
  }
});

// Get global patterns from a specific round
router.get('/rounds/:round_id/patterns',
  param('round_id').isUUID().withMessage('Invalid round ID'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { round_id } = req.params;

    try {
      const patterns = await new Promise((resolve, reject) => {
        db.all(`
          SELECT pattern_items, aggregated_utility, global_support, contributing_stores, created_at
          FROM global_patterns 
          WHERE round_id = ?
          ORDER BY aggregated_utility DESC
        `, [round_id], (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      const formattedPatterns = patterns.map(row => ({
        items: JSON.parse(row.pattern_items),
        aggregated_utility: row.aggregated_utility,
        global_support: row.global_support,
        contributing_stores: row.contributing_stores,
        created_at: row.created_at
      }));

      res.json({
        patterns: formattedPatterns,
        count: formattedPatterns.length
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get federated round status
router.get('/rounds/:round_id/status',
  param('round_id').isUUID().withMessage('Invalid round ID'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { round_id } = req.params;

    try {
      const round = await new Promise((resolve, reject) => {
        db.get(`
          SELECT id, round_number, status, min_clients_required, participating_clients,
                 started_at, completed_at, patterns_aggregated
          FROM federated_rounds 
          WHERE id = ?
        `, [round_id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      if (!round) {
        throw new NotFoundError('Federated round not found');
      }

      res.json(round);

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get all global patterns (latest from all rounds)
router.get('/global-patterns', async (req, res, next) => {
  const db = getDatabase();

  try {
    const patterns = await new Promise((resolve, reject) => {
      db.all(`
        SELECT gp.pattern_items, gp.aggregated_utility, gp.global_support, 
               gp.contributing_stores, gp.created_at, fr.round_number
        FROM global_patterns gp
        JOIN federated_rounds fr ON gp.round_id = fr.id
        WHERE fr.status = 'completed'
        ORDER BY gp.aggregated_utility DESC
        LIMIT 100
      `, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });

    const formattedPatterns = patterns.map(row => ({
      items: JSON.parse(row.pattern_items),
      aggregated_utility: row.aggregated_utility,
      global_support: row.global_support,
      contributing_stores: row.contributing_stores,
      round_number: row.round_number,
      created_at: row.created_at
    }));

    res.json({
      patterns: formattedPatterns,
      count: formattedPatterns.length
    });

  } catch (error) {
    next(error);
  } finally {
    db.close();
  }
});

export default router;
