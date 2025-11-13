#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Use PROD ChemLink DB
host = os.getenv('CHEMLINK_PRD_DB_HOST')
port = os.getenv('CHEMLINK_PRD_DB_PORT')
dbname = os.getenv('CHEMLINK_PRD_DB_NAME')
user = os.getenv('CHEMLINK_PRD_DB_USER')
password = os.getenv('CHEMLINK_PRD_DB_PASSWORD')

conn = psycopg2.connect(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
cursor = conn.cursor()

print("\n" + "="*80)
print("CHEMLINK DB ACTIVITY ANALYTICS (PROD)")
print("="*80)

# Query 4: Activity Breakdown
print("\n" + "-"*80)
print("Query 4: MAU by Activity Type - Breakdown")
print("-"*80)

query4 = """
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

cursor.execute(query4)
results = cursor.fetchall()
print(f"\nResults ({len(results)} rows):\n")
print("month | activity_type | unique_users | total_activities")
print("-"*80)
for row in results[:15]:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
if len(results) > 15:
    print(f"\n... and {len(results) - 15} more rows")

# Query 5: Activity Distribution
print("\n" + "-"*80)
print("Query 5: Activity Distribution Percentages")
print("-"*80)

query5 = """
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

cursor.execute(query5)
results = cursor.fetchall()
print(f"\nResults ({len(results)} rows):\n")
print("month | activity_type | unique_users | total | percentage")
print("-"*80)
for row in results[:15]:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}%")
if len(results) > 15:
    print(f"\n... and {len(results) - 15} more rows")

# Query 6: Intensity Levels
print("\n" + "-"*80)
print("Query 6: Activity Intensity Levels")
print("-"*80)

query6 = """
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
    ROUND(AVG(total_activities), 2) as avg_activities,
    ROUND(AVG(view_count), 2) as avg_views,
    ROUND(AVG(vote_count), 2) as avg_votes,
    ROUND(AVG(collection_count), 2) as avg_collections,
    ROUND(AVG(profile_update_count), 2) as avg_updates
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

cursor.execute(query6)
results = cursor.fetchall()
print(f"\nResults ({len(results)} rows):\n")
print("month | intensity | users | avg_act | avg_views | avg_votes | avg_coll | avg_upd")
print("-"*80)
for row in results[:15]:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}")
if len(results) > 15:
    print(f"\n... and {len(results) - 15} more rows")

cursor.close()
conn.close()

print("\n" + "="*80)
print("ALL CHEMLINK QUERIES COMPLETED!")
print("="*80 + "\n")
