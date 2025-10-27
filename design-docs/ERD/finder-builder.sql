-- ==============================================================================
-- ChemLink Profile Builder vs Finder Analysis Queries
-- ==============================================================================
-- Purpose: Analyze the Profile Builder and Finder functionality in ChemLink
-- Database: chemlink-service-stg (PostgreSQL)
-- Created: October 21, 2025
-- Author: Jay Constantine Sanchez (Data Architect)
-- ==============================================================================

-- ==============================================================================
-- 1. SEARCH FOR SPECIFIC EMAIL ADDRESSES
-- ==============================================================================
-- Search for your email addresses to find person records
SELECT 
    id,
	person_id
    first_name, 
    last_name, 
    email, 
    has_finder,
    created_at
FROM persons 
WHERE email IN ('jsanchez@nmblr.ai', 'jaypersanchez@gmail.com', 'virlanchainworks@gmail.com')
ORDER BY created_at DESC;

-- ==============================================================================
-- 2. COMPLETE PROFILE DATA (Profile Builder Core)
-- ==============================================================================
-- Get complete profile for Jayper Sanchez (adjust person_id as needed)
SELECT 
    p.id,
    p.first_name || ' ' || p.last_name as full_name,
    p.email,
    p.headline_description,
    p.linked_in_url,
    p.career_goals,
    p.business_experience_summary,
    l.country as current_location,
    c.name as current_company,
    r.title as current_role,
    p.has_finder,
    p.created_at,
    p.updated_at
FROM persons p
LEFT JOIN locations l ON p.location_id = l.id
LEFT JOIN companies c ON p.company_id = c.id
LEFT JOIN roles r ON p.role_id = r.id
WHERE p.email = 'jsanchez@nmblr.ai';

-- ==============================================================================
-- 3. PROFESSIONAL EXPERIENCE DATA (Profile Builder)
-- ==============================================================================
-- Get work experience history - shows Profile Builder functionality
SELECT 
    e.id,
    e.description,
    c.name as company_name,
    r.title as role_title,
    p.name as project_name,
    loc.country as location,
    e.start_date,
    e.end_date,
    e.type,
    e.created_at
FROM experiences e 
LEFT JOIN companies c ON e.company_id = c.id
LEFT JOIN roles r ON e.role_id = r.id  
LEFT JOIN projects p ON e.project_id = p.id
LEFT JOIN locations loc ON e.location_id = loc.id
WHERE e.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND e.deleted_at IS NULL
ORDER BY e.created_at DESC;

-- ==============================================================================
-- 4. EDUCATION BACKGROUND (Profile Builder)
-- ==============================================================================
-- Get education data - another Profile Builder component
SELECT 
    ed.id,
    s.name as school_name,
    d.name as degree_name,
    ed.field_of_study,
    ed.start_date,
    ed.end_date,
    ed.description,
    ed.created_at
FROM education ed
LEFT JOIN schools s ON ed.school_id = s.id
LEFT JOIN degrees d ON ed.degree_id = d.id  
WHERE ed.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND ed.deleted_at IS NULL
ORDER BY ed.start_date DESC;

-- ==============================================================================
-- 5. LANGUAGE SKILLS (Profile Builder)
-- ==============================================================================
-- Get language proficiency data
SELECT 
    pl.id,
    l.name as language_name,
    l.code as language_code,
    pl.proficiency,
    pl.created_at
FROM person_languages pl
LEFT JOIN languages l ON pl.language_id = l.id
WHERE pl.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND pl.deleted_at IS NULL
ORDER BY pl.created_at DESC;

-- ==============================================================================
-- 6. AI/ML FINDER DATA - EMBEDDINGS (Finder Functionality)
-- ==============================================================================
-- Get AI embeddings for semantic search - this is the Finder feature
SELECT 
    e.id,
    e.type,
    LEFT(e.embedded_text, 200) as text_sample,
    e.score_multiplier,
    e.start_date,
    e.end_date,
    e.created_at
