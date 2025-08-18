# Database Design and Data Storage Specifications

## 1. Database Architecture

### 1.1 Recommended Database Stack
- **Primary Database**: PostgreSQL 14+ with TimescaleDB extension
- **Caching Layer**: Redis 6+ for session management and real-time data
- **Search Engine**: Elasticsearch 8+ for log analysis and pattern search
- **File Storage**: MinIO or AWS S3 for transaction files and exports
- **Message Queue**: Apache Kafka for federated learning coordination

### 1.2 Database Schema Design

## 2. Core Data Models

### 2.1 User Management Tables

```sql
-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('store_manager', 'regional_coordinator', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true
);

-- Store/Client information
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    manager_id UUID REFERENCES users(id),
    region_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

### 2.2 Transaction Data Tables

```sql
-- Raw transaction files metadata
CREATE TABLE transaction_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('csv', 'json')),
    upload_timestamp TIMESTAMPTZ DEFAULT NOW(),
    processing_status VARCHAR(20) DEFAULT 'pending' 
        CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    s3_bucket VARCHAR(255),
    s3_key VARCHAR(500)
);

-- Processed transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) NOT NULL,
    file_id UUID REFERENCES transaction_files(id),
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    items TEXT[] NOT NULL, -- Array of item names
    quantities DECIMAL[] NOT NULL, -- Array of quantities
    unit_utilities DECIMAL[] NOT NULL, -- Array of unit utilities
    total_utility DECIMAL NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for efficient querying
CREATE INDEX idx_transactions_store_date ON transactions(store_id, transaction_date);
CREATE INDEX idx_transactions_total_utility ON transactions(total_utility);
```

### 2.3 Pattern Mining Tables

```sql
-- Local mining jobs
CREATE TABLE mining_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    min_utility DECIMAL NOT NULL,
    min_support DECIMAL NOT NULL,
    max_pattern_length INTEGER DEFAULT 5,
    use_pruning BOOLEAN DEFAULT true,
    batch_size INTEGER DEFAULT 1000,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    execution_time_seconds DECIMAL,
    memory_used_mb DECIMAL,
    patterns_found INTEGER DEFAULT 0,
    error_message TEXT
);

-- Local patterns discovered by stores
CREATE TABLE local_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mining_job_id UUID REFERENCES mining_jobs(id) NOT NULL,
    store_id UUID REFERENCES stores(id) NOT NULL,
    pattern_items TEXT[] NOT NULL,
    utility DECIMAL NOT NULL,
    support DECIMAL NOT NULL,
    confidence DECIMAL NOT NULL,
    pattern_length INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_local_patterns_store ON local_patterns(store_id);
CREATE INDEX idx_local_patterns_utility ON local_patterns(utility DESC);
```

### 2.4 Privacy Configuration Tables

```sql
-- Privacy settings per store
CREATE TABLE privacy_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) NOT NULL,
    epsilon DECIMAL NOT NULL DEFAULT 1.0,
    noise_type VARCHAR(20) DEFAULT 'laplace' 
        CHECK (noise_type IN ('laplace', 'gaussian')),
    hash_patterns BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Privacy application history
CREATE TABLE privacy_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) NOT NULL,
    pattern_id UUID REFERENCES local_patterns(id) NOT NULL,
    original_utility DECIMAL NOT NULL,
    noisy_utility DECIMAL NOT NULL,
    noise_added DECIMAL NOT NULL,
    epsilon_used DECIMAL NOT NULL,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.5 Federated Learning Tables

```sql
-- Federated learning rounds
CREATE TABLE federated_rounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    min_clients_required INTEGER DEFAULT 2,
    participating_clients INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds DECIMAL,
    patterns_aggregated INTEGER DEFAULT 0,
    global_privacy_budget DECIMAL DEFAULT 1.0
);

-- Client participation in rounds
CREATE TABLE round_participations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID REFERENCES federated_rounds(id) NOT NULL,
    store_id UUID REFERENCES stores(id) NOT NULL,
    patterns_contributed INTEGER NOT NULL,
    contribution_timestamp TIMESTAMPTZ DEFAULT NOW(),
    privacy_epsilon DECIMAL NOT NULL
);

-- Global aggregated patterns
CREATE TABLE global_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID REFERENCES federated_rounds(id) NOT NULL,
    pattern_items TEXT[] NOT NULL,
    aggregated_utility DECIMAL NOT NULL,
    global_support DECIMAL NOT NULL,
    contributing_stores INTEGER NOT NULL,
    client_coverage_percent DECIMAL NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_global_patterns_utility ON global_patterns(aggregated_utility DESC);
CREATE INDEX idx_global_patterns_round ON global_patterns(round_id);
```

