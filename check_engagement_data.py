#!/usr/bin/env python3
"""
Check the actual date range of engagement data (posts/comments) in production
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from db_config import get_engagement_db_connection

load_dotenv()

# Check posts date range
posts_query = """
SELECT 
    MIN(created_at) as earliest_post,
    MAX(created_at) as latest_post,
    COUNT(*) as total_posts,
    COUNT(DISTINCT DATE_TRUNC('month', created_at)) as distinct_months
FROM posts 
WHERE deleted_at IS NULL;
"""

# Check comments date range
comments_query = """
SELECT 
    MIN(created_at) as earliest_comment,
    MAX(created_at) as latest_comment,
    COUNT(*) as total_comments,
    COUNT(DISTINCT DATE_TRUNC('month', created_at)) as distinct_months
FROM comments 
WHERE deleted_at IS NULL;
"""

# Monthly breakdown
monthly_query = """
SELECT 
    DATE_TRUNC('month', activity_date) as month,
    COUNT(DISTINCT person_id) as active_users,
    COUNT(*) as total_activity
FROM (
    SELECT person_id, created_at as activity_date FROM posts WHERE deleted_at IS NULL
    UNION ALL
    SELECT person_id, created_at FROM comments WHERE deleted_at IS NULL
) activity
GROUP BY month 
ORDER BY month DESC;
"""

try:
    conn = get_engagement_db_connection()
    
    print("\n" + "="*80)
    print("📊 ENGAGEMENT DATA RANGE ANALYSIS (PRODUCTION)")
    print("="*80 + "\n")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Posts
        cursor.execute(posts_query)
        posts_result = cursor.fetchone()
        print("POSTS:")
        print(f"  Earliest: {posts_result['earliest_post']}")
        print(f"  Latest: {posts_result['latest_post']}")
        print(f"  Total: {posts_result['total_posts']}")
        print(f"  Distinct Months: {posts_result['distinct_months']}")
        print()
        
        # Comments
        cursor.execute(comments_query)
        comments_result = cursor.fetchone()
        print("COMMENTS:")
        print(f"  Earliest: {comments_result['earliest_comment']}")
        print(f"  Latest: {comments_result['latest_comment']}")
        print(f"  Total: {comments_result['total_comments']}")
        print(f"  Distinct Months: {comments_result['distinct_months']}")
        print()
        
        # Monthly breakdown
        cursor.execute(monthly_query)
        monthly_results = cursor.fetchall()
        
        print("MONTHLY ACTIVE USERS (All Time):")
        print(f"{'Month':<20} {'Active Users':<15} {'Total Activity':<15}")
        print("-" * 50)
        for row in monthly_results:
            month = row['month'].strftime('%Y-%m') if row['month'] else 'NULL'
            active = row['active_users']
            activity = row['total_activity']
            print(f"{month:<20} {active:<15} {activity:<15}")
    
    conn.close()
    print("\n" + "="*80 + "\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
