# ChemLink Development Environment Setup Guide

## Overview
This document outlines the complete setup process for the ChemLink development environment, including database connections, VPN access, and data architecture analysis.

## Prerequisites
- macOS environment
- Node.js v21.7.1 (via NVM)
- Docker Desktop
- AWS VPN Client

## 1. Node.js Setup with NVM

### Install NVM (Node Version Manager)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
```

### Configure Shell Profile
```bash
# Add to ~/.zshrc
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Reload shell configuration
source ~/.zshrc
```

### Install and Use Node.js
```bash
# Install Node.js v21.7.1 (ChemLink compatible version)
nvm install 21.7.1
nvm use 21.7.1
nvm alias default 21.7.1

# Verify installation
node --version  # Should show v21.7.1
npm --version   # Should show v10.5.0
```

## 2. Docker Database Setup

### Docker Compose Configuration
Updated `docker-compose.yml` to include both PostgreSQL and Neo4j:

```yaml
services:
  postgres:
    image: postgres:15
    container_name: postgres-container
    restart: always
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev

  neo4j:
    image: neo4j:5.14
    container_name: neo4j-container
    restart: always
    ports:
      - "7474:7474"  # Neo4j Browser
      - "7687:7687"  # Bolt protocol
    volumes:
      - ./docker/data:/data
      - ./docker/logs:/logs
      - ./docker/conf:/conf
      - ./docker/plugins:/plugins
    environment:
      NEO4J_AUTH: neo4j/cy_ejB5eYuQkPtrpeJTTqPn53IEZjL2muiSlB6V4QpM
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: "apoc.*"
      NEO4J_dbms_security_procedures_allowlist: "apoc.*"
      NEO4J_dbms_memory_heap_max__size: "2G"
      NEO4J_dbms_memory_pagecache_size: "1G"

volumes:
  postgres_data:
```

### Docker Commands
```bash
# Start both databases
docker-compose up -d

# Check status
docker-compose ps

# Stop and remove containers/volumes
docker-compose down -v

# View logs
docker-compose logs neo4j
docker-compose logs postgres
```

## 3. AWS VPN Setup

### VPN Configuration Process
1. **Download OpenVPN Config**: Downloaded `cvpn-endpoint-084a2365f3dbf4cad.ovpn`
2. **AWS VPN Client**: Import profile into AWS VPN Client
3. **Connect**: Establish VPN connection for private AWS resource access

### Verify VPN Connection
```bash
# Check IP and location
curl -s ipinfo.io

# Check network interfaces
ifconfig | grep -A 5 -E "(tun|tap|vpn|aws)"
```

## 4. PostgreSQL Client Setup

### Install PostgreSQL Client
```bash
# Install libpq (PostgreSQL client tools)
brew install libpq

# Add to PATH (add to ~/.zshrc for permanent)
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"

# Verify installation
psql --version
```

### Database Connections
**ChemLink Service Staging Database:**
```bash
DB_HOST: rds-global-live-us-stg.cm5lwb7yhfav.us-west-1.rds.amazonaws.com
DB_NAME: chemlink-service-stg
DB_USERNAME: chemlink-service-stg
DB_PASSWORD: chemlink-service-stgpasswd
```

**Engagement Platform Staging Database:**
```bash
DB_HOST: rds-global-live-us-stg.cm5lwb7yhfav.us-west-1.rds.amazonaws.com
DB_NAME: engagement-platform-stg
DB_USERNAME: engagement-platform-stg
DB_PASSWORD: engagement-platform-stgpasswd
```

### Connect via Command Line
```bash
# Using environment variable for password
export PGPASSWORD="engagement-platform-stgpasswd"

# Connect to database
psql -h rds-global-live-us-stg.cm5lwb7yhfav.us-west-1.rds.amazonaws.com \
     -d engagement-platform-stg \
     -U engagement-platform-stg

# List tables
psql -h rds-global-live-us-stg.cm5lwb7yhfav.us-west-1.rds.amazonaws.com \
     -d engagement-platform-stg \
     -U engagement-platform-stg \
     -c "\dt"
