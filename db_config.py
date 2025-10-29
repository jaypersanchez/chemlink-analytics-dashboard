import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_chemlink_env_connection():
    """Get ChemLink connection based on APP_ENV setting"""
    # Reload dotenv to get latest environment
    load_dotenv(override=True)
    app_env = os.getenv('APP_ENV', 'uat').lower()
    
    if app_env == 'prod':
        return get_chemlink_prd_db_connection()
    elif app_env == 'dev':
        return get_chemlink_dev_db_connection()
    else:  # default to uat/staging
        return get_chemlink_db_connection()

def get_engagement_db_connection():
    """Get connection to Engagement Platform database based on APP_ENV"""
    load_dotenv(override=True)
    app_env = os.getenv('APP_ENV', 'uat').lower()
    
    if app_env == 'prod':
        return get_engagement_prd_db_connection()
    else:  # default to uat/staging
        return get_engagement_uat_db_connection()

def get_engagement_uat_db_connection():
    """Get connection to Engagement Platform UAT/Staging database"""
    return psycopg2.connect(
        host=os.getenv('ENGAGEMENT_DB_HOST'),
        port=os.getenv('ENGAGEMENT_DB_PORT', 5432),
        database=os.getenv('ENGAGEMENT_DB_NAME'),
        user=os.getenv('ENGAGEMENT_DB_USER'),
        password=os.getenv('ENGAGEMENT_DB_PASSWORD')
    )

def get_engagement_prd_db_connection():
    """Get connection to Engagement Platform Production database (READ-ONLY)"""
    return psycopg2.connect(
        host=os.getenv('ENGAGEMENT_PRD_DB_HOST'),
        port=os.getenv('ENGAGEMENT_PRD_DB_PORT', 5432),
        database=os.getenv('ENGAGEMENT_PRD_DB_NAME'),
        user=os.getenv('ENGAGEMENT_PRD_DB_USER'),
        password=os.getenv('ENGAGEMENT_PRD_DB_PASSWORD')
    )

def get_chemlink_db_connection():
    """Get connection to ChemLink Service database"""
    return psycopg2.connect(
        host=os.getenv('CHEMLINK_DB_HOST'),
        port=os.getenv('CHEMLINK_DB_PORT', 5432),
        database=os.getenv('CHEMLINK_DB_NAME'),
        user=os.getenv('CHEMLINK_DB_USER'),
        password=os.getenv('CHEMLINK_DB_PASSWORD')
    )

def get_chemlink_dev_db_connection():
    """Get connection to ChemLink Development database"""
    return psycopg2.connect(
        host=os.getenv('CHEMLINK_DEV_DB_HOST'),
        port=os.getenv('CHEMLINK_DEV_DB_PORT', 5432),
        database=os.getenv('CHEMLINK_DEV_DB_NAME'),
        user=os.getenv('CHEMLINK_DEV_DB_USER'),
        password=os.getenv('CHEMLINK_DEV_DB_PASSWORD')
    )

def get_chemlink_prd_db_connection():
    """Get connection to ChemLink Production database (READ-ONLY)"""
    return psycopg2.connect(
        host=os.getenv('CHEMLINK_PRD_DB_HOST'),
        port=os.getenv('CHEMLINK_PRD_DB_PORT', 5432),
        database=os.getenv('CHEMLINK_PRD_DB_NAME'),
        user=os.getenv('CHEMLINK_PRD_DB_USER'),
        password=os.getenv('CHEMLINK_PRD_DB_PASSWORD')
    )

def execute_query(connection, query, params=None):
    """Execute a query and return results as list of dictionaries"""
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        connection.close()
