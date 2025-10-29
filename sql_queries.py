"""
SQL Queries used in the ChemLink Analytics Dashboard
This file contains all queries for reference and documentation
"""

SQL_QUERIES = {
    "new_users_monthly": {
        "name": "New Users - Monthly Trend",
        "database": "ChemLink DB",
        "query": """-- Rolling 12-month window (current month + 11 previous months)
-- Returns available data if less than 12 months exists
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as new_users
FROM persons 
WHERE deleted_at IS NULL
  AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
GROUP BY month 
ORDER BY month DESC;"""
    },
    "growth_rate_monthly": {
        "name": "User Growth Rate - Monthly",
        "database": "ChemLink DB",
        "query": """-- Rolling 12-month window with month-over-month growth rate calculation
-- Shows percentage change compared to previous month
-- Returns available data if less than 12 months exists
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
        "query": """-- Rolling 12-month window (current month + 11 previous months)
-- Returns available data if less than 12 months exists
SELECT 
    DATE_TRUNC('month', activity_date) as month,
    COUNT(DISTINCT person_id) as active_users
FROM (
    SELECT person_id, created_at as activity_date 
    FROM posts 
    WHERE deleted_at IS NULL
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
    UNION ALL
    SELECT person_id, created_at 
    FROM comments 
    WHERE deleted_at IS NULL
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
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
    "top_companies": {
        "name": "Top Companies",
        "database": "ChemLink DB",
        "query": """SELECT 
    c.name as company_name,
    COUNT(DISTINCT p.id) as user_count,
    COUNT(DISTINCT e.id) as total_experiences
FROM companies c
LEFT JOIN persons p ON c.id = p.company_id AND p.deleted_at IS NULL
LEFT JOIN experiences e ON c.id = e.company_id AND e.deleted_at IS NULL
WHERE c.deleted_at IS NULL
  AND (p.id IS NOT NULL OR e.id IS NOT NULL)
GROUP BY c.id, c.name
ORDER BY user_count DESC, total_experiences DESC;"""
    },
    "top_roles": {
        "name": "Top Roles/Job Titles",
        "database": "ChemLink DB",
        "query": """SELECT 
    r.title as role_title,
    COUNT(DISTINCT e.person_id) as user_count,
    COUNT(DISTINCT e.company_id) as companies_count,
    AVG(EXTRACT(YEAR FROM COALESCE(e.end_date, CURRENT_DATE)) - EXTRACT(YEAR FROM e.start_date)) as avg_years_in_role
FROM roles r
JOIN experiences e ON r.id = e.role_id
WHERE r.deleted_at IS NULL
  AND e.deleted_at IS NULL
GROUP BY r.id, r.title
ORDER BY user_count DESC;"""
    },
    "education_distribution": {
        "name": "Education Distribution",
        "database": "ChemLink DB",
        "query": """SELECT 
    d.name as degree_type,
    COUNT(DISTINCT ed.person_id) as user_count,
    COUNT(DISTINCT ed.school_id) as schools_count,
    STRING_AGG(DISTINCT s.name, ', ' ORDER BY s.name LIMIT 5) as top_schools
FROM degrees d
JOIN education ed ON d.id = ed.degree_id
LEFT JOIN schools s ON ed.school_id = s.id
WHERE d.deleted_at IS NULL
  AND ed.deleted_at IS NULL
GROUP BY d.id, d.name
ORDER BY user_count DESC;"""
    },
    "geographic_distribution": {
        "name": "Geographic Distribution",
        "database": "ChemLink DB",
        "query": """SELECT 
    COALESCE(l.country, 'Unknown') as country,
    COUNT(DISTINCT p.id) as user_count,
    COUNT(DISTINCT p.company_id) as companies_count,
    ROUND(COUNT(DISTINCT p.id) * 100.0 / (SELECT COUNT(*) FROM persons WHERE deleted_at IS NULL), 2) as percentage
FROM persons p
LEFT JOIN locations l ON p.location_id = l.id
WHERE p.deleted_at IS NULL
GROUP BY l.country
ORDER BY user_count DESC;"""
    },
    "top_skills_projects": {
        "name": "Top Skills & Project Types",
        "database": "ChemLink DB",
        "query": """SELECT 
    pr.name as project_name,
    pr.description as project_description,
    COUNT(DISTINCT pr.person_id) as user_count,
    MIN(pr.start_date) as first_project,
    MAX(COALESCE(pr.end_date, CURRENT_DATE)) as last_project
FROM projects pr
WHERE pr.deleted_at IS NULL
  AND pr.name IS NOT NULL
GROUP BY pr.name, pr.description
HAVING COUNT(DISTINCT pr.person_id) > 1
ORDER BY user_count DESC;"""
    },
    "account_funnel": {
        "name": "Account Creation Drop-off Funnel",
        "database": "ChemLink DB",
        "query": """SELECT 
    COUNT(*) as total_accounts,
    COUNT(CASE WHEN first_name IS NOT NULL AND last_name IS NOT NULL THEN 1 END) as step_basic_info,
    COUNT(CASE WHEN headline_description IS NOT NULL AND LENGTH(headline_description) > 10 THEN 1 END) as step_headline,
    COUNT(CASE WHEN location_id IS NOT NULL THEN 1 END) as step_location,
    COUNT(CASE WHEN company_id IS NOT NULL THEN 1 END) as step_company,
    COUNT(CASE WHEN linked_in_url IS NOT NULL THEN 1 END) as step_linkedin,
    COUNT(CASE WHEN finder_enabled = true THEN 1 END) as step_finder_enabled
FROM persons
WHERE deleted_at IS NULL;"""
    },
    "profile_additions": {
        "name": "Profile Additions to Collections",
        "database": "ChemLink DB",
        "query": """SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as profiles_added
FROM collection_profiles
WHERE deleted_at IS NULL
GROUP BY month
ORDER BY month DESC
LIMIT 12;"""
    },
    "collections_created": {
        "name": "Collections Created",
        "database": "ChemLink DB",
        "query": """-- Total Collections
SELECT COUNT(*) as total_collections
FROM collections
WHERE deleted_at IS NULL;

-- Collections by Privacy Type
SELECT 
    COALESCE(privacy, 'Not Set') as privacy_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM collections WHERE deleted_at IS NULL), 2) as percentage
FROM collections
WHERE deleted_at IS NULL
GROUP BY privacy
ORDER BY count DESC;

-- Collections Created Over Time (Monthly)
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as collections_created
FROM collections
WHERE deleted_at IS NULL
GROUP BY month
ORDER BY month DESC
LIMIT 12;"""
    },
    "collections_shared": {
        "name": "Shared Collections",
        "database": "ChemLink DB",
        "query": """-- Total Shared Collections
SELECT COUNT(DISTINCT collection_id) as shared_collections
FROM collection_collaborators
WHERE deleted_at IS NULL;

-- Total Collaboration Invites
SELECT COUNT(*) as total_shares
FROM collection_collaborators
WHERE deleted_at IS NULL;

-- Collections by Access Type
SELECT 
    COALESCE(access_type, 'Not Set') as access_type,
    COUNT(*) as share_count,
    COUNT(DISTINCT collection_id) as collections_with_access
FROM collection_collaborators
WHERE deleted_at IS NULL
GROUP BY access_type
ORDER BY share_count DESC;"""
    },
    "finder_searches": {
        "name": "Finder Search Analytics",
        "database": "ChemLink DB",
        "query": """-- Total Searches
SELECT COUNT(*) as total_searches
FROM query_embeddings
WHERE deleted_at IS NULL;

-- Searches by Intent
SELECT 
    COALESCE(intent, 'Not Specified') as intent,
    COUNT(*) as search_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM query_embeddings WHERE deleted_at IS NULL), 2) as percentage
FROM query_embeddings
WHERE deleted_at IS NULL
GROUP BY intent
ORDER BY search_count DESC
LIMIT 10;

-- Searches Over Time (Monthly) - all available data
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as searches
FROM query_embeddings
WHERE deleted_at IS NULL
GROUP BY month
ORDER BY month DESC;"""
    },
    "finder_engagement": {
        "name": "Finder Engagement Rate",
        "database": "ChemLink DB",
        "query": """-- Total Votes on Search Results
SELECT COUNT(*) as total_votes
FROM query_votes
WHERE deleted_at IS NULL;

-- Votes by Type (upvote/downvote)
SELECT 
    COALESCE(type, 'Unknown') as vote_type,
    COUNT(*) as vote_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM query_votes WHERE deleted_at IS NULL), 2) as percentage
FROM query_votes
WHERE deleted_at IS NULL
GROUP BY type
ORDER BY vote_count DESC;

-- Active Voters (Users who engaged with search results)
SELECT COUNT(DISTINCT voter_id) as active_users
FROM query_votes
WHERE deleted_at IS NULL;

-- Engagement Rate (% of searches that get votes)
SELECT 
    (SELECT COUNT(*) FROM query_votes WHERE deleted_at IS NULL)::float / 
    NULLIF((SELECT COUNT(*) FROM query_embeddings WHERE deleted_at IS NULL), 0) * 100 as engagement_rate_pct;"""
    }
}
