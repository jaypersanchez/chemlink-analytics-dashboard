import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Connect to ChemLink database
print("=" * 80)
print("CHEMLINK DATABASE - Checking for location/country data")
print("=" * 80)

try:
    conn_chemlink = psycopg2.connect(
        host=os.getenv('CHEMLINK_DB_HOST'),
        port=os.getenv('CHEMLINK_DB_PORT', 5432),
        database=os.getenv('CHEMLINK_DB_NAME'),
        user=os.getenv('CHEMLINK_DB_USER'),
        password=os.getenv('CHEMLINK_DB_PASSWORD')
    )
    
    cursor = conn_chemlink.cursor(cursor_factory=RealDictCursor)
    
    # Check persons table structure
    print("\n1. Checking persons table columns related to location:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'persons' 
        AND (column_name LIKE '%location%' OR column_name LIKE '%country%')
        ORDER BY column_name;
    """)
    cols = cursor.fetchall()
    if cols:
        for col in cols:
            print(f"   - {col['column_name']}: {col['data_type']}")
    else:
        print("   No location/country columns found")
    
    # Check if locations table exists
    print("\n2. Checking if 'locations' table exists:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'locations';
    """)
    result = cursor.fetchone()
    locations_exists = result is not None
    print(f"   Result: {'YES - locations table exists!' if locations_exists else 'NO - locations table does not exist'}")
    
    if locations_exists:
        print("\n3. Locations table structure:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'locations'
            ORDER BY ordinal_position;
        """)
        loc_cols = cursor.fetchall()
        for col in loc_cols:
            print(f"   - {col['column_name']}: {col['data_type']}")
        
        print("\n4. Sample locations data:")
        cursor.execute("SELECT * FROM locations LIMIT 5;")
        locs = cursor.fetchall()
        for loc in locs:
            print(f"   - {dict(loc)}")
    
    # Check persons table for location_id
    print("\n5. Sample persons with location_id:")
    cursor.execute("""
        SELECT id, first_name, last_name, location_id, created_at
        FROM persons 
        WHERE location_id IS NOT NULL 
        LIMIT 5;
    """)
    persons = cursor.fetchall()
    if persons:
        for p in persons:
            print(f"   - {p['first_name']} {p['last_name']}: location_id={p['location_id']}")
    else:
        print("   No persons with location_id found")
    
    conn_chemlink.close()
    
except Exception as e:
    print(f"Error querying ChemLink database: {e}")

# Connect to Engagement database
print("\n" + "=" * 80)
print("ENGAGEMENT DATABASE - Checking for location/country data")
print("=" * 80)

try:
    conn_engagement = psycopg2.connect(
        host=os.getenv('ENGAGEMENT_DB_HOST'),
        port=os.getenv('ENGAGEMENT_DB_PORT', 5432),
        database=os.getenv('ENGAGEMENT_DB_NAME'),
        user=os.getenv('ENGAGEMENT_DB_USER'),
        password=os.getenv('ENGAGEMENT_DB_PASSWORD')
    )
    
    cursor = conn_engagement.cursor(cursor_factory=RealDictCursor)
    
    # Check persons table in engagement db
    print("\n1. Checking persons table columns related to location:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'persons' 
        AND (column_name LIKE '%location%' OR column_name LIKE '%country%')
        ORDER BY column_name;
    """)
    cols = cursor.fetchall()
    if cols:
        for col in cols:
            print(f"   - {col['column_name']}: {col['data_type']}")
    else:
        print("   No location/country columns found in persons table")
    
    # Check if locations table exists
    print("\n2. Checking if 'locations' table exists:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'locations';
    """)
    result = cursor.fetchone()
    print(f"   Result: {'YES - locations table exists' if result else 'NO - locations table does not exist'}")
    
    # Try to find MAU with any location indicators
    print("\n3. Testing MAU query WITH location join:")
    try:
        cursor.execute("""
            SELECT 
                DATE_TRUNC('month', activity_date) as month,
                COUNT(DISTINCT person_id) as active_users
            FROM (
                SELECT person_id, created_at as activity_date 
                FROM posts WHERE deleted_at IS NULL
                UNION ALL
                SELECT person_id, created_at 
                FROM comments WHERE deleted_at IS NULL
            ) monthly_activity
            GROUP BY DATE_TRUNC('month', activity_date)
            ORDER BY month DESC
            LIMIT 3;
        """)
        mau_data = cursor.fetchall()
        print("   MAU Query successful (without location):")
        for row in mau_data:
            print(f"   - {row['month']}: {row['active_users']} active users")
    except Exception as e:
        print(f"   Error: {e}")
    
    conn_engagement.close()
    
except Exception as e:
    print(f"Error querying Engagement database: {e}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("\nTo enable MAU by country, we need:")
print("1. A 'locations' table with country information")
print("2. Persons table with location_id foreign key")
print("3. Or alternative: Add country column directly to persons table")
print("\nCheck the results above to see what's available.")
