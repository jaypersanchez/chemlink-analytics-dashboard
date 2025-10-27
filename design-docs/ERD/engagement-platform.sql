-- ==============================================================================
-- ChemLink Engagement Platform Analysis Queries
-- ==============================================================================
-- Purpose: Analyze the Engagement Platform (LinkedIn-like social features)
-- Database: engagement-platform-stg (PostgreSQL)
-- Created: October 21, 2025
-- Author: Jay Constantine Sanchez (Data Architect)
-- ==============================================================================

-- ==============================================================================
-- 1. SEARCH FOR SPECIFIC USER PROFILES
-- ==============================================================================
-- Search for specific email addresses in the social platform
SELECT 
    id,
    external_id, -- Links to ChemLink Service database
    first_name,
    last_name, 
    email,
    company_name,
    role_title,
    employment_status,
    created_at
FROM persons 
WHERE email IN ('jsanchez@nmblr.ai', 'jaypersanchez@gmail.com', 'virlanchainworks@gmail.com')
ORDER BY created_at DESC;

-- ==============================================================================
-- 2. COMPLETE SOCIAL PROFILE (User Profile Data)
-- ==============================================================================
-- Get complete social profile for Jayper Sanchez
SELECT 
    p.id,
    p.external_id,
    p.iam_id,
    p.first_name || ' ' || p.last_name as full_name,
    p.email,
    p.company_name,
    p.role_title,
    p.employment_status,
    p.mobile_number,
    p.mobile_number_country_code,
    p.profile_picture_key,
    p.profile_pic_updated_at,
    p.created_at,
    p.updated_at
FROM persons p
WHERE p.email = 'jsanchez@nmblr.ai';

-- ==============================================================================
-- 3. USER'S SOCIAL ACTIVITY SUMMARY
-- ==============================================================================
-- Check social engagement activity for a specific user
SELECT 'POSTS_CREATED' as activity_type, COUNT(*) as count
FROM posts 
WHERE person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND deleted_at IS NULL

UNION ALL

SELECT 'COMMENTS_MADE' as activity_type, COUNT(*) as count  
FROM comments
WHERE person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND deleted_at IS NULL

UNION ALL

SELECT 'GROUP_MEMBERSHIPS' as activity_type, COUNT(*) as count
FROM group_members  
WHERE person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND deleted_at IS NULL

UNION ALL

SELECT 'MENTIONS_RECEIVED' as activity_type, COUNT(*) as count
FROM mentions
WHERE mentioned_person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND deleted_at IS NULL

ORDER BY activity_type;

-- ==============================================================================
-- 4. USER'S POSTS AND CONTENT
-- ==============================================================================
-- Get all posts created by the user
SELECT 
    p.id as post_id,
    p.type,
    p.content,
    p.link_url,
    p.media_keys,
    p.status,
    g.name as group_name,
    p.created_at,
    p.updated_at
FROM posts p
LEFT JOIN groups g ON p.group_id = g.id
WHERE p.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND p.deleted_at IS NULL
ORDER BY p.created_at DESC;

-- ==============================================================================
-- 5. USER'S COMMENTS AND INTERACTIONS
-- ==============================================================================
-- Get all comments made by the user
SELECT 
    c.id as comment_id,
    c.content,
    p.content as post_content,
    author.first_name || ' ' || author.last_name as post_author,
    c.parent_comment_id,
    c.created_at
FROM comments c
JOIN posts p ON c.post_id = p.id
JOIN persons author ON p.person_id = author.id
WHERE c.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND c.deleted_at IS NULL
ORDER BY c.created_at DESC;

-- ==============================================================================
-- 6. USER'S GROUP MEMBERSHIPS
-- ==============================================================================
-- Get groups the user is member of
SELECT 
    g.id as group_id,
    g.name as group_name,
    g.description,
    gm.role as member_role,
    gm.confirmed_at,
    creator.first_name || ' ' || creator.last_name as created_by,
    g.created_at as group_created,
    gm.created_at as membership_date
FROM group_members gm
JOIN groups g ON gm.group_id = g.id
LEFT JOIN persons creator ON g.created_by = creator.id
WHERE gm.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND gm.deleted_at IS NULL
  AND g.deleted_at IS NULL
