# ChemLink Service - Metrics and KPIs

This document outlines the measurement queries and key performance indicators (KPIs) available in the ChemLink Service database systems, suitable for analytics, business intelligence, and operational monitoring.

## Overview

The ChemLink Service consists of two main database systems:
1. **Profile Builder/Finder** (`finder-builder.sql`) - User profiles, experiences, and AI-powered matching
2. **Engagement Platform** (`engagement-platform.sql`) - Social features, posts, comments, and community engagement

---

## Profile Builder/Finder Metrics

### 1. User Profile Metrics and Counts
**Query #9**: Overview of users with counts of experiences, education, embeddings, and finder status.
- **Purpose**: Measures profile richness and completeness at a glance
- **Key Metrics**: Experience count, Education count, Embedding count, Finder status
- **Use Case**: Profile quality assessment, user segmentation

### 2. Database Health Metrics  
**Query #10**: Database statistics summarizing total and active records per main tables.
- **Purpose**: Monitor data growth and system health
- **Key Metrics**: Total records by table (`persons`, `experiences`, `education`, `embeddings`, `collections`)
- **Use Case**: System monitoring, cleanup planning, capacity management

### 3. AI/ML Search Analytics
**Query #11**: Query embeddings and votes analytics for search performance.
- **Purpose**: Analyze search query intents and user feedback
- **Key Metrics**: Vote counts, vote types, query performance
- **Use Case**: AI model tuning, search optimization, user satisfaction

### 4. Profile Completeness Scores
**Query #12**: Computes completeness score per user based on data availability.
- **Purpose**: Quantify profile quality and readiness for matching
- **Key Metrics**: 
  - Completeness score (0-100)
  - Profile categories: `FINDER_ENABLED`, `BUILDER_ONLY`, `BASIC_PROFILE`
  - Data presence flags (headline, LinkedIn, location, company, experiences, education, languages)
- **Use Case**: Profile quality KPI, user onboarding optimization

---

## Engagement Platform Metrics

### 1. Platform-Wide Activity Metrics
**Query #8**: High-level platform activity snapshot.
- **Purpose**: Overall platform health and engagement overview
- **Key Metrics**: 
  - Total users, Active users (who posted)
  - Total posts, comments
  - Group count, group memberships
  - User mentions
- **Use Case**: Executive dashboards, platform health monitoring

### 2. User Engagement Scoring
**Query #10**: Per-user engagement metrics and scoring.
- **Purpose**: Identify active and influential users
- **Key Metrics**: 
  - Posts count, Comments count
  - Group memberships, Mentions received
  - Engagement score and level (`HIGHLY_ENGAGED`, `MODERATELY_ENGAGED`, `NOT_ENGAGED`)
- **Use Case**: User segmentation, community management, influence tracking

### 3. Content Performance Breakdown
**Query #11**: Analysis by content type and performance.
- **Purpose**: Understand content preferences and effectiveness
- **Key Metrics**: 
  - Posts by content type
  - Unique authors per type
  - Average post length
  - Posts with links/media
- **Use Case**: Content strategy, feature usage analysis

### 4. Group Activity Metrics
**Query #13**: Community and group engagement analysis.
- **Purpose**: Track group health and growth
- **Key Metrics**: 
  - Member count per group
  - Post count per group
  - Latest member join date
  - Latest post activity
- **Use Case**: Community management, group moderation, growth tracking

### 5. Timeline and Growth Trends
**Query #14**: Daily activity trends and growth patterns.
- **Purpose**: Identify usage patterns and growth trends
- **Key Metrics**: 
  - Daily content creation
  - Active users per day
  - Content type activity over time
  - Active contributor lists
- **Use Case**: Trend analysis, growth monitoring, usage forecasting

### 6. Cross-Platform Profile Syncing
**Query #12**: Integration between Engagement Platform and Profile Builder.
- **Purpose**: Monitor data consistency across systems
- **Key Metrics**: 
  - Profile mapping between systems
  - Sync status (`SYNCED_WITH_CHEMLINK` vs `ENGAGEMENT_ONLY`)
  - Cross-platform activity metrics
- **Use Case**: Data integrity monitoring, integration health checks

---

## Metrics Summary Table

| Category | Key Metrics/Fields | Data Source | Business Value |
|----------|-------------------|-------------|----------------|
| **User Profile Metrics** | Experience count, Education count, Embedding count, Finder status | Profile Builder | Profile quality assessment |
| **Profile Completeness** | Completeness score (0-100), data presence flags | Profile Builder | Onboarding optimization |
| **Database Health** | Record counts by table, active vs total records | Both systems | System monitoring |
| **AI/ML Analytics** | Query intents, vote counts, search performance | Profile Builder | AI model optimization |
| **Platform Activity** | Users, posts, comments, groups, memberships | Engagement Platform | Overall platform health |
| **User Engagement** | Engagement score/level, activity metrics | Engagement Platform | User segmentation |
| **Content Analysis** | Content types, authors, length, media usage | Engagement Platform | Content strategy |
| **Group Metrics** | Member/post counts, activity dates | Engagement Platform | Community management |
| **Timeline Trends** | Daily activity, growth patterns | Engagement Platform | Growth analysis |
| **Cross-Platform Sync** | Profile mappings, sync status | Both systems | Data integration health |

---

## Implementation Recommendations

### Dashboard Categories
1. **Executive Dashboard**: Platform-wide metrics, user growth, engagement trends
2. **Product Analytics**: Feature usage, content performance, user behavior
3. **Operational Monitoring**: Database health, sync status, system performance
4. **Community Management**: Group activity, user engagement levels, content moderation

### Key Performance Indicators (KPIs)
- **User Acquisition**: New user registrations, profile completion rates
- **User Engagement**: Daily/Monthly active users, engagement score distribution
- **Content Health**: Posts per user, content type diversity, interaction rates
- **Platform Growth**: User growth rate, group formation, cross-platform adoption
- **Data Quality**: Profile completeness scores, sync success rates, data consistency

### Visualization Suggestions
- **Time Series Charts**: Daily activity trends, user growth over time
- **Distribution Charts**: Engagement level distribution, completeness score histogram  
- **Heat Maps**: Content activity by type and time, group engagement patterns
- **Funnel Charts**: Profile completion funnel, user onboarding progression
- **Network Graphs**: User interaction patterns, group membership overlap

---

## Usage Notes

- All queries provide both **quantitative metrics** (counts, scores) and **qualitative classifications** (engagement levels, profile status)
- Metrics enable monitoring of **user adoption, profile quality, platform engagement, content success, and system integration**
- Suitable for building dashboards, executive reports, operational monitoring, and product analytics
- Regular execution recommended for trend analysis and proactive system management

---

*Last Updated: 2025-10-21*  
*Database Systems: ChemLink Profile Builder/Finder, ChemLink Engagement Platform*