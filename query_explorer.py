#!/usr/bin/env python3
"""
Interactive Query Explorer for ChemLink Analytics Dashboard

This tool helps you deeply understand each metric by:
1. Running queries interactively
2. Showing raw results with explanations
3. Breaking down calculations step-by-step
4. Validating data makes sense

Usage:
    python query_explorer.py                    # Interactive menu
    python query_explorer.py --query dau        # Run specific query
    python query_explorer.py --list             # List all available queries
"""

import sys
import argparse
from datetime import datetime
from tabulate import tabulate
from db_config import get_engagement_db_connection, get_chemlink_env_connection, execute_query
from sql_queries import SQL_QUERIES

class QueryExplorer:
    def __init__(self):
        self.engagement_conn = None
        self.chemlink_conn = None
    
    def connect_dbs(self):
        """Establish database connections"""
        print("🔌 Connecting to databases...")
        try:
            self.engagement_conn = get_engagement_db_connection()
            self.chemlink_conn = get_chemlink_env_connection()
            print("✅ Connected to both databases\n")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            sys.exit(1)
    
    def get_db_connection(self, db_name):
        """Get the appropriate database connection"""
        if "Engagement" in db_name:
            return self.engagement_conn
        elif "ChemLink" in db_name:
            return self.chemlink_conn
        else:
            # Default to ChemLink for cross-database queries
            return self.chemlink_conn
    
    def list_queries(self):
        """Display all available queries"""
        print("\n📊 AVAILABLE QUERIES\n" + "="*80)
        
        categories = {
            "Growth Metrics": ["new_users_monthly", "growth_rate_monthly"],
            "Engagement - Posts/Comments": ["dau", "mau", "activity_by_type_monthly", 
                                            "activity_distribution_current", "activity_intensity_levels"],
            "Engagement - Content": ["post_frequency", "engagement_rate", "content_type"],
            "Users": ["active_posters", "post_reach"],
            "Profiles": ["profile_completion", "profile_freshness"],
            "Companies & Roles": ["top_companies", "top_roles", "education_distribution"],
            "Geography": ["geographic_distribution"],
            "Features": ["account_funnel", "profile_additions", "collections_created",
                        "collections_shared", "finder_searches", "finder_engagement"],
            "ChemLink Comprehensive": ["dau_comprehensive", "mau_comprehensive", 
                                       "user_type", "collections_privacy"]
        }
        
        for category, query_keys in categories.items():
            print(f"\n🔸 {category}")
            for key in query_keys:
                if key in SQL_QUERIES:
                    query_info = SQL_QUERIES[key]
                    print(f"   • {key:30s} - {query_info['name']}")
                    print(f"     {'':32s} DB: {query_info['database']}")
    
    def explain_query(self, query_key):
        """Explain what a query does in business terms"""
        if query_key not in SQL_QUERIES:
            print(f"❌ Query '{query_key}' not found")
            return None
        
        query_info = SQL_QUERIES[query_key]
        
        # Business context explanations
        explanations = {
            "dau": {
                "what": "Counts unique users who posted OR commented each day",
                "why": "Shows daily community engagement - are people actively participating?",
                "interpret": "Higher = more engaged community. Look for trends and patterns.",
                "caveat": "Doesn't count passive readers, only active contributors"
            },
            "mau": {
                "what": "Counts unique users who posted OR commented in each month",
                "why": "Monthly snapshot of community health - smooths out daily noise",
                "interpret": "Growing MAU = healthy community. Flat/declining = need intervention",
                "caveat": "Same user posting multiple times only counts once"
            },
            "activity_by_type_monthly": {
                "what": "Breaks down MAU by activity type: who posts vs who comments",
                "why": "Understand WHAT users do - posting shows creation, commenting shows engagement",
                "interpret": "High comment:post ratio = engaged discussions. Low = one-way broadcasting",
                "caveat": "Same user can be in both categories if they post AND comment"
            },
            "activity_distribution_current": {
                "what": "Shows percentage split of posters vs commenters THIS MONTH",
                "why": "Quick snapshot of current engagement patterns",
                "interpret": "Imbalanced = investigate (e.g., 90% comments, 10% posts = few creators)",
                "caveat": "Current month only - may be incomplete early in month"
            },
            "activity_intensity_levels": {
                "what": "Categorizes users by activity level: Power/Active/Regular/Casual",
                "why": "Find your power users and understand engagement depth",
                "interpret": "More power users = stronger engagement. Many casual = shallow engagement",
                "caveat": "Thresholds (20+, 10-19, etc.) are arbitrary - adjust based on your product"
            },
            "new_users_monthly": {
                "what": "Counts new account sign-ups per month",
                "why": "Tracks top-of-funnel growth - are you acquiring users?",
                "interpret": "Steady growth = good. Spikes = marketing campaigns. Decline = alarm",
                "caveat": "New users ≠ active users. Check activation separately"
            },
            "growth_rate_monthly": {
                "what": "Percentage change in new users month-over-month",
                "why": "Shows acceleration/deceleration of growth",
                "interpret": "Positive = accelerating. Negative = slowing. Use to forecast",
                "caveat": "Small base numbers make percentages volatile"
            },
            "post_frequency": {
                "what": "Daily post count and posts per user",
                "why": "Measures content creation intensity",
                "interpret": "Low posts/user = struggling. High = vibrant creation",
                "caveat": "Quality matters too - lots of spam posts is bad"
            },
            "engagement_rate": {
                "what": "Comments per post by content type",
                "why": "Which content types drive discussion?",
                "interpret": "High = engaging content. Low = content not resonating",
                "caveat": "Some content types (questions) naturally get more comments"
            }
        }
        
        explanation = explanations.get(query_key, {
            "what": "Check the SQL query for details",
            "why": "This metric tracks user behavior",
            "interpret": "Look for trends and anomalies",
            "caveat": "Consider business context when interpreting"
        })
        
        print("\n" + "="*80)
        print(f"📊 QUERY: {query_info['name']}")
        print("="*80)
        print(f"\n🔹 DATABASE: {query_info['database']}")
        print(f"\n🔹 WHAT IT DOES:\n   {explanation['what']}")
        print(f"\n🔹 WHY IT MATTERS:\n   {explanation['why']}")
        print(f"\n🔹 HOW TO INTERPRET:\n   {explanation['interpret']}")
        print(f"\n⚠️  IMPORTANT CAVEAT:\n   {explanation['caveat']}")
        print("\n" + "-"*80)
        print("📝 SQL QUERY:")
        print("-"*80)
        print(query_info['query'])
        print("="*80 + "\n")
        
        return query_info
    
    def run_query(self, query_key, show_sql=True, limit=None):
        """Execute a query and display results"""
        if show_sql:
            query_info = self.explain_query(query_key)
            if not query_info:
                return
        else:
            query_info = SQL_QUERIES[query_key]
        
        conn = self.get_db_connection(query_info['database'])
        
        try:
            print(f"⏳ Executing query '{query_key}'...\n")
            
            query = query_info['query']
            if limit:
                # Add LIMIT if not already present
                if 'LIMIT' not in query.upper():
                    query = query.rstrip(';') + f' LIMIT {limit};'
            
            results = execute_query(conn, query)
            
            if not results:
                print("📭 No results returned")
                return
            
            print(f"✅ Found {len(results)} row(s)\n")
            
            # Display as table
            if results:
                headers = results[0].keys()
                rows = [list(row.values()) for row in results]
                print(tabulate(rows, headers=headers, tablefmt='grid'))
            
            # Add context-specific insights
            self._add_insights(query_key, results)
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    def _add_insights(self, query_key, results):
        """Add automated insights based on query results"""
        if not results:
            return
        
        print("\n" + "="*80)
        print("💡 INSIGHTS")
        print("="*80)
        
        if query_key == "dau" and results:
            # Calculate average DAU
            avg_dau = sum(r.get('active_users', 0) for r in results) / len(results)
            print(f"📈 Average DAU (last {len(results)} days): {avg_dau:.0f} users")
            
            # Check for posting vs commenting
            if 'users_who_posted' in results[0]:
                total_posts = sum(r.get('users_who_posted', 0) for r in results)
                total_comments = sum(r.get('users_who_commented', 0) for r in results)
                if total_posts > 0:
                    ratio = total_comments / total_posts
                    print(f"💬 Comment:Post ratio: {ratio:.2f}x (more comments = better engagement)")
        
        elif query_key == "mau" and results:
            # Show growth trend
            if len(results) >= 2:
                current = results[0].get('active_users', 0)
                previous = results[1].get('active_users', 0)
                change = ((current - previous) / previous * 100) if previous > 0 else 0
                trend = "📈 Growing" if change > 0 else "📉 Declining" if change < 0 else "➡️  Flat"
                print(f"{trend} - MAU changed {change:+.1f}% from last month ({previous} → {current})")
        
        elif query_key == "activity_distribution_current" and results:
            # Analyze balance
            for row in results:
                activity_type = row.get('activity_type', '')
                percentage = row.get('percentage', 0)
                if activity_type == 'post' and percentage < 30:
                    print(f"⚠️  Warning: Only {percentage}% are posting - few content creators!")
                elif activity_type == 'comment' and percentage > 70:
                    print(f"✅ Good: {percentage}% commenting - high engagement with content")
        
        elif query_key == "activity_intensity_levels" and results:
            # Analyze user distribution
            latest_month = results[0].get('month') if results else None
            latest_data = [r for r in results if r.get('month') == latest_month]
            
            if latest_data:
                total_users = sum(r.get('user_count', 0) for r in latest_data)
                power_users = sum(r.get('user_count', 0) for r in latest_data 
                                 if 'Power' in r.get('intensity_level', ''))
                casual_users = sum(r.get('user_count', 0) for r in latest_data 
                                  if 'Casual' in r.get('intensity_level', ''))
                
                if total_users > 0:
                    power_pct = (power_users / total_users) * 100
                    casual_pct = (casual_users / total_users) * 100
                    
                    print(f"👥 User Distribution (latest month):")
                    print(f"   • Power Users: {power_pct:.1f}% ({power_users}/{total_users})")
                    print(f"   • Casual Users: {casual_pct:.1f}% ({casual_users}/{total_users})")
                    
                    if power_pct < 5:
                        print(f"⚠️  Low power user percentage - may need more engagement incentives")
                    elif power_pct > 15:
                        print(f"✅ Strong power user base - core community is engaged")
        
        elif query_key == "growth_rate_monthly" and results:
            # Analyze growth trends
            rates = [r.get('growth_rate_pct', 0) for r in results if r.get('growth_rate_pct') is not None]
            if rates:
                avg_rate = sum(rates) / len(rates)
                print(f"📊 Average monthly growth rate: {avg_rate:+.1f}%")
                
                if avg_rate > 10:
                    print("🚀 Strong growth! Consider scaling infrastructure")
                elif avg_rate < 0:
                    print("⚠️  Negative growth - investigate churn and acquisition")
                else:
                    print("➡️  Steady growth - monitor for changes")
        
        print("="*80 + "\n")
    
    def compare_queries(self, query_keys):
        """Run multiple queries side by side for comparison"""
        print("\n" + "="*80)
        print("🔀 COMPARING QUERIES")
        print("="*80 + "\n")
        
        for key in query_keys:
            self.run_query(key, show_sql=False, limit=5)
            print("\n" + "-"*80 + "\n")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("\n" + "="*80)
        print("🔍 CHEMLINK ANALYTICS - INTERACTIVE QUERY EXPLORER")
        print("="*80)
        print("\nThis tool helps you understand every metric in your dashboard.")
        print("You'll see: SQL queries, business context, and data insights.\n")
        
        while True:
            print("\nOptions:")
            print("  1. List all queries")
            print("  2. Explore a specific query")
            print("  3. Compare multiple queries")
            print("  4. Quick DAU/MAU snapshot")
            print("  5. Exit")
            
            choice = input("\nYour choice (1-5): ").strip()
            
            if choice == "1":
                self.list_queries()
            
            elif choice == "2":
                query_key = input("\nEnter query key (e.g., 'dau', 'mau'): ").strip()
                self.run_query(query_key)
            
            elif choice == "3":
                keys = input("\nEnter query keys separated by commas: ").strip()
                query_keys = [k.strip() for k in keys.split(",")]
                self.compare_queries(query_keys)
            
            elif choice == "4":
                print("\n📊 QUICK ENGAGEMENT SNAPSHOT\n")
                self.run_query("dau", show_sql=False, limit=7)
                print("\n")
                self.run_query("mau", show_sql=False, limit=3)
            
            elif choice == "5":
                print("\n👋 Goodbye!\n")
                break
            
            else:
                print("\n❌ Invalid choice. Please try again.")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive Query Explorer for ChemLink Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--list', action='store_true', help='List all available queries')
    parser.add_argument('--query', type=str, help='Run a specific query')
    parser.add_argument('--compare', type=str, help='Compare queries (comma-separated)')
    parser.add_argument('--limit', type=int, help='Limit results to N rows')
    
    args = parser.parse_args()
    
    explorer = QueryExplorer()
    explorer.connect_dbs()
    
    if args.list:
        explorer.list_queries()
    elif args.query:
        explorer.run_query(args.query, show_sql=True, limit=args.limit)
    elif args.compare:
        keys = [k.strip() for k in args.compare.split(',')]
        explorer.compare_queries(keys)
    else:
        # Interactive mode
        explorer.interactive_mode()


if __name__ == "__main__":
    main()