ORDER BY gm.created_at DESC;

-- ==============================================================================
-- 7. USER'S MENTIONS AND NOTIFICATIONS
-- ==============================================================================
-- Get mentions involving the user
SELECT 
    g.id as group_id,
    g.name as group_name,
    g.description,
    gm.role as member_role,
    gm.confirmed_at,
    creator.first_name || ' ' || creator.last_name as created_by,
    g.created_at as group_created,
    gm.created_at as membership_date
FROM group_members gm
JOIN groups g ON gm.group_id = g.id
LEFT JOIN persons creator ON g.created_by = creator.id
WHERE gm.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND gm.deleted_at IS NULL
  AND g.deleted_at IS NULL
ORDER BY gm.created_at DESC;

-- ==============================================================================
-- 8. PLATFORM ACTIVITY STATISTICS
-- ==============================================================================
-- Overall platform engagement metrics
SELECT 'TOTAL_USERS' as metric, COUNT(*) as count FROM persons WHERE deleted_at IS NULL
UNION ALL
SELECT 'ACTIVE_USERS' as metric, COUNT(DISTINCT person_id) as count FROM posts WHERE deleted_at IS NULL
UNION ALL
SELECT 'TOTAL_POSTS' as metric, COUNT(*) as count FROM posts WHERE deleted_at IS NULL
UNION ALL  
SELECT 'TOTAL_COMMENTS' as metric, COUNT(*) as count FROM comments WHERE deleted_at IS NULL
UNION ALL
SELECT 'TOTAL_GROUPS' as metric, COUNT(*) as count FROM groups WHERE deleted_at IS NULL
UNION ALL
SELECT 'TOTAL_GROUP_MEMBERS' as metric, COUNT(*) as count FROM group_members WHERE deleted_at IS NULL
UNION ALL
SELECT 'TOTAL_MENTIONS' as metric, COUNT(*) as count FROM mentions WHERE deleted_at IS NULL
ORDER BY metric;

-- ==============================================================================
-- 9. RECENT PLATFORM ACTIVITY
-- ==============================================================================
-- Get recent posts across the platform (feed view)
SELECT 
    p.id as post_id,
    per.first_name || ' ' || per.last_name as author_name,
    per.email as author_email,
    per.company_name,
    per.role_title,
    p.type,
    LEFT(p.content, 200) as content_preview,
    p.link_url,
    p.status,
    g.name as group_name,
    (SELECT COUNT(*) FROM comments WHERE post_id = p.id AND deleted_at IS NULL) as comment_count,
    p.created_at
FROM posts p
JOIN persons per ON p.person_id = per.id
LEFT JOIN groups g ON p.group_id = g.id
WHERE p.deleted_at IS NULL
ORDER BY p.created_at DESC
LIMIT 20;

-- ==============================================================================
-- 10. USER ENGAGEMENT ANALYSIS
-- ==============================================================================
-- Analyze user engagement levels across the platform
WITH user_engagement AS (
    SELECT 
        p.id,
        p.first_name || ' ' || p.last_name as full_name,
        p.email,
        p.company_name,
        p.external_id,
        -- Engagement metrics
        (SELECT COUNT(*) FROM posts WHERE person_id = p.id AND deleted_at IS NULL) as post_count,
        (SELECT COUNT(*) FROM comments WHERE person_id = p.id AND deleted_at IS NULL) as comment_count,
        (SELECT COUNT(*) FROM group_members WHERE person_id = p.id AND deleted_at IS NULL) as group_memberships,
        (SELECT COUNT(*) FROM mentions WHERE mentioned_person_id = p.id AND deleted_at IS NULL) as mentions_received,
        p.created_at
    FROM persons p
    WHERE p.deleted_at IS NULL
)
SELECT 
    full_name,
    email,
    company_name,
    external_id,
    post_count,
    comment_count,
    group_memberships,
    mentions_received,
    -- Calculate engagement score
    (post_count * 3 + comment_count * 2 + group_memberships + mentions_received) as engagement_score,
    -- Engagement level
    CASE 
        WHEN (post_count + comment_count + group_memberships) > 5 THEN 'HIGHLY_ENGAGED'
        WHEN (post_count + comment_count + group_memberships) > 0 THEN 'MODERATELY_ENGAGED'  
        ELSE 'NOT_ENGAGED'
    END as engagement_level,
    created_at
