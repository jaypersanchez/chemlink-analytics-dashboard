#!/usr/bin/env python3
"""Run a single query and show results"""
import sys
from db_config import get_engagement_db_connection, get_chemlink_env_connection, execute_query
from sql_queries import SQL_QUERIES
from datetime import datetime

def run_query(query_key):
    if query_key not in SQL_QUERIES:
        print(f"Query '{query_key}' not found")
        return
    
    query_info = SQL_QUERIES[query_key]
    
    print("\n" + "="*80)
    print(f"QUERY: {query_key}")
    print(f"NAME: {query_info['name']}")
    print(f"DATABASE: {query_info['database']}")
    print("="*80)
    
    print("\nSQL:")
    print("-"*80)
    print(query_info['query'])
    print("-"*80)
    
    # Connect to appropriate database
    if "Engagement" in query_info['database']:
        conn = get_engagement_db_connection()
    else:
        conn = get_chemlink_env_connection()
    
    print("\nRunning query...")
    try:
        results = execute_query(conn, query_info['query'])
        
        if not results:
            print("No results returned")
            return
        
        print(f"\n✅ Got {len(results)} rows\n")
        print("RESULTS:")
        print("="*80)
        
        for i, row in enumerate(results, 1):
            print(f"\nRow {i}:")
            for key, value in row.items():
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d')
                print(f"  {key}: {value}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_query(sys.argv[1])
    else:
        print("Usage: python3 run_single_query.py <query_key>")
        print("Example: python3 run_single_query.py dau")
