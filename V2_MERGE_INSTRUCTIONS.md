# V2 Merge Instructions

## What's Been Done
✅ Created `templates/v2/` folder
✅ Created `static/v2/` folder  
✅ Copied v2 template to `templates/v2/index.html`
✅ Copied v2 static files to `static/v2/`

## What You Need to Do

### 1. Add V2 Database Connection (at top of app.py after imports)

```python
# Add this after the existing imports and before the Flask app initialization
import psycopg2.extras as extras

def get_analytics_db_connection():
    """Connect to local analytics database for V2"""
    return psycopg2.connect(
        host=os.getenv('ANALYTICS_DB_HOST', 'localhost'),
        database='chemlink_analytics',
        user=os.getenv('ANALYTICS_DB_USER', 'postgres'),
        password=os.getenv('ANALYTICS_DB_PASSWORD', 'postgres'),
        cursor_factory=extras.RealDictCursor
    )

def execute_analytics_query(query):
    """Execute query on analytics DB and return results"""
    conn = get_analytics_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row[key] = value.isoformat()
            return results
    finally:
        conn.close()
```

### 2. Add V2 Routes (at the END of app.py, before `if __name__ == '__main__':`)

```python
# ============================================================================
# V2 DASHBOARD - AGGREGATED METRICS
# ============================================================================

@app.route('/v2')
def dashboard_v2():
    """V2 Dashboard using aggregated metrics"""
    return render_template('v2/index.html')

# Growth Metrics
@app.route('/v2/api/new-users/daily')
def v2_new_users_daily():
    query = """
        SELECT metric_date as date, new_signups, new_finder_signups, 
               new_standard_signups, total_users_cumulative
        FROM aggregates.daily_metrics
        WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY metric_date DESC;
    """
    return jsonify(execute_analytics_query(query))

@app.route('/v2/api/new-users/monthly')
def v2_new_users_monthly():
    query = """
        SELECT metric_month as month, new_signups, 
               total_users_end_of_month, growth_rate_pct
        FROM aggregates.monthly_metrics
        ORDER BY metric_month DESC;
    """
    return jsonify(execute_analytics_query(query))

@app.route('/v2/api/growth-rate/monthly')
def v2_growth_rate_monthly():
    query = """
        SELECT metric_month as month, new_signups, growth_rate_pct
        FROM aggregates.monthly_metrics
        ORDER BY metric_month DESC;
    """
    return jsonify(execute_analytics_query(query))

# Active Users
@app.route('/v2/api/active-users/daily')
def v2_active_users_daily():
    query = """
        SELECT metric_date as date, dau, active_posters, active_commenters,
               active_voters, active_collectors, engagement_rate
        FROM aggregates.daily_metrics
        WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY metric_date DESC;
    """
    return jsonify(execute_analytics_query(query))

@app.route('/v2/api/active-users/monthly')
def v2_active_users_monthly():
    query = """
        SELECT metric_month as month, mau, avg_dau, finder_mau,
               standard_mau, activation_rate
        FROM aggregates.monthly_metrics
        ORDER BY metric_month DESC;
    """
    return jsonify(execute_analytics_query(query))

# Engagement
@app.route('/v2/api/engagement/daily')
def v2_engagement_daily():
    query = """
        SELECT metric_date as date, posts_created, comments_created,
               votes_cast, collections_created, views_given,
               engagement_rate, social_engagement_rate
        FROM aggregates.daily_metrics
        WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY metric_date DESC;
    """
    return jsonify(execute_analytics_query(query))

@app.route('/v2/api/engagement/monthly')
def v2_engagement_monthly():
    query = """
        SELECT metric_month as month, total_posts, total_comments,
               total_votes, total_collections, avg_activities_per_user,
               avg_engagement_score, activation_rate
        FROM aggregates.monthly_metrics
        ORDER BY metric_month DESC;
    """
    return jsonify(execute_analytics_query(query))

# User Segmentation
@app.route('/v2/api/users/segmentation')
def v2_user_segmentation():
    query = """
        SELECT engagement_level, COUNT(*) as user_count,
               ROUND(AVG(engagement_score), 2) as avg_score,
               ROUND(AVG(total_activities), 2) as avg_activities
        FROM aggregates.user_engagement_levels
        GROUP BY engagement_level
        ORDER BY CASE engagement_level
            WHEN 'POWER_USER' THEN 1
            WHEN 'ACTIVE' THEN 2
            WHEN 'CASUAL' THEN 3
            WHEN 'LURKER' THEN 4
            ELSE 5 END;
    """
    return jsonify(execute_analytics_query(query))
```

### 3. Update static file references in templates/v2/index.html

Change:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<script src="{{ url_for('static', filename='dashboard.js') }}"></script>
```

To:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='v2/style.css') }}">
<script src="{{ url_for('static', filename='v2/dashboard.js') }}"></script>
```

### 4. Update API endpoints in static/v2/dashboard.js

Change all API endpoints from:
- `/api/...` → `/v2/api/...`

For example:
```javascript
// OLD
fetch('/api/new-users/monthly')

// NEW  
fetch('/v2/api/new-users/monthly')
```

### 5. Test It

```bash
./start.sh
```

Then access:
- V1: http://localhost:5000/
- V2: http://localhost:5000/v2

Both accessible through single ngrok URL! 🎯

## Summary

This approach keeps v1 **100% untouched** - all v2 code is isolated in:
- `templates/v2/` folder
- `static/v2/` folder
- V2 routes added at end of `app.py` with `/v2` prefix

Zero risk of breaking v1!
