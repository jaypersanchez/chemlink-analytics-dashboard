#!/usr/bin/env python3
"""
Database Schema Comparison Tool
Compares schemas across DEV, UAT, and PROD environments

Usage:
    python compare_schemas.py
"""

import psycopg2
import os
from collections import defaultdict
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_url(env_name):
    """Construct database URL from environment variables"""
    if env_name == 'DEV':
        host = os.getenv('CHEMLINK_DEV_DB_HOST')
        port = os.getenv('CHEMLINK_DEV_DB_PORT')
        dbname = os.getenv('CHEMLINK_DEV_DB_NAME')
        user = os.getenv('CHEMLINK_DEV_DB_USER')
        password = os.getenv('CHEMLINK_DEV_DB_PASSWORD')
    elif env_name == 'UAT':
        host = os.getenv('ENGAGEMENT_DB_HOST')
        port = os.getenv('ENGAGEMENT_DB_PORT')
        dbname = os.getenv('ENGAGEMENT_DB_NAME')
        user = os.getenv('ENGAGEMENT_DB_USER')
        password = os.getenv('ENGAGEMENT_DB_PASSWORD')
    elif env_name == 'PROD':
        host = os.getenv('ENGAGEMENT_PRD_DB_HOST')
        port = os.getenv('ENGAGEMENT_PRD_DB_PORT')
        dbname = os.getenv('ENGAGEMENT_PRD_DB_NAME')
        user = os.getenv('ENGAGEMENT_PRD_DB_USER')
        password = os.getenv('ENGAGEMENT_PRD_DB_PASSWORD')
    else:
        raise ValueError(f"Unknown environment: {env_name}")
    
    if not all([host, port, dbname, user, password]):
        raise ValueError(f"Missing database credentials for {env_name}")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

def get_db_connection(env_name):
    """Get database connection for environment"""
    db_url = get_db_url(env_name)
    return psycopg2.connect(db_url)