```

## 5. ChemLink Data Architecture

### Database Architecture
ChemLink uses a **dual-database architecture**:

1. **PostgreSQL** (Primary): Stores application data
   - User profiles, companies, experiences, education
   - Social engagement features (posts, comments, groups)
   - Transactional data integrity

2. **Neo4j** (Graph): Stores relationships for expert finding
   - Professional networks and connections
   - Graph-based expert discovery algorithms
   - Complex relationship queries

### Data Tables (PostgreSQL)
```sql
-- Core engagement platform tables
persons         -- User profiles (32 records in staging)
posts           -- Social media posts
comments        -- Post comments  
groups          -- User communities
group_members   -- Group membership relationships
mentions        -- User mentions in content
pgmigrations    -- Database migration history
```

### Data Models (Neo4j)
```cypher
// Node Types
Person, Company, Role, Project, Location, Language, 
Education, School, Degree, Experience

// Relationship Types  
WORKS_AT, WORKS_AS, WORKED_ON, LIVES_AT, SPEAKS,
EDUCATED_AT, STUDIED_AT, EARNED, EXPERIENCED_IN
```

### Sample Data Analysis
- **32 person records** in staging database
- **Mix of real and test data**
- **Chemonics employees**: Real profiles (e.g., tdudka@chemonics.com)
- **Test accounts**: Various development/testing profiles

## 6. Environment Configuration

### Update .env for Staging Database
```bash
# Database Configuration
DB_HOST=rds-global-live-us-stg.cm5lwb7yhfav.us-west-1.rds.amazonaws.com
DB_NAME=engagement-platform-stg
DB_USERNAME=engagement-platform-stg
DB_PASSWORD=engagement-platform-stgpasswd

# Neo4j Configuration (Local Docker)
NEO4J_CONNECTION_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=cy_ejB5eYuQkPtrpeJTTqPn53IEZjL2muiSlB6V4QpM
```

## 7. Access Points

### Neo4j Browser
- **URL**: http://localhost:7474
- **Username**: neo4j
- **Password**: cy_ejB5eYuQkPtrpeJTTqPn53IEZjL2muiSlB6V4QpM
- **Bolt URL**: neo4j://localhost:7687

### PostgreSQL Staging Database
- **Host**: rds-global-live-us-stg.cm5lwb7yhfav.us-west-1.rds.amazonaws.com
- **Port**: 5432
- **Database**: engagement-platform-stg
- **Username**: engagement-platform-stg
- **Password**: engagement-platform-stgpasswd

## 8. Troubleshooting

### Common Issues
1. **Neo4j Authentication**: Clean restart with `docker-compose down -v`
2. **VPN Access**: Ensure AWS VPN Client is connected before database access
3. **Node Dependencies**: Use `npm install --legacy-peer-deps` for conflict resolution
4. **Private Packages**: `@talino/*` packages require private registry access

### Useful Commands
```bash
# Check Docker containers
docker ps -a

# Test database connectivity  
psql -h rds-global-live-us-stg.cm5lwb7yhfav.us-west-1.rds.amazonaws.com \
     -d engagement-platform-stg \
     -U engagement-platform-stg \
     -c "SELECT version();"

# Neo4j health check
curl -u neo4j:cy_ejB5eYuQkPtrpeJTTqPn53IEZjL2muiSlB6V4QpM \
     http://localhost:7474/db/neo4j/
```

## Next Steps

1. **Install PGAdmin 4** for GUI database management
2. **Connect ChemLink service** to staging database
3. **Sync PostgreSQL data** to Neo4j for graph relationships
4. **Implement expert finding** algorithms using graph data
5. **Deploy frontend applications** (chemlink-finder, chemlink-builder)

---

**Document Created**: October 21, 2025  
**Environment**: macOS with Docker, AWS VPN access  
**Database**: PostgreSQL (staging) + Neo4j (local)  
**Node.js**: v21.7.1 via NVM