from flask import Flask, jsonify, render_template
from flask_cors import CORS
from db_config import get_engagement_db_connection, get_chemlink_db_connection, execute_query
import json
from datetime import datetime
from sql_queries import SQL_QUERIES

app = Flask(__name__)
CORS(app)

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = DateTimeEncoder

# ============================================================================
# GROWTH METRICS ROUTES
# ============================================================================

@app.route('/api/new-users/daily')
def new_users_daily():
    """Get new user sign-ups for the current day"""
    query = """
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
          AND DATE(created_at) = CURRENT_DATE
        ORDER BY created_at DESC;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/new-users/weekly')
def new_users_weekly():
    """Get new user sign-ups by week"""
    query = """
        SELECT 
            DATE_TRUNC('week', created_at) as week,
            COUNT(*) as new_users
        FROM persons 
        WHERE deleted_at IS NULL
        GROUP BY week 
        ORDER BY week DESC
        LIMIT 12;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/new-users/monthly')
def new_users_monthly():
    """Get new user sign-ups by month (rolling 12 months)"""
    query = """
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            COUNT(*) as new_users
        FROM persons 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        GROUP BY month 
        ORDER BY month DESC;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/growth-rate/weekly')
def growth_rate_weekly():
    """Get weekly growth rate"""
    query = """
        WITH weekly_users AS (
            SELECT DATE_TRUNC('week', created_at) as week,
                   COUNT(*) as new_users
            FROM persons WHERE deleted_at IS NULL
            GROUP BY week
        )
        SELECT 
            week, 
            new_users,
            LAG(new_users) OVER (ORDER BY week) as prev_week,
            ROUND(((new_users - LAG(new_users) OVER (ORDER BY week)) * 100.0 / 
                   NULLIF(LAG(new_users) OVER (ORDER BY week), 0)), 2) as growth_rate_pct
        FROM weekly_users 
        ORDER BY week DESC
        LIMIT 12;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/growth-rate/monthly')
def growth_rate_monthly():
    """Get monthly growth rate (rolling 12 months)"""
    query = """
        WITH monthly_users AS (
            SELECT DATE_TRUNC('month', created_at) as month,
                   COUNT(*) as new_users
            FROM persons 
            WHERE deleted_at IS NULL
              AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
            GROUP BY month
        )
        SELECT 
            month, 
            new_users,
            LAG(new_users) OVER (ORDER BY month) as prev_month,
            ROUND(((new_users - LAG(new_users) OVER (ORDER BY month)) * 100.0 / 
                   NULLIF(LAG(new_users) OVER (ORDER BY month), 0)), 2) as growth_rate_pct
        FROM monthly_users 
        ORDER BY month DESC;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/active-users/daily')
def active_users_daily():
    """Get daily active users (DAU)"""
    query = """
        SELECT 
            DATE(activity_date) as date,
            COUNT(DISTINCT person_id) as active_users,
            COUNT(CASE WHEN activity_type = 'post' THEN 1 END) as users_who_posted,
            COUNT(CASE WHEN activity_type = 'comment' THEN 1 END) as users_who_commented
        FROM (
            SELECT person_id, created_at as activity_date, 'post' as activity_type 
            FROM posts WHERE deleted_at IS NULL
            UNION ALL
            SELECT person_id, created_at, 'comment' 
            FROM comments WHERE deleted_at IS NULL
        ) daily_activity
        WHERE activity_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(activity_date)
        ORDER BY date DESC;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/active-users/weekly')
def active_users_weekly():
    """Get weekly active users (WAU)"""
    query = """
        SELECT 
            DATE_TRUNC('week', activity_date) as week,
            COUNT(DISTINCT person_id) as active_users
        FROM (
            SELECT person_id, created_at as activity_date FROM posts WHERE deleted_at IS NULL
            UNION ALL
            SELECT person_id, created_at FROM comments WHERE deleted_at IS NULL
        ) weekly_activity
        GROUP BY week
        ORDER BY week DESC
        LIMIT 12;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/active-users/monthly')
def active_users_monthly():
    """Get monthly active users (MAU)"""
    query = """
        SELECT 
            DATE_TRUNC('month', activity_date) as month,
            COUNT(DISTINCT person_id) as active_users
        FROM (
            SELECT person_id, created_at as activity_date 
            FROM posts WHERE deleted_at IS NULL
            UNION ALL
            SELECT person_id, created_at 
            FROM comments WHERE deleted_at IS NULL
        ) monthly_activity
        GROUP BY DATE_TRUNC('month', activity_date)
        ORDER BY month DESC
        LIMIT 12;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/active-users/monthly-by-country')
