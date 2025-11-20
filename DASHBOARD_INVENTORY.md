# ChemLink Analytics Dashboard - Complete Inventory

**Document Version:** 1.0
**Last Updated:** 2025-11-20
**Environment:** APP_ENV=kube (Kubernetes Development)

---

## Executive Summary

The ChemLink Analytics Dashboard V1 consists of **34 charts + 1 table** visualizing data from **3 databases** using **32 unique SQL queries**. The dashboard is organized into 6 main metric categories providing comprehensive insights into user growth, engagement, feature adoption, and talent marketplace intelligence.

---

## Database Architecture

### Active Databases (APP_ENV=kube)

| Database | Host | Port | Usage | Query Count |
|----------|------|------|-------|-------------|
| **chemlink-service-dev** | localhost (k8s port-forward) | 5433 | User profiles, companies, finder, collections | 20 queries |
| **engagement-platform-dev** | localhost (k8s port-forward) | 5433 | Posts, comments, engagement metrics | 10 queries |
| **chemonics-kratos-prd** | AWS RDS (production) | 5432 | Authentication sessions (read-only) | 2 queries |

### Database NOT Used in V1
- ❌ **chemlink_analytics** - Only used by V2 (`/v2/api/*`) routes for aggregate graph analytics

---

## Complete Chart Inventory (34 Charts + 1 Table)

### 1. GROWTH METRICS (10 Charts)

| # | Chart Name | Endpoint | Query | Database | Notes |
|---|------------|----------|-------|----------|-------|
| 1 | New Users - Monthly | `/api/new-users/monthly` | `new_users_monthly` | chemlink-service-dev | Rolling 12-month window |
| 2 | User Growth Rate - Monthly | `/api/growth-rate/monthly` | `growth_rate_monthly` | chemlink-service-dev | Month-over-month % change using LAG() |
| 3 | DAU (Posts/Comments) | `/api/active-users/daily` | `dau` | engagement-platform-dev | UNION posts + comments |
| 4 | MAU (Posts/Comments) | `/api/active-users/monthly` | `mau` | engagement-platform-dev | Rolling 12-month window |
| 5 | MAU by Country | `/api/active-users/monthly-by-country` | `mau_by_country` | engagement + chemlink | ⚠️ Cross-database 2-step query |
| 6 | DAU - Comprehensive | `/api/active-users/daily-comprehensive` | `dau_comprehensive` | chemlink-service-dev | All activity types |
| 7 | MAU - Comprehensive | `/api/active-users/monthly-comprehensive` | `mau_comprehensive` | chemlink-service-dev | All activity types |
| 8 | Login Velocity (24hr) | `/api/auth/login-velocity/hourly` | `login_velocity_hourly` | kratos-prd | ⚠️ Hidden by default, uses PROD |
| 9 | Unique Identities (30d) | `/api/auth/unique-identities/daily` | `unique_identities_daily` | kratos-prd | ⚠️ Hidden by default, uses PROD |
| 10 | Active Users by Type | `/api/active-users/by-user-type` | `user_type` | chemlink-service-dev | Finder vs Standard users |

**Key Technical Details:**
- **Rolling Windows**: All monthly metrics use 12-month rolling windows (`CURRENT_DATE - INTERVAL '11 months'`)
- **Cross-Database Query**: MAU by Country requires app-layer merge of engagement activity + ChemLink location data
- **Kratos Queries**: Always pull from production, even in dev/kube mode

---

### 2. USER ENGAGEMENT (4 Charts + 1 Table)

| # | Chart Name | Endpoint | Query | Database | Notes |
|---|------------|----------|-------|----------|-------|
| 11 | Post Frequency - Daily | `/api/engagement/post-frequency` | `post_frequency` | engagement-platform-dev | Last 30 days |
| 12 | Post Engagement Rate by Type | `/api/engagement/post-engagement-rate` | `engagement_rate` | engagement-platform-dev | Avg comments per post |
| 13 | Content Type Distribution | `/api/engagement/content-analysis` | `content_type` | engagement-platform-dev | All-time data |
| 14 | Top 10 Active Posters | `/api/engagement/active-posters` | `active_posters` | engagement-platform-dev | ⚠️ Contains PII (names, emails) |

**Table:**
- **Top Performing Posts** | `/api/engagement/post-reach` | `post_reach` | engagement-platform-dev | ⚠️ Contains PII (post content, author names)

