# Post Reach - What We Have vs. What We Need

## 🎯 Business Pain Point
**"We don't know if valuable content is actually being seen by our community or getting buried"**

---

## 📊 What "Post Reach" Means

**Post Reach** = How many people actually **viewed** a post

**Why it matters:**
- A post with 1,000 views but 2 comments = high reach, low engagement
- A post with 10 views and 5 comments = low reach, high engagement
- Helps identify content that gets seen vs. content that gets buried

---

## 🟡 What We Have Now (Partial)

### Current Query #11 (Content Analysis):
```sql
SELECT 
    p.type,
    COUNT(*) as post_count,
    COUNT(DISTINCT p.person_id) as unique_authors,
    AVG(char_length(p.content)) as avg_content_length,
    COUNT(CASE WHEN p.link_url IS NOT NULL THEN 1 END) as posts_with_links,
    COUNT(CASE WHEN p.media_keys IS NOT NULL THEN 1 END) as posts_with_media,
    MIN(p.created_at) as first_post,
    MAX(p.created_at) as latest_post
FROM posts p
WHERE p.deleted_at IS NULL
GROUP BY p.type
ORDER BY post_count DESC;
```

**What this shows:**
- ✅ How many posts of each type exist
- ✅ Who's posting
- ✅ Content characteristics

**What this DOESN'T show:**
- ❌ How many people viewed each post
- ❌ Which posts get the most reach
- ❌ If content is being seen or ignored

---

## ❌ The Missing Piece: View Tracking

### What We Need to Measure Reach:

**Scenario:**
```
Post #1: "New feature announcement"
- Posted by: Sarah
- Views: 500 people saw it
- Comments: 12 people engaged

Post #2: "Random meme"  
- Posted by: Mike
- Views: 50 people saw it
- Comments: 15 people engaged
```

**Currently we can only see:**
- Post #1: 12 comments
- Post #2: 15 comments

**We CANNOT see:**
- Post #1: 500 views (high reach!)
- Post #2: 50 views (low reach)

---

## 🔧 What's Needed to Make This Complete

### Step 1: Add View Tracking Schema

**New table required:**
```sql
CREATE TABLE post_views (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    viewer_person_id INTEGER REFERENCES persons(id),
    viewed_at TIMESTAMP DEFAULT NOW(),
    view_duration_seconds INTEGER, -- Optional: how long they looked
    source VARCHAR(50), -- 'feed', 'profile', 'search', 'notification'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX idx_post_views_post ON post_views(post_id);
CREATE INDEX idx_post_views_viewer ON post_views(viewer_person_id);
CREATE INDEX idx_post_views_date ON post_views(viewed_at);
```

---

### Step 2: Track When Users View Posts

**Where to capture views:**

#### Frontend Implementation:
```javascript
// When a post appears on user's screen
function trackPostView(postId) {
    // Send to backend
    fetch('/api/analytics/post-view', {
        method: 'POST',
        body: JSON.stringify({
            post_id: postId,
            viewed_at: new Date(),
            source: 'feed' // or 'profile', 'search', etc.
        })
    });
}
```

#### When to Track:
1. **Post appears in feed** → Log view
2. **User clicks on post** → Log detailed view
3. **Post is visible for 2+ seconds** → Log engaged view (more accurate)

---

### Step 3: Enhanced Query With Reach Data

**Once we have view tracking, this query would work:**
```sql
-- Post Reach Analysis (FUTURE STATE)
SELECT 
    p.id,
    p.type,
    LEFT(p.content, 100) as preview,
    author.first_name || ' ' || author.last_name as author_name,
    p.created_at,
    -- REACH METRICS
    COUNT(DISTINCT pv.viewer_person_id) as unique_views,
    COUNT(DISTINCT c.person_id) as unique_commenters,
    COUNT(c.id) as total_comments,
    -- ENGAGEMENT RATE
    ROUND((COUNT(DISTINCT c.person_id)::float / 
           NULLIF(COUNT(DISTINCT pv.viewer_person_id), 0) * 100), 2) as engagement_rate_pct
FROM posts p
JOIN persons author ON p.person_id = author.id
LEFT JOIN post_views pv ON p.id = pv.post_id
LEFT JOIN comments c ON p.id = c.post_id AND c.deleted_at IS NULL
WHERE p.deleted_at IS NULL
    AND p.created_at >= NOW() - INTERVAL '7 days'
GROUP BY p.id, p.type, p.content, author.first_name, author.last_name, p.created_at
ORDER BY unique_views DESC
LIMIT 20;
```

**Example Output:**
| Post | Author | Views | Comments | Engagement Rate |
|------|--------|-------|----------|-----------------|
| "New Feature..." | Sarah | 500 | 12 | 2.4% |
| "Industry News..." | Mike | 350 | 8 | 2.3% |
| "Random Meme" | Tom | 50 | 15 | 30% |

---

## 🎯 High-Level Requirements Summary

### What's Needed:

