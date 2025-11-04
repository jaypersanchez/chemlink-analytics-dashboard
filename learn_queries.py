#!/usr/bin/env python3
"""
Learn Your Dashboard Queries - Interactive Session
Let's go through each query together and understand the actual data
"""

from db_config import get_engagement_db_connection, get_chemlink_env_connection, execute_query
from sql_queries import SQL_QUERIES
import json
from datetime import datetime

def show_query_and_results(query_key, conn):
    """Show the query, run it, and display results for analysis"""
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
    
    print("\nRunning query...")
    try:
        results = execute_query(conn, query_info['query'])
        
        if not results:
            print("No results returned")
            return
        
        print(f"\nGot {len(results)} rows")
        print("\nRESULTS:")
        print("="*80)
        
        # Show results in readable format
        for i, row in enumerate(results, 1):
            print(f"\nRow {i}:")
            for key, value in row.items():
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d')
                print(f"  {key}: {value}")
            
            if i >= 10:  # Limit to first 10 rows
                remaining = len(results) - i
                if remaining > 0:
                    print(f"\n... and {remaining} more rows")
                break
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Error: {e}")

# Which queries are actually used in the dashboard?
DASHBOARD_QUERIES = [
    # Growth
    "new_users_monthly",
    "growth_rate_monthly",
    
    # Engagement - Basic (Engagement DB)
    "dau",
    "mau",
    "activity_by_type_monthly",
    "activity_distribution_current",
    "activity_intensity_levels",
    
    # Engagement - Comprehensive (ChemLink DB)
    "dau_comprehensive",
    "mau_comprehensive",
    "user_type",
    "collections_privacy",
]

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CHEMLINK ANALYTICS - LEARN YOUR QUERIES")
    print("="*80)
    print("\nLet's examine each query used in your dashboard")
    print("We'll look at the SQL and actual data together\n")
    
    # Connect to databases
    print("Connecting to databases...")
    engagement_conn = get_engagement_db_connection()
    chemlink_conn = get_chemlink_env_connection()
    print("Connected!\n")
    
    # Show all queries we'll examine
    print("Dashboard queries we'll examine:")
    for i, qkey in enumerate(DASHBOARD_QUERIES, 1):
        if qkey in SQL_QUERIES:
            print(f"  {i}. {qkey} - {SQL_QUERIES[qkey]['name']}")
    
    print("\n" + "="*80)
    input("\nPress ENTER to start examining queries one by one...")
    
    # Go through each query
    for qkey in DASHBOARD_QUERIES:
        if qkey not in SQL_QUERIES:
            continue
        
        # Reconnect if needed (connections may have closed)
        try:
            db_name = SQL_QUERIES[qkey]['database']
            if "Engagement" in db_name:
                conn = get_engagement_db_connection()
            else:
                conn = get_chemlink_env_connection()
        except:
            print("Reconnecting to database...")
            if "Engagement" in db_name:
                conn = get_engagement_db_connection()
            else:
                conn = get_chemlink_env_connection()
        
        # Show query and results
        show_query_and_results(qkey, conn)
        
        # Pause for discussion
        print("\n" + "="*80)
        response = input("\nPress ENTER for next query (or 'q' to quit): ")
        if response.lower() == 'q':
            break
    
    print("\n✅ Done! You now have a deep understanding of your dashboard data.\n")
