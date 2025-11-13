# Analytics Architecture Session - November 3, 2025

## Session Summary
**Topic:** Architectural design for unified analytics database  
**Duration:** ~30 minutes  
**Outcome:** Decision to create separate `chemlink-analytics-db` project

---

## 🎯 Original Question

**User asked:** "List out all the gaps or missing features that don't exist which prevent us from providing analytics. Should we have another instance of postgres for analytics that combines data from both databases?"

---

## 🔍 Key Discussion Points

### 1. Identified Gaps in Current Analytics

#### **Cross-Database Analytics Missing**
- Can't track user journey: signup → profile → engagement
- Can't measure activation rate
- Can't correlate profile completeness with behavior
- Can't identify which user types become power users

#### **No Unified Data Model**
- Two isolated databases (engagement-platform, chemlink-service)
- Only linked by `external_id` field
- No materialized views or joins
- No aggregated metrics tables

#### **Untracked Activity Types**
**Engagement DB:**
- Mentions, reports, group creation, moderation
- Post type breakdown (text/link/image/file)

**ChemLink DB:**
- Profile views, search behavior
- Finder usage patterns, collection sharing

#### **No Historical Aggregations**
- No daily/weekly/monthly rollups
- No cohort analysis tables
- No retention/churn calculations
- No user lifecycle tracking

#### **Data Quality Issues**
- 302 soft-deleted posts (96.8% deletion rate)
- Ghost test accounts in production
- Schema bugs (query_votes uses voter_id not person_id)
- No consistency validation between DBs

---

## ✅ Proposed Solution: Analytics Database

### Architecture
```
┌─────────────────────┐    ┌─────────────────────┐
│ engagement-platform │    │ chemlink-service    │
│ (Social Features)   │    │ (Profile/Finder)    │
└──────────┬──────────┘    └──────────┬──────────┘
           │                          │
           │  ETL/Sync Process        │
           └────────┬─────────────────┘
                    ↓
         ┌──────────────────────┐
         │  Analytics Database  │
         │  (Local Postgres)    │
         │                      │
         │  • Unified views     │
         │  • Materialized agg. │
         │  • Reference tables  │
         │  • AI training data  │
         └──────────────────────┘
```

### What Analytics DB Provides

1. **Unified User View** - Combines data from both source DBs
2. **Daily Metrics Aggregation** - Pre-calculated KPIs
3. **Cohort Analysis** - Retention by signup date
4. **User Journey Events** - Lifecycle tracking
5. **AI Training Datasets** - Clean exports for Alchemi AI

---

## 🚀 Decision Made

**Create separate project:** `chemlink-analytics-db`

**Reasoning:**
- Cleaner separation of concerns
- Easier to manage ETL pipeline independently
- Can iterate on schema without touching dashboard
- Better for team collaboration (different repos)

---

## 📋 Context Preservation Strategy

### Files Created

#### 1. `ANALYTICS_DB_CONTEXT.md` (This Project)
**Purpose:** Complete handoff document for new project  
**Contains:**
- Why we're building analytics DB
- Current system architecture
- Key findings from analytics deep dive
- Requirements for analytics DB
- Schema design proposals
- ETL pipeline requirements
- Success criteria
- Known issues to address

#### 2. `ARCHITECTURE_SESSION_2025-11-03.md` (This File)
**Purpose:** Conversation summary for historical record  
**Contains:**
- Original question/problem
- Discussion points
- Solution architecture
- Decision rationale
- Next steps

### How to Use Context in New Project

**When starting `chemlink-analytics-db`:**

1. **First read:** `ANALYTICS_DB_CONTEXT.md` (comprehensive requirements)
2. **Then reference:**
   - `ANALYTICS_FINDINGS_REPORT.md` (detailed query analysis)
   - `design-docs/ERD/*.sql` (query patterns and examples)
   - `app.py` (current metrics needed by dashboard)
   - `.env.example` (DB connection template)

3. **For historical context:**
   - This file (`ARCHITECTURE_SESSION_2025-11-03.md`)
   - `SESSION_MEMORY.md` (running session notes)

---

## 🎯 Next Steps

### Immediate (User Action)
```bash
cd ~/projects
mkdir chemlink-analytics-db
cd chemlink-analytics-db

# Reference the context document
cat ../chemlink-analytics-dashboard/ANALYTICS_DB_CONTEXT.md
```

### Phase 1: Setup (Week 1)
- [ ] Create analytics database locally
- [ ] Design schema (staging, core, aggregates, ai)
- [ ] Document table structures

### Phase 2: ETL Pipeline (Week 2)
- [ ] Build extract scripts (both source DBs)
- [ ] Build transform logic (joins, calculations)
- [ ] Build load process (populate analytics DB)
- [ ] Schedule automation

### Phase 3: Materialized Views (Week 3)
- [ ] Create unified_users view
- [ ] Create daily_metrics aggregations
- [ ] Create cohort_retention tables
- [ ] Create user_journey_events

### Phase 4: AI Data Export (Week 4)
- [ ] Export training datasets
- [ ] Feature engineering for ML
- [ ] Create labeled datasets
- [ ] Document for Alchemi AI consumption

---

## 💡 Key Insights from This Session

1. **Separate project is the right call** - Keeps concerns isolated
2. **Context preservation is critical** - Handoff doc captures everything
3. **Local Postgres is perfect for MVP** - Can migrate to cloud later
4. **AI readiness is a key goal** - Not just dashboards
5. **Data quality must improve** - Clean before unifying

---

## 📊 Current State (Reminder)

**Two Production Databases:**
- `chemlink-service-stg`: 2,094 users, 34+ active
- `engagement-platform-stg`: 0 real users (social unadopted)

**Analytics Gaps:**
- No cross-DB queries
- No unified metrics
- No AI training data
- Missing activity tracking

**Solution:** New analytics database to bridge the gap

---

## 🔗 Related Files

**In this project:**
- `/ANALYTICS_DB_CONTEXT.md` - Main handoff document ⭐
- `/ANALYTICS_FINDINGS_REPORT.md` - Detailed query analysis
- `/SESSION_MEMORY.md` - Running notes
- `/design-docs/ERD/*.sql` - Query examples
- `/app.py` - Current dashboard API

**In new project (to be created):**
- `/README.md` - Project overview
- `/schema/` - DDL files
- `/etl/` - Pipeline scripts
- `/docs/ARCHITECTURE.md` - Technical design

---

**End of session summary**