def get_tables(conn):
    """Get all tables in the database"""
    query = """
        SELECT 
            schemaname,
            tablename,
            tableowner
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY schemaname, tablename;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_table_columns(conn, schema, table):
    """Get all columns for a specific table"""
    query = """
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
    """
    cursor = conn.cursor()
    cursor.execute(query, (schema, table))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_table_indexes(conn, schema, table):
    """Get all indexes for a specific table"""
    query = """
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = %s AND tablename = %s
        ORDER BY indexname;
    """
    cursor = conn.cursor()
    cursor.execute(query, (schema, table))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_table_constraints(conn, schema, table):
    """Get all constraints for a specific table"""
    query = """
        SELECT
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        LEFT JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.table_schema = %s AND tc.table_name = %s
        ORDER BY tc.constraint_type, tc.constraint_name;
    """
    cursor = conn.cursor()
    cursor.execute(query, (schema, table))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_schema_snapshot(env_name):
    """Get complete schema snapshot for an environment"""
    print(f"Fetching schema for {env_name}...")
    
    try:
        conn = get_db_connection(env_name)
        snapshot = {
            'environment': env_name,
            'timestamp': datetime.now().isoformat(),
            'tables': {}
        }
        
        tables = get_tables(conn)
        
        for schema, table, owner in tables:
            table_key = f"{schema}.{table}"
            
            # Get columns
            columns = get_table_columns(conn, schema, table)
            
            # Get indexes
            indexes = get_table_indexes(conn, schema, table)
            
            # Get constraints
            constraints = get_table_constraints(conn, schema, table)
            
            snapshot['tables'][table_key] = {
                'schema': schema,
                'table': table,
                'owner': owner,
                'columns': [
                    {
                        'name': col[0],
                        'type': col[1],
                        'max_length': col[2],
                        'nullable': col[3],
                        'default': col[4],
                        'position': col[5]
                    } for col in columns
                ],
                'indexes': [
                    {
                        'name': idx[0],
                        'definition': idx[1]
                    } for idx in indexes
                ],
                'constraints': [
                    {
                        'name': cons[0],
                        'type': cons[1],
                        'column': cons[2],
                        'foreign_table': cons[3],
                        'foreign_column': cons[4]
                    } for cons in constraints
                ]
            }
        
        conn.close()
        print(f"✓ Found {len(snapshot['tables'])} tables in {env_name}")
        return snapshot
        
    except Exception as e:
        print(f"✗ Error fetching schema for {env_name}: {e}")
        return None

def compare_schemas(snapshots):
    """Compare schemas across environments"""
    comparison = {
        'summary': {},
        'tables': {
            'missing_in_dev': [],
            'missing_in_uat': [],
            'missing_in_prod': [],
            'common_to_all': [],
            'differences': []
        },
        'column_differences': [],
        'index_differences': [],
        'constraint_differences': []
    }
    
    # Get all unique table names
    all_tables = set()
    for env, snapshot in snapshots.items():
        if snapshot:
            all_tables.update(snapshot['tables'].keys())
    
    # Compare table existence
    for table in sorted(all_tables):
        in_dev = table in snapshots.get('DEV', {}).get('tables', {})
        in_uat = table in snapshots.get('UAT', {}).get('tables', {})
        in_prod = table in snapshots.get('PROD', {}).get('tables', {})
        
        if in_dev and in_uat and in_prod:
            comparison['tables']['common_to_all'].append(table)
            # Compare details for common tables
            compare_table_details(table, snapshots, comparison)
        else:
            if not in_dev:
                comparison['tables']['missing_in_dev'].append(table)
            if not in_uat:
                comparison['tables']['missing_in_uat'].append(table)
            if not in_prod:
                comparison['tables']['missing_in_prod'].append(table)
    
    # Generate summary
    comparison['summary'] = {
        'total_unique_tables': len(all_tables),
        'common_to_all': len(comparison['tables']['common_to_all']),
        'missing_in_dev': len(comparison['tables']['missing_in_dev']),
        'missing_in_uat': len(comparison['tables']['missing_in_uat']),
        'missing_in_prod': len(comparison['tables']['missing_in_prod']),
        'tables_with_differences': len(comparison['tables']['differences'])
    }
    
    return comparison

def compare_table_details(table, snapshots, comparison):
    """Compare column, index, and constraint details for a table"""
    dev_table = snapshots.get('DEV', {}).get('tables', {}).get(table, {})
    uat_table = snapshots.get('UAT', {}).get('tables', {}).get(table, {})
    prod_table = snapshots.get('PROD', {}).get('tables', {}).get(table, {})
    
    has_diff = False
    
    # Compare columns
    dev_cols = {col['name']: col for col in dev_table.get('columns', [])}
    uat_cols = {col['name']: col for col in uat_table.get('columns', [])}
    prod_cols = {col['name']: col for col in prod_table.get('columns', [])}
    
    all_cols = set(dev_cols.keys()) | set(uat_cols.keys()) | set(prod_cols.keys())
    
    for col_name in all_cols:
        in_dev = col_name in dev_cols
        in_uat = col_name in uat_cols
        in_prod = col_name in prod_cols
        
        if not (in_dev and in_uat and in_prod):
            has_diff = True
            comparison['column_differences'].append({
                'table': table,
                'column': col_name,
                'in_dev': in_dev,
                'in_uat': in_uat,
                'in_prod': in_prod,
                'dev_type': dev_cols.get(col_name, {}).get('type'),
                'uat_type': uat_cols.get(col_name, {}).get('type'),
                'prod_type': prod_cols.get(col_name, {}).get('type')
            })
        elif dev_cols[col_name]['type'] != uat_cols[col_name]['type'] or \
             uat_cols[col_name]['type'] != prod_cols[col_name]['type']:
            has_diff = True
            comparison['column_differences'].append({
                'table': table,
                'column': col_name,
                'in_dev': True,
                'in_uat': True,
                'in_prod': True,
                'dev_type': dev_cols[col_name]['type'],
                'uat_type': uat_cols[col_name]['type'],
                'prod_type': prod_cols[col_name]['type'],
                'issue': 'Type mismatch'
            })
    
    # Compare indexes
    dev_idx = {idx['name'] for idx in dev_table.get('indexes', [])}
    uat_idx = {idx['name'] for idx in uat_table.get('indexes', [])}
    prod_idx = {idx['name'] for idx in prod_table.get('indexes', [])}
    
    all_idx = dev_idx | uat_idx | prod_idx
    
    for idx_name in all_idx:
        in_dev = idx_name in dev_idx
        in_uat = idx_name in uat_idx
        in_prod = idx_name in prod_idx
        
        if not (in_dev and in_uat and in_prod):
            has_diff = True
            comparison['index_differences'].append({
                'table': table,
                'index': idx_name,
                'in_dev': in_dev,
                'in_uat': in_uat,
                'in_prod': in_prod
            })
    
    if has_diff:
        comparison['tables']['differences'].append(table)

def generate_report(comparison, snapshots):
    """Generate human-readable report"""
    report = []
    report.append("=" * 80)
    report.append("DATABASE SCHEMA COMPARISON REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 80)
    summary = comparison['summary']
    report.append(f"Total Unique Tables:        {summary['total_unique_tables']}")
    report.append(f"Tables in All Environments: {summary['common_to_all']}")
    report.append(f"Tables Missing in DEV:      {summary['missing_in_dev']}")
    report.append(f"Tables Missing in UAT:      {summary['missing_in_uat']}")
    report.append(f"Tables Missing in PROD:     {summary['missing_in_prod']}")
    report.append(f"Tables with Differences:    {summary['tables_with_differences']}")
    report.append("")
    
    # Environment details
    report.append("ENVIRONMENT DETAILS")
    report.append("-" * 80)
    for env, snapshot in snapshots.items():
        if snapshot:
            report.append(f"{env}: {len(snapshot['tables'])} tables")
    report.append("")
    
    # Tables missing in each environment
    if comparison['tables']['missing_in_dev']:
        report.append("TABLES MISSING IN DEV")
        report.append("-" * 80)
        for table in comparison['tables']['missing_in_dev']:
            report.append(f"  • {table}")
        report.append("")
    
    if comparison['tables']['missing_in_uat']:
        report.append("TABLES MISSING IN UAT")
        report.append("-" * 80)
        for table in comparison['tables']['missing_in_uat']:
            report.append(f"  • {table}")
        report.append("")
    
    if comparison['tables']['missing_in_prod']:
        report.append("TABLES MISSING IN PROD")
        report.append("-" * 80)
        for table in comparison['tables']['missing_in_prod']:
            report.append(f"  • {table}")
        report.append("")
    
    # Column differences
    if comparison['column_differences']:
        report.append("COLUMN DIFFERENCES")
        report.append("-" * 80)
        for diff in comparison['column_differences']:
            report.append(f"Table: {diff['table']}")
            report.append(f"  Column: {diff['column']}")
            report.append(f"    DEV:  {'✓' if diff['in_dev'] else '✗'} ({diff.get('dev_type', 'N/A')})")
            report.append(f"    UAT:  {'✓' if diff['in_uat'] else '✗'} ({diff.get('uat_type', 'N/A')})")
            report.append(f"    PROD: {'✓' if diff['in_prod'] else '✗'} ({diff.get('prod_type', 'N/A')})")
            if diff.get('issue'):
                report.append(f"    Issue: {diff['issue']}")
            report.append("")
    
    # Index differences
    if comparison['index_differences']:
        report.append("INDEX DIFFERENCES")
        report.append("-" * 80)
        for diff in comparison['index_differences']:
            report.append(f"Table: {diff['table']}")
            report.append(f"  Index: {diff['index']}")
            report.append(f"    DEV:  {'✓' if diff['in_dev'] else '✗'}")
            report.append(f"    UAT:  {'✓' if diff['in_uat'] else '✗'}")
            report.append(f"    PROD: {'✓' if diff['in_prod'] else '✗'}")
            report.append("")
    
    # UAT vs PROD similarity
    report.append("UAT vs PROD SIMILARITY ANALYSIS")
    report.append("-" * 80)
    uat_tables = set(snapshots.get('UAT', {}).get('tables', {}).keys())
    prod_tables = set(snapshots.get('PROD', {}).get('tables', {}).keys())
    common = uat_tables & prod_tables
    
    if uat_tables and prod_tables:
        similarity = (len(common) / max(len(uat_tables), len(prod_tables))) * 100
        report.append(f"Schema Similarity: {similarity:.2f}%")
        report.append(f"Tables in both: {len(common)}")
        report.append(f"Only in UAT: {len(uat_tables - prod_tables)}")
        report.append(f"Only in PROD: {len(prod_tables - uat_tables)}")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    """Main execution"""
    print("\nDatabase Schema Comparison Tool")
    print("=" * 80)
    print()
    
    # Fetch schemas
    snapshots = {}
    for env in ['DEV', 'UAT', 'PROD']:
        snapshot = get_schema_snapshot(env)
        if snapshot:
            snapshots[env] = snapshot
    
    if not snapshots:
        print("\n✗ No schemas fetched. Check database connections.")
        return
    
    print()
    print("Comparing schemas...")
    
    # Compare
    comparison = compare_schemas(snapshots)
    
    # Generate report
    report = generate_report(comparison, snapshots)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"schema_comparison_report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Save JSON
    json_file = f"schema_comparison_data_{timestamp}.json"
    with open(json_file, 'w') as f:
        # Convert snapshots to JSON-serializable format
        json_data = {
            'snapshots': snapshots,
            'comparison': comparison
        }
        json.dump(json_data, f, indent=2, default=str)
    
    print()
    print(report)
    print()
    print(f"✓ Report saved to: {report_file}")
    print(f"✓ JSON data saved to: {json_file}")

if __name__ == '__main__':
    main()
