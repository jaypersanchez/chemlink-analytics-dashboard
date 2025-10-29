#!/usr/bin/env python3
"""
Test monthly user growth rate query on both UAT and PROD environments
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

QUERY = """
WITH monthly_users AS (
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
ORDER BY month DESC
LIMIT 12;
"""

def get_uat_connection():
    """Get UAT (staging) connection"""
    return psycopg2.connect(
        host=os.getenv('CHEMLINK_DB_HOST'),
        port=os.getenv('CHEMLINK_DB_PORT', 5432),
        database=os.getenv('CHEMLINK_DB_NAME'),
        user=os.getenv('CHEMLINK_DB_USER'),
        password=os.getenv('CHEMLINK_DB_PASSWORD')
    )

def get_prod_connection():
    """Get PROD connection"""
    return psycopg2.connect(
        host=os.getenv('CHEMLINK_PRD_DB_HOST'),
        port=os.getenv('CHEMLINK_PRD_DB_PORT', 5432),
        database=os.getenv('CHEMLINK_PRD_DB_NAME'),
        user=os.getenv('CHEMLINK_PRD_DB_USER'),
        password=os.getenv('CHEMLINK_PRD_DB_PASSWORD')
    )

def run_query(conn, env_name):
    """Run query and display results"""
    print(f"\n{'='*80}")
    print(f"🔍 {env_name} ENVIRONMENT")
    print(f"{'='*80}")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(QUERY)
            results = cursor.fetchall()
            
            if not results:
                print("❌ No data returned from query")
            else:
                print(f"✅ Found {len(results)} months of data\n")
                print(f"{'Month':<20} {'New Users':<12} {'Prev Month':<12} {'Growth %':<12}")
                print("-" * 80)
                for row in results:
                    month = row['month'].strftime('%Y-%m') if row['month'] else 'NULL'
                    new_users = row['new_users'] or 0
                    prev_month = row['prev_month'] or 'N/A'
                    growth = row['growth_rate_pct'] if row['growth_rate_pct'] is not None else 'N/A'
                    print(f"{month:<20} {new_users:<12} {prev_month!s:<12} {growth!s:<12}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def main():
    print("\n" + "="*80)
    print("📊 MONTHLY USER GROWTH RATE - ENVIRONMENT COMPARISON")
    print("="*80)
    
    # Test UAT
    try:
        uat_conn = get_uat_connection()
        run_query(uat_conn, "UAT/STAGING")
    except Exception as e:
        print(f"\n❌ UAT Connection Error: {e}")
    
    # Test PROD
    try:
        prod_conn = get_prod_connection()
        run_query(prod_conn, "PRODUCTION")
    except Exception as e:
        print(f"\n❌ PROD Connection Error: {e}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
