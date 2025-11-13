# New Users Metric - Simple Explanation

## 🎯 The Business Pain Point
**"We don't know if our marketing efforts are working or how fast we're acquiring users compared to competitors"**

---

## 📊 How These Queries Solve It

### Query 1: Recent User List
```sql
SELECT 
    id,
    first_name || ' ' || last_name as full_name,
    email,
    has_finder,
    (SELECT COUNT(*) FROM experiences WHERE person_id = p.id AND deleted_at IS NULL) as experience_count,
    (SELECT COUNT(*) FROM education WHERE person_id = p.id AND deleted_at IS NULL) as education_count,
    (SELECT COUNT(*) FROM embeddings WHERE person_id = p.id AND deleted_at IS NULL) as embedding_count,
    created_at
FROM persons p
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 20;
```

**What it does:**
- Shows the **most recent 20 users** who signed up
- Lists their names, emails, and when they joined (`created_at`)
- Shows how complete their profiles are (experiences, education, embeddings)

**Why it's useful:**
- See **who** is signing up in real-time
- Check if new users are completing their profiles
- Spot patterns (are they mostly recruiters? job seekers? complete vs incomplete profiles?)

---

### Query 2: Weekly User Growth Trend
```sql
SELECT 
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) as new_users
FROM persons 
WHERE deleted_at IS NULL
GROUP BY week ORDER BY week DESC;
```

**What it does:**
- Counts how many new users signed up **each week**
- Groups all signups by week and counts them
- Orders from most recent week to oldest

**Why it's useful:**
- See if signups are **increasing or decreasing** over time
- Spot trends: "We jumped from 10 users/week to 30 users/week after our marketing campaign"
- Compare weeks to see growth patterns

---

## 🎨 How to Present This Data

### Option 1: Line Chart (Best for Trends)
**Visual:** Line graph showing weekly signups over time

```
New Users Per Week

50 |                    ●
   |                 ●
40 |              ●
   |           ●
30 |        ●
   |     ●
20 |  ●
   |________________________
   Week1 Week2 Week3 Week4
```

**Key Insights to Show:**
- "We grew from 20 to 50 new users per week (150% growth)"
- "Signups increased after [marketing campaign name] launched"
- "Consistent upward trend shows market demand"

---

### Option 2: Bar Chart (Best for Comparison)
**Visual:** Bars showing each week's signup count

```
New Users Per Week

Week 1: ████████ (20)
Week 2: ████████████ (30)
Week 3: ████████████████ (40)
Week 4: ████████████████████ (50)
```

**Key Insights to Show:**
- Week-over-week growth percentage
- Highlight biggest growth week
- Show trajectory toward goals

---

### Option 3: Metric Card + Sparkline (Best for Dashboard)
**Visual:** Big number with mini trend graph

```
┌──────────────────────────┐
│  NEW USERS THIS WEEK     │
│                          │
│        45  ↗ +25%       │
│     [mini line graph]    │
│                          │
│  Last Week: 36           │
│  This Month: 180         │
└──────────────────────────┘
```

**Key Insights to Show:**
- Current week's total (big number)
- % change from last week
- Mini trend shows direction (up/down)

---

### Option 4: Table (Best for Detailed Review)
**Visual:** Simple table with key numbers

| Week Starting | New Users | Growth vs Last Week | Notes |
|---------------|-----------|---------------------|-------|
| Oct 14, 2025  | 50        | +25% ↗             | Campaign launch |
| Oct 7, 2025   | 40        | +33% ↗             | Strong momentum |
| Sep 30, 2025  | 30        | +50% ↗             | First jump |
| Sep 23, 2025  | 20        | -                  | Baseline |

---

## 💡 How This Answers the Pain Point

### Before (Pain Point):
❌ "Did our Facebook ads work?" → **No idea**  
❌ "Are we growing faster this month?" → **Just guessing**  
❌ "How many users signed up after the email campaign?" → **Can't tell**

### After (With These Queries):
✅ "Did our Facebook ads work?" → **Yes! Signups jumped 25% the week they ran**  
✅ "Are we growing faster this month?" → **Yes! 150% growth month-over-month**  
✅ "How many users signed up after the email campaign?" → **45 new users that week vs. 20 the week before**

---

## 📋 What to Say in Your Presentation

### Simple Version:
**"These queries show us user acquisition trends. We can see how many people sign up each week and track if that number is growing or shrinking. This tells us if our marketing is working."**

### More Detailed Version:
**"We track new user registrations by week. The first query shows us the most recent signups so we can see who's joining and how engaged they are. The second query gives us trend data - are we growing 10% per week or 50% per week? This lets us measure marketing effectiveness and compare our growth to industry benchmarks."**

---

## 🎯 Recommended Dashboard Layout

```
┌─────────────────────────────────────────────┐
│  GROWTH OVERVIEW                            │
├─────────────────────────────────────────────┤
│                                             │
│  📈 NEW USERS THIS WEEK                     │
│     45        ↗ +25%                        │
│                                             │
│  📊 WEEKLY GROWTH TREND                     │
│     [Line chart: last 8 weeks]              │
│                                             │
│  👥 RECENT SIGNUPS                          │
│     [Table: last 10 users with dates]       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## ✅ Next Steps to Make This Real

1. **Run Query 2** → Get actual weekly numbers
2. **Pick a visualization** → Start with simple line chart
3. **Add context** → Label when marketing campaigns happened
4. **Set a goal** → "We want 100 new users/week by December"
5. **Track weekly** → Update the chart every Monday

---

*This metric is your baseline for measuring all marketing and growth initiatives. Without it, you're flying blind. With it, you can make data-driven decisions about where to invest your marketing budget.*