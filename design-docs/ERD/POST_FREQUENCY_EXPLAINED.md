# Post Frequency Metric - Simple Explanation

## 🎯 The Business Pain Point
**"We can't tell if our platform is gaining momentum or if community activity is declining over time"**

---

## 📊 What This Metric Measures
**Post Frequency** = How much content is being created daily/weekly on the platform

**Why it matters:**
- Shows if your community is growing or dying
- Detects trends (increasing activity = momentum, decreasing = problem)
- Helps predict if you need intervention (community revival campaigns)
- Measures platform health over time

---

## ✅ What the Query Does

**Query #14 from engagement-platform.sql:**

```sql
SELECT 
    DATE(created_at) as post_date,
    COUNT(*) as posts_created,
    COUNT(DISTINCT person_id) as active_users,
    COUNT(CASE WHEN type = 'text' THEN 1 END) as text_posts,
    COUNT(CASE WHEN type = 'link' THEN 1 END) as link_posts,
    COUNT(CASE WHEN type = 'image' THEN 1 END) as image_posts,
    COUNT(CASE WHEN type = 'file' THEN 1 END) as file_posts,
    STRING_AGG(DISTINCT (SELECT first_name || ' ' || last_name FROM persons WHERE id = posts.person_id), ', ') as active_users_list
FROM posts
WHERE deleted_at IS NULL
GROUP BY DATE(created_at)
ORDER BY post_date DESC
LIMIT 30;
```

---

## 🔍 What This Query Returns

### Example Output (Last 7 Days):

| Date | Posts | Active Users | Text | Link | Image | File |
|------|-------|--------------|------|------|-------|------|
| Oct 21 | 45 | 18 | 25 | 12 | 6 | 2 |
| Oct 20 | 38 | 15 | 20 | 10 | 6 | 2 |
| Oct 19 | 52 | 22 | 30 | 15 | 5 | 2 |
| Oct 18 | 41 | 16 | 24 | 11 | 4 | 2 |
| Oct 17 | 35 | 14 | 20 | 9 | 5 | 1 |
| Oct 16 | 29 | 12 | 18 | 7 | 3 | 1 |
| Oct 15 | 48 | 19 | 28 | 13 | 6 | 1 |

**What each column means:**
- **Date**: The day posts were created
- **Posts**: Total number of posts that day
- **Active Users**: How many different people posted
- **Text/Link/Image/File**: Breakdown by content type
- **Active Users List**: Names of who posted (helpful for small communities)

---

## 📈 What the Data Tells You

### Scenario 1: Growing Platform ✅
```
Oct 15: 20 posts
Oct 16: 25 posts
Oct 17: 30 posts
Oct 18: 35 posts
Oct 19: 42 posts
```
**Interpretation:** Activity increasing = platform gaining momentum

### Scenario 2: Declining Platform ⚠️
```
Oct 15: 50 posts
Oct 16: 42 posts
Oct 17: 35 posts
Oct 18: 28 posts
Oct 19: 20 posts
```
**Interpretation:** Activity decreasing = need intervention

### Scenario 3: Stable Platform ➡️
```
Oct 15: 30 posts
Oct 16: 32 posts
Oct 17: 29 posts
Oct 18: 31 posts
Oct 19: 30 posts
```
**Interpretation:** Consistent activity = healthy equilibrium

### Scenario 4: Weekend Effect 📅
```
Mon: 45 posts
Tue: 42 posts
Wed: 40 posts
Thu: 38 posts
Fri: 35 posts
Sat: 15 posts ⬇️
Sun: 12 posts ⬇️
```
**Interpretation:** Normal weekly pattern (work-related platform)

---

## 📊 How to Visualize This Data

### Option 1: Line Chart (Best for Trends)
```
Posts Per Day (Last 30 Days)

60 |              ●
50 |         ●    |    ●
40 |    ●    |    |    |    ●
30 | ●  |    |    |    |    |  ●
20 |_|__|____|____|____|____|___|____
   Day1 Day5 Day10 Day15 Day20 Day25 Day30
```

**Shows:** Overall trend up or down

---

### Option 2: Calendar Heatmap (Best for Patterns)
```
October 2025

Sun Mon Tue Wed Thu Fri Sat
 1   2   3   4   5   6   7
🟢  🟢  🟡  🟢  🟢  🔴  🔴
 8   9  10  11  12  13  14
🟢  🟢  🟢  🟢  🟡  🔴  🔴
15  16  17  18  19  20  21
🟢  🟢  🟢  🟢  🟢  🟡  🔴

🟢 = High activity (40+ posts)
🟡 = Medium activity (20-39 posts)
🔴 = Low activity (<20 posts)
```

**Shows:** Daily patterns, weekends vs. weekdays

---