**Key Technical Details:**
- **Engagement Score Formula**: `(posts × 3) + (comments × 2)`
- **User Tiers**: Power User (20+), Active (10+), Regular (5+), Casual (1-4)
- **PII Warning**: Active Posters and Top Posts should be hidden in production UI

---

### 3. ACTIVITY TYPE ANALYTICS (3 Charts)

| # | Chart Name | Endpoint | Query | Database | Notes |
|---|------------|----------|-------|----------|-------|
| 15 | MAU by Activity Type | `/api/activity/by-type-monthly` | `activity_by_type_monthly` | engagement-platform-dev | Posts vs Comments split |
| 16 | Activity Distribution - Current Month | `/api/activity/distribution-current` | `activity_distribution_current` | engagement-platform-dev | Pie chart % breakdown |
| 17 | User Engagement Intensity Levels | `/api/activity/intensity-levels` | `activity_intensity_levels` | engagement-platform-dev | Stacked bars by tier |

**Key Technical Details:**
- **Intensity Tiers**: Same as engagement score (Power/Active/Regular/Casual)
- **Current Month**: Uses `DATE_TRUNC('month', CURRENT_DATE)` for current month filter

---

### 4. FEATURE ADOPTION & FUNNELS (8 Charts)

| # | Chart Name | Endpoint | Query | Database | Notes |
|---|------------|----------|-------|----------|-------|
| 18 | Account Creation Funnel (Bar) | `/api/funnel/account-creation` | `account_funnel` | chemlink-service-dev | Shares same data as #19 |
| 19 | Account Creation Funnel (Pyramid) | `/api/funnel/account-creation` | `account_funnel` | chemlink-service-dev | Visual variant of #18 |
| 20 | Finder Search Volume | `/api/finder/searches` | `finder_searches` (query 1) | chemlink-service-dev | Total searches timeline |
| 21 | Search Intent Distribution | `/api/finder/searches` | `finder_searches` (query 2) | chemlink-service-dev | Breakdown by intent |
| 22 | Finder Engagement Rate | `/api/finder/engagement` | `finder_engagement` | chemlink-service-dev | ⚠️ Multi-query endpoint (4 queries) |
| 23 | Profile Additions to Collections | `/api/collections/profile-additions` | `profile_additions` | chemlink-service-dev | Monthly trend |
| 24 | Collections Created | `/api/collections/created` | `collections_created` | chemlink-service-dev | ⚠️ Multi-query endpoint (3 queries) |
| 25 | Shared Collections | `/api/collections/shared` | `collections_shared` | chemlink-service-dev | ⚠️ Multi-query endpoint (3 queries) |
| 26 | Collections by Privacy | `/api/collections/created-by-privacy` | `collections_privacy` | chemlink-service-dev | Public vs Private split |

**Key Technical Details:**
- **Funnel Steps**: Total → Basic Info → Headline → Location → Company → LinkedIn → Finder Enabled
- **Multi-Query Endpoints**:
  - `finder_searches`: Total count + By intent + Monthly timeline
  - `finder_engagement`: Total votes + By type (upvote/downvote) + Active voters + Engagement rate %
  - `collections_created`: Total + By privacy + Monthly timeline
  - `collections_shared`: Shared count + Access types + Total invites
- **Query Votes Table**: ⚠️ Has NO `deleted_at` column (noted in queries)

---

### 5. PROFILE QUALITY METRICS (3 Charts)

| # | Chart Name | Endpoint | Query | Database | Notes |
|---|------------|----------|-------|----------|-------|
| 27 | Profile Completion Score | `/api/profile/completion-rate` | `profile_completion` | chemlink-service-dev | Shares same data as #28 |
| 28 | Profile Status Breakdown | `/api/profile/completion-rate` | `profile_completion` | chemlink-service-dev | Pie chart variant of #27 |
| 29 | Profile Update Freshness | `/api/profile/update-frequency` | `profile_freshness` | chemlink-service-dev | FRESH/AGING/STALE buckets |

**Key Technical Details:**
- **Completion Score**: 0-7 scale (headline, linkedin, location, company, experience, education, languages)
- **Profile Status Categories**:
  - `FINDER_ENABLED`: Has embeddings (AI-powered search)
  - `BUILDER_ONLY`: Has experience/education but no embeddings
  - `BASIC_PROFILE`: Minimal data
