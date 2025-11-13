# Chemlink Service - Architecture Documentation

## Overview

Chemlink Service is a Node.js/TypeScript-based backend service that provides AI-powered job-candidate matching capabilities. The system combines graph database technology (Neo4j) with vector embeddings (PostgreSQL) and large language models to deliver intelligent candidate search and profile matching.

## Architecture Diagrams

### Solution Architecture
- **File**: `solution-architecture.puml`
- **Focus**: High-level system components, service interactions, and external integrations
- **Generate**: `plantuml solution-architecture.puml`

### Data Architecture
- **File**: `data-architecture.puml`
- **Focus**: Data models, storage patterns, and data flow
- **Generate**: `plantuml data-architecture.puml`

## Key Components

### Core Services
- **Finder Service**: Main matching engine using Neo4j Cypher queries and LLM processing
- **Person Service**: Profile management and data retrieval
- **Authentication Service**: Integration with Ory Identity
- **Embedding Service**: Vector storage and similarity search

### Data Stores
- **Neo4j**: Primary graph database for relationships and complex queries
- **PostgreSQL**: Vector embeddings, user data, and analytics
- **AWS S3**: File storage for profile pictures and documents

### AI/ML Integration
- **AWS Bedrock (Claude)**: Query processing and profile summarization
- **OpenAI**: Text embeddings and language processing
- **Vector Search**: Semantic similarity matching

## Critical Questions for Solution Architects

### Scalability & Performance
1. **Search Performance**: How does the dual-database approach (Neo4j + PostgreSQL) impact query performance at scale?
2. **LLM Costs**: What's the cost model for AWS Bedrock and OpenAI usage? Is there rate limiting in place?
3. **Concurrent Users**: How many concurrent search requests can the system handle?
4. **Cache Strategy**: Is there caching for frequently accessed profiles or search results?

### Reliability & Availability
5. **Database Failover**: What's the disaster recovery plan for Neo4j and PostgreSQL?
6. **LLM Service Degradation**: How does the system behave when AI services are unavailable?
7. **Data Consistency**: How is consistency maintained between Neo4j and PostgreSQL?
8. **Monitoring**: What observability tools are in place for system health?

### Security & Compliance
9. **Data Privacy**: How is PII handled, especially in embeddings and logs?
10. **API Security**: What authentication/authorization patterns are implemented?
11. **Data Retention**: What's the data lifecycle management strategy?
12. **Compliance**: Are there GDPR, CCPA, or other regulatory requirements?

### Integration & Dependencies
13. **External Service Dependencies**: What happens when AWS Bedrock, OpenAI, or S3 are unavailable?
14. **API Versioning**: How are breaking changes handled for API consumers?
15. **Third-party Integrations**: Are there plans for LinkedIn, job boards, or ATS integrations?

## Critical Questions for Data Architects

### Data Model & Design
1. **Graph Schema Evolution**: How are schema changes managed in Neo4j without downtime?
2. **Data Normalization**: Are person profiles normalized across different data sources?
3. **Relationship Modeling**: Are all relevant career relationships captured in the graph model?
4. **Temporal Data**: How are career progressions and time-based relationships handled?

### Data Quality & Governance
5. **Data Validation**: What validation rules ensure profile data quality?
6. **Duplicate Detection**: How are duplicate persons/companies identified and merged?
7. **Data Lineage**: Can you trace the source of profile information?
8. **Master Data Management**: Is there a single source of truth for companies, skills, locations?

### Vector Embeddings & Search
9. **Embedding Strategy**: Which fields are embedded and how often are they updated?
10. **Vector Dimensionality**: What's the embedding dimension and how does it impact storage?
11. **Similarity Thresholds**: How are matching thresholds determined and tuned?
12. **Embedding Drift**: How is model drift detected and handled?

### Data Integration & ETL
13. **Data Ingestion**: What's the process for ingesting resume/profile data?
14. **Real-time vs Batch**: Are updates processed in real-time or batched?
15. **Data Transformation**: How are free-text fields normalized (skills, companies, locations)?
16. **Error Handling**: What happens when profile parsing fails?

## Potential Concerns & Risks

