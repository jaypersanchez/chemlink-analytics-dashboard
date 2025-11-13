# Analytics Dashboard Deep Dive - Session Memory
**Last Updated:** November 3, 2025  
**Current Status:** ✅ ALL 11 QUERIES COMPLETE  
**Purpose:** Learning exercise to deeply understand dashboard queries and data

---

## 🎯 What We're Doing

**Goal:** Go through all 11 analytics queries surgically to understand:
- What tables/columns each query uses
- What the raw data actually means
- What insights we can derive
- Data quality issues
- Architecture implications for AI training

**Why:** Jay needs to deeply understand this data since:
1. He built the dashboard quickly for the client
2. This data will train Alchemi AI eventually
3. Need to own the knowledge, not just surface-level metrics

**Approach:** Query-by-query walkthrough with questions/discussion

---

## ✅ Queries Completed (11 of 11 - COMPLETE!)

### **Query #1: new_users_monthly** ✅
**Database:** ChemLink DB  
**Tables:** `persons`  
**Columns:** `created_at`, `deleted_at`  

**What it shows:**
- Count of new accounts created per month
- Last 12 months rolling window
- Soft delete pattern (deleted_at IS NULL = active users)

**Results:**
- June 2025: 1,084 signups (peak)
- Oct 2025: 99 signups
- Total: 2,094 active accounts

**Key Learning:** Simple COUNT with GROUP BY month. Uses soft deletes (deleted_at flag).

---

### **Query #2: growth_rate_monthly** ✅
**Database:** ChemLink DB  
**Tables:** `persons`  
**Key SQL Concept:** `LAG()` window function

**What it shows:**
- Month-over-month growth rate percentage
- Uses LAG() to get previous month's value for comparison

**Formula:** `(current - previous) / previous * 100`

**Results:**
- Volatile growth post-launch
- June → July: -83.86%
- July → Aug: +240.57%

**Key Learning:** Window functions for comparing rows. Percentage change calculation.

---

### **Query #3: dau (Daily Active Users)** ✅
**Database:** Engagement DB  
**Tables:** `posts`, `comments`  
**Key SQL Concept:** UNION ALL, COUNT DISTINCT, CASE statements

**What it shows:**
- Unique users who posted OR commented each day
- Breaks down by activity type (posts vs comments)
- Last 30 days

**Results:**
- Oct 28-30: 1-2 active users per day
- 10 total posts, 0 comments
- Only posting, no commenting (one-way broadcast)

**Key Learning:** 
- UNION ALL combines multiple tables
- COUNT(DISTINCT person_id) = unique users
- COUNT(CASE...) = conditional counting

**CRITICAL DISCOVERY:** Cross-DB validation revealed these 2 users are "ghost accounts" - they exist in Engagement DB but NOT in ChemLink DB!

---

### **Query #4: mau (Monthly Active Users)** ✅
**Database:** Engagement DB  
**Tables:** `posts`, `comments`  
**Similar to:** Query #3 but monthly instead of daily

**Results:**
- October 2025: 2 active users
- Same ghost accounts as DAU

**Key Learning:** Same pattern as DAU, just grouped by month instead of day.