FROM user_engagement
ORDER BY engagement_score DESC, post_count DESC;
-- Top 20 Active Posters
SELECT 
    p.first_name || ' ' || p.last_name as name,
    p.email,
    COUNT(DISTINCT po.id) as post_count,
    COUNT(DISTINCT c.id) as comment_count,
    COUNT(DISTINCT po.id) + COUNT(DISTINCT c.id) as total_contributions,
    (COUNT(DISTINCT po.id) * 3 + COUNT(DISTINCT c.id) * 2) as engagement_score,
    CASE 
        WHEN COUNT(DISTINCT po.id) >= 20 THEN 'Power User'
        WHEN COUNT(DISTINCT po.id) >= 10 THEN 'Active User'
        WHEN COUNT(DISTINCT po.id) >= 5 THEN 'Regular User'
        ELSE 'Casual User'
    END as user_tier
FROM persons p
LEFT JOIN posts po ON p.id = po.person_id AND po.deleted_at IS NULL
LEFT JOIN comments c ON p.id = c.person_id AND c.deleted_at IS NULL
WHERE p.deleted_at IS NULL
GROUP BY p.id, p.first_name, p.last_name, p.email
HAVING COUNT(DISTINCT po.id) > 0 OR COUNT(DISTINCT c.id) > 0
ORDER BY engagement_score DESC, post_count DESC
LIMIT 20;
-- Top Posts by Reach (using comments as proxy)
SELECT 
    p.id as post_id,
    LEFT(p.content, 100) as post_preview,
    author.first_name || ' ' || author.last_name as author,
    p.type as content_type,
    COUNT(DISTINCT c.id) as comment_count,
    COUNT(DISTINCT c.person_id) as unique_commenters,
    p.created_at,
    EXTRACT(days FROM NOW() - p.created_at) as days_old
FROM posts p
JOIN persons author ON p.person_id = author.id
LEFT JOIN comments c ON p.id = c.post_id AND c.deleted_at IS NULL
WHERE p.deleted_at IS NULL
    AND p.created_at >= NOW() - INTERVAL '30 days'
GROUP BY p.id, p.content, author.first_name, author.last_name, p.type, p.created_at
HAVING COUNT(DISTINCT c.id) > 0
ORDER BY comment_count DESC, unique_commenters DESC
LIMIT 20;
-- Engagement Summary Dashboard
SELECT 
    'Total Posts (30d)' as metric,
    COUNT(*)::text as value
FROM posts
WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'Active Posters (30d)',
    COUNT(DISTINCT person_id)::text
FROM posts
WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'Total Comments (30d)',
    COUNT(*)::text
FROM comments
WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'Avg Posts/Day',
    ROUND(COUNT(*)::numeric / 30, 1)::text
FROM posts
WHERE deleted_at IS NULL AND created_at >= NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'Avg Comments/Post',
    ROUND(
        (SELECT COUNT(*) FROM comments WHERE deleted_at IS NULL)::numeric /
        NULLIF((SELECT COUNT(*) FROM posts WHERE deleted_at IS NULL), 0), 2
    )::text;
-- ==============================================================================
-- 11. CONTENT ANALYSIS BY TYPE
-- ==============================================================================
-- Analyze different types of content being posted
SELECT 
    p.type,
    COUNT(*) as post_count,
    COUNT(DISTINCT p.person_id) as unique_authors,
    AVG(char_length(p.content)) as avg_content_length,
    COUNT(CASE WHEN p.link_url IS NOT NULL THEN 1 END) as posts_with_links,
    COUNT(CASE WHEN p.media_keys IS NOT NULL THEN 1 END) as posts_with_media,
    MIN(p.created_at) as first_post,
    MAX(p.created_at) as latest_post
