# Average Session Duration - Analysis Required

## 🎯 Business Pain Point
**"We don't know if users find our platform engaging enough to spend meaningful time, or if they bounce quickly"**

---

## 📊 What We Need to Measure
**Average Session Duration** = How long users spend on the platform per visit

---

## 🔍 Analysis Work Required

### Step 1: Understand Current Authentication System
**Questions to Answer:**
1. **How do users log in?**
   - JWT tokens? Session cookies? OAuth?
   - Where is authentication handled? (frontend, backend, middleware)

2. **Are login events currently logged?**
   - Check if there's a login timestamp anywhere
   - Look for authentication service logs
   - Check if IAM system tracks logins

3. **Are logout events captured?**
   - Explicit logout button clicks
   - Session expiration events
   - Token refresh activities

**Action Items:**
- [ ] Review authentication code/service
- [ ] Check for existing login/logout logs
- [ ] Interview backend engineers about auth flow

---

### Step 2: Identify Activity Indicators
**What Counts as "Active"?**

If we don't have explicit session tracking, we can **infer activity** from:

| Activity Type | Data Source | Indicates User is Active |
|--------------|-------------|-------------------------|
| **Posts Created** | `posts.created_at` | User was on platform |
| **Comments Made** | `comments.created_at` | User was on platform |
| **Profile Updates** | `persons.updated_at` | User was on platform |
| **Search Queries** | `query_embeddings.created_at` | User was searching |
| **Collections Created** | `collections.created_at` | User was organizing |

**Action Items:**
- [ ] Map all user-generated actions to timestamps
- [ ] Determine activity timeout threshold (e.g., 30 min of inactivity = session end)

---

### Step 3: Define Session Logic
**How to Calculate a "Session":**

```
Session Start: First activity timestamp
Session End: Last activity timestamp (before 30+ min gap)
Duration: End time - Start time
```

**Example:**
```
User actions on Oct 22:
9:00 AM - Login
9:05 AM - View profiles
9:10 AM - Create post
9:45 AM - Comment on post
[45 min gap - no activity]
10:30 AM - New login (NEW SESSION)

Session 1 Duration: 45 minutes (9:00 AM - 9:45 AM)
Session 2 Duration: [ongoing]
```

**Action Items:**
- [ ] Define inactivity timeout (typically 30 minutes)
- [ ] Write session grouping logic
- [ ] Test on sample user data

---

### Step 4: Schema Design
**What Database Changes Are Needed:**

#### Option A: Simple Tracking (Minimal Effort)
```sql
-- Add to existing persons table
ALTER TABLE persons 
ADD COLUMN last_login_at TIMESTAMP,
ADD COLUMN last_activity_at TIMESTAMP;
```

**Implementation:**
- Update `last_login_at` on authentication
- Update `last_activity_at` on any user action
- Calculate session duration = `last_activity_at - last_login_at`

**Pros:** Quick to implement
**Cons:** Only tracks current session, no historical data

---

#### Option B: Full Session Tracking (Comprehensive)
```sql
-- New table to track all sessions
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES persons(id),
    session_id VARCHAR(100) UNIQUE,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    device_type VARCHAR(50),
    browser VARCHAR(50),
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX idx_sessions_person_started ON user_sessions(person_id, started_at);
```

**Implementation:**
- Create session on login
- Update `ended_at` on logout or timeout
- Calculate duration on session end

**Pros:** Full historical data, accurate tracking
**Cons:** More development effort

---

### Step 5: Integration Points
**Where to Capture Session Data:**

1. **Authentication Service**
   - Log all login events with timestamp
   - Generate session ID
   - Track device/browser info

2. **API Middleware**
   - Update `last_activity_at` on every API call
   - Detect session timeouts
   - Handle logout events

3. **Frontend Tracking**
   - Send heartbeat every 5 minutes while user is active
   - Detect tab close/browser close
   - Track idle time

**Action Items:**
- [ ] Identify authentication service location
- [ ] Review API architecture for middleware options
- [ ] Assess frontend tracking capabilities