**MAJOR INSIGHT:** 
- 2,094 accounts exist (Query #1)
- Only 2 "active" users (Query #4)
- Those 2 are ghost test accounts
- **0 real user activation** on social features

---

### **Query #5: activity_by_type_monthly** ✅
**Database:** Engagement DB  
**Tables:** `posts`, `comments`  
**Key Addition:** Groups by BOTH month AND activity_type

**What it shows:**
- Breaks down MAU by what they did (post vs comment)
- Shows unique users AND total activity count

**Results:**
- Oct 2025: 2 users, 10 posts, 0 comments
- Average 5 posts per user
- No commenting = no community interaction

**Key Learning:** GROUP BY multiple columns to segment data further.

---

### **Query #6: activity_distribution_current** ✅
**Database:** Engagement DB  
**Tables:** `posts`, `comments`  
**Key SQL Concepts:** Double CTE, CROSS JOIN, NULLIF, percentage calculation

**What it shows:**
- Percentage split of active users by activity type THIS MONTH
- Example: "70% posters, 30% commenters"
- Only counts users who ARE active (not all users)

**SQL Pattern:**
```sql
WITH activity_counts AS (...),
     monthly_total AS (SUM(unique_users))
SELECT activity_type, percentage
FROM activity_counts CROSS JOIN monthly_total
```

**Results:**
- **No data for December 2025** (current month)
- All activity was in October 2025
- December has 0 active users

**Key Learning:**
- **Double CTE pattern**: First CTE gets counts, second CTE aggregates totals
- **CROSS JOIN**: Pairs every activity type with total for percentage math
- **NULLIF**: Prevents division by zero (`NULLIF(total, 0)`)
- This query ONLY shows users who acted, not all users

**MAJOR DISCOVERY - Untracked Activity Types:**

Currently tracked:
- ✅ Posts (text, link, image, file types)
- ✅ Comments

NOT tracked (but data exists):
- ❌ **Mentions** (1 mention exists, 1 user)
- ❌ **Reports** (0 reports currently)
- ❌ **Group Creation** (0 groups currently)
- ❌ **Group Joining** (0 memberships currently)

**Post Type Breakdown in DB:**
- Text posts: 165
- Link posts: 65  
- Image posts: 50
- File posts: 32
- **Total: 312 posts** (all approved status)
- ⚠️ **302 posts are soft-deleted!** (we only saw 10 from ghost accounts)

**Action Item:** Need mechanism to track:
1. Mentions (`mentioned_by_person_id` in `mentions` table)
2. Reports (`reporter_id` in `reports` table)  
3. Group creation (`created_by` in `groups` table)
4. Group joining (`person_id` + `confirmed_at` in `group_members` table)
5. Possibly break down posts by TYPE (text/link/image/file)

---

## 🚨 Major Findings So Far

### **Finding #1: Zero Real User Engagement**
- Production has 2,094 accounts
- 100% of engagement activity = 2 ghost test accounts
- 0 real users have ever posted/commented
- Activation rate: 0.00%

**Status:** Not a bug, just early-stage / soft launch. Features live but not adopted yet.

### **Finding #2: Orphaned Records (Data Integrity)**
- 2 users with posts in Engagement DB don't exist in ChemLink DB
- PostgreSQL can't enforce foreign keys across separate databases
- Application layer handles referential integrity

**Root cause:** Test accounts deleted from ChemLink but posts remained in Engagement

**Action needed:** 
- Clean up 2 ghost accounts (quick win)
- Add automated validation monitoring

### **Finding #3: Two-Database Architecture**
**Setup:**
- ChemLink DB: User profiles, accounts, demographics
- Engagement DB: Posts, comments, social activity

**Limitation:** Can't JOIN across databases in SQL
**Impact:** Can't easily answer "What % of signups activate?" without app-layer joins

**Opportunity:** Phase 2 - Build unified data warehouse for cross-platform analytics

### **Finding #4: Soft-Deleted Post Volume**
- Total posts in DB: 312
- Active posts in queries: 10 (ghost accounts only)
- **302 posts soft-deleted** (96.8% deletion rate)

**Question raised:** Why so many soft-deleted posts? Test data cleanup?

### **Finding #5: Untracked Activity Types (Query #6)**
**Currently tracking:** Posts, Comments only (2 activity types)

**Available but NOT tracked:**
- Mentions (1 active mention exists)
- Reports/Moderation (0 currently)
- Group creation (0 currently)
- Group membership (0 currently)
- Post types (text/link/image/file breakdown)

**Impact:** Dashboard shows incomplete engagement picture  
**Action needed:** Add queries/charts for these activity types

---

## ✅ Queries #7-11 Completed

### **Query #7: activity_intensity_levels** ✅
**Database:** Engagement DB  
**Tables:** `posts`, `comments`  
**Key SQL Concepts:** Triple-nested CTEs, CASE-based categorization, custom ORDER BY

**What it shows:**
- Categorizes users by activity volume: Power (20+), Active (10-19), Regular (5-9), Casual (1-4)
- Last 12 months rolling

**Results (October 2025):**
- 1 Regular User (5-9 activities): 9 posts
- 1 Casual User (1-4 activities): 1 post  
- Both ghost accounts, 0 comments

**Key Learning:** Intensity bucketing for user segmentation and targeted interventions

---

### **Query #8: dau_comprehensive** ⚠️ SCHEMA BUG FOUND
**Database:** ChemLink DB  
**Tables:** `view_access`, `query_votes`, `collections`, `query_embeddings`, `persons`  
**Status:** Query FAILED - schema errors

**Bugs found:**
1. `query_votes` uses `voter_id`, not `person_id`
2. `query_votes` has NO `deleted_at` column
3. `query_embeddings` has NO person tracking (system-level)
4. `persons` has BOTH `id` (bigint) AND `person_id` (uuid)

**After fixing:**
- 18 days with activity in last 30 days
- Avg DAU: 3.6 users
- Peak DAU: 9 users
- Nov 3: 7 active users

**Activity Breakdown:**
- View Access: 19 users, 44 activities
- Query Votes: 8 users, 22 votes
- Collections: 10 users, 36 collections
- Profile Updates: 34 users

**MAJOR DISCOVERY:** Real user activity exists in ChemLink DB! Core features being used.

---

### **Query #9: mau_comprehensive** ⚠️ SCHEMA BUG
**Database:** ChemLink DB  
**Status:** Query FAILED (same schema issues as #8)

**After fixing:**
- October 2025: 2,088 MAU (bulk onboarding month!)
  - 2,084 profile updates
  - 14 view access
  - 10 collections
  - 8 query votes
- November 2025: 7 MAU (only view access)
- -99.7% MoM decline (post-launch dropoff)

**Key Insight:** October = launch month. November shows true organic baseline.

---

### **Query #10: user_type** ⚠️ SCHEMA BUG
**Database:** ChemLink DB  
**Tables:** Activity tables + `persons`  
**Status:** Query FAILED (same schema issues)

**After fixing:**
- Finder Users: 19 total (0.9%)
- Standard Users: 2,086 total (99.1%)

**October Activity:**
- Finder: 14/19 active (74% activation!)
- Standard: 10/2,086 active (0.5%)

**November Activity:**
- Standard only: 7 users
- No Finder users active

**Key Insight:** Premium "Finder" segment is small but highly engaged.

---

### **Query #11: collections_privacy** ✅
**Database:** ChemLink DB  
**Table:** `collections`  
**Key SQL Concepts:** COALESCE for NULL handling

**Results:**
- October 2025 only month with data
- PUBLIC: 27 collections (8 creators)
- PRIVATE: 9 collections (7 creators)
- 75% public, 25% private

**Key Learning:** Users prefer public sharing. Suggests collaboration mindset.

---

## 🔲 ALL QUERIES COMPLETE

### **Query #7: activity_intensity_levels**
**Database:** Engagement DB  
**Purpose:** Categorize users as Power/Active/Regular/Casual by activity count  
**Status:** Not started

### **Query #8: dau_comprehensive**
**Database:** ChemLink DB  
**Purpose:** DAU tracking ALL activity types (not just posts/comments)  
**Tables:** view_access, query_votes, collections, query_embeddings, persons  
**Status:** Not started

### **Query #9: mau_comprehensive**
**Database:** ChemLink DB  
**Purpose:** MAU tracking ALL activity types  
**Status:** Not started

### **Query #10: user_type**
**Database:** ChemLink DB  
**Purpose:** Active users segmented by Standard vs Finder Users  
**Status:** Not started

### **Query #11: collections_privacy**
**Database:** ChemLink DB  
**Purpose:** Collections created by privacy type (Public vs Private)  
**Status:** Not started

---

## 🛠️ Tools & Scripts Created

### **run_single_query.py**
- Runs individual query by key
- Shows SQL, database, and results
- Usage: `python3 run_single_query.py <query_key>`

### **check_orphaned_records.py**
- Cross-DB validation script
- Finds engagement records with no matching ChemLink user
- Discovered the 2 ghost accounts

### **verify_real_users.py**
- Validates which "active" users are real vs test accounts
- Showed 0 real users, 2 ghost users

### **ANALYTICS_FINDINGS_REPORT.md**
- Comprehensive report of findings (revised for mild/proactive tone)
- Client-safe language
- Positions findings as opportunities

---

## 📊 Production Environment

**Status:** Connected to PRODUCTION databases (APP_ENV=prod)

**ChemLink Production DB:**
- 2,094 active user accounts
- Data from June 2025 onwards

**Engagement Production DB:**
- 312 posts total in DB (165 text, 65 link, 50 image, 32 file)
- 302 posts soft-deleted (96.8%)
- 10 active posts (all from ghost accounts)
- 0 comments
- 2 test users
- 1 mention
- 0 reports, 0 groups, 0 group memberships

**Important:** All analysis is on live production data, not staging/dev.

---

## 🎓 Key SQL Concepts Learned So Far

1. **Soft Deletes:** `deleted_at IS NULL` pattern
2. **Window Functions:** `LAG()` for previous row values
3. **UNION ALL:** Combining multiple tables
4. **COUNT DISTINCT:** Unique user counting
5. **CASE Statements:** Conditional counting
6. **GROUP BY Multiple Columns:** Segmented analysis
7. **DATE_TRUNC:** Time bucketing (month, day)
8. **CTEs (WITH clauses):** Multi-step queries

---

## 🎯 Next Steps

### **Immediate (Continue Deep Dive):**
1. Query #6: activity_distribution_current
2. Query #7: activity_intensity_levels
3. Query #8-11: ChemLink comprehensive metrics

### **After Query Analysis Complete:**
1. Clean up 2 ghost test accounts
2. Add data source labels to dashboard
3. Set up validation monitoring script

### **Future (AI Preparation):**
Jay has PostgreSQL locally and wants to ramp up skills for Alchemi AI training.

**Skills to build:**
- Advanced SQL (window functions, CTEs, time-series)
- Feature engineering (raw data → ML features)
- Python data pipelines (pandas, ETL)
- Cohort analysis
- JSONB for event data

---

## 💬 Communication Context

**Client Situation:**
- Dashboard already proposed to client
- Findings need careful framing (not "we found problems")
- Tone: Proactive, validation-focused, opportunity-spotting
- Position as: "Quality assurance before you make decisions"

**Chat Room Update:**
- Short, conversational format
- Emphasize: Infrastructure solid, baseline established, Phase 2 opportunities
- Avoid: "Zero users", "data integrity issues", "critical problems"
- Frame as: "Early-stage", "test cleanup", "enhancement opportunities"

---

## 📝 Session Notes

**Learning Style:** 
- Surgical, query-by-query
- Ask questions freely
- Understand tables, columns, conditions
- Verify with cross-DB checks
- Real production data inspection

**What's Working:**
- Deep dive approach revealing insights simple dashboards miss
- Cross-database validation catching data quality issues
- Understanding data architecture for future AI work

**ROI:** 2 hours → Major insights about data quality, architecture, activation rates

---

## 🔄 How to Resume Next Session

**Say this to AI:**
"Let's continue the analytics deep dive. We finished Query #5 (activity_by_type_monthly). Ready for Query #6. Read SESSION_MEMORY.md for full context."

**AI will:**
1. Read this file
2. Remember all queries completed
3. Know the findings (ghost accounts, orphaned records, etc.)
4. Continue with Query #6: activity_distribution_current
5. Maintain same surgical approach with questions

---

**Last Query Completed:** #11 (collections_privacy)  
**Status:** ✅ ALL 11 QUERIES COMPLETE  
**Next Action:** Fix schema bugs in queries #8, #9, #10