### Option 3: Metric Cards (Best for Dashboard)
```
┌─────────────────────────┐  ┌─────────────────────────┐
│  POSTS THIS WEEK        │  │  TREND vs LAST WEEK     │
│                         │  │                         │
│      285  ↗ +15%       │  │      ↗ GROWING         │
│                         │  │                         │
│  Daily Avg: 41 posts    │  │  Last Week: 248 posts   │
└─────────────────────────┘  └─────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐
│  ACTIVE POSTERS         │  │  MOST POPULAR TYPE      │
│                         │  │                         │
│      75 users           │  │      📝 Text (55%)     │
│                         │  │                         │
│  Avg per user: 3.8 posts│  │  🔗 Link (30%)         │
└─────────────────────────┘  └─────────────────────────┘
```

---

### Option 4: Bar Chart (Best for Type Breakdown)
```
Content Type Distribution (Last 7 Days)

Text  ████████████████████ 160 posts (55%)
Link  ████████████ 85 posts (30%)
Image ████ 35 posts (12%)
File  ██ 10 posts (3%)
```

---

## 🎯 How to Use This Data

### 1. **Momentum Monitoring**
Run weekly to see if activity is increasing:
```sql
-- Weekly summary
SELECT 
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) as posts,
    COUNT(DISTINCT person_id) as active_users
FROM posts
WHERE deleted_at IS NULL
GROUP BY week
ORDER BY week DESC
LIMIT 8;
```

### 2. **Detect Decline Early**
Set alerts when daily posts drop below threshold:
```
Target: 30+ posts per day
Alert: If posts < 20 for 3 consecutive days
```

### 3. **Content Strategy**
See which content types are popular:
- If images dominate → focus on visual features
- If text dominates → focus on discussion features
- If links dominate → users are sharing external content

### 4. **Identify Peak Times**
Find best times to launch campaigns:
```
Monday-Friday: 40+ posts/day (high activity)
Saturday-Sunday: 15 posts/day (low activity)

→ Launch campaigns on Monday morning
```

---

## 💡 What to Say in Your Update

### Simple Version:
**"Post Frequency is production-ready. Query #14 shows daily post counts, active users, and content type breakdown for the last 30 days. We can use this immediately to track if community activity is growing or declining over time."**

### Detailed Version:
**"The query tracks daily posting activity with breakdowns by content type (text, link, image, file) and shows how many unique users posted each day. This gives us a clear view of platform momentum - whether we're seeing increasing, decreasing, or stable activity. Perfect for building a calendar heatmap or trend chart to visualize community health. No modifications needed."**

---

## ✅ Why This Query is "Excellent"

### Complete data tracking:
- ✅ **Daily granularity**: See activity by day
- ✅ **User count**: Know how many people are active
- ✅ **Content types**: Understand what users post
- ✅ **Active users list**: See who's contributing
- ✅ **30-day view**: Enough data to spot trends

### Production ready:
- Works with existing schema
- Performs well (simple GROUP BY)
- Output is dashboard-ready
- No modifications needed

---

## 🚨 Red Flags to Watch For

### Warning Signs:
1. **Declining daily posts** (50 → 40 → 30 → 20)
   - **Action**: Launch re-engagement campaign

2. **Declining active users** (posts stay same, but fewer people posting)
   - **Action**: Few power users carrying the platform, need to engage more users

3. **Weekend ghost town** (5 posts on Sat/Sun vs. 50 on weekdays)
   - **Action**: Either normal pattern or opportunity to drive weekend engagement

4. **Content type concentration** (95% text, 5% everything else)
   - **Action**: Feature diversity may not be working

---

## 🚀 Next Steps

1. **Run the query** - See last 30 days of activity
2. **Calculate baseline** - What's your daily average?
3. **Identify trends** - Growing, stable, or declining?
4. **Set targets** - What's your goal posts/day?
5. **Build visualization** - Line chart or calendar heatmap
6. **Monitor weekly** - Track if you're hitting targets

---

## 📋 Quick Analysis Questions You Can Answer

✅ **"How many posts per day on average?"**
```sql
SELECT AVG(daily_count) FROM (
    SELECT DATE(created_at), COUNT(*) as daily_count 
    FROM posts 
    WHERE deleted_at IS NULL 
    GROUP BY DATE(created_at)
) daily_posts;
```

✅ **"What's our busiest day of the week?"**
```sql
SELECT 
    TO_CHAR(created_at, 'Day') as day_of_week,
    COUNT(*) as posts
FROM posts
WHERE deleted_at IS NULL
GROUP BY TO_CHAR(created_at, 'Day')
ORDER BY posts DESC;
```

✅ **"Are we growing month-over-month?"**
```sql
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as posts,
    LAG(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', created_at)) as prev_month
FROM posts
WHERE deleted_at IS NULL
GROUP BY month
ORDER BY month DESC;
```

---

*This metric is your platform's heartbeat. If posts are increasing, you're growing. If declining, you need to act fast. This query makes it easy to monitor continuously.*