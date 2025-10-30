# Session Tracking - Data Architecture & Technical Design

**Date:** October 30, 2025  
**Author:** Jay Persanchez  
**Status:** Technical Design - For Review  
**Purpose:** Database schema, data flows, storage strategy, and performance optimization for session/navigation tracking

---

## Executive Summary

This document provides the **technical data architecture** for implementing session and navigation tracking in ChemLink. It covers:
- Database schema design
- Data retention & archival strategy
- Performance optimization (indexes, partitioning)
- Data warehouse integration
- Privacy & compliance (GDPR/CCPA)
- Query patterns & aggregation strategy

---

## Table of Contents

1. [Database Schema Design](#1-database-schema-design)
2. [Data Storage Strategy](#2-data-storage-strategy)
3. [Performance Optimization](#3-performance-optimization)
4. [Data Retention & Archival](#4-data-retention--archival)
5. [Analytics Query Patterns](#5-analytics-query-patterns)
6. [Data Warehouse Integration](#6-data-warehouse-integration)
7. [Privacy & Compliance](#7-privacy--compliance)
8. [Monitoring & Observability](#8-monitoring--observability)

---

## 1. Database Schema Design

### 1.1 Core Tables

#### **`user_sessions` - Session Lifecycle**

```sql
CREATE TABLE user_sessions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- User Identity
    person_id BIGINT NOT NULL,
    session_key VARCHAR(64) UNIQUE NOT NULL,  -- Client-side session identifier
    
    -- Timestamps
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,  -- NULL = still active
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Computed Duration (auto-calculated)
    duration_seconds INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (COALESCE(ended_at, last_activity_at) - started_at))
    ) STORED,
    
    -- Technical Metadata
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(20) CHECK (device_type IN ('desktop', 'mobile', 'tablet', 'unknown')),
    browser VARCHAR(50),
    browser_version VARCHAR(20),
    os VARCHAR(50),
    os_version VARCHAR(20),
    screen_resolution VARCHAR(20),  -- e.g., "1920x1080"
    timezone VARCHAR(50),  -- IANA timezone (e.g., "America/New_York")
    
    -- Session Attributes
    is_active BOOLEAN DEFAULT true,
    is_authenticated BOOLEAN DEFAULT true,
    referrer_domain VARCHAR(255),  -- External referrer if applicable
    utm_source VARCHAR(100),  -- Marketing attribution
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key (deferred for flexibility)
    CONSTRAINT fk_person FOREIGN KEY (person_id) 
        REFERENCES persons(id) ON DELETE CASCADE,
    
    -- Indexes (see section 3)
    CONSTRAINT chk_duration CHECK (duration_seconds >= 0)
);

-- Composite index for common query patterns
CREATE INDEX idx_sessions_person_started ON user_sessions (person_id, started_at DESC);
CREATE INDEX idx_sessions_active ON user_sessions (is_active, last_activity_at DESC) WHERE is_active = true;
CREATE INDEX idx_sessions_date ON user_sessions (DATE(started_at), device_type);
CREATE INDEX idx_sessions_duration ON user_sessions (duration_seconds) WHERE duration_seconds IS NOT NULL;

-- GIN index for marketing attribution queries
CREATE INDEX idx_sessions_utm ON user_sessions USING gin ((
    jsonb_build_object(
        'source', utm_source, 
        'medium', utm_medium, 
        'campaign', utm_campaign
    )
));

-- Trigger to auto-update updated_at
CREATE TRIGGER update_sessions_timestamp
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
```

**Design Rationale:**
- `session_key`: UUID from client for idempotency
- `duration_seconds`: Computed column for fast aggregations
- `device_type`: Enables segmentation by platform
- `utm_*` fields: Marketing attribution tracking
- `is_active` boolean: Fast filtering of current sessions

---

#### **`page_views` - Page Navigation Tracking**

```sql
CREATE TABLE page_views (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    session_id UUID NOT NULL,
    person_id BIGINT NOT NULL,
    
    -- Page Metadata
    page_url VARCHAR(1000) NOT NULL,  -- Full URL path (no domain)
    page_title VARCHAR(500),
    page_category VARCHAR(100),  -- e.g., "Profile", "Finder", "Collections"
    referrer VARCHAR(1000),  -- Previous page (internal navigation)
    external_referrer VARCHAR(500),  -- External source if applicable
    query_params JSONB,  -- URL parameters as JSON
    
    -- Timing
    viewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exited_at TIMESTAMP,  -- NULL = user still on page
    time_on_page_seconds INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (exited_at - viewed_at))
    ) STORED,
    
    -- Engagement Metrics
    scroll_depth_percent INTEGER CHECK (scroll_depth_percent BETWEEN 0 AND 100),
    clicks_count INTEGER DEFAULT 0,
    interactions_count INTEGER DEFAULT 0,  -- Forms, buttons, etc.
    
    -- Page Performance
    page_load_time_ms INTEGER,  -- Client-side page load time
    time_to_interactive_ms INTEGER,  -- Performance metric
    
    -- Sequence Tracking
    page_sequence_number INTEGER NOT NULL,  -- Order within session (1, 2, 3...)
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    CONSTRAINT fk_session FOREIGN KEY (session_id) 
        REFERENCES user_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_person FOREIGN KEY (person_id) 
        REFERENCES persons(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_time_on_page CHECK (time_on_page_seconds >= 0 OR time_on_page_seconds IS NULL),
    CONSTRAINT chk_sequence CHECK (page_sequence_number > 0)
);

-- Indexes for common queries
CREATE INDEX idx_pageviews_session ON page_views (session_id, page_sequence_number);
CREATE INDEX idx_pageviews_person_date ON page_views (person_id, DATE(viewed_at) DESC);
CREATE INDEX idx_pageviews_url ON page_views (page_url, viewed_at DESC);
CREATE INDEX idx_pageviews_category ON page_views (page_category, viewed_at DESC);

-- GIN index for query parameter searches
CREATE INDEX idx_pageviews_params ON page_views USING gin (query_params);

-- Index for engagement analysis
CREATE INDEX idx_pageviews_engagement ON page_views (
    viewed_at DESC, 
    time_on_page_seconds, 
    scroll_depth_percent
) WHERE time_on_page_seconds IS NOT NULL;
```

**Design Rationale:**
- `page_sequence_number`: Enables navigation path analysis
- `page_category`: Groups pages for aggregation (e.g., all profile pages)
- `query_params` as JSONB: Flexible parameter tracking without schema changes
- `time_on_page_seconds`: Computed column for fast analytics
- Separate `external_referrer`: Tracks acquisition sources

---

#### **`user_events` - Granular Interaction Tracking**

```sql
CREATE TABLE user_events (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    session_id UUID NOT NULL,
    person_id BIGINT NOT NULL,
    page_view_id UUID,  -- Optional: which page the event occurred on
    
    -- Event Classification
    event_type VARCHAR(50) NOT NULL,  -- click, search, form_submit, scroll, hover, etc.
    event_category VARCHAR(50),  -- Feature: Finder, Collections, Profile, etc.
    event_action VARCHAR(100),  -- Action: Search, Create, Update, Delete, View
    event_label VARCHAR(255),  -- Specific identifier (e.g., button name, search query)
    event_value NUMERIC(10, 2),  -- Optional numeric value (e.g., search result count)
    
    -- Element Identification
    element_id VARCHAR(100),  -- DOM element ID
    element_class VARCHAR(255),  -- CSS classes
    element_text VARCHAR(500),  -- Button/link text
    element_selector VARCHAR(500),  -- Full CSS selector path
    
    -- Position Context
    viewport_position JSONB,  -- {x: 100, y: 200} - click position
    scroll_position INTEGER,  -- Vertical scroll at time of event
    
    -- Additional Context
    metadata JSONB,  -- Flexible field for event-specific data
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    CONSTRAINT fk_session FOREIGN KEY (session_id) 
        REFERENCES user_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_person FOREIGN KEY (person_id) 
        REFERENCES persons(id) ON DELETE CASCADE,
    CONSTRAINT fk_pageview FOREIGN KEY (page_view_id) 
        REFERENCES page_views(id) ON DELETE SET NULL
);

-- Indexes optimized for event analytics
CREATE INDEX idx_events_session ON user_events (session_id, created_at);
CREATE INDEX idx_events_person_date ON user_events (person_id, DATE(created_at) DESC);
CREATE INDEX idx_events_type_date ON user_events (event_type, created_at DESC);
CREATE INDEX idx_events_category_action ON user_events (event_category, event_action, created_at DESC);

-- GIN indexes for flexible searching
CREATE INDEX idx_events_metadata ON user_events USING gin (metadata);
CREATE INDEX idx_events_viewport ON user_events USING gin (viewport_position);

-- Partial index for high-value events
CREATE INDEX idx_events_high_value ON user_events (created_at DESC, event_value) 
    WHERE event_value > 0;
```

**Design Rationale:**
- Flexible event taxonomy: `type` → `category` → `action` → `label`
- `metadata` JSONB: Store arbitrary event-specific data
- `viewport_position`: Enables heatmap analysis
- `element_selector`: Reconstruct exact element clicked
- Partial indexes: Optimize for common query patterns

---

### 1.2 Materialized Views for Analytics

#### **`session_metrics_daily` - Pre-aggregated Session Stats**

```sql
CREATE MATERIALIZED VIEW session_metrics_daily AS
SELECT 
    DATE(us.started_at) as date,
    us.device_type,
    us.browser,
    
    -- Volume Metrics
    COUNT(*) as total_sessions,
    COUNT(DISTINCT us.person_id) as unique_users,
    COUNT(*) FILTER (WHERE us.duration_seconds < 30) as bounce_sessions,
    COUNT(*) FILTER (WHERE us.duration_seconds >= 600) as engaged_sessions, -- 10+ min
    
    -- Duration Metrics
    AVG(us.duration_seconds) as avg_duration_seconds,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY us.duration_seconds) as median_duration_seconds,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY us.duration_seconds) as p90_duration_seconds,
    MIN(us.duration_seconds) as min_duration_seconds,
    MAX(us.duration_seconds) as max_duration_seconds,
    
    -- Page View Metrics
    AVG(pv_stats.page_views_per_session) as avg_pages_per_session,
    AVG(pv_stats.avg_time_per_page) as avg_time_per_page_seconds,
    
    -- Engagement Metrics
    COUNT(*) FILTER (WHERE pv_stats.page_views_per_session >= 3) as multi_page_sessions,
    AVG(event_stats.events_per_session) as avg_events_per_session,
    
    -- Bounce Rate
    ROUND(
        COUNT(*) FILTER (WHERE us.duration_seconds < 30)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as bounce_rate_percent

FROM user_sessions us

-- Join page view aggregates
LEFT JOIN (
    SELECT 
        session_id,
        COUNT(*) as page_views_per_session,
        AVG(time_on_page_seconds) as avg_time_per_page
    FROM page_views
    WHERE time_on_page_seconds IS NOT NULL
    GROUP BY session_id
) pv_stats ON us.id = pv_stats.session_id

-- Join event aggregates
LEFT JOIN (
    SELECT 
        session_id,
        COUNT(*) as events_per_session
    FROM user_events
    GROUP BY session_id
) event_stats ON us.id = event_stats.session_id

WHERE us.started_at >= CURRENT_DATE - INTERVAL '90 days'
  AND us.ended_at IS NOT NULL  -- Only completed sessions

GROUP BY DATE(us.started_at), us.device_type, us.browser;

-- Indexes on materialized view
CREATE UNIQUE INDEX idx_session_metrics_date_device ON session_metrics_daily (date DESC, device_type, browser);
CREATE INDEX idx_session_metrics_date ON session_metrics_daily (date DESC);

-- Refresh schedule (daily at 1 AM)
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule(
    'refresh-session-metrics',
    '0 1 * * *',  -- Every day at 1 AM
    $$REFRESH MATERIALIZED VIEW CONCURRENTLY session_metrics_daily$$
);
```

**Benefits:**
- Sub-second query times for dashboard
- Pre-calculated percentiles (expensive operation)
- Reduces load on production tables
- Concurrent refresh doesn't block reads

---

#### **`page_metrics_hourly` - Real-time Page Performance**

```sql
CREATE MATERIALIZED VIEW page_metrics_hourly AS
SELECT 
    DATE_TRUNC('hour', pv.viewed_at) as hour,
    pv.page_category,
    pv.page_url,
    
    -- Volume
    COUNT(*) as total_views,
    COUNT(DISTINCT pv.person_id) as unique_viewers,
    COUNT(DISTINCT pv.session_id) as unique_sessions,
    
    -- Engagement
    AVG(pv.time_on_page_seconds) as avg_time_on_page_seconds,
    AVG(pv.scroll_depth_percent) as avg_scroll_depth_percent,
    AVG(pv.clicks_count) as avg_clicks_per_view,
    
    -- Performance
    AVG(pv.page_load_time_ms) as avg_load_time_ms,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY pv.page_load_time_ms) as p90_load_time_ms,
    
    -- Entry/Exit
    COUNT(*) FILTER (WHERE pv.page_sequence_number = 1) as entry_count,
    COUNT(*) FILTER (WHERE is_exit_page) as exit_count,
    
    -- Bounce Rate (single page sessions)
    ROUND(
        COUNT(*) FILTER (WHERE is_bounce_page)::NUMERIC / 
        NULLIF(COUNT(*) FILTER (WHERE pv.page_sequence_number = 1), 0) * 100,
        2
    ) as bounce_rate_percent

FROM page_views pv

-- Identify exit pages
LEFT JOIN LATERAL (
    SELECT NOT EXISTS (
        SELECT 1 FROM page_views pv2 
        WHERE pv2.session_id = pv.session_id 
        AND pv2.page_sequence_number > pv.page_sequence_number
    ) as is_exit_page
) exit_check ON true

-- Identify bounce pages (single page session)
LEFT JOIN LATERAL (
    SELECT pv.page_sequence_number = 1 AND NOT EXISTS (
        SELECT 1 FROM page_views pv2 
        WHERE pv2.session_id = pv.session_id 
        AND pv2.page_sequence_number > 1
    ) as is_bounce_page
) bounce_check ON true

WHERE pv.viewed_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'

GROUP BY DATE_TRUNC('hour', pv.viewed_at), pv.page_category, pv.page_url;

-- Indexes
CREATE INDEX idx_page_metrics_hour ON page_metrics_hourly (hour DESC, page_category);
CREATE INDEX idx_page_metrics_url ON page_metrics_hourly (page_url, hour DESC);

-- Refresh every hour
SELECT cron.schedule(
    'refresh-page-metrics',
    '0 * * * *',  -- Every hour at :00
    $$REFRESH MATERIALIZED VIEW CONCURRENTLY page_metrics_hourly$$
);
```

---

### 1.3 Supporting Tables

#### **`session_attribution` - Marketing Attribution**

```sql
CREATE TABLE session_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL UNIQUE,
    person_id BIGINT NOT NULL,
    
    -- Attribution Data
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    utm_term VARCHAR(100),
    utm_content VARCHAR(100),
    
    -- Referrer Analysis
    referrer_domain VARCHAR(255),
    referrer_url VARCHAR(1000),
    referrer_category VARCHAR(50),  -- social, search, direct, email, etc.
    
    -- Channel Classification
    channel_type VARCHAR(50),  -- organic, paid, direct, social, email, referral
    channel_subtype VARCHAR(50),
    
    -- Landing Page
    landing_page_url VARCHAR(1000),
    landing_page_category VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_session FOREIGN KEY (session_id) 
        REFERENCES user_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_person FOREIGN KEY (person_id) 
        REFERENCES persons(id) ON DELETE CASCADE
);

CREATE INDEX idx_attribution_source ON session_attribution (utm_source, utm_campaign, created_at DESC);
CREATE INDEX idx_attribution_channel ON session_attribution (channel_type, created_at DESC);
CREATE INDEX idx_attribution_person ON session_attribution (person_id, created_at DESC);
```

---

#### **`user_journey_paths` - Common Navigation Sequences**

```sql
-- Stores aggregated navigation patterns for fast retrieval
CREATE TABLE user_journey_paths (
    id SERIAL PRIMARY KEY,
    
    -- Path Definition
    path_sequence TEXT[],  -- Array of page URLs in order
    path_length INTEGER,
    
    -- Metrics
    session_count INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    avg_time_seconds NUMERIC(10, 2),
    conversion_rate NUMERIC(5, 2),  -- % who reached goal
    
    -- Segmentation
    device_type VARCHAR(20),
    date_range_start DATE,
    date_range_end DATE,
    
    -- Timestamps
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_path_length CHECK (path_length = array_length(path_sequence, 1))
);

CREATE INDEX idx_journey_paths_sequence ON user_journey_paths USING gin (path_sequence);
CREATE INDEX idx_journey_paths_metrics ON user_journey_paths (session_count DESC, date_range_end DESC);
```

---

## 2. Data Storage Strategy

### 2.1 Database Selection

**Primary Storage: PostgreSQL**

| Aspect | Rationale |
|--------|-----------|
| **ACID Compliance** | Ensures data integrity for financial/sensitive data |
| **JSONB Support** | Flexible metadata storage without schema changes |
| **Partitioning** | Time-based partitioning for scalability |
| **Materialized Views** | Pre-aggregated analytics queries |
| **Window Functions** | Complex session analysis (LAG, LEAD, ROW_NUMBER) |
| **GIN Indexes** | Fast JSONB and array searches |
| **pg_cron Extension** | Built-in scheduled aggregations |

**Alternative: TimescaleDB**
- If session volume >10M/day, migrate to TimescaleDB (PostgreSQL extension)
- Automatic time-based partitioning
- Better compression for historical data
- Continuous aggregates (real-time rollups)

---

### 2.2 Table Partitioning Strategy

**Partition by Month (Recommended)**

```sql
-- Parent table (partitioned)
CREATE TABLE user_sessions (
    -- ... all columns as defined above
) PARTITION BY RANGE (started_at);

-- Monthly partitions
CREATE TABLE user_sessions_2025_10 PARTITION OF user_sessions
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE user_sessions_2025_11 PARTITION OF user_sessions
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- Auto-create next month's partition (trigger)
CREATE OR REPLACE FUNCTION create_next_month_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_name TEXT := 'user_sessions_' || TO_CHAR(partition_date, 'YYYY_MM');
    partition_start TEXT := TO_CHAR(partition_date, 'YYYY-MM-DD');
    partition_end TEXT := TO_CHAR(partition_date + INTERVAL '1 month', 'YYYY-MM-DD');
BEGIN
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF user_sessions 
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, partition_start, partition_end
    );
END;
$$ LANGUAGE plpgsql;

-- Schedule partition creation
SELECT cron.schedule(
    'create-monthly-partition',
    '0 0 1 * *',  -- 1st day of each month at midnight
    $$SELECT create_next_month_partition()$$
);
```

**Benefits:**
- Fast queries (partition pruning)
- Easy data archival (drop old partitions)
- Parallel operations on partitions
- Reduced index size per partition

---

### 2.3 Data Distribution (if Sharding Required)

**Sharding Strategy: By User ID**

```sql
-- Shard 1: person_id % 4 = 0
-- Shard 2: person_id % 4 = 1
-- Shard 3: person_id % 4 = 2
-- Shard 4: person_id % 4 = 3

-- Use Citus or pg_partman for automatic distribution
```

**Rationale:**
- All sessions for a user in same shard (co-location)
- Avoids cross-shard joins for user analytics
- Scales horizontally to billions of sessions

---

## 3. Performance Optimization

### 3.1 Index Strategy

**Rule of Thumb:**
- Index columns in `WHERE`, `JOIN`, `ORDER BY`, `GROUP BY`
- Keep indexes lean (<10 per table for write-heavy tables)
- Use partial indexes for filtered queries
- Monitor index usage with `pg_stat_user_indexes`

**Monitoring Query:**
```sql
-- Find unused indexes (candidates for removal)
SELECT 
    schemaname, tablename, indexname, idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

### 3.2 Query Optimization Patterns

#### **Pattern 1: Session Duration Analysis**

```sql
-- ❌ SLOW: Window function on full table
SELECT 
    person_id,
    AVG(duration_seconds) OVER (PARTITION BY person_id)
FROM user_sessions
WHERE started_at >= '2025-01-01';

-- ✅ FAST: Use materialized view
SELECT 
    person_id,
    avg_duration_seconds
FROM (
    SELECT 
        person_id,
        AVG(duration_seconds) as avg_duration_seconds
    FROM user_sessions
    WHERE started_at >= '2025-01-01'
    GROUP BY person_id
) sub;
```

#### **Pattern 2: Navigation Path Analysis**

```sql
-- ❌ SLOW: Self-join for sequences
SELECT 
    pv1.page_url as from_page,
    pv2.page_url as to_page,
    COUNT(*) as transitions
FROM page_views pv1
JOIN page_views pv2 ON pv1.session_id = pv2.session_id 
    AND pv2.page_sequence_number = pv1.page_sequence_number + 1
GROUP BY pv1.page_url, pv2.page_url;

-- ✅ FAST: Window function with filter
SELECT 
    page_url as from_page,
    next_page as to_page,
    COUNT(*) as transitions
FROM (
    SELECT 
        page_url,
        LEAD(page_url) OVER (PARTITION BY session_id ORDER BY page_sequence_number) as next_page
    FROM page_views
    WHERE viewed_at >= CURRENT_DATE - INTERVAL '7 days'
) paths
WHERE next_page IS NOT NULL
GROUP BY page_url, next_page
ORDER BY transitions DESC
LIMIT 100;
```

---

### 3.3 Write Optimization

**Batch Inserts** (High Volume Environments)

```python
# ❌ SLOW: Individual inserts
for event in events:
    cursor.execute("INSERT INTO user_events (...) VALUES (...)", event)
    
# ✅ FAST: Bulk insert
psycopg2.extras.execute_batch(
    cursor,
    "INSERT INTO user_events (...) VALUES (...)",
    events,
    page_size=1000
)

# ✅ FASTEST: COPY command
with cursor.copy("COPY user_events (...) FROM STDIN") as copy:
    for event in events:
        copy.write_row(event)
```

**Write Buffer** (If >1000 writes/sec)

```python
# Use Redis as write buffer, flush to DB every 5 seconds
redis_client.lpush('event_queue', json.dumps(event_data))

# Background worker (async)
while True:
    events = redis_client.lrange('event_queue', 0, 999)
    if events:
        bulk_insert_to_db(events)
        redis_client.ltrim('event_queue', len(events), -1)
    time.sleep(5)
```

---

## 4. Data Retention & Archival

### 4.1 Retention Policy

| Data Type | Hot Storage | Warm Storage | Cold Storage | Deletion |
|-----------|-------------|--------------|--------------|----------|
| **Sessions** | 90 days | 1 year | 3 years | After 3 years |
| **Page Views** | 90 days | 6 months | 2 years | After 2 years |
| **Events** | 30 days | 3 months | 1 year | After 1 year |
| **Aggregates** | Permanent | - | - | Never (compressed) |

---

### 4.2 Archival Strategy

**Step 1: Move to Warm Storage (Compression)**

```sql
-- Compress old partitions (PostgreSQL 14+)
ALTER TABLE user_sessions_2024_01 SET (
    fillfactor = 100,
    autovacuum_enabled = false
);
VACUUM FULL user_sessions_2024_01;

-- Or use TimescaleDB compression
ALTER TABLE user_sessions SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'person_id',
    timescaledb.compress_orderby = 'started_at DESC'
);

SELECT compress_chunk(chunk_name)
FROM timescaledb_information.chunks
WHERE range_end < CURRENT_DATE - INTERVAL '90 days';
```

**Step 2: Export to S3/Data Lake**

```bash
# Export monthly partition to S3
pg_dump -h localhost -U user -d database \
    --table=user_sessions_2024_01 \
    --format=custom \
    | gzip \
    | aws s3 cp - s3://chemlink-analytics-archive/sessions/2024-01.dump.gz

# Store in Parquet format (better for analytics)
psql -c "COPY (SELECT * FROM user_sessions_2024_01) TO STDOUT WITH CSV" \
    | python convert_to_parquet.py \
    | aws s3 cp - s3://chemlink-analytics-archive/sessions/2024-01.parquet
```

**Step 3: Drop Old Partitions**

```sql
-- Archive script (run monthly via cron)
DO $$
DECLARE
    partition_name TEXT;
BEGIN
    -- Find partitions older than 3 years
    FOR partition_name IN
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE 'user_sessions_20%'
        AND tablename < 'user_sessions_' || TO_CHAR(CURRENT_DATE - INTERVAL '3 years', 'YYYY_MM')
    LOOP
        -- Verify backup exists before dropping
        IF EXISTS (SELECT 1 FROM archived_partitions WHERE partition = partition_name) THEN
            EXECUTE format('DROP TABLE %I', partition_name);
            RAISE NOTICE 'Dropped partition: %', partition_name;
        END IF;
    END LOOP;
END $$;
```

---

## 5. Analytics Query Patterns

### 5.1 Common Query Patterns

#### **Dashboard: Session Duration Over Time**

```sql
-- Optimized for dashboard rendering
SELECT 
    date,
    device_type,
    total_sessions,
    unique_users,
    avg_duration_seconds / 60.0 as avg_duration_minutes,
    bounce_rate_percent
FROM session_metrics_daily
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC, device_type;

-- Execution time: <50ms (materialized view)
```

#### **Dashboard: Top Pages by Engagement**

```sql
-- Top 20 pages by time spent
SELECT 
    page_category,
    page_url,
    SUM(total_views) as total_views,
    SUM(unique_viewers) as unique_viewers,
    AVG(avg_time_on_page_seconds) as avg_time_seconds,
    AVG(avg_scroll_depth_percent) as avg_scroll_depth,
    AVG(bounce_rate_percent) as bounce_rate
FROM page_metrics_hourly
WHERE hour >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY page_category, page_url
ORDER BY AVG(avg_time_on_page_seconds) DESC
LIMIT 20;

-- Execution time: <100ms
```

#### **Advanced: Cohort Retention Analysis**

```sql
-- User retention by signup cohort
WITH cohorts AS (
    SELECT 
        person_id,
        DATE_TRUNC('month', created_at) as cohort_month
    FROM persons
),
activity AS (
    SELECT DISTINCT
        person_id,
        DATE_TRUNC('month', started_at) as activity_month
    FROM user_sessions
    WHERE started_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
)
SELECT 
    c.cohort_month,
    DATE_PART('month', AGE(a.activity_month, c.cohort_month)) as months_since_signup,
    COUNT(DISTINCT a.person_id) as active_users,
    COUNT(DISTINCT a.person_id)::FLOAT / COUNT(DISTINCT c.person_id) * 100 as retention_pct
FROM cohorts c
LEFT JOIN activity a ON c.person_id = a.person_id
WHERE c.cohort_month >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
GROUP BY c.cohort_month, months_since_signup
ORDER BY c.cohort_month, months_since_signup;
```

---

### 5.2 Query Performance Benchmarks

| Query Type | Target | Max Acceptable |
|------------|--------|----------------|
| Dashboard load (all charts) | <500ms | 2s |
| Single metric (DAU, MAU) | <50ms | 200ms |
| Top N pages | <100ms | 500ms |
| User journey paths | <200ms | 1s |
| Complex cohort analysis | <2s | 10s |
| Ad-hoc exploration | <5s | 30s |

**Monitoring:**
```sql
-- Track slow queries
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slowest queries
SELECT 
    query,
    calls,
    total_exec_time / 1000.0 as total_seconds,
    mean_exec_time / 1000.0 as avg_seconds,
    max_exec_time / 1000.0 as max_seconds
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- >100ms average
ORDER BY mean_exec_time DESC
LIMIT 20;
```

---

## 6. Data Warehouse Integration

### 6.1 ETL Pipeline Architecture

```
┌──────────────────────────────────────────────────────────┐
│               Production PostgreSQL                      │
│  • user_sessions (hot data, 90 days)                   │
│  • page_views                                           │
│  • user_events                                          │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼ (nightly ETL via Airflow/dbt)
┌──────────────────────────────────────────────────────────┐
│              Data Warehouse (Snowflake/Redshift)         │
│  • fact_sessions (all historical data)                  │
│  • fact_page_views                                      │
│  • dim_pages (page metadata)                            │
│  • dim_devices (device/browser taxonomy)                │
│  • agg_session_metrics_daily (pre-rolled up)           │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼ (BI tools query)
┌──────────────────────────────────────────────────────────┐
│           BI Layer (Tableau/Looker/Metabase)             │
│  • Executive dashboards                                  │
│  • Ad-hoc analysis                                       │
│  • Data science notebooks                                │
└──────────────────────────────────────────────────────────┘
```

---

### 6.2 Dimensional Model (Star Schema)

```sql
-- Fact Table: Session Facts
CREATE TABLE fact_sessions (
    session_id UUID PRIMARY KEY,
    person_id BIGINT NOT NULL,
    
    -- Dimensions (foreign keys)
    date_id INTEGER NOT NULL,          -- → dim_date
    device_id INTEGER NOT NULL,        -- → dim_devices
    channel_id INTEGER NOT NULL,       -- → dim_channels
    
    -- Measures
    duration_seconds INTEGER,
    page_views_count INTEGER,
    events_count INTEGER,
    is_bounce BOOLEAN,
    is_conversion BOOLEAN,
    
    -- Timestamps
    started_at TIMESTAMP,
    ended_at TIMESTAMP
)
PARTITION BY RANGE (date_id);

-- Dimension: Date (pre-computed)
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,       -- YYYYMMDD format
    date DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    week INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Dimension: Devices
CREATE TABLE dim_devices (
    device_id SERIAL PRIMARY KEY,
    device_type VARCHAR(20),
    browser VARCHAR(50),
    browser_version VARCHAR(20),
    os VARCHAR(50),
    os_version VARCHAR(20)
);

-- Dimension: Channels (Marketing Attribution)
CREATE TABLE dim_channels (
    channel_id SERIAL PRIMARY KEY,
    channel_type VARCHAR(50),
    channel_subtype VARCHAR(50),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100)
);
```

---

### 6.3 ETL Job (dbt Example)

```sql
-- models/fact_sessions.sql
{{ config(
    materialized='incremental',
    unique_key='session_id',
    partition_by={
        'field': 'date_id',
        'data_type': 'int64',
        'granularity': 'day'
    }
) }}

SELECT 
    us.id as session_id,
    us.person_id,
    
    -- Dimension lookups
    TO_NUMBER(TO_CHAR(us.started_at, 'YYYYMMDD'), '99999999') as date_id,
    COALESCE(dd.device_id, 0) as device_id,
    COALESCE(dc.channel_id, 0) as channel_id,
    
    -- Measures
    us.duration_seconds,
    pv_agg.page_views_count,
    ev_agg.events_count,
    (us.duration_seconds < 30) as is_bounce,
    (ev_agg.conversion_events > 0) as is_conversion,
    
    us.started_at,
    us.ended_at

FROM {{ source('prod', 'user_sessions') }} us

LEFT JOIN {{ ref('dim_devices') }} dd 
    ON us.device_type = dd.device_type 
    AND us.browser = dd.browser

LEFT JOIN {{ ref('dim_channels') }} dc 
    ON us.utm_source = dc.utm_source 
    AND us.utm_campaign = dc.utm_campaign

LEFT JOIN (
    SELECT session_id, COUNT(*) as page_views_count
    FROM {{ source('prod', 'page_views') }}
    GROUP BY session_id
) pv_agg ON us.id = pv_agg.session_id

LEFT JOIN (
    SELECT 
        session_id, 
        COUNT(*) as events_count,
        COUNT(*) FILTER (WHERE event_category = 'Conversion') as conversion_events
    FROM {{ source('prod', 'user_events') }}
    GROUP BY session_id
) ev_agg ON us.id = ev_agg.session_id

WHERE us.ended_at IS NOT NULL

{% if is_incremental() %}
    AND us.started_at >= (SELECT MAX(started_at) FROM {{ this }})
{% endif %}
```

---

## 7. Privacy & Compliance

### 7.1 GDPR/CCPA Requirements

**Data Subject Rights:**

```sql
-- Right to Access: Export all user data
CREATE FUNCTION export_user_data(user_person_id BIGINT)
RETURNS TABLE (
    data_type TEXT,
    data_json JSONB
) AS $$
BEGIN
    -- Sessions
    RETURN QUERY
    SELECT 
        'sessions'::TEXT,
        jsonb_agg(to_jsonb(us.*))
    FROM user_sessions us
    WHERE us.person_id = user_person_id;
    
    -- Page Views
    RETURN QUERY
    SELECT 
        'page_views'::TEXT,
        jsonb_agg(to_jsonb(pv.*))
    FROM page_views pv
    WHERE pv.person_id = user_person_id;
    
    -- Events
    RETURN QUERY
    SELECT 
        'events'::TEXT,
        jsonb_agg(to_jsonb(ue.*))
    FROM user_events ue
    WHERE ue.person_id = user_person_id;
END;
$$ LANGUAGE plpgsql;

-- Right to Erasure (Delete)
CREATE FUNCTION delete_user_data(user_person_id BIGINT)
RETURNS VOID AS $$
BEGIN
    -- Cascade deletes due to FK constraints
    DELETE FROM user_sessions WHERE person_id = user_person_id;
    
    -- Log deletion for audit
    INSERT INTO data_deletion_log (person_id, deleted_at, deleted_by)
    VALUES (user_person_id, CURRENT_TIMESTAMP, current_user);
END;
$$ LANGUAGE plpgsql;

-- Right to Anonymize (Alternative to deletion)
CREATE FUNCTION anonymize_user_data(user_person_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE user_sessions 
    SET ip_address = NULL,
        user_agent = 'ANONYMIZED',
        person_id = 0  -- Pseudo-ID
    WHERE person_id = user_person_id;
    
    UPDATE page_views 
    SET person_id = 0
    WHERE person_id = user_person_id;
    
    UPDATE user_events 
    SET person_id = 0,
        metadata = NULL
    WHERE person_id = user_person_id;
END;
$$ LANGUAGE plpgsql;
```

---

### 7.2 PII Handling

**Strategy: Minimize PII Collection**

```sql
-- ✅ GOOD: Hash IP addresses
CREATE OR REPLACE FUNCTION hash_ip(ip INET)
RETURNS TEXT AS $$
    SELECT encode(digest(host(ip)::text || 'SALT_STRING', 'sha256'), 'hex')
$$ LANGUAGE SQL IMMUTABLE;

-- Store hashed IP
INSERT INTO user_sessions (ip_address, ...)
VALUES (hash_ip('192.168.1.1'::INET), ...);

-- ❌ BAD: Store raw IP addresses
-- Violates GDPR minimization principle
```

**Encryption at Rest:**
```sql
-- Enable pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive fields
ALTER TABLE user_sessions 
ADD COLUMN ip_address_encrypted BYTEA;

-- Insert with encryption
INSERT INTO user_sessions (ip_address_encrypted, ...)
VALUES (pgp_sym_encrypt('192.168.1.1', 'encryption_key'), ...);

-- Query with decryption
SELECT 
    pgp_sym_decrypt(ip_address_encrypted, 'encryption_key') as ip_address
FROM user_sessions;
```

---

### 7.3 Consent Management

```sql
CREATE TABLE user_consent (
    person_id BIGINT PRIMARY KEY,
    analytics_consent BOOLEAN DEFAULT false,
    analytics_consent_date TIMESTAMP,
    marketing_consent BOOLEAN DEFAULT false,
    marketing_consent_date TIMESTAMP,
    consent_version INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_person FOREIGN KEY (person_id) 
        REFERENCES persons(id) ON DELETE CASCADE
);

-- Only track users with consent
CREATE POLICY analytics_consent_policy ON user_sessions
    FOR SELECT
    USING (
        person_id IN (
            SELECT person_id FROM user_consent 
            WHERE analytics_consent = true
        )
    );

-- Enable row-level security
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
```

---

## 8. Monitoring & Observability

### 8.1 Data Quality Monitoring

```sql
-- Automated data quality checks (run hourly)
CREATE TABLE data_quality_checks (
    id SERIAL PRIMARY KEY,
    check_name VARCHAR(100),
    check_type VARCHAR(50),  -- completeness, validity, consistency
    table_name VARCHAR(100),
    status VARCHAR(20),  -- pass, warn, fail
    message TEXT,
    metric_value NUMERIC,
    threshold NUMERIC,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example: Check for session duration anomalies
INSERT INTO data_quality_checks (check_name, check_type, table_name, status, message, metric_value, threshold)
SELECT 
    'session_duration_p99',
    'validity',
    'user_sessions',
    CASE 
        WHEN p99_duration > 86400 THEN 'warn'  -- >24 hours
        WHEN p99_duration > 172800 THEN 'fail'  -- >48 hours
        ELSE 'pass'
    END,
    'P99 session duration: ' || p99_duration || ' seconds',
    p99_duration,
    86400
FROM (
    SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_seconds) as p99_duration
    FROM user_sessions
    WHERE started_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
) sub;
```

---

### 8.2 System Health Metrics

```sql
-- Track database performance
CREATE TABLE db_performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collect metrics (run every 5 minutes)
INSERT INTO db_performance_metrics (metric_name, metric_value)
VALUES
    ('active_sessions', (SELECT count(*) FROM pg_stat_activity WHERE state = 'active')),
    ('table_size_sessions_gb', (SELECT pg_total_relation_size('user_sessions') / 1024.0^3)),
    ('table_size_page_views_gb', (SELECT pg_total_relation_size('page_views') / 1024.0^3)),
    ('cache_hit_ratio', (
        SELECT 
            ROUND(sum(blks_hit)::NUMERIC / NULLIF(sum(blks_hit) + sum(blks_read), 0) * 100, 2)
        FROM pg_stat_database
    ));
```

---

### 8.3 Alerting Thresholds

```yaml
# Alert configuration (Prometheus/Grafana)
alerts:
  - name: HighSessionWriteRate
    condition: rate(user_sessions_inserts[5m]) > 10000
    severity: warning
    message: "Session write rate exceeding 10k/sec"
    
  - name: SessionTableSizeGrowth
    condition: table_size_gb{table="user_sessions"} > 500
    severity: critical
    message: "Session table exceeding 500GB - trigger archival"
    
  - name: SlowQueryDetected
    condition: query_duration_seconds > 5
    severity: warning
    message: "Query taking >5 seconds - investigate optimization"
    
  - name: LowCacheHitRatio
    condition: cache_hit_ratio < 95
    severity: warning
    message: "Cache hit ratio below 95% - increase shared_buffers"
```

---

## Summary & Recommendations

### Recommended Implementation Path

**Phase 1: Foundation (Week 1)**
1. Create core tables (user_sessions, page_views, user_events)
2. Set up partitioning (monthly)
3. Create essential indexes
4. Implement basic ETL

**Phase 2: Optimization (Week 2)**
1. Create materialized views
2. Set up automated aggregations (pg_cron)
3. Implement data quality checks
4. Performance testing & tuning

**Phase 3: Advanced Features (Week 3-4)**
1. Data warehouse integration (dbt models)
2. Consent management & GDPR compliance
3. Advanced analytics (cohorts, funnels)
4. Monitoring & alerting

**Phase 4: Scale & Optimize (Ongoing)**
1. TimescaleDB migration (if needed)
2. Sharding implementation
3. ML feature engineering
4. Real-time stream processing

---

**Next Steps:**
1. Review with data engineering team
2. Get DBA approval for schema changes
3. Set up staging environment for testing
4. Create migration scripts
5. Begin Phase 1 implementation

---

**Document Maintained By:** Jay Persanchez  
**Last Updated:** October 30, 2025  
**Version:** 1.0