FROM posts p
WHERE p.deleted_at IS NULL
GROUP BY p.type
ORDER BY post_count DESC;
-- Engagement Rate
WITH user_engagement AS (
    SELECT 
        p.id,
        p.first_name || ' ' || p.last_name as full_name,
        p.email,  -- ← MISSING THIS!
        (SELECT COUNT(*) FROM posts WHERE person_id = p.id AND deleted_at IS NULL) as post_count,
        (SELECT COUNT(*) FROM comments WHERE person_id = p.id AND deleted_at IS NULL) as comment_count,
        (SELECT COUNT(*) FROM group_members WHERE person_id = p.id AND deleted_at IS NULL) as group_memberships,
        (SELECT COUNT(*) FROM mentions WHERE mentioned_person_id = p.id AND deleted_at IS NULL) as mentions_received
    FROM persons p
    WHERE p.deleted_at IS NULL
)
SELECT 
    full_name,
    email,
    post_count,
    comment_count,
    group_memberships,
    mentions_received,
    (post_count * 3 + comment_count * 2 + group_memberships + mentions_received) as engagement_score,
    CASE 
        WHEN (post_count + comment_count + group_memberships) > 5 THEN 'HIGHLY_ENGAGED'
        WHEN (post_count + comment_count + group_memberships) > 0 THEN 'MODERATELY_ENGAGED'  
        ELSE 'NOT_ENGAGED'
    END as engagement_level
FROM user_engagement
ORDER BY engagement_score DESC;
-- Post Engagement Rate
SELECT 
    p.type as content_type,
    COUNT(DISTINCT p.id) as total_posts,
    COUNT(DISTINCT c.id) as total_comments,
    COUNT(DISTINCT c.person_id) as unique_commenters,
    ROUND(COUNT(DISTINCT c.id)::numeric / NULLIF(COUNT(DISTINCT p.id), 0), 2) as avg_comments_per_post,
    ROUND((COUNT(DISTINCT c.person_id)::numeric / NULLIF(COUNT(DISTINCT p.id), 0)) * 100, 2) as engagement_rate_pct
FROM posts p
LEFT JOIN comments c ON p.id = c.post_id AND c.deleted_at IS NULL
WHERE p.deleted_at IS NULL
    AND p.created_at >= NOW() - INTERVAL '30 days'
GROUP BY p.type
ORDER BY engagement_rate_pct DESC;
-- Post Frequency (Daily for last 30 days)
SELECT 
    DATE(created_at) as post_date,
    COUNT(*) as posts_created,
    COUNT(DISTINCT person_id) as active_users,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT person_id), 2) as avg_posts_per_user
FROM posts
WHERE deleted_at IS NULL
    AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY post_date DESC;
-- Daily Active Contributors (Proxy DAU)
SELECT 
    DATE(activity_date) as date,
    COUNT(DISTINCT person_id) as active_users,
    COUNT(CASE WHEN activity_type = 'post' THEN 1 END) as users_who_posted,
    COUNT(CASE WHEN activity_type = 'comment' THEN 1 END) as users_who_commented
FROM (
    SELECT person_id, created_at as activity_date, 'post' as activity_type 
    FROM posts WHERE deleted_at IS NULL
    UNION ALL
    SELECT person_id, created_at, 'comment' 
    FROM comments WHERE deleted_at IS NULL
) daily_activity
WHERE activity_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(activity_date)
ORDER BY date DESC;
-- Weekly Active Users
SELECT 
    DATE_TRUNC('week', activity_date) as week,
    COUNT(DISTINCT person_id) as active_users