FROM embeddings e
WHERE e.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND e.deleted_at IS NULL
ORDER BY e.created_at DESC;

-- ==============================================================================
-- 7. COLLECTIONS & EXPERT LISTS (Finder Functionality)
-- ==============================================================================
-- Get collections created by or containing this person
SELECT 
    'CREATED' as relationship_type,
    c.id as collection_id,
    c.name as collection_name,
    c.description,
    c.privacy,
    c.created_at
FROM collections c
WHERE c.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND c.deleted_at IS NULL

UNION ALL

SELECT 
    'MEMBER_OF' as relationship_type,
    c.id as collection_id,
    c.name as collection_name,
    c.description,
    c.privacy,
    cp.created_at
FROM collection_profiles cp
JOIN collections c ON cp.collection_id = c.id
WHERE cp.person_id = (SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai')
  AND cp.deleted_at IS NULL
  AND c.deleted_at IS NULL
ORDER BY created_at DESC;

-- ==============================================================================
-- 8. COMPLETE PROFILE SUMMARY (All-in-One Analysis)
-- ==============================================================================
-- Comprehensive profile view combining all Profile Builder data
WITH person_data AS (
    SELECT id FROM persons WHERE email = 'jsanchez@nmblr.ai'
)
SELECT 
    'PROFILE' as data_category,
    p.first_name || ' ' || p.last_name as name,
    p.email,
    p.headline_description as details,
    l.country as additional_info
FROM persons p
LEFT JOIN locations l ON p.location_id = l.id
WHERE p.id = (SELECT id FROM person_data)

UNION ALL

SELECT 
    'EXPERIENCE' as data_category,
    c.name as name,
    r.title as email,
    e.description as details,
    e.start_date || ' to ' || COALESCE(e.end_date, 'Present') as additional_info
FROM experiences e 
LEFT JOIN companies c ON e.company_id = c.id
LEFT JOIN roles r ON e.role_id = r.id
WHERE e.person_id = (SELECT id FROM person_data)
  AND e.deleted_at IS NULL

UNION ALL

SELECT 
    'EDUCATION' as data_category,
    s.name as name,
    d.name as email,
    ed.field_of_study as details,
    ed.start_date || ' to ' || COALESCE(ed.end_date, 'Present') as additional_info
FROM education ed
LEFT JOIN schools s ON ed.school_id = s.id
LEFT JOIN degrees d ON ed.degree_id = d.id
WHERE ed.person_id = (SELECT id FROM person_data)
  AND ed.deleted_at IS NULL

UNION ALL

SELECT 
    'AI_EMBEDDING' as data_category,
    e.type as name,
    '' as email,
    LEFT(e.embedded_text, 100) as details,
    e.score_multiplier as additional_info
FROM embeddings e
WHERE e.person_id = (SELECT id FROM person_data)
  AND e.deleted_at IS NULL

ORDER BY data_category, name;

-- ==============================================================================
-- 9. SEARCH ALL USERS FOR ANALYSIS
-- ==============================================================================
-- Get overview of all users for comparison
SELECT 
    id,
    first_name || ' ' || last_name as full_name,
    email,
    has_finder,
    (SELECT COUNT(*) FROM experiences WHERE person_id = p.id AND deleted_at IS NULL) as experience_count,
    (SELECT COUNT(*) FROM education WHERE person_id = p.id AND deleted_at IS NULL) as education_count,
    (SELECT COUNT(*) FROM embeddings WHERE person_id = p.id AND deleted_at IS NULL) as embedding_count,
    created_at
FROM persons p
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 20;

-- Get overview of all users signeup for the day
SELECT 
    id,
    first_name || ' ' || last_name as full_name,
    email,
    has_finder,
    (SELECT COUNT(*) FROM experiences WHERE person_id = p.id AND deleted_at IS NULL) as experience_count,
    (SELECT COUNT(*) FROM education WHERE person_id = p.id AND deleted_at IS NULL) as education_count,
    (SELECT COUNT(*) FROM embeddings WHERE person_id = p.id AND deleted_at IS NULL) as embedding_count,
    created_at
FROM persons p
WHERE deleted_at IS NULL
  AND DATE(created_at) = CURRENT_DATE
ORDER BY created_at DESC;

-- Get overview of all users signedup for the week
SELECT 
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) as new_users
FROM persons 
WHERE deleted_at IS NULL
GROUP BY week ORDER BY week DESC;

