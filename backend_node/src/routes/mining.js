/**
 * Mining operations routes
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
const validateMiningRequest = [
  body('store_id').isString().notEmpty().withMessage('Store ID is required'),
  body('min_utility').isNumeric().withMessage('Min utility must be a number'),
  body('min_support').optional().isFloat({ min: 0, max: 1 }).withMessage('Min support must be between 0 and 1'),
  body('max_pattern_length').optional().isInt({ min: 1 }).withMessage('Max pattern length must be a positive integer'),
  body('use_pruning').optional().isBoolean().withMessage('Use pruning must be a boolean'),
  body('batch_size').optional().isInt({ min: 1 }).withMessage('Batch size must be a positive integer')
];

function handleValidationErrors(req, res, next) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw new ValidationError('Validation failed', { errors: errors.array() });
  }
  next();
}

// Function to run mining job using Python subprocess
async function runMiningJob(jobId, storeId, minUtility, minSupport = 0.1) {
  const db = getDatabase();
  
  try {
    // Update job status to running
    await new Promise((resolve, reject) => {
      db.run(`
        UPDATE mining_jobs 
        SET status = 'running', started_at = CURRENT_TIMESTAMP 
        WHERE id = ?
      `, [jobId], function(err) {
        if (err) reject(err);
        else resolve();
      });
    });

    // Get transactions for this store
    const transactionsData = await new Promise((resolve, reject) => {
      db.all(`
        SELECT items, quantities, unit_utilities 
        FROM transactions 
        WHERE store_id = ?
      `, [storeId], (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });

    if (!transactionsData || transactionsData.length === 0) {
      throw new Error('No transactions found for this store');
    }

    // Prepare data for Python script
    const transactionsForPython = transactionsData.map(row => ({
      items: JSON.parse(row.items),
      quantities: JSON.parse(row.quantities),
      unit_utilities: JSON.parse(row.unit_utilities)
    }));

    // Create Python script path
    const pythonScriptPath = path.join(__dirname, '..', '..', '..', 'algorithms', 'mining_wrapper.py');
    
    // Prepare input data
    const inputData = {
      transactions: transactionsForPython,
      min_utility: minUtility,
      min_support: minSupport
    };

    const startTime = Date.now();

    // Run Python mining algorithm
    const patterns = await new Promise((resolve, reject) => {
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
          reject(new Error(`Python script failed: ${stderr}`));
        } else {
          try {
            const result = JSON.parse(stdout);
            resolve(result.patterns || []);
          } catch (parseError) {
            reject(new Error(`Failed to parse Python output: ${parseError.message}`));
          }
        }
      });

      // Send input data to Python script
      try {
        pythonProcess.stdin.write(JSON.stringify(inputData));
        pythonProcess.stdin.end();
      } catch (error) {
        reject(new Error(`Failed to write to Python process: ${error.message}`));
      }
    });

    const executionTime = (Date.now() - startTime) / 1000;

    // Store patterns in database
    let patternsCount = 0;
    for (const pattern of patterns) {
      const patternId = uuidv4();
      
      await new Promise((resolve, reject) => {
        db.run(`
          INSERT INTO local_patterns 
          (id, mining_job_id, store_id, pattern_items, utility, support, confidence)
          VALUES (?, ?, ?, ?, ?, ?, ?)
        `, [
          patternId,
          jobId,
          storeId,
          JSON.stringify(pattern.items),
          pattern.utility,
          pattern.support || 0.0,
          pattern.confidence || 0.0
        ], function(err) {
          if (err) reject(err);
          else resolve();
        });
      });
      patternsCount++;
    }

    // Update job completion
    await new Promise((resolve, reject) => {
      db.run(`
        UPDATE mining_jobs 
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
            execution_time_seconds = ?, patterns_found = ?
        WHERE id = ?
      `, [executionTime, patternsCount, jobId], function(err) {
        if (err) reject(err);
        else resolve();
      });
    });

    console.log(`Mining job ${jobId} completed. Found ${patternsCount} patterns in ${executionTime.toFixed(2)}s`);

  } catch (error) {
    console.error(`Mining job ${jobId} failed:`, error.message);
    
    await new Promise((resolve) => {
      db.run(`
        UPDATE mining_jobs 
        SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `, [error.message, jobId], () => resolve());
    });
  } finally {
    db.close();
  }
}

// Start HUI mining job
router.post('/start',
  validateMiningRequest,
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const jobId = uuidv4();
    const {
      store_id,
      min_utility,
      min_support = 0.1,
      max_pattern_length = 5,
      use_pruning = true,
      batch_size = 1000
    } = req.body;

    try {
      // Insert mining job record
      await new Promise((resolve, reject) => {
        db.run(`
          INSERT INTO mining_jobs 
          (id, store_id, min_utility, min_support, max_pattern_length, use_pruning, batch_size)
          VALUES (?, ?, ?, ?, ?, ?, ?)
        `, [
          jobId,
          store_id,
          min_utility,
          min_support,
          max_pattern_length,
          use_pruning,
          batch_size
        ], function(err) {
          if (err) reject(err);
          else resolve();
        });
      });

      // Start mining in background
      setImmediate(() => {
        runMiningJob(jobId, store_id, min_utility, min_support);
      });

      res.json({
        job_id: jobId,
        status: 'started'
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get mining job status
router.get('/status/:job_id',
  param('job_id').isUUID().withMessage('Invalid job ID'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { job_id } = req.params;

    try {
      const result = await new Promise((resolve, reject) => {
        db.get(`
          SELECT status, started_at, completed_at, execution_time_seconds, 
                 patterns_found, error_message
          FROM mining_jobs 
          WHERE id = ?
        `, [job_id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      if (!result) {
        throw new NotFoundError('Job not found');
      }

      res.json({
        job_id: job_id,
        status: result.status,
        started_at: result.started_at,
        completed_at: result.completed_at,
        execution_time_seconds: result.execution_time_seconds,
        patterns_found: result.patterns_found,
        error_message: result.error_message
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

// Get mining results
router.get('/results/:job_id',
  param('job_id').isUUID().withMessage('Invalid job ID'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { job_id } = req.params;

    try {
      const patterns = await new Promise((resolve, reject) => {
        db.all(`
          SELECT pattern_items, utility, support, confidence
          FROM local_patterns 
          WHERE mining_job_id = ?
          ORDER BY utility DESC
        `, [job_id], (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      const formattedPatterns = patterns.map(row => ({
        items: JSON.parse(row.pattern_items),
        utility: row.utility,
        support: row.support,
        confidence: row.confidence
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

// Get all mining jobs for a store
router.get('/jobs/:store_id',
  param('store_id').isString().notEmpty().withMessage('Store ID is required'),
  handleValidationErrors,
  async (req, res, next) => {
    const db = getDatabase();
    const { store_id } = req.params;

    try {
      const jobs = await new Promise((resolve, reject) => {
        db.all(`
          SELECT id, status, min_utility, started_at, completed_at, 
                 execution_time_seconds, patterns_found, error_message
          FROM mining_jobs 
          WHERE store_id = ?
          ORDER BY started_at DESC
        `, [store_id], (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      res.json({
        jobs: jobs,
        count: jobs.length
      });

    } catch (error) {
      next(error);
    } finally {
      db.close();
    }
  }
);

export default router;
