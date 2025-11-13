#!/usr/bin/env python3
"""
Test Activity Type Analytics Queries
"""
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_engagement_connection():
    host = os.getenv('ENGAGEMENT_DB_HOST')
    port = os.getenv('ENGAGEMENT_DB_PORT')
    dbname = os.getenv('ENGAGEMENT_DB_NAME')
    user = os.getenv('ENGAGEMENT_DB_USER')
    password = os.getenv('ENGAGEMENT_DB_PASSWORD')
    return psycopg2.connect(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")

def get_chemlink_connection():
    host = os.getenv('CHEMLINK_DEV_DB_HOST')
    port = os.getenv('CHEMLINK_DEV_DB_PORT')
    dbname = os.getenv('CHEMLINK_DEV_DB_NAME')
    user = os.getenv('CHEMLINK_DEV_DB_USER')
    password = os.getenv('CHEMLINK_DEV_DB_PASSWORD')
    return psycopg2.connect(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")

def run_query(conn, query, description):
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")
    print(f"\nQuery:\n{query}\n")
    print(f"{'-'*80}")
    
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    print(f"Results ({len(results)} rows):\n")
    print(" | ".join(columns))
    print("-" * 80)
    
    for row in results[:10]:  # Show first 10 rows
        print(" | ".join(str(val) for val in row))
    
    if len(results) > 10:
        print(f"\n... and {len(results) - 10} more rows")
    
    cursor.close()
    return results

print("\n" + "="*80)
print("ACTIVITY TYPE ANALYTICS - TEST QUERIES")
print("="*80)

# ============================================================================
# ENGAGEMENT DB QUERIES
# ============================================================================

print("\n\n" + "#"*80)
print("# ENGAGEMENT DB: POSTS & COMMENTS ACTIVITIES")
print("#"*80)

conn_engagement = get_engagement_connection()

# Query 1: DAU by Activity Type - Breakdown
query1_dau_breakdown = """
SELECT 
    DATE(activity_date) as date,
    activity_type,
    COUNT(DISTINCT person_id) as unique_users,
    COUNT(*) as total_activities
FROM (
    SELECT person_id, created_at as activity_date, 'post' as activity_type 
    FROM posts WHERE deleted_at IS NULL
    UNION ALL
    SELECT person_id, created_at, 'comment' 
    FROM comments WHERE deleted_at IS NULL
) daily_activity
WHERE activity_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(activity_date), activity_type
ORDER BY date DESC, activity_type;
"""
run_query(conn_engagement, query1_dau_breakdown, "Query 1: DAU by Activity Type - Daily Breakdown")

# Query 1b: MAU by Activity Type - Breakdown
query1_mau_breakdown = """
SELECT 
    DATE_TRUNC('month', activity_date) as month,
    activity_type,
    COUNT(DISTINCT person_id) as unique_users,
    COUNT(*) as total_activities
FROM (
    SELECT person_id, created_at as activity_date, 'post' as activity_type 
    FROM posts 
    WHERE deleted_at IS NULL
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
    UNION ALL
    SELECT person_id, created_at, 'comment' 
    FROM comments 
    WHERE deleted_at IS NULL
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
) monthly_activity
GROUP BY DATE_TRUNC('month', activity_date), activity_type
ORDER BY month DESC, activity_type;
"""
run_query(conn_engagement, query1_mau_breakdown, "Query 1b: MAU by Activity Type - Monthly Breakdown")

# Query 2: Activity Distribution Percentages (MAU)
query2_distribution = """
WITH activity_counts AS (
    SELECT 
        DATE_TRUNC('month', activity_date) as month,
        activity_type,
        COUNT(DISTINCT person_id) as unique_users
    FROM (
        SELECT person_id, created_at as activity_date, 'post' as activity_type 
        FROM posts 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT person_id, created_at, 'comment' 
        FROM comments 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
    ) monthly_activity
    GROUP BY month, activity_type
),
monthly_totals AS (
    SELECT 
        month,
        SUM(unique_users) as total_active_users
    FROM activity_counts
    GROUP BY month
)
SELECT 
    ac.month,
    ac.activity_type,
    ac.unique_users,
    mt.total_active_users,
    ROUND((ac.unique_users::numeric / mt.total_active_users) * 100, 2) as percentage
FROM activity_counts ac
JOIN monthly_totals mt ON ac.month = mt.month
ORDER BY ac.month DESC, ac.activity_type;
"""
run_query(conn_engagement, query2_distribution, "Query 2: Activity Distribution Percentages (MAU)")

# Query 3: Activity Intensity Levels (MAU)
query3_intensity = """
WITH user_activity_counts AS (
    SELECT 
        DATE_TRUNC('month', activity_date) as month,
        person_id,
        COUNT(*) as total_activities,
        COUNT(CASE WHEN activity_type = 'post' THEN 1 END) as post_count,
        COUNT(CASE WHEN activity_type = 'comment' THEN 1 END) as comment_count
    FROM (
        SELECT person_id, created_at as activity_date, 'post' as activity_type 
        FROM posts 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT person_id, created_at, 'comment' 
        FROM comments 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
    ) all_activity
    GROUP BY month, person_id
),
intensity_categorized AS (
    SELECT 
        month,
        person_id,
        total_activities,
        post_count,
        comment_count,
        CASE 
            WHEN total_activities >= 20 THEN 'Power User (20+)'
            WHEN total_activities >= 10 THEN 'Active User (10-19)'
            WHEN total_activities >= 5 THEN 'Regular User (5-9)'
            ELSE 'Casual User (1-4)'
        END as intensity_level
    FROM user_activity_counts
)
SELECT 
    month,
    intensity_level,
    COUNT(DISTINCT person_id) as user_count,
    ROUND(AVG(total_activities), 2) as avg_activities_per_user,
    ROUND(AVG(post_count), 2) as avg_posts_per_user,
    ROUND(AVG(comment_count), 2) as avg_comments_per_user
FROM intensity_categorized
GROUP BY month, intensity_level
ORDER BY month DESC, 
    CASE intensity_level
        WHEN 'Power User (20+)' THEN 1
        WHEN 'Active User (10-19)' THEN 2
        WHEN 'Regular User (5-9)' THEN 3
        ELSE 4
    END;
"""
run_query(conn_engagement, query3_intensity, "Query 3: Activity Intensity Levels (MAU)")

conn_engagement.close()

# ============================================================================
# CHEMLINK DB QUERIES
# ============================================================================

print("\n\n" + "#"*80)
print("# CHEMLINK DB: COMPREHENSIVE ACTIVITIES")
print("#"*80)

conn_chemlink = get_chemlink_connection()

# Query 4: MAU by ChemLink Activity Type - Breakdown
query4_chemlink_breakdown = """
SELECT 
    DATE_TRUNC('month', activity_date) as month,
    activity_type,
    COUNT(DISTINCT person_id) as unique_users,
    COUNT(*) as total_activities
FROM (
    SELECT person_id, created_at as activity_date, 'view_access' as activity_type 
    FROM view_access 
    WHERE deleted_at IS NULL
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
    UNION ALL
    SELECT voter_id as person_id, created_at as activity_date, 'query_vote' as activity_type 
    FROM query_votes 
    WHERE deleted_at IS NULL
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
    UNION ALL
    SELECT person_id, created_at as activity_date, 'collection_created' as activity_type 
    FROM collections 
    WHERE deleted_at IS NULL
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
    UNION ALL
    SELECT id as person_id, updated_at as activity_date, 'profile_update' as activity_type 
    FROM persons 
    WHERE deleted_at IS NULL
      AND updated_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
      AND updated_at != created_at
) all_activity
GROUP BY month, activity_type
ORDER BY month DESC, activity_type;
"""
run_query(conn_chemlink, query4_chemlink_breakdown, "Query 4: ChemLink MAU by Activity Type - Breakdown")

# Query 5: ChemLink Activity Distribution Percentages
query5_chemlink_distribution = """
WITH activity_counts AS (
    SELECT 
        DATE_TRUNC('month', activity_date) as month,
        activity_type,
        COUNT(DISTINCT person_id) as unique_users
    FROM (
        SELECT person_id, created_at as activity_date, 'view_access' as activity_type 
        FROM view_access 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT voter_id as person_id, created_at as activity_date, 'query_vote' as activity_type 
        FROM query_votes 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT person_id, created_at as activity_date, 'collection_created' as activity_type 
        FROM collections 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT id as person_id, updated_at as activity_date, 'profile_update' as activity_type 
        FROM persons 
        WHERE deleted_at IS NULL
          AND updated_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
          AND updated_at != created_at
    ) all_activity
    GROUP BY month, activity_type
),
monthly_totals AS (
    SELECT 
        month,
        SUM(unique_users) as total_active_users
    FROM activity_counts
    GROUP BY month
)
SELECT 
    ac.month,
    ac.activity_type,
    ac.unique_users,
    mt.total_active_users,
    ROUND((ac.unique_users::numeric / NULLIF(mt.total_active_users, 0)) * 100, 2) as percentage
FROM activity_counts ac
JOIN monthly_totals mt ON ac.month = mt.month
ORDER BY ac.month DESC, ac.activity_type;
"""
run_query(conn_chemlink, query5_chemlink_distribution, "Query 5: ChemLink Activity Distribution Percentages")

# Query 6: ChemLink Activity Intensity Levels
query6_chemlink_intensity = """
WITH user_activity_counts AS (
    SELECT 
        DATE_TRUNC('month', activity_date) as month,
        person_id,
        COUNT(*) as total_activities,
        COUNT(CASE WHEN activity_type = 'view_access' THEN 1 END) as view_count,
        COUNT(CASE WHEN activity_type = 'query_vote' THEN 1 END) as vote_count,
        COUNT(CASE WHEN activity_type = 'collection_created' THEN 1 END) as collection_count,
        COUNT(CASE WHEN activity_type = 'profile_update' THEN 1 END) as profile_update_count
    FROM (
        SELECT person_id, created_at as activity_date, 'view_access' as activity_type 
        FROM view_access 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT voter_id as person_id, created_at as activity_date, 'query_vote' as activity_type 
        FROM query_votes 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT person_id, created_at as activity_date, 'collection_created' as activity_type 
        FROM collections 
        WHERE deleted_at IS NULL
          AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        UNION ALL
        SELECT id as person_id, updated_at as activity_date, 'profile_update' as activity_type 
        FROM persons 
        WHERE deleted_at IS NULL
          AND updated_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
          AND updated_at != created_at
    ) all_activity
    GROUP BY month, person_id
),
intensity_categorized AS (
    SELECT 
        month,
        person_id,
        total_activities,
        view_count,
        vote_count,
        collection_count,
        profile_update_count,
        CASE 
            WHEN total_activities >= 50 THEN 'Power User (50+)'
            WHEN total_activities >= 20 THEN 'Active User (20-49)'
            WHEN total_activities >= 10 THEN 'Regular User (10-19)'
            ELSE 'Casual User (1-9)'
        END as intensity_level
    FROM user_activity_counts
)
SELECT 
    month,
    intensity_level,
    COUNT(DISTINCT person_id) as user_count,
    ROUND(AVG(total_activities), 2) as avg_activities_per_user,
    ROUND(AVG(view_count), 2) as avg_views,
    ROUND(AVG(vote_count), 2) as avg_votes,
    ROUND(AVG(collection_count), 2) as avg_collections,
    ROUND(AVG(profile_update_count), 2) as avg_profile_updates
FROM intensity_categorized
GROUP BY month, intensity_level
ORDER BY month DESC, 
    CASE intensity_level
        WHEN 'Power User (50+)' THEN 1
        WHEN 'Active User (20-49)' THEN 2
        WHEN 'Regular User (10-19)' THEN 3
        ELSE 4
    END;
"""
run_query(conn_chemlink, query6_chemlink_intensity, "Query 6: ChemLink Activity Intensity Levels")

conn_chemlink.close()

print("\n" + "="*80)
print("ALL QUERIES COMPLETED!")
print("="*80 + "\n")