def active_users_monthly_by_country():
    """Get monthly active users by country using cross-database join"""
    # Step 1: Get MAU from engagement database
    engagement_query = """
        SELECT 
            DATE_TRUNC('month', activity_date) as month,
            person_id,
            COUNT(CASE WHEN activity_type = 'post' THEN 1 END) as posts,
            COUNT(CASE WHEN activity_type = 'comment' THEN 1 END) as comments
        FROM (
            SELECT person_id, created_at as activity_date, 'post' as activity_type 
            FROM posts WHERE deleted_at IS NULL
            UNION ALL
            SELECT person_id, created_at, 'comment' 
            FROM comments WHERE deleted_at IS NULL
        ) monthly_activity
        GROUP BY DATE_TRUNC('month', activity_date), person_id
        ORDER BY month DESC;
    """
    
    conn_engagement = get_engagement_db_connection()
    engagement_data = execute_query(conn_engagement, engagement_query)
    
    # Step 2: Get location data from chemlink database
    # Get unique person_ids from engagement data
    person_ids = list(set([row['person_id'] for row in engagement_data]))
    
    if not person_ids:
        return jsonify([])
    
    # Safely construct IN clause for SQL - convert both sides to text for comparison
    id_placeholders = ','.join(['%s'] * len(person_ids))
    location_query = f"""
        SELECT 
            p.id::text as person_id,
            COALESCE(l.country, 'Unknown') as country
        FROM persons p
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE p.id::text IN ({id_placeholders})
          AND p.deleted_at IS NULL;
    """
    
    conn_chemlink = get_chemlink_db_connection()
    location_data = execute_query(conn_chemlink, location_query, person_ids)
    
    # Step 3: Create a lookup dictionary for person_id -> country
    country_lookup = {row['person_id']: row['country'] for row in location_data}
    
    # Step 4: Combine the data
    result_dict = {}
    for row in engagement_data:
        month = row['month']
        person_id = row['person_id']
        country = country_lookup.get(person_id, 'Unknown')
        
        key = (str(month), country)
        if key not in result_dict:
            result_dict[key] = {
                'month': month,
                'country': country,
                'active_users': set(),
                'total_posts': 0,
                'total_comments': 0,
                'users_who_posted': set(),
                'users_who_commented': set()
            }
        
        result_dict[key]['active_users'].add(person_id)
        result_dict[key]['total_posts'] += row['posts']
        result_dict[key]['total_comments'] += row['comments']
        
        if row['posts'] > 0:
            result_dict[key]['users_who_posted'].add(person_id)
        if row['comments'] > 0:
            result_dict[key]['users_who_commented'].add(person_id)
    
    # Step 5: Convert to final format
    results = []
    for (month, country), data in result_dict.items():
        results.append({
            'month': month,
            'country': country,
            'active_users': len(data['active_users']),
            'total_posts': data['total_posts'],
            'total_comments': data['total_comments'],
            'users_who_posted': len(data['users_who_posted']),
            'users_who_commented': len(data['users_who_commented'])
        })
    
    # Sort by month descending, then active_users descending
    results.sort(key=lambda x: (x['month'], -x['active_users']), reverse=True)
    
    return jsonify(results)

# ============================================================================
# USER ACTIVITY & ENGAGEMENT ROUTES
# ============================================================================