### Technical Debt
- **Dual Database Complexity**: Managing two databases increases operational overhead
- **LLM Dependencies**: Heavy reliance on external AI services creates vendor lock-in risk
- **Data Synchronization**: Keeping Neo4j and PostgreSQL in sync is challenging

### Performance Bottlenecks
- **Complex Queries**: Neo4j Cypher queries with multiple intents may be slow
- **LLM Latency**: Real-time profile summarization adds significant latency
- **Vector Search**: High-dimensional vector operations can be CPU intensive

### Data Quality Issues
- **Inconsistent Formats**: Resume parsing may produce inconsistent skill/company names
- **Stale Data**: Profile information may become outdated without refresh mechanisms
- **Bias in Matching**: AI models may introduce unconscious bias in candidate ranking

## Recommendations

### Immediate Actions
1. **Performance Monitoring**: Implement comprehensive APM for query performance tracking
2. **Cost Monitoring**: Set up billing alerts for AI service usage
3. **Data Backup**: Establish automated backup strategies for both databases
4. **API Documentation**: Create comprehensive API documentation with examples

### Short-term Improvements (3-6 months)
1. **Caching Layer**: Implement Redis for frequently accessed profiles and search results
2. **Rate Limiting**: Add proper rate limiting for API endpoints
3. **Data Pipeline**: Build robust ETL pipeline for profile data ingestion
4. **Error Handling**: Improve error handling and retry mechanisms for external services

### Long-term Considerations (6-12 months)
1. **Microservices**: Consider splitting into domain-specific microservices
2. **Event Sourcing**: Implement event sourcing for profile changes and search analytics
3. **Machine Learning**: Build custom ML models to reduce dependency on external services
4. **Multi-region**: Plan for multi-region deployment for global scalability

## Technology Stack Summary

### Backend
- **Runtime**: Node.js with TypeScript
- **Framework**: Express.js
- **Authentication**: Ory Identity
- **File Processing**: Multer, PDF-parse, PapaParse

### Databases
- **Graph Database**: Neo4j 5.14 with APOC plugins
- **Relational Database**: PostgreSQL with vector extensions
- **Object Storage**: AWS S3

### AI/ML
- **LLM**: AWS Bedrock (Claude), OpenAI
- **Embeddings**: Vector storage in PostgreSQL
- **Text Processing**: Langchain

### Infrastructure
- **Containerization**: Docker
- **Deployment**: Kubernetes (Helm charts available)
- **Monitoring**: Winston logging
- **Migration**: node-pg-migrate

## Dos and Don'ts

### DO
✅ **Monitor LLM costs** - Track usage and implement budgets  
✅ **Implement circuit breakers** - For external service failures  
✅ **Cache search results** - For better performance  
✅ **Validate input data** - Especially for profile uploads  
✅ **Version your APIs** - For backward compatibility  
✅ **Log comprehensive metrics** - For debugging and optimization  
✅ **Test with real data** - Use anonymized production data for testing  

### DON'T
❌ **Ignore data consistency** - Between Neo4j and PostgreSQL  
❌ **Store sensitive data in logs** - Especially in embeddings  
❌ **Skip input validation** - For security and data quality  
❌ **Rely solely on external AI** - Have fallback mechanisms  
❌ **Ignore query performance** - Monitor slow Neo4j queries  
❌ **Mix concerns in services** - Keep domain services focused  
❌ **Skip database migrations** - Always use migration scripts  

## Getting Started

1. **Review the diagrams** by running:
   ```bash
   plantuml design-docs/solution-architecture.puml
   plantuml design-docs/data-architecture.puml
   ```

2. **Explore the codebase** focusing on:
   - `src/component/finder/service.ts` - Main matching logic
   - `src/component/graph-db/` - Neo4j integration
   - `src/component/embedding/` - Vector operations
   - `docker-compose.yml` - Local development setup

3. **Set up local environment**:
   ```bash
   npm install
   docker-compose up -d  # Starts Neo4j
   npm run dev
   ```

4. **Review configuration** in `.env.example` for required environment variables

This documentation should provide both solution and data architects with a comprehensive understanding of the current system architecture and critical considerations for future development.