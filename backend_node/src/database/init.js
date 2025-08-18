/**
 * Database initialization and schema setup for SQLite
 */

import sqlite3 from 'sqlite3';
import { promisify } from 'util';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Database path
const DATABASE_PATH = join(dirname(__dirname), '..', 'hui_system.db');

// Create logs directory if it doesn't exist
const logsDir = join(dirname(__dirname), '..', 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Promisify sqlite3 methods for async/await usage
function createDatabase() {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DATABASE_PATH, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve(db);
      }
    });
  });
}

export async function initDatabase() {
  const db = await createDatabase();
  
  // Promisify database methods
  const dbRun = promisify(db.run.bind(db));
  const dbGet = promisify(db.get.bind(db));
  const dbAll = promisify(db.all.bind(db));

  try {
    // Enable foreign keys
    await dbRun('PRAGMA foreign_keys = ON');

    // Users table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('store_manager', 'regional_coordinator', 'admin')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
      )
    `);

    // Stores table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS stores (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT,
        manager_id TEXT REFERENCES users(id),
        ip_address TEXT,
        connection_status TEXT DEFAULT 'inactive' CHECK (connection_status IN ('active', 'inactive')),
        last_seen TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
      )
    `);

    // Transactions table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        store_id TEXT REFERENCES stores(id),
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        items TEXT NOT NULL,
        quantities TEXT NOT NULL,
        unit_utilities TEXT NOT NULL,
        total_utility REAL NOT NULL
      )
    `);

    // Mining jobs table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS mining_jobs (
        id TEXT PRIMARY KEY,
        store_id TEXT REFERENCES stores(id),
        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
        min_utility REAL NOT NULL,
        min_support REAL DEFAULT 0.1,
        max_pattern_length INTEGER DEFAULT 5,
        use_pruning BOOLEAN DEFAULT 1,
        batch_size INTEGER DEFAULT 1000,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        execution_time_seconds REAL,
        patterns_found INTEGER DEFAULT 0,
        error_message TEXT
      )
    `);

    // Local patterns table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS local_patterns (
        id TEXT PRIMARY KEY,
        mining_job_id TEXT REFERENCES mining_jobs(id),
        store_id TEXT REFERENCES stores(id),
        pattern_items TEXT NOT NULL,
        utility REAL NOT NULL,
        support REAL NOT NULL,
        confidence REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Federated rounds table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS federated_rounds (
        id TEXT PRIMARY KEY,
        round_number INTEGER NOT NULL,
        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
        min_clients_required INTEGER DEFAULT 2,
        participating_clients INTEGER DEFAULT 0,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        patterns_aggregated INTEGER DEFAULT 0
      )
    `);

    // Global patterns table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS global_patterns (
        id TEXT PRIMARY KEY,
        round_id TEXT REFERENCES federated_rounds(id),
        pattern_items TEXT NOT NULL,
        aggregated_utility REAL NOT NULL,
        global_support REAL NOT NULL,
        contributing_stores INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Insert default test data
    await dbRun(`
      INSERT OR IGNORE INTO users (id, email, password_hash, role) 
      VALUES ('user1', 'store1@example.com', 'hashed_password', 'store_manager')
    `);

    await dbRun(`
      INSERT OR IGNORE INTO users (id, email, password_hash, role) 
      VALUES ('user2', 'coordinator@example.com', 'hashed_password', 'regional_coordinator')
    `);

    await dbRun(`
      INSERT OR IGNORE INTO stores (id, name, location, manager_id) 
      VALUES ('store1', 'Downtown Store', 'New York, NY', 'user1')
    `);

    console.log('Database initialized successfully');
    
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  } finally {
    db.close();
  }
}

export function getDatabase() {
  return new sqlite3.Database(DATABASE_PATH);
}

export { DATABASE_PATH };