FROM (
    SELECT person_id, created_at as activity_date FROM posts WHERE deleted_at IS NULL
    UNION ALL
    SELECT person_id, created_at FROM comments WHERE deleted_at IS NULL
) weekly_activity
GROUP BY week
ORDER BY week DESC
LIMIT 12;
-- Monthly Active Users (MAU) - Activity-Based
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
ORDER BY month DESC;
-- ==============================================================================
-- 12. CROSS-PLATFORM PROFILE MAPPING
-- ==============================================================================
-- Show relationship between Engagement Platform and ChemLink Service profiles
SELECT 
    ep.id as engagement_id,
    ep.external_id as chemlink_person_id,
    ep.first_name || ' ' || ep.last_name as name,
    ep.email,
    ep.company_name as engagement_company,
    ep.role_title as engagement_role,
    ep.employment_status,
    -- Engagement metrics
    (SELECT COUNT(*) FROM posts WHERE person_id = ep.id AND deleted_at IS NULL) as posts_created,
    (SELECT COUNT(*) FROM comments WHERE person_id = ep.id AND deleted_at IS NULL) as comments_made,
    -- Profile status
    CASE 
        WHEN ep.external_id IS NOT NULL THEN 'SYNCED_WITH_CHEMLINK'
        ELSE 'ENGAGEMENT_ONLY'
    END as profile_sync_status,
    ep.created_at
FROM persons ep
WHERE ep.deleted_at IS NULL
ORDER BY posts_created DESC, ep.created_at DESC
LIMIT 25;

-- ==============================================================================
-- 13. GROUP ACTIVITY ANALYSIS
-- ==============================================================================
-- Analyze group creation and membership patterns
SELECT 
    g.id as group_id,
    g.name as group_name,
    g.description,
    creator.first_name || ' ' || creator.last_name as created_by,
    creator.email as creator_email,
    COUNT(gm.id) as member_count,
    COUNT(p.id) as post_count,
    g.created_at,
    MAX(gm.created_at) as latest_member_joined,
    MAX(p.created_at) as latest_post
FROM groups g
LEFT JOIN persons creator ON g.created_by = creator.id
LEFT JOIN group_members gm ON g.id = gm.group_id AND gm.deleted_at IS NULL
LEFT JOIN posts p ON g.id = p.group_id AND p.deleted_at IS NULL
WHERE g.deleted_at IS NULL
GROUP BY g.id, g.name, g.description, creator.first_name, creator.last_name, creator.email, g.created_at
ORDER BY member_count DESC, post_count DESC;

-- ==============================================================================
-- 14. CONTENT TIMELINE ANALYSIS
-- ==============================================================================
-- Show content creation timeline and patterns
SELECT 
    DATE(created_at) as post_date,
    COUNT(*) as posts_created,
    COUNT(DISTINCT person_id) as active_users,
    COUNT(CASE WHEN type = 'text' THEN 1 END) as text_posts,
    COUNT(CASE WHEN type = 'link' THEN 1 END) as link_posts,
    COUNT(CASE WHEN type = 'image' THEN 1 END) as image_posts,
    COUNT(CASE WHEN type = 'file' THEN 1 END) as file_posts,
    STRING_AGG(DISTINCT (SELECT first_name || ' ' || last_name FROM persons WHERE id = posts.person_id), ', ') as active_users_list
FROM posts
WHERE deleted_at IS NULL
GROUP BY DATE(created_at)
ORDER BY post_date DESC
LIMIT 30;

-- ==============================================================================
-- 15. COMPLETE USER SOCIAL PROFILE VIEW
-- ==============================================================================
-- Comprehensive view of a user's social engagement profile
WITH user_profile AS (
    SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai'
)
SELECT 
    'PROFILE_INFO' as data_category,
    p.first_name || ' ' || p.last_name as name,
    p.email as email,
    p.company_name as details,
    p.role_title as additional_info
FROM persons p
WHERE p.id = (SELECT id FROM user_profile)

UNION ALL

SELECT 
    'POST' as data_category,
    po.type as name,
    LEFT(po.content, 50) as email,
    po.status as details,
    po.created_at::text as additional_info
FROM posts po
WHERE po.person_id = (SELECT id FROM user_profile)
  AND po.deleted_at IS NULL

UNION ALL

SELECT 
    'COMMENT' as data_category,
    'Comment on post' as name,
    LEFT(c.content, 50) as email,
    post_author.first_name || ' ' || post_author.last_name as details,
    c.created_at::text as additional_info
FROM comments c
JOIN posts p ON c.post_id = p.id
JOIN persons post_author ON p.person_id = post_author.id
WHERE c.person_id = (SELECT id FROM user_profile)
  AND c.deleted_at IS NULL

UNION ALL