- **Freshness Buckets**:
  - `FRESH`: < 3 months since update
  - `AGING`: 3-6 months
  - `STALE`: 6+ months

---

### 6. TALENT MARKETPLACE INTELLIGENCE (5 Charts)

| # | Chart Name | Endpoint | Query | Database | Notes |
|---|------------|----------|-------|----------|-------|
| 30 | Top Companies | `/api/talent/top-companies` | `top_companies` | chemlink-service-dev | All-time data |
| 31 | Top Roles/Job Titles | `/api/talent/top-roles` | `top_roles` | chemlink-service-dev | All-time data |
| 32 | Education Distribution | `/api/talent/education-distribution` | `education_distribution` | chemlink-service-dev | All-time data |
| 33 | Geographic Distribution | `/api/talent/geographic-distribution` | `geographic_distribution` | chemlink-service-dev | All-time data |
| 34 | Top Skills & Projects | `/api/talent/top-skills-projects` | `top_skills_projects` | chemlink-service-dev | All-time data |

**Key Technical Details:**
- **Top Companies**: Ranked by user count + experience count
- **Education**: Uses `STRING_AGG()` to list top 5 schools (could truncate)
- **Geographic**: Includes percentage calculation based on total users
- All queries respect `deleted_at IS NULL` for soft deletes

---

### 7. SUMMARY SECTION

**Quick Stats Cards** (top of dashboard)
- **Endpoint**: `/api/engagement/summary`
- **Database**: engagement-platform-dev
- **Data**: Aggregate counts for last 30 days (posts, comments, active users, etc.)

---

## SQL Query Reference

### Query Complexity Breakdown

| Query Type | Count | Description |
|------------|-------|-------------|
| Single SELECT | 20 | Standard aggregation queries |
| WITH (CTE) | 5 | Complex queries with Common Table Expressions |
| Multi-query endpoints | 4 | Endpoints that execute 3-4 separate queries |
| Cross-database | 1 | Requires app-layer join (MAU by Country) |

### Queries by Database

**ChemLink Service DB (20 queries):**
1. `new_users_monthly`
2. `growth_rate_monthly`
3. `dau_comprehensive`
4. `mau_comprehensive`
5. `mau_by_country` (step 2)
6. `user_type`
7. `profile_completion`
8. `profile_freshness`
9. `top_companies`
10. `top_roles`
11. `education_distribution`
12. `geographic_distribution`
13. `top_skills_projects`
14. `account_funnel`
15. `finder_searches` (3 queries)
16. `finder_engagement` (4 queries)
17. `profile_additions`
18. `collections_created` (3 queries)
19. `collections_shared` (3 queries)
20. `collections_privacy`

**Engagement Platform DB (10 queries):**
1. `dau`
2. `mau`
3. `mau_by_country` (step 1)
4. `post_frequency`
5. `engagement_rate`
6. `content_type`
7. `active_posters`
8. `post_reach`
9. `activity_by_type_monthly`
10. `activity_distribution_current`
11. `activity_intensity_levels`

**Kratos Identity DB (2 queries):**
1. `login_velocity_hourly`
2. `unique_identities_daily`

---

## Critical Production Considerations

### ⚠️ Known Issues & Risks

1. **Cross-Database Query (MAU by Country)**
   - Requires 2-step process with app-layer merge
   - Person IDs may not match between databases
   - Currently shows "Unknown" for all countries due to ID mismatch
   - **Risk**: Query may fail or return incorrect data in prod

2. **PII Exposure**
   - **Active Posters chart**: Contains names and emails
   - **Top Posts table**: Contains post content and author names
   - **Action Required**: Hide these in production UI or implement proper access controls

3. **Kratos Production Database**
   - Login Velocity and Unique Identities queries hit PROD even in dev/kube mode
   - Currently hidden in UI by default (`.hidden-chart` CSS class)
   - **Risk**: Could expose production authentication patterns

4. **SQL Injection Vulnerabilities**
   - Some V2 endpoints use f-strings with user input
   - Example: `/v2/api/graph/company-network/<company_name>` uses `ILIKE '%{company_name}%'`
   - **Risk**: Potential SQL injection attack vector
   - **Status**: V2 endpoints not used in current dashboard

