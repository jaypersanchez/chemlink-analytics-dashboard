# ChemLink Analytics - Context for Analytics DB Project

**Created:** November 3, 2025  
**Purpose:** Context handoff for new `chemlink-analytics-db` project  
**Source Project:** chemlink-analytics-dashboard

---

## 🎯 Why We're Building an Analytics Database

### The Problem
**Two isolated databases can't answer key business questions:**

1. **engagement-platform-stg** (Social features)
   - Posts, comments, groups, mentions
   - Only tracks social engagement
   - 2 ghost test users, 0 real social activity

2. **chemlink-service-stg** (Profile/Finder features)  
   - User profiles, experiences, education
   - Embeddings for AI search
   - 2,094 users, 34+ actively using core features

**Gap:** Can't answer:
- User journey: signup → profile building → engagement
- Activation rate (% of signups who become active)
- Profile completeness vs. engagement correlation
- Which user types become power users

### The Solution
**Separate Analytics Database** (Local Postgres)
- Unified views combining both source databases
- Materialized aggregations for fast queries
- Reference tables for data quality
- Clean datasets for Alchemi AI training

---

## 📊 Current System Architecture

### Database Connections (from `.env`)
```
# ChemLink Service (Profile/Finder)
CHEMLINK_DB_HOST=...
CHEMLINK_DB_NAME=chemlink-service-stg
- Tables: persons, experiences, education, embeddings, collections, query_votes

# Engagement Platform (Social)  
ENGAGEMENT_DB_HOST=...
ENGAGEMENT_DB_NAME=engagement-platform-stg
- Tables: persons, posts, comments, groups, group_members, mentions

# Link Between DBs
engagement.persons.external_id → chemlink.persons.id
```

### Current Dashboard Tech Stack
- Flask backend (`app.py`)
- 11 API endpoints for analytics queries
- Chart.js frontend
- Direct SQL queries to both databases

---

## 🔍 Key Findings from Analytics Deep Dive

### 1. Real User Activity (Core Product)
**ChemLink DB - Last 30 Days:**
- 34+ active users using core features
- 19 users viewing content
- 8 users voting on queries
- 10 users creating collections
- 34 users updating profiles

**Engagement DB:**
- 0 real users (social features unadopted)
- Only 2 ghost test accounts
- 302 soft-deleted posts (96.8% - cleanup needed)

