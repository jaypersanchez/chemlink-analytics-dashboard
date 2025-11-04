#!/usr/bin/env python3
"""
Check for orphaned engagement records
Records in Engagement DB that reference non-existent users in ChemLink DB
"""

from db_config import get_engagement_db_connection, get_chemlink_env_connection, execute_query

print("\n" + "="*80)
print("CHECKING FOR ORPHANED ENGAGEMENT RECORDS")
print("="*80)

# Step 1: Get all valid person IDs from ChemLink DB
print("\n1. Fetching valid person IDs from ChemLink DB...")
chemlink_conn = get_chemlink_env_connection()
chemlink_query = "SELECT id FROM persons WHERE deleted_at IS NULL;"
valid_persons = execute_query(chemlink_conn, chemlink_query)
valid_person_ids = {str(row['id']) for row in valid_persons}
print(f"   ✅ Found {len(valid_person_ids)} valid persons in ChemLink DB")

# Step 2: Get all person_ids from Engagement DB posts
print("\n2. Fetching person_ids from Engagement DB posts...")
engagement_conn = get_engagement_db_connection()
posts_query = "SELECT DISTINCT person_id FROM posts WHERE deleted_at IS NULL;"
post_persons = execute_query(engagement_conn, posts_query)
post_person_ids = {str(row['person_id']) for row in post_persons}
print(f"   ✅ Found {len(post_person_ids)} unique person_ids in posts")

# Step 3: Get all person_ids from Engagement DB comments
print("\n3. Fetching person_ids from Engagement DB comments...")
engagement_conn = get_engagement_db_connection()  # Reconnect
comments_query = "SELECT DISTINCT person_id FROM comments WHERE deleted_at IS NULL;"
comment_persons = execute_query(engagement_conn, comments_query)
comment_person_ids = {str(row['person_id']) for row in comment_persons}
print(f"   ✅ Found {len(comment_person_ids)} unique person_ids in comments")

# Step 4: Find orphaned records
print("\n" + "="*80)
print("RESULTS")
print("="*80)

orphaned_post_ids = post_person_ids - valid_person_ids
orphaned_comment_ids = comment_person_ids - valid_person_ids

print(f"\n📊 Orphaned Posts:")
print(f"   Person IDs in posts but NOT in ChemLink: {len(orphaned_post_ids)}")
if orphaned_post_ids:
    print(f"   Orphaned person_ids: {list(orphaned_post_ids)[:10]}")  # Show first 10
    if len(orphaned_post_ids) > 10:
        print(f"   ... and {len(orphaned_post_ids) - 10} more")

print(f"\n📊 Orphaned Comments:")
print(f"   Person IDs in comments but NOT in ChemLink: {len(orphaned_comment_ids)}")
if orphaned_comment_ids:
    print(f"   Orphaned person_ids: {list(orphaned_comment_ids)[:10]}")
    if len(orphaned_comment_ids) > 10:
        print(f"   ... and {len(orphaned_comment_ids) - 10} more")

# Step 5: Count total orphaned posts/comments
if orphaned_post_ids:
    orphaned_ids_str = "', '".join(orphaned_post_ids)
    orphaned_posts_count_query = f"""
        SELECT COUNT(*) as count 
        FROM posts 
        WHERE deleted_at IS NULL 
          AND person_id IN ('{orphaned_ids_str}');
    """
    result = execute_query(engagement_conn, orphaned_posts_count_query)
    print(f"\n   Total orphaned POSTS (rows): {result[0]['count']}")

if orphaned_comment_ids:
    orphaned_ids_str = "', '".join(orphaned_comment_ids)
    orphaned_comments_count_query = f"""
        SELECT COUNT(*) as count 
        FROM comments 
        WHERE deleted_at IS NULL 
          AND person_id IN ('{orphaned_ids_str}');
    """
    result = execute_query(engagement_conn, orphaned_comments_count_query)
    print(f"   Total orphaned COMMENTS (rows): {result[0]['count']}")

# Step 6: Check reverse - persons in Engagement but not in ChemLink
print(f"\n" + "="*80)
print("REVERSE CHECK")
print("="*80)
engagement_persons_query = "SELECT id FROM persons;"
engagement_persons = execute_query(engagement_conn, engagement_persons_query)
engagement_person_ids = {str(row['id']) for row in engagement_persons}

print(f"\n📊 Persons in Engagement DB: {len(engagement_person_ids)}")
print(f"📊 Persons in ChemLink DB: {len(valid_person_ids)}")

missing_in_chemlink = engagement_person_ids - valid_person_ids
missing_in_engagement = valid_person_ids - engagement_person_ids

print(f"\n⚠️  Persons in Engagement DB but NOT in ChemLink DB: {len(missing_in_chemlink)}")
if missing_in_chemlink:
    print(f"   Sample IDs: {list(missing_in_chemlink)[:5]}")

print(f"\n⚠️  Persons in ChemLink DB but NOT in Engagement DB: {len(missing_in_engagement)}")
print(f"   (This is normal - users who haven't created profiles in engagement system)")

print("\n" + "="*80 + "\n")