-- Monthly Growth Rate (READY TO RUN)
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
           LAG(new_users) OVER (ORDER BY month)), 2) as growth_rate_pct
FROM monthly_users 
ORDER BY month DESC;
-- Proxy DAU: Users who posted or commented today
SELECT 
    COUNT(DISTINCT person_id) as active_users_today
FROM (
    SELECT person_id FROM posts 
    WHERE deleted_at IS NULL 
    AND DATE(created_at) = CURRENT_DATE
    
    UNION
    
    SELECT person_id FROM comments 
    WHERE deleted_at IS NULL 
    AND DATE(created_at) = CURRENT_DATE
) today_activity;
-- Simple Monthly Active Users by Country
SELECT 
    DATE_TRUNC('month', activity_date) as month,
    COALESCE(l.country, 'Unknown') as country,
    COUNT(DISTINCT person_id) as active_users
FROM (
    SELECT person_id, created_at as activity_date 
    FROM posts WHERE deleted_at IS NULL
    UNION ALL
    SELECT person_id, created_at 
    FROM comments WHERE deleted_at IS NULL
) monthly_activity
LEFT JOIN persons p ON monthly_activity.person_id = p.id
LEFT JOIN locations l ON p.location_id = l.id
GROUP BY DATE_TRUNC('month', activity_date), l.country
ORDER BY month DESC, active_users DESC;

-- Weekly Growth Rate (will have more data)
WITH weekly_users AS (
    SELECT DATE_TRUNC('week', created_at) as week,
           COUNT(*) as new_users
    FROM persons WHERE deleted_at IS NULL
    GROUP BY week
)
SELECT 
    week, 
    new_users,
    LAG(new_users) OVER (ORDER BY week) as prev_week,
    ROUND(((new_users - LAG(new_users) OVER (ORDER BY week)) * 100.0 / 
           LAG(new_users) OVER (ORDER BY week)), 2) as growth_rate_pct
FROM weekly_users 
ORDER BY week DESC;

-- ==============================================================================
-- 10. DATABASE STATISTICS SUMMARY
-- ==============================================================================
-- Get database statistics for Profile Builder vs Finder analysis
SELECT 
    'Persons' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as active_records
FROM persons

UNION ALL

SELECT 
    'Experiences' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as active_records
FROM experiences

UNION ALL

SELECT 
    'Education' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as active_records
FROM education

UNION ALL

SELECT 
    'Embeddings' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as active_records
FROM embeddings

UNION ALL

SELECT 
    'Collections' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as active_records
FROM collections

ORDER BY table_name;

-- ==============================================================================
-- 11. QUERY EMBEDDINGS & VOTES (Advanced Finder Analytics)
-- ==============================================================================
-- Analyze search queries and user feedback (ML training data)
-- Top Skills Searched with Vote Data
SELECT 
    qe.intent,
    LEFT(qe.embedded_text, 100) as search_sample,
    COUNT(DISTINCT qe.id) as search_count,
    COUNT(qv.id) as vote_count,
    STRING_AGG(DISTINCT qv.vote, ', ') as vote_types
FROM query_embeddings qe
LEFT JOIN query_votes qv ON qe.id = qv.query_embedding_id
WHERE qe.deleted_at IS NULL
    AND qe.intent IS NOT NULL
GROUP BY qe.intent, qe.embedded_text
ORDER BY search_count DESC
LIMIT 20;