@app.route('/api/engagement/post-frequency')
def post_frequency():
    """Get daily posting activity (last 30 days)"""
    query = """
        SELECT 
            DATE(created_at) as post_date,
            COUNT(*) as posts_created,
            COUNT(DISTINCT person_id) as active_users,
            ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT person_id), 0), 2) as avg_posts_per_user
        FROM posts
        WHERE deleted_at IS NULL
            AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(created_at)
        ORDER BY post_date DESC;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/engagement/post-engagement-rate')
def post_engagement_rate():
    """Get post engagement rate by content type"""
    query = """
        SELECT 
            p.type as content_type,
            COUNT(DISTINCT p.id) as total_posts,
            COUNT(DISTINCT c.id) as total_comments,
            COUNT(DISTINCT c.person_id) as unique_commenters,
            ROUND(COUNT(DISTINCT c.id)::numeric / NULLIF(COUNT(DISTINCT p.id), 0), 2) as avg_comments_per_post,
            ROUND((COUNT(DISTINCT c.person_id)::numeric / NULLIF(COUNT(DISTINCT p.id), 0)) * 100, 2) as engagement_rate_pct
        FROM posts p
        LEFT JOIN comments c ON p.id = c.post_id AND c.deleted_at IS NULL
        WHERE p.deleted_at IS NULL
            AND p.created_at >= NOW() - INTERVAL '30 days'
        GROUP BY p.type
        ORDER BY engagement_rate_pct DESC;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/engagement/content-analysis')
def content_analysis():
    """Analyze different types of content being posted"""
    query = """
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
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/engagement/active-posters')
def active_posters():
    """Get top active posters"""
    query = """
        SELECT 
            p.first_name || ' ' || p.last_name as name,
            p.email,
            COUNT(DISTINCT po.id) as post_count,
            COUNT(DISTINCT c.id) as comment_count,
            COUNT(DISTINCT po.id) + COUNT(DISTINCT c.id) as total_contributions,
            (COUNT(DISTINCT po.id) * 3 + COUNT(DISTINCT c.id) * 2) as engagement_score,
            CASE 
                WHEN COUNT(DISTINCT po.id) >= 20 THEN 'Power User'
                WHEN COUNT(DISTINCT po.id) >= 10 THEN 'Active User'
                WHEN COUNT(DISTINCT po.id) >= 5 THEN 'Regular User'
                ELSE 'Casual User'
            END as user_tier
        FROM persons p
        LEFT JOIN posts po ON p.id = po.person_id AND po.deleted_at IS NULL
        LEFT JOIN comments c ON p.id = c.person_id AND c.deleted_at IS NULL
        WHERE p.deleted_at IS NULL
        GROUP BY p.id, p.first_name, p.last_name, p.email
        HAVING COUNT(DISTINCT po.id) > 0 OR COUNT(DISTINCT c.id) > 0
        ORDER BY engagement_score DESC, post_count DESC
        LIMIT 20;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/engagement/post-reach')