### 2.6 System Configuration Tables

```sql
-- Server-wide configuration
CREATE TABLE server_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    data_type VARCHAR(20) NOT NULL CHECK (data_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

-- Insert default configurations
INSERT INTO server_configs (config_key, config_value, data_type, description) VALUES
('min_utility_threshold', '0', 'number', 'Global minimum utility threshold'),
('min_support_threshold', '0', 'number', 'Global minimum support threshold'),
('privacy_budget', '0', 'number', 'Global privacy budget'),
('min_clients_per_round', '0', 'number', 'Minimum clients required per round'),
('max_pattern_length', '0', 'number', 'Maximum pattern length allowed'),
('noise_level', '0', 'number', 'Additional noise level for aggregation');
```

### 2.7 Logging and Audit Tables

```sql
-- System activity logs
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    store_id UUID REFERENCES stores(id),
    action_type VARCHAR(50) NOT NULL,
    action_description TEXT NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    additional_data JSONB
);

-- Create TimescaleDB hypertable for efficient time-series queries
SELECT create_hypertable('activity_logs', 'created_at');

-- Performance metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL NOT NULL,
    store_id UUID REFERENCES stores(id),
    round_id UUID REFERENCES federated_rounds(id),
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

SELECT create_hypertable('performance_metrics', 'recorded_at');
```

## 3. Data Storage and Processing Workflow

### 3.1 Transaction File Upload Process

```
1. Client uploads file → Store in MinIO/S3 with metadata in transaction_files
2. Background job processes file → Parse and validate data
3. Valid transactions → Insert into transactions table
4. Invalid data → Log errors in transaction_files.error_message
5. Update processing_status → 'completed' or 'failed'
```

### 3.2 Pattern Mining Workflow

```
1. User initiates mining → Create mining_jobs record
2. Background worker picks up job → Update status to 'running'
3. Execute mining algorithm → Process transactions from database
4. Store discovered patterns → Insert into local_patterns
5. Update job completion → Set status, execution_time, patterns_found
```

### 3.3 Federated Learning Workflow

```
1. Coordinator starts round → Create federated_rounds record
2. Notify participating stores → Send round invitation
3. Stores contribute patterns → Apply privacy, insert round_participations
4. Server aggregates patterns → Secure multi-party computation
5. Generate global patterns → Insert into global_patterns
6. Complete round → Update federated_rounds status
```

## 4. Data Retention and Archival

### 4.1 Retention Policies
- **Transaction Data**: Keep for 2 years, then archive to cold storage
- **Activity Logs**: Keep for 1 year, then compress and archive
- **Performance Metrics**: Keep detailed data for 6 months, aggregated data for 2 years
- **Global Patterns**: Keep indefinitely with versioning
- **Local Patterns**: Keep for 1 year or until next successful mining

### 4.2 Backup Strategy
- **Daily**: Incremental backups of all transactional data
- **Weekly**: Full database backup with point-in-time recovery
- **Monthly**: Archive old data to separate storage system
- **Disaster Recovery**: Cross-region replication for critical data

## 5. Security Considerations

### 5.1 Data Encryption
- **At Rest**: AES-256 encryption for all sensitive data
- **In Transit**: TLS 1.3 for all communications
- **Application Level**: Additional encryption for pattern data

### 5.2 Access Control
- **Row Level Security**: Stores can only access their own data
- **Column Level**: Sensitive fields encrypted with separate keys
- **API Access**: JWT tokens with role-based permissions

### 5.3 Audit Requirements
- **All Data Access**: Log every read/write operation
- **Pattern Sharing**: Track all federated learning contributions
- **Configuration Changes**: Audit all system configuration updates
- **User Actions**: Complete activity trail for compliance