5. **Query Performance**
   - `profile_completion`: Uses subqueries for counts - could be slow on large datasets
   - All monthly queries use rolling 12-month windows - ensure indexes on `created_at`
   - **Recommendation**: Monitor slow query logs in production

6. **Data Inconsistencies**
   - `query_votes` table has NO `deleted_at` column (intentional, noted in queries)
   - Some queries assume UTC timestamps - verify timezone handling in prod

### ✅ Production Readiness Checklist

- [ ] Verify person ID mapping between engagement-platform-dev and chemlink-service-dev
- [ ] Implement PII redaction for Active Posters and Top Posts
- [ ] Review Kratos query necessity - consider removing or using dev Kratos
- [ ] Add database connection pooling for performance
- [ ] Implement query result caching (Redis/Memcached)
- [ ] Set up monitoring/alerting for slow queries
- [ ] Test all 34 charts with production data volumes
- [ ] Verify all `deleted_at IS NULL` filters are applied correctly
- [ ] Confirm timezone handling (UTC vs local)
- [ ] Load test dashboard with concurrent users

---

## V2 Routes (Not Used in Current Dashboard)

The codebase contains **18 V2 endpoints** (`/v2/api/*`) that query the `chemlink_analytics` database:

### V2 Basic Metrics (8 endpoints)
- `/v2/api/new-users/daily`
- `/v2/api/new-users/monthly`
- `/v2/api/growth-rate/monthly`
- `/v2/api/active-users/daily`
- `/v2/api/active-users/monthly`
- `/v2/api/engagement/daily`
- `/v2/api/engagement/monthly`
- `/v2/api/users/segmentation`

### V2 Graph Analytics (10 endpoints)
Query pre-aggregated `aggregates.*` schema tables (NOT actual Neo4j):
- `/v2/api/graph/connection-recommendations`
- `/v2/api/graph/connection-recommendations/<user_id>`
- `/v2/api/graph/company-network`
- `/v2/api/graph/company-network/<company_name>`
- `/v2/api/graph/skills-matching`
- `/v2/api/graph/skills-matching/<user_id>`
- `/v2/api/graph/career-paths`
- `/v2/api/graph/location-networks`
- `/v2/api/graph/alumni-networks`
- `/v2/api/graph/project-collaborations`

**Status**: These endpoints are implemented but NOT used by the dashboard UI. They require the `chemlink_analytics` database with `aggregates.*` schema tables.

---

## Architecture Notes

### Environment Configuration
- **Current Setting**: `APP_ENV=kube`
- **Effect**:
  - ChemLink queries → `chemlink-service-dev` (localhost:5433)
  - Engagement queries → `engagement-platform-dev` (localhost:5433)
  - Kratos queries → `chemonics-kratos-prd` (AWS RDS - PRODUCTION)

### Database Connection Functions
- `get_chemlink_env_connection()` - Routes to kube/dev/uat/prod based on APP_ENV
- `get_engagement_db_connection()` - Routes to kube/uat/prod based on APP_ENV
- `get_kratos_db_connection()` - Always uses PROD (fallback to env vars)
- `get_analytics_db_connection()` - Hardcoded to localhost:5432 `chemlink_analytics`

### Chart Rendering Technology
- **Library**: Chart.js 4.4.0
- **Method**: Dynamic data fetching via `/api/*` endpoints
- **Format**: All dates returned as ISO 8601 strings
- **Special Handling**: Custom `DateTimeEncoder` for Python datetime serialization

---

## File Locations

| File | Purpose |
|------|---------|
| `app.py` | Flask application with all API routes (lines 1-1612) |
| `sql_queries.py` | SQL query definitions in dictionary format |
| `db_config.py` | Database connection configuration |
| `templates/dashboard.html` | Main dashboard HTML with 34 chart containers |
| `static/js/dashboard.js` | Chart rendering and data fetching logic |
| `.env` | Database credentials and environment configuration |

---

## Maintenance & Updates

**To add a new chart:**
1. Add SQL query to `sql_queries.py` (optional, for documentation)
2. Create Flask route in `app.py` with appropriate database connection
3. Add chart container to `templates/dashboard.html`
4. Add chart rendering function to `static/js/dashboard.js`

**To change data source:**
1. Update `APP_ENV` in `.env` (kube/dev/uat/prod)
2. Verify database connection strings in `.env`
3. Test all endpoints to ensure data compatibility

---

**Document End**
