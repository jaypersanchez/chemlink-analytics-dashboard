#!/usr/bin/env python3
from db_config import get_engagement_db_connection, get_chemlink_env_connection, execute_query

print('='*80)
print('VERIFYING: Are there ANY real users posting?')
print('='*80)

# Step 1: Get valid person IDs from ChemLink
chemlink_conn = get_chemlink_env_connection()
valid_ids = execute_query(chemlink_conn, 'SELECT id FROM persons WHERE deleted_at IS NULL;')
valid_id_set = {str(row['id']) for row in valid_ids}
print(f'\n✅ Valid users in ChemLink DB: {len(valid_id_set)}')

# Step 2: Get all posts with person info
engagement_conn = get_engagement_db_connection()
posts = execute_query(engagement_conn, '''
    SELECT person_id, COUNT(*) as post_count, 
           MIN(created_at) as first_post, 
           MAX(created_at) as last_post
    FROM posts 
    WHERE deleted_at IS NULL
    GROUP BY person_id
    ORDER BY post_count DESC;
''')

print(f'\n📊 Total unique posters: {len(posts)}')
print(f'\nPerson ID                                 Posts  First Post   Last Post    Status')
print('-'*90)

real_users = 0
ghost_users = 0

for row in posts:
    person_id = str(row['person_id'])
    is_real = person_id in valid_id_set
    status = '✅ REAL' if is_real else '❌ GHOST'
    
    if is_real:
        real_users += 1
    else:
        ghost_users += 1
    
    first = row['first_post'].strftime('%Y-%m-%d') if row['first_post'] else 'N/A'
    last = row['last_post'].strftime('%Y-%m-%d') if row['last_post'] else 'N/A'
    
    print(f'{person_id:40s} {row["post_count"]:6d} {first:12s} {last:12s} {status}')

print('\n' + '='*80)
print(f'SUMMARY:')
print(f'  Real users posting: {real_users}')
print(f'  Ghost users posting: {ghost_users}')
print(f'  Total posts from ghosts: {sum(row["post_count"] for row in posts if str(row["person_id"]) not in valid_id_set)}')
print('='*80)