SELECT 
    'GROUP_MEMBERSHIP' as data_category,
    g.name as name,
    gm.role as email,
    g.description as details,
    gm.created_at::text as additional_info
FROM group_members gm
JOIN groups g ON gm.group_id = g.id
WHERE gm.person_id = (SELECT id FROM user_profile)
  AND gm.deleted_at IS NULL
  AND g.deleted_at IS NULL

ORDER BY data_category, additional_info DESC;
--- ==============================================================================
-- 16. Profile update frequency
--- ==============================================================================
SELECT 
    id,
    first_name || ' ' || last_name as name,
    updated_at as last_profile_update,
    CURRENT_DATE - DATE(updated_at) as days_since_update,
    CASE 
        WHEN CURRENT_DATE - DATE(updated_at) > 180 THEN 'STALE (6+ months)'
        WHEN CURRENT_DATE - DATE(updated_at) > 90 THEN 'AGING (3-6 months)'
        ELSE 'FRESH (< 3 months)'
    END as profile_status
FROM persons
WHERE deleted_at IS NULL
ORDER BY days_since_update DESC;
-- Profile Update Frequency per User
SELECT 
    p.id,
    p.first_name || ' ' || p.last_name as full_name,
    p.email,
    p.updated_at as last_profile_update,
    EXTRACT(days FROM NOW() - p.updated_at) as days_since_update,
    CASE 
        WHEN p.updated_at >= NOW() - INTERVAL '30 days' THEN 'Fresh (< 1 month)'
        WHEN p.updated_at >= NOW() - INTERVAL '90 days' THEN 'Aging (1-3 months)'
        WHEN p.updated_at >= NOW() - INTERVAL '180 days' THEN 'Stale (3-6 months)'
        ELSE 'Very Stale (6+ months)'
    END as profile_freshness,
    (SELECT COUNT(*) FROM experiences WHERE person_id = p.id AND deleted_at IS NULL) as experience_count,
    (SELECT COUNT(*) FROM education WHERE person_id = p.id AND deleted_at IS NULL) as education_count
FROM persons p
WHERE p.deleted_at IS NULL
ORDER BY p.updated_at DESC;

-- ==============================================================================
-- USAGE INSTRUCTIONS:
-- ==============================================================================
-- 1. Start with Query #1 to find the user ID in engagement platform
-- 2. Use Query #2 for basic social profile overview  
-- 3. Run Query #3 for user's activity summary
-- 4. Use Queries #4-7 for detailed social engagement analysis
-- 5. Run Query #8-9 for platform-wide statistics
-- 6. Use Query #10-11 for engagement analytics
-- 7. Use Query #12 to understand cross-platform profile mapping
-- 8. Use Query #13-14 for group and content analysis
-- 9. Use Query #15 for complete user social profile
-- 10. Use Query #16 to determine how often users update their profile
-- 
-- Social Features: posts, comments, groups, group_members, mentions
-- User Management: persons (simplified profiles synced via external_id)
-- Content Types: text, link, image, file posts
-- ==============================================================================

SELECT 
    p.type,
    COUNT(*) as post_count,
    COUNT(DISTINCT p.person_id) as unique_authors,
    AVG(char_length(p.content)) as avg_content_length,
    COUNT(CASE WHEN p.link_url IS NOT NULL THEN 1 END) as posts_with_links,
    COUNT(CASE WHEN p.media_keys IS NOT NULL THEN 1 END) as posts_with_media
FROM posts p
WHERE p.deleted_at IS NULL
GROUP BY p.type
ORDER BY post_count DESC;

WITH monthly_users AS (
    SELECT DATE_TRUNC('month', created_at) as month,
           COUNT(*) as new_users
    FROM persons WHERE deleted_at IS NULL
    GROUP BY month
)
SELECT 
    month, 
    new_users,
    LAG(new_users) OVER (ORDER BY month) as prev_month,
    ROUND(((new_users - LAG(new_users) OVER (ORDER BY month)) * 100.0 / 
           NULLIF(LAG(new_users) OVER (ORDER BY month), 0)), 2) as growth_rate_pct
FROM monthly_users 
ORDER BY month DESC;