#### 1. **Database Changes** (Data Architect - YOU)
- Design `post_views` table schema ✅ (provided above)
- Define indexes for performance
- Document data retention policy (keep 90 days? 1 year?)

#### 2. **Backend Implementation** (Data Engineer)
- Create API endpoint to receive view events
- Implement view logging
- Add deduplication (don't count same user viewing twice in 1 minute)
- Set up batch processing for high volume

#### 3. **Frontend Integration** (Frontend Team)
- Add tracking code when posts are displayed
- Implement "in viewport" detection
- Send view events to backend API

#### 4. **Analytics Queries** (Data Analyst - uses your design)
- Run reach analysis queries
- Build dashboard visualizations
- Create reports on content performance

---

## 📋 Implementation Effort Estimate

| Task | Owner | Effort | Timeline |
|------|-------|--------|----------|
| **Schema Design** | Data Architect (YOU) | Low | ✅ Done (see above) |
| **Backend API** | Data Engineer | Medium | 1-2 weeks |
| **Frontend Tracking** | Frontend Dev | Medium | 1-2 weeks |
| **Query Development** | Data Analyst | Low | 2-3 days |
| **Dashboard Build** | Data Analyst | Medium | 1 week |
| **Testing & Validation** | All | Medium | 1 week |
| **Total** | - | - | **3-5 weeks** |

---

## 💡 Alternative: Use Comments as Proxy (Interim Solution)

### What You Can Measure NOW (Without View Tracking):

**Proxy Metric: Comment Engagement**
```sql
-- Posts with most engagement (using comments as proxy for reach)
SELECT 
    p.id,
    LEFT(p.content, 100) as preview,
    author.first_name || ' ' || author.last_name as author,
    COUNT(c.id) as comment_count,
    COUNT(DISTINCT c.person_id) as unique_commenters,
    p.created_at
FROM posts p
JOIN persons author ON p.person_id = author.id
LEFT JOIN comments c ON p.id = c.post_id AND c.deleted_at IS NULL
WHERE p.deleted_at IS NULL
GROUP BY p.id, p.content, author.first_name, author.last_name, p.created_at
ORDER BY comment_count DESC
LIMIT 20;
```

**What this tells you:**
- Which posts get the most discussion
- Popular content (even without view counts)
- Content that drives engagement

**Limitation:**
- Doesn't show posts with high views but low comments
- Can't measure true "reach"

---

## 📊 Dashboard Mockup (Future State)

### With View Tracking:
```
┌─────────────────────────────────────────┐
│  TOP POSTS BY REACH (Last 7 Days)      │
├─────────────────────────────────────────┤
│                                         │
│  1. "New Feature Launch"                │
│     👁️ 1,250 views  💬 45 comments     │
│     Engagement: 3.6%                    │
│                                         │
│  2. "Industry Analysis"                 │
│     👁️ 890 views  💬 23 comments       │
│     Engagement: 2.6%                    │
│                                         │
│  3. "Team Update"                       │
│     👁️ 650 views  💬 12 comments       │
│     Engagement: 1.8%                    │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🎯 What to Say in Your Update

### Simple Version:
**"Post Reach requires view tracking infrastructure that doesn't exist yet. Currently, we can only measure comment engagement as a proxy. To get true reach metrics, we need to add a post_views table and implement frontend tracking when posts are displayed. This is a 3-5 week effort involving backend, frontend, and analytics work."**

### Detailed Version:
**"Query #11 gives us content analysis, but it can't measure reach because we don't track post views. To complete this metric, I've designed a post_views table schema and documented the tracking requirements. Implementation requires: (1) backend API to capture view events, (2) frontend code to detect when posts are displayed, and (3) analytics queries to measure reach and engagement rates. As an interim solution, we can use comment counts as a proxy for engagement, but it won't show us true view-based reach."**

---

## ✅ Your Deliverable as Data Architect

### What You've Provided:
1. ✅ **Schema Design** - `post_views` table specification
2. ✅ **Gap Analysis** - What's missing and why
3. ✅ **Query Design** - Future-state reach analysis query
4. ✅ **Requirements** - What each team needs to do
5. ✅ **Effort Estimate** - 3-5 weeks total implementation
6. ✅ **Interim Solution** - Proxy metric using comments

### What Happens Next:
- **Data Engineer** builds the view tracking system
- **Frontend Team** adds tracking code
- **Data Analyst** builds dashboard with your queries

---

## 🚨 Key Decision Points

### Before Implementation, Decide:

1. **Granularity**: Track every view or only "engaged views" (2+ seconds)?
2. **Deduplication**: Count multiple views by same user in same session?
3. **Privacy**: Store individual viewer IDs or aggregate counts?
4. **Performance**: Real-time tracking or batch processing?
5. **Retention**: Keep view data for 30 days? 1 year? Forever?

---

*This is a classic "instrumentation gap" - the data architecture is straightforward, but requires cross-team implementation to capture the view events. Your job as Data Architect is done once you've designed the schema and documented requirements.* ✅