---

### Step 6: Data Validation
**What to Check Before Going Live:**

1. **Data Quality**
   - Are sessions being created correctly?
   - Do session durations make sense? (not 0 seconds, not 24+ hours)
   - Are timeouts working properly?

2. **Performance Impact**
   - Does tracking slow down API responses?
   - Can database handle session write volume?
   - Do queries run fast enough for dashboards?

3. **Edge Cases**
   - User closes browser without logout
   - User opens multiple tabs
   - Session timeout during active use

**Action Items:**
- [ ] Create test scenarios
- [ ] Run pilot with subset of users
- [ ] Monitor performance metrics

---

## 📋 Summary of Analysis Tasks

### Phase 1: Investigation (Week 1)
- [ ] **Audit current auth system** - How do logins work today?
- [ ] **Map activity indicators** - What actions do users take?
- [ ] **Define session logic** - When does a session start/end?
- [ ] **Estimate data volume** - How many sessions/day do we expect?

### Phase 2: Design (Week 2)
- [ ] **Choose implementation approach** (Option A vs B)
- [ ] **Design schema changes** - Write SQL DDL statements
- [ ] **Plan integration points** - Where to add tracking code?
- [ ] **Document edge cases** - How to handle special scenarios?

### Phase 3: Development (Weeks 3-4)
- [ ] **Implement session tracking** - Backend changes
- [ ] **Add frontend instrumentation** - Track user activity
- [ ] **Create analytics queries** - Calculate average duration
- [ ] **Build dashboard views** - Visualize the data

### Phase 4: Validation (Week 5)
- [ ] **Test with sample users** - Verify accuracy
- [ ] **Monitor performance** - Check for bottlenecks
- [ ] **Adjust timeout thresholds** - Fine-tune session logic
- [ ] **Launch to production** - Roll out to all users

---

## 🎯 Deliverables from Analysis

### Documentation:
1. **Auth System Flow Diagram** - Visual map of how authentication works
2. **Session Definition Document** - Clear rules for session start/end
3. **Schema Design Proposal** - SQL scripts for database changes
4. **Integration Plan** - Where and how to add tracking code

### Queries:
```sql
-- Once data exists, this query will work:
SELECT 
    person_id,
    AVG(duration_minutes) as avg_session_duration,
    COUNT(*) as total_sessions
FROM user_sessions
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY person_id;
```

### Dashboard Mockup:
```
┌─────────────────────────────┐
│ AVERAGE SESSION DURATION    │
│                             │
│     23 minutes              │
│     ↗ +5 min from last week │
│                             │
│ [Line chart: daily avg]     │
└─────────────────────────────┘
```

---

## ⏱️ Time Estimate

| Task | Effort Level | Time Estimate |
|------|-------------|---------------|
| **Investigation** | Low | 2-3 days |
| **Design** | Medium | 3-5 days |
| **Development** | High | 2-3 weeks |
| **Validation** | Medium | 1 week |
| **Total** | - | **4-6 weeks** |

---

## 💡 Quick Win Alternative

**If 4-6 weeks is too long:**

Use **proxy metrics** from existing data:
- Profile update frequency
- Post/comment activity patterns  
- Search query timestamps

**Approximate session duration:**
```sql
-- Rough estimate using existing activity
WITH user_activity AS (
    SELECT person_id, created_at as activity_at FROM posts
    UNION ALL
    SELECT person_id, created_at FROM comments
    UNION ALL
    SELECT person_id, created_at FROM query_embeddings
)
SELECT 
    person_id,
    DATE(activity_at) as day,
    MAX(activity_at) - MIN(activity_at) as estimated_session_duration
FROM user_activity
GROUP BY person_id, DATE(activity_at);
```

**Pros:** Works with existing data today
**Cons:** Less accurate, misses passive browsing time

---

*Bottom line: Full session tracking requires significant development effort. Start with investigation phase to understand feasibility and timeline for your specific system.*