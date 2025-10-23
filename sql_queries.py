"""
SQL Queries used in the ChemLink Analytics Dashboard
This file contains all queries for reference and documentation
"""

SQL_QUERIES = {
    "new_users_monthly": {
        "name": "New Users - Monthly Trend",
        "database": "ChemLink DB",
        "query": """SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as new_users
FROM persons 
WHERE deleted_at IS NULL
GROUP BY month 
ORDER BY month DESC;"""
    },
    "growth_rate_monthly": {
        "name": "User Growth Rate - Monthly",
        "database": "ChemLink DB",
        "query": """WITH monthly_users AS (
    SELECT DATE_TRUNC('month', created_at) as month,
           COUNT(*) as new_users
    FROM persons WHERE deleted_at IS NULL
    GROUP BY month
)
SELECT 
    month, 
    new_users,
    LAG(new_users) OVER (ORDER BY month) as prev_month,
    ROUND(((new_users - LAG(new_users) OVER (ORDER BY month)) * 100.0 / 
           NULLIF(LAG(new_users) OVER (ORDER BY month), 0)), 2) as growth_rate_pct
FROM monthly_users 
ORDER BY month DESC;"""
    },
    "dau": {
        "name": "Daily Active Users (DAU)",
        "database": "Engagement DB",
        "query": """SELECT 
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
ORDER BY date DESC;"""
    },
    "mau": {
        "name": "Monthly Active Users (MAU)",
        "database": "Engagement DB",
        "query": """SELECT 
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
ORDER BY month DESC;"""
    },
    "mau_by_country": {
        "name": "MAU by Country",
        "database": "Cross-database (Engagement + ChemLink)",
        "query": """-- Step 1: Get active users from Engagement DB
SELECT person_id, DATE_TRUNC('month', activity_date) as month
FROM (
    SELECT person_id, created_at as activity_date FROM posts WHERE deleted_at IS NULL
    UNION ALL
    SELECT person_id, created_at FROM comments WHERE deleted_at IS NULL
) activity

-- Step 2: Join with ChemLink DB for location data
-- Note: Person IDs currently don't match between databases
JOIN persons p ON activity.person_id::text = p.id::text
LEFT JOIN locations l ON p.location_id = l.id
GROUP BY month, l.country;"""
    },
    "post_frequency": {
        "name": "Post Frequency - Daily",
        "database": "Engagement DB",
        "query": """SELECT 
    DATE(created_at) as post_date,
    COUNT(*) as posts_created,
    COUNT(DISTINCT person_id) as active_users,
    ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT person_id), 0), 2) as avg_posts_per_user
FROM posts
WHERE deleted_at IS NULL
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY post_date DESC;"""
    },
    "engagement_rate": {
        "name": "Post Engagement Rate by Type",
        "database": "Engagement DB",
        "query": """SELECT 
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
ORDER BY engagement_rate_pct DESC;"""
    },
    "content_type": {
        "name": "Content Type Distribution",
        "database": "Engagement DB",
        "query": """SELECT 
    p.type,
    COUNT(*) as post_count,
    COUNT(DISTINCT p.person_id) as unique_authors,
    AVG(char_length(p.content)) as avg_content_length,
    COUNT(CASE WHEN p.link_url IS NOT NULL THEN 1 END) as posts_with_links,
    COUNT(CASE WHEN p.media_keys IS NOT NULL THEN 1 END) as posts_with_media
FROM posts p
WHERE p.deleted_at IS NULL
GROUP BY p.type
ORDER BY post_count DESC;"""
    },
    "active_posters": {
        "name": "Top Active Posters",
        "database": "Engagement DB",
        "query": """SELECT 
    p.first_name || ' ' || p.last_name as name,
    p.email,
    COUNT(DISTINCT po.id) as post_count,
    COUNT(DISTINCT c.id) as comment_count,
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
ORDER BY engagement_score DESC
LIMIT 20;"""
    },
    "post_reach": {
        "name": "Top Performing Posts",
        "database": "Engagement DB",
        "query": """SELECT 
    p.id as post_id,
    LEFT(p.content, 100) as post_preview,
    author.first_name || ' ' || author.last_name as author,
    p.type as content_type,
    COUNT(DISTINCT c.id) as comment_count,
    COUNT(DISTINCT c.person_id) as unique_commenters,
    p.created_at,
    EXTRACT(days FROM NOW() - p.created_at)::integer as days_old,
    (COUNT(DISTINCT c.id) * 10 + COUNT(DISTINCT c.person_id) * 5) as engagement_score
FROM posts p
JOIN persons author ON p.person_id = author.id
LEFT JOIN comments c ON p.id = c.post_id AND c.deleted_at IS NULL
WHERE p.deleted_at IS NULL
  AND p.created_at >= NOW() - INTERVAL '30 days'
GROUP BY p.id, p.content, author.first_name, author.last_name, p.type, p.created_at
ORDER BY engagement_score DESC, comment_count DESC, p.created_at DESC
LIMIT 20;"""
    },
    "profile_completion": {
        "name": "Profile Completion Score",
        "database": "ChemLink DB",
        "query": """WITH profile_completeness AS (
    SELECT 
        p.id,
        (CASE WHEN p.headline_description IS NOT NULL AND LENGTH(p.headline_description) > 10 THEN 1 ELSE 0 END +
         CASE WHEN p.linked_in_url IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN p.location_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN p.company_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN (SELECT COUNT(*) FROM experiences WHERE person_id = p.id AND deleted_at IS NULL) > 0 THEN 1 ELSE 0 END +
         CASE WHEN (SELECT COUNT(*) FROM education WHERE person_id = p.id AND deleted_at IS NULL) > 0 THEN 1 ELSE 0 END +
         CASE WHEN (SELECT COUNT(*) FROM person_languages WHERE person_id = p.id AND deleted_at IS NULL) > 0 THEN 1 ELSE 0 END
        ) as profile_completeness_score
    FROM persons p
    WHERE p.deleted_at IS NULL
)
SELECT 
    profile_completeness_score,
    COUNT(*) as user_count
FROM profile_completeness
GROUP BY profile_completeness_score
ORDER BY profile_completeness_score;"""
    },
    "profile_freshness": {
        "name": "Profile Update Freshness",
        "database": "ChemLink DB",
        "query": """SELECT 
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
ORDER BY days_since_update DESC;"""
    },
    "job_listings_growth": {
        "name": "Job Listings Growth",
        "database": "Engagement DB",
        "query": """SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as job_posts,
    COUNT(DISTINCT person_id) as unique_posters
FROM posts
WHERE deleted_at IS NULL
  AND type ILIKE '%job%'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;"""
    },
    "top_job_categories": {
        "name": "Top Job Categories",
        "database": "Engagement DB",
        "query": """SELECT 
    type as job_category,
    COUNT(*) as job_count,
    COUNT(DISTINCT person_id) as unique_posters,
    COUNT(CASE WHEN link_url IS NOT NULL THEN 1 END) as jobs_with_external_links,
    AVG(CHAR_LENGTH(content)) as avg_description_length,
    MIN(created_at) as first_posted,
    MAX(created_at) as last_posted
FROM posts
WHERE deleted_at IS NULL
  AND type ILIKE '%job%'
GROUP BY type
ORDER BY job_count DESC;"""
    }
}
