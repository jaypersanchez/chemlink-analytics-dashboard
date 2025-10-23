from db_config import get_engagement_db_connection, execute_query

# Check if there's job-related data
query = """
SELECT 
    type,
    COUNT(*) as count,
    MIN(created_at) as first_post,
    MAX(created_at) as last_post
FROM posts
WHERE deleted_at IS NULL
GROUP BY type
ORDER BY count DESC;
"""

conn = get_engagement_db_connection()
results = execute_query(conn, query)

print('Post types in Engagement DB:')
for row in results:
    print(f"  {row['type']}: {row['count']} posts")
    print(f"    First: {row['first_post']}")
    print(f"    Last: {row['last_post']}")
    print()

# Check if we can see job content
job_query = """
SELECT 
    id,
    type,
    LEFT(content, 100) as preview,
    created_at,
    link_url
FROM posts
WHERE type ILIKE '%job%'
  AND deleted_at IS NULL
LIMIT 5;
"""

conn2 = get_engagement_db_connection()
job_results = execute_query(conn2, job_query)

print('\nSample job posts:')
for row in job_results:
    print(f"  ID: {row['id']}")
    print(f"  Type: {row['type']}")
    print(f"  Preview: {row['preview']}")
    print(f"  Link: {row['link_url']}")
    print()