-- ==============================================================================
-- 12. PROFILE COMPLETENESS ANALYSIS
-- ==============================================================================
-- Analyze how complete profiles are (useful for Profile Builder analytics)
WITH profile_completeness AS (
    SELECT 
        p.id,
        p.first_name || ' ' || p.last_name as full_name,
        p.email,
        -- Profile completeness indicators
        CASE WHEN p.headline_description IS NOT NULL AND LENGTH(p.headline_description) > 10 THEN 1 ELSE 0 END as has_headline,
        CASE WHEN p.linked_in_url IS NOT NULL THEN 1 ELSE 0 END as has_linkedin,
        CASE WHEN p.location_id IS NOT NULL THEN 1 ELSE 0 END as has_location,
        CASE WHEN p.company_id IS NOT NULL THEN 1 ELSE 0 END as has_company,
        -- Related data counts
        (SELECT COUNT(*) FROM experiences WHERE person_id = p.id AND deleted_at IS NULL) as experience_count,
        (SELECT COUNT(*) FROM education WHERE person_id = p.id AND deleted_at IS NULL) as education_count,
        (SELECT COUNT(*) FROM person_languages WHERE person_id = p.id AND deleted_at IS NULL) as language_count,
        (SELECT COUNT(*) FROM embeddings WHERE person_id = p.id AND deleted_at IS NULL) as embedding_count,
        p.has_finder
    FROM persons p
    WHERE p.deleted_at IS NULL
)
SELECT 
    full_name,
    email,
    -- Calculate completeness score
    (has_headline + has_linkedin + has_location + has_company + 
     CASE WHEN experience_count > 0 THEN 1 ELSE 0 END +
     CASE WHEN education_count > 0 THEN 1 ELSE 0 END +
     CASE WHEN language_count > 0 THEN 1 ELSE 0 END) as profile_completeness_score,
    experience_count,
    education_count,
    language_count,
    embedding_count,
    has_finder,
    -- Profile Builder vs Finder status
    CASE 
        WHEN embedding_count > 0 THEN 'FINDER_ENABLED'
        WHEN experience_count > 0 OR education_count > 0 THEN 'BUILDER_ONLY'
        ELSE 'BASIC_PROFILE'
    END as profile_status
FROM profile_completeness
ORDER BY profile_completeness_score DESC, embedding_count DESC;

-- Profile Visibility from Social Activity
SELECT 
    p.id,
    p.first_name || ' ' || p.last_name as full_name,
    p.email,
    -- Activity that drives visibility
    (SELECT COUNT(*) FROM posts WHERE person_id = p.id AND deleted_at IS NULL) as posts_created,
    (SELECT COUNT(*) FROM comments WHERE person_id = p.id AND deleted_at IS NULL) as comments_made,
    (SELECT COUNT(*) FROM mentions WHERE mentioned_person_id = p.id AND deleted_at IS NULL) as times_mentioned,
    -- Visibility score (proxy for profile views)
    (
        (SELECT COUNT(*) FROM posts WHERE person_id = p.id AND deleted_at IS NULL) * 5 +
        (SELECT COUNT(*) FROM comments WHERE person_id = p.id AND deleted_at IS NULL) * 2 +
        (SELECT COUNT(*) FROM mentions WHERE mentioned_person_id = p.id AND deleted_at IS NULL) * 3
    ) as visibility_score
FROM persons p
WHERE p.deleted_at IS NULL
ORDER BY visibility_score DESC
LIMIT 50;



-- ==============================================================================
-- USAGE INSTRUCTIONS:
-- ==============================================================================
-- 1. Start with Query #1 to find the person ID
-- 2. Use Query #2 for basic profile overview  
-- 3. Run Queries #3-7 for detailed Profile Builder vs Finder analysis
-- 4. Use Query #8 for a comprehensive summary
-- 5. Run Query #9 to see all users in the system
-- 6. Use Query #10 for database statistics
-- 7. Use Query #11-12 for advanced analytics
-- 
-- Profile Builder Tables: persons, experiences, education, person_languages
-- Finder Tables: embeddings, query_embeddings, query_votes, collections
-- Reference Tables: companies, roles, projects, locations, schools, degrees, languages
-- ==============================================================================