def post_reach():
    """Get top posts by engagement (last 30 days)"""
    query = """
        SELECT 
            p.id as post_id,
            LEFT(p.content, 100) as post_preview,
            author.first_name || ' ' || author.last_name as author,
            p.type as content_type,
            COUNT(DISTINCT c.id) as comment_count,
            COUNT(DISTINCT c.person_id) as unique_commenters,
            p.created_at,
            EXTRACT(days FROM NOW() - p.created_at)::integer as days_old,
            -- Calculate engagement score: comments are weighted higher
            (COUNT(DISTINCT c.id) * 10 + COUNT(DISTINCT c.person_id) * 5) as engagement_score
        FROM posts p
        JOIN persons author ON p.person_id = author.id
        LEFT JOIN comments c ON p.id = c.post_id AND c.deleted_at IS NULL
        WHERE p.deleted_at IS NULL
            AND p.created_at >= NOW() - INTERVAL '30 days'
        GROUP BY p.id, p.content, author.first_name, author.last_name, p.type, p.created_at
        ORDER BY engagement_score DESC, comment_count DESC, p.created_at DESC
        LIMIT 20;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/engagement/summary')
def engagement_summary():
    """Get summary dashboard metrics"""
    query = """
        SELECT 
            'Total Posts (30d)' as metric,
            COUNT(*)::text as value
        FROM posts
        WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

        UNION ALL

        SELECT 
            'Active Posters (30d)',
            COUNT(DISTINCT person_id)::text
        FROM posts
        WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

        UNION ALL

        SELECT 
            'Total Comments (30d)',
            COUNT(*)::text
        FROM comments
        WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

        UNION ALL

        SELECT 
            'Avg Posts/Day',
            ROUND(COUNT(*)::numeric / 30, 1)::text
        FROM posts
        WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

        UNION ALL

        SELECT 
            'Avg Comments/Post',
            ROUND(
                (SELECT COUNT(*) FROM comments WHERE deleted_at IS NULL)::numeric /
                NULLIF((SELECT COUNT(*) FROM posts WHERE deleted_at IS NULL), 0), 2
            )::text;
    """
    conn = get_engagement_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

# ============================================================================
# PROFILE METRICS ROUTES
# ============================================================================

@app.route('/api/profile/completion-rate')
def profile_completion_rate():
    """Get profile completion statistics"""
    query = """
        WITH profile_completeness AS (
            SELECT 
                p.id,
                p.first_name || ' ' || p.last_name as full_name,
                p.email,
                CASE WHEN p.headline_description IS NOT NULL AND LENGTH(p.headline_description) > 10 THEN 1 ELSE 0 END as has_headline,
                CASE WHEN p.linked_in_url IS NOT NULL THEN 1 ELSE 0 END as has_linkedin,
                CASE WHEN p.location_id IS NOT NULL THEN 1 ELSE 0 END as has_location,
                CASE WHEN p.company_id IS NOT NULL THEN 1 ELSE 0 END as has_company,
                (SELECT COUNT(*) FROM experiences WHERE person_id = p.id AND deleted_at IS NULL) as experience_count,
                (SELECT COUNT(*) FROM education WHERE person_id = p.id AND deleted_at IS NULL) as education_count,
                (SELECT COUNT(*) FROM person_languages WHERE person_id = p.id AND deleted_at IS NULL) as language_count,
                (SELECT COUNT(*) FROM embeddings WHERE person_id = p.id AND deleted_at IS NULL) as embedding_count,
                p.has_finder
            FROM persons p
            WHERE p.deleted_at IS NULL
        )
        SELECT 
            full_name,
            email,
            (has_headline + has_linkedin + has_location + has_company + 
             CASE WHEN experience_count > 0 THEN 1 ELSE 0 END +
             CASE WHEN education_count > 0 THEN 1 ELSE 0 END +
             CASE WHEN language_count > 0 THEN 1 ELSE 0 END) as profile_completeness_score,
            experience_count,
            education_count,
            language_count,
            embedding_count,
            has_finder,
            CASE 
                WHEN embedding_count > 0 THEN 'FINDER_ENABLED'
                WHEN experience_count > 0 OR education_count > 0 THEN 'BUILDER_ONLY'
                ELSE 'BASIC_PROFILE'
            END as profile_status
        FROM profile_completeness
        ORDER BY profile_completeness_score DESC, embedding_count DESC
        LIMIT 50;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/profile/update-frequency')
def profile_update_frequency():
    """Get profile update frequency statistics"""
    query = """
        SELECT 
            id,
            first_name || ' ' || last_name as name,
            updated_at as last_profile_update,
            CURRENT_DATE - DATE(updated_at) as days_since_update,
            CASE 
                WHEN CURRENT_DATE - DATE(updated_at) > 180 THEN 'STALE (6+ months)'
                WHEN CURRENT_DATE - DATE(updated_at) > 90 THEN 'AGING (3-6 months)'
                ELSE 'FRESH (< 3 months)'
            END as profile_status
        FROM persons
        WHERE deleted_at IS NULL
        ORDER BY days_since_update DESC
        LIMIT 50;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

# ============================================================================
# TALENT MARKETPLACE INTELLIGENCE ROUTES
# ============================================================================

@app.route('/api/talent/top-companies')
def top_companies():
    """Get top companies by user count"""
    query = """
        SELECT 
            c.name as company_name,
            COUNT(DISTINCT p.id) as user_count,
            COUNT(DISTINCT e.id) as total_experiences,
            STRING_AGG(DISTINCT l.country, ', ') as countries
        FROM companies c
        LEFT JOIN persons p ON c.id = p.company_id AND p.deleted_at IS NULL
        LEFT JOIN experiences e ON c.id = e.company_id AND e.deleted_at IS NULL
        LEFT JOIN locations l ON c.location_id = l.id
        WHERE c.deleted_at IS NULL
          AND (p.id IS NOT NULL OR e.id IS NOT NULL)
        GROUP BY c.id, c.name
        ORDER BY user_count DESC, total_experiences DESC
        LIMIT 20;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/talent/top-roles')
def top_roles():
    """Get top roles/job titles"""
    query = """
        SELECT 
            r.title as role_title,
            COUNT(DISTINCT e.person_id) as user_count,
            COUNT(DISTINCT e.company_id) as companies_count,
            ROUND(AVG(EXTRACT(YEAR FROM COALESCE(e.end_date, CURRENT_DATE)) - 
                  EXTRACT(YEAR FROM e.start_date)), 1) as avg_years_in_role
        FROM roles r
        JOIN experiences e ON r.id = e.role_id
        WHERE r.deleted_at IS NULL
          AND e.deleted_at IS NULL
        GROUP BY r.id, r.title
        ORDER BY user_count DESC
        LIMIT 20;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/talent/education-distribution')
def education_distribution():
    """Get education/degree distribution"""
    query = """
        SELECT 
            d.name as degree_type,
            COUNT(DISTINCT ed.person_id) as user_count,
            COUNT(DISTINCT ed.school_id) as schools_count
        FROM degrees d
        JOIN education ed ON d.id = ed.degree_id
        WHERE d.deleted_at IS NULL
          AND ed.deleted_at IS NULL
        GROUP BY d.id, d.name
        ORDER BY user_count DESC;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/talent/geographic-distribution')
def geographic_distribution():
    """Get user distribution by country"""
    query = """
        SELECT 
            COALESCE(l.country, 'Unknown') as country,
            COUNT(DISTINCT p.id) as user_count,
            COUNT(DISTINCT p.company_id) as companies_count,
            ROUND(COUNT(DISTINCT p.id) * 100.0 / 
                  (SELECT COUNT(*) FROM persons WHERE deleted_at IS NULL), 2) as percentage
        FROM persons p
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE p.deleted_at IS NULL
        GROUP BY l.country
        ORDER BY user_count DESC
        LIMIT 15;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

@app.route('/api/talent/top-skills-projects')
def top_skills_projects():
    """Get top skills and project types"""
    query = """
        SELECT 
            pr.name as project_name,
            LEFT(pr.description, 100) as project_description,
            COUNT(DISTINCT pr.person_id) as user_count,
            MIN(pr.start_date) as first_project,
            MAX(COALESCE(pr.end_date, CURRENT_DATE)) as last_project
        FROM projects pr
        WHERE pr.deleted_at IS NULL
          AND pr.name IS NOT NULL
        GROUP BY pr.name, pr.description
        HAVING COUNT(DISTINCT pr.person_id) > 1
        ORDER BY user_count DESC
        LIMIT 20;
    """
    conn = get_chemlink_db_connection()
    results = execute_query(conn, query)
    return jsonify(results)

# ============================================================================
# METADATA & SQL QUERIES ENDPOINTS
# ============================================================================

@app.route('/api/sql-queries')
def get_sql_queries():
    """Get all SQL queries used in the dashboard"""
    return jsonify(SQL_QUERIES)

@app.route('/api/sql-queries/<query_id>')
def get_sql_query(query_id):
    """Get a specific SQL query by ID"""
    if query_id in SQL_QUERIES:
        return jsonify(SQL_QUERIES[query_id])
    return jsonify({"error": "Query not found"}), 404

@app.route('/api/metrics-metadata')
def metrics_metadata():
    """Get metadata for all metrics including categories and business pain points"""
    metadata = {
        "categories": [
            {
                "id": "growth",
                "name": "Growth Metrics",
                "description": "Track user acquisition and platform expansion",
                "metrics": [
                    {
                        "id": "new_users_monthly",
                        "name": "New Users - Monthly Trend",
                        "pain_point": "We don't know if our marketing efforts are working or how fast we're acquiring users compared to competitors",
                        "endpoint": "/api/new-users/monthly"
                    },
                    {
                        "id": "growth_rate_monthly",
                        "name": "User Growth Rate - Monthly",
                        "pain_point": "We can't measure if our growth is accelerating, stagnating, or declining month-over-month for investor/board reporting",
                        "endpoint": "/api/growth-rate/monthly"
                    },
                    {
                        "id": "dau",
                        "name": "Daily Active Users (DAU)",
                        "pain_point": "We have no visibility into daily engagement patterns or which days/features drive the most activity",
                        "endpoint": "/api/active-users/daily"
                    },
                    {
                        "id": "mau",
                        "name": "Monthly Active Users (MAU)",
                        "pain_point": "We can't tell if users are actually using our platform regularly or just signing up and abandoning it",
                        "endpoint": "/api/active-users/monthly"
                    },
                    {
                        "id": "mau_by_country",
                        "name": "MAU by Country",
                        "pain_point": "We can't tell if users are actually using our platform regularly or just signing up and abandoning it",
                        "endpoint": "/api/active-users/monthly-by-country"
                    }
                ]
            },
            {
                "id": "engagement",
                "name": "User Engagement & Social Activity",
                "description": "Measure community interactions and content performance",
                "metrics": [
                    {
                        "id": "post_frequency",
                        "name": "Post Frequency - Daily",
                        "pain_point": "We can't tell if our platform is gaining momentum or if community activity is declining over time",
                        "endpoint": "/api/engagement/post-frequency"
                    },
                    {
                        "id": "engagement_rate",
                        "name": "Post Engagement Rate by Type",
                        "pain_point": "We don't know if our community features are creating meaningful interactions or just noise",
                        "endpoint": "/api/engagement/post-engagement-rate"
                    },
                    {
                        "id": "content_type",
                        "name": "Content Type Distribution",
                        "pain_point": "We don't know if our community features are creating meaningful interactions or just noise",
                        "endpoint": "/api/engagement/content-analysis"
                    },
                    {
                        "id": "active_posters",
                        "name": "Top Active Posters",
                        "pain_point": "We need to identify and nurture our most valuable community contributors for platform growth",
                        "endpoint": "/api/engagement/active-posters"
                    },
                    {
                        "id": "post_reach",
                        "name": "Top Performing Posts",
                        "pain_point": "We don't know if valuable content is actually being seen by our community or getting buried",
                        "endpoint": "/api/engagement/post-reach"
                    }
                ]
            },
            {
                "id": "profile",
                "name": "Profile Quality Metrics",
                "description": "Monitor user profile completeness and data freshness",
                "metrics": [
                    {
                        "id": "profile_completion",
                        "name": "Profile Completion Score",
                        "pain_point": "Incomplete profiles hurt our AI matching accuracy and reduce platform value for both job seekers and recruiters",
                        "endpoint": "/api/profile/completion-rate"
                    },
                    {
                        "id": "profile_status",
                        "name": "Profile Status Breakdown",
                        "pain_point": "Incomplete profiles hurt our AI matching accuracy and reduce platform value for both job seekers and recruiters",
                        "endpoint": "/api/profile/completion-rate"
                    },
                    {
                        "id": "profile_freshness",
                        "name": "Profile Update Freshness",
                        "pain_point": "Stale profiles make our talent database less valuable - we need to encourage users to keep information current",
                        "endpoint": "/api/profile/update-frequency"
                    }
                ]
            },
            {
                "id": "talent",
                "name": "Talent Marketplace Intelligence",
                "description": "Understand who's on your platform and what they offer",
                "metrics": [
                    {
                        "id": "top_companies",
                        "name": "Top Companies",
                        "pain_point": "We don't know if we're attracting talent from premium companies or if our network is high-quality enough to attract employers",
                        "endpoint": "/api/talent/top-companies"
                    },
                    {
                        "id": "top_roles",
                        "name": "Top Roles/Job Titles",
                        "pain_point": "Without knowing what roles our users have, we can't build features that match their needs or target the right employers",
                        "endpoint": "/api/talent/top-roles"
                    },
                    {
                        "id": "education_distribution",
                        "name": "Education Distribution",
                        "pain_point": "Can't prove to recruiters that our talent pool is high-quality without showing education credentials and top schools",
                        "endpoint": "/api/talent/education-distribution"
                    },
                    {
                        "id": "geographic_distribution",
                        "name": "Geographic Distribution",
                        "pain_point": "We're spending marketing budget blindly without knowing where our users are concentrated or which markets to prioritize",
                        "endpoint": "/api/talent/geographic-distribution"
                    },
                    {
                        "id": "top_skills_projects",
                        "name": "Top Skills & Projects",
                        "pain_point": "Don't know what kind of work our users do or if they're doing cutting-edge projects that would attract premium employers",
                        "endpoint": "/api/talent/top-skills-projects"
                    }
                ]
            }
        ]
    }
    return jsonify(metadata)

# ============================================================================
# MAIN DASHBOARD ROUTE
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
