import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_engagement_db_connection():
    """Get connection to Engagement Platform database"""
    return psycopg2.connect(
        host=os.getenv('ENGAGEMENT_DB_HOST'),
        port=os.getenv('ENGAGEMENT_DB_PORT', 5432),
        database=os.getenv('ENGAGEMENT_DB_NAME'),
        user=os.getenv('ENGAGEMENT_DB_USER'),
        password=os.getenv('ENGAGEMENT_DB_PASSWORD')
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