### 2. Schema Issues Found
**query_votes table:**
- Uses `voter_id`, not `person_id` (breaks joins)
- NO `deleted_at` column (can't filter soft deletes)

**query_embeddings table:**
- NO person tracking (system-level data only)

**persons table (ChemLink):**
- Has BOTH `id` (bigint) AND `person_id` (uuid) - confusing

### 3. Untracked Activity Types
**Engagement DB:**
- ❌ Mentions (1 exists, not tracked)
- ❌ Reports/moderation
- ❌ Group creation/membership
- ❌ Post type breakdown (text/link/image/file)

**ChemLink DB:**
- ❌ Profile views
- ❌ Search behavior (query_embeddings has no person_id)
- ❌ Finder usage patterns
- ❌ Collection sharing

### 4. User Segmentation Insights
**Finder (Premium) vs Standard:**
- Finder users: 19 total (0.9%)
- Standard users: 2,086 total (99.1%)
- **Finder activation: 74%** (14/19 active in Oct)
- **Standard activation: 0.5%** (10/2,086 active in Oct)

### 5. Growth Timeline
**User Signups:**
- June 2025: 1,084 users (launch spike)
- July 2025: 175 users (-83.86% drop)
- August 2025: 596 users (+240.57% recovery)
- September 2025: 139 users
- October 2025: 99 users
- **Total:** 2,094 active accounts

**October 2025 = Launch month** (2,088 MAU from bulk onboarding)

---

## 🎯 What Analytics DB Must Provide

### Core Requirements

#### 1. Unified User View
```sql
-- Must combine data from both databases
SELECT 
    chemlink_id,
    email,
    signup_date,
    has_finder,
    -- Profile metrics
    experience_count,
    education_count,
    profile_completion_score,
    -- Engagement metrics  
    posts_created,
    comments_made,
    votes_cast,
    collections_created,
    -- Calculated fields
    days_since_signup,
    user_lifecycle_stage,
    activation_status
FROM analytics.unified_users;
```

#### 2. Daily/Monthly Aggregations
- New signups per day/week/month
- DAU/WAU/MAU (real metrics, not just social)
- Activity breakdown by type
- Retention cohorts

#### 3. Cross-Database Analytics
**Questions to answer:**
- What % of signups complete their profile?
- What % of profile completers become active?
- Does profile completeness predict engagement?
- Which cohort (June vs Oct) has better activation?
- What's the typical user journey timeline?

#### 4. AI Training Datasets
**For Alchemi AI to learn:**
- Predict: Which new users will activate?
- Detect: Unusual patterns (orphaned records, anomalies)
- Recommend: Actions to improve activation rate
- Segment: User types for personalization

### Data Quality Requirements
- No ghost test accounts
- Soft-deletes properly handled
- Cross-DB consistency validated
- Historical data preserved (don't update in place)

---

## 📁 Source Project File Structure

```
chemlink-analytics-dashboard/
├── app.py                           # Flask API with 11 analytics endpoints
├── db_config.py                     # DB connection helpers
├── sql_queries.py                   # SQL query definitions
├── requirements.txt                 # Python deps: Flask, psycopg2, python-dotenv
├── .env                            # DB credentials (NOT in git)
├── .env.example                    # Template for credentials
├── templates/dashboard.html         # Frontend dashboard
├── static/
│   ├── css/styles.css
│   └── js/dashboard.js             # Chart.js visualizations
├── design-docs/
│   └── ERD/
│       ├── engagement-platform.sql  # 600+ lines of query examples
│       └── finder-builder.sql       # 400+ lines of query examples
├── ANALYTICS_FINDINGS_REPORT.md     # Deep dive findings (all 11 queries)
├── SESSION_MEMORY.md                # Running session context
└── compare_schemas.py               # Schema comparison tool
```

---

## 🔑 Critical Files to Reference

### 1. `design-docs/ERD/engagement-platform.sql`
**Contains:**
- Complete table structure examples
- User engagement queries
- Activity tracking patterns
- Cross-platform profile mapping
- Content analysis queries

### 2. `design-docs/ERD/finder-builder.sql`  
**Contains:**
- Profile builder data structure
- Finder/AI feature queries
- Experience/education patterns
- Collections and embeddings
- Profile completeness analysis

### 3. `ANALYTICS_FINDINGS_REPORT.md`
**Contains:**
- All 11 query analysis results
- Schema bugs discovered
- Untracked activity types
- User segmentation insights
- Action items and roadmap

### 4. `app.py`
**Reference for:**
- Current query patterns
- API endpoint structure
- What metrics stakeholders need
- How data is currently fetched

### 5. `db_config.py`
**Connection patterns:**
- Multi-environment support (UAT, Prod)
- Connection pooling approach
- Query execution patterns

---

## 🗺️ Proposed Analytics DB Schema

### Schema Organization
```
chemlink_analytics/
├── staging/          # Raw copies from source DBs
├── core/            # Cleaned, transformed data
├── aggregates/      # Materialized views for dashboards
└── ai/              # Training datasets for Alchemi AI
```

### Key Tables/Views Needed

#### `core.unified_users`
Master user table combining both databases

#### `aggregates.daily_metrics`
Pre-calculated daily KPIs (new signups, DAU, activity counts)

#### `aggregates.cohort_retention`  
Retention analysis by signup cohort

#### `core.user_journey_events`
Event stream for tracking user lifecycle

#### `ai.training_data_activation`
Features + labels for predicting user activation

#### `ai.training_data_engagement`
Features + labels for predicting engagement level

#### `core.reference_tables`
Clean lookup tables (companies, roles, locations, etc.)

---

## 🔄 ETL Pipeline Requirements

### Extract
- Pull from `chemlink-service-stg` (read-only)
- Pull from `engagement-platform-stg` (read-only)
- Schedule: Daily at midnight (initial), hourly (future)

### Transform
- Join using `external_id` relationship
- Calculate derived metrics (profile_completion_score, engagement_score)
- Clean data (remove ghost accounts, validate consistency)
- Handle soft deletes properly

### Load  
- Insert into staging schema
- Transform into core schema
- Refresh materialized views
- Export AI training datasets

### Tools Needed
- Python (psycopg2 for DB connections)
- pandas (data transformation)
- SQLAlchemy (ORM, optional)
- Schedule library (or cron jobs)

---

## 🎯 Success Criteria

### Phase 1: Foundation
✅ Analytics DB created locally  
✅ Schema designed and implemented  
✅ ETL pipeline extracts from both source DBs  
✅ Unified user view working

### Phase 2: Analytics
✅ Daily metrics aggregation running  
✅ Cohort analysis tables populated  
✅ User journey tracking implemented  
✅ Dashboard queries 10x faster

### Phase 3: AI Readiness
✅ Clean training datasets exported  
✅ Features engineered for ML models  
✅ Historical data preserved properly  
✅ Alchemi AI can consume data easily

---

## 🚨 Known Issues to Address

### Data Quality
- [ ] Remove 2 ghost test accounts from Engagement DB
- [ ] Investigate 302 soft-deleted posts (96.8% deletion rate)
- [ ] Fix schema bugs in query_votes table
- [ ] Validate external_id consistency between DBs

### Missing Data
- [ ] Add tracking for mentions, groups, moderation
- [ ] Capture profile view events
- [ ] Track search behavior (need person_id in query_embeddings)
- [ ] Log collection sharing activity

### Schema Improvements
- [ ] Standardize person_id vs id usage
- [ ] Add deleted_at to query_votes
- [ ] Add person_id to query_embeddings (if possible)
- [ ] Document relationship between tables

---

## 💡 Key Insights to Remember

1. **Core product is healthy** - 34+ users actively using features
2. **Social features unadopted** - Need activation strategy
3. **Finder users 148x more engaged** than standard users
4. **October was launch month** - 2,088 users onboarded in bulk
5. **Data exists** - Just siloed and needs unification
6. **Dashboard has bugs** - But they're hiding good news!

---

## 📚 Reference Documents in Source Project

- `ANALYTICS_FINDINGS_REPORT.md` - Complete analysis of all 11 queries
- `SESSION_MEMORY.md` - Running context and decisions
- `ANALYST_HANDOFF.md` - Original handoff document
- `README.md` - Current dashboard documentation
- `design-docs/ERD/*.sql` - Comprehensive query examples

---

## 🔗 Connection to New Project

**When starting `chemlink-analytics-db`:**

1. Read this document first (you're here!)
2. Review `ANALYTICS_FINDINGS_REPORT.md` for detailed findings
3. Reference SQL files in `design-docs/ERD/` for query patterns
4. Copy `.env.example` to get DB connection template
5. Study `app.py` to understand required metrics

**This document should be enough to bootstrap the new project without losing context.**

---

## 🎯 Next Steps

1. Create new project: `chemlink-analytics-db`
2. Design schema (use this doc as requirements)
3. Build ETL pipeline
4. Create materialized views
5. Export AI training data
6. Connect dashboard to analytics DB (future)

---

**Questions? Reference this doc + the source project files listed above.**
