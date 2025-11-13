# Hiring Lifecycle System - Complete Architecture

## 🎯 What We Need to Track

The complete journey from job posting → candidate hired → employee offboarded:

1. **Job Postings** - Open positions
2. **Recruiter Outreach** - Recruiters contacting candidates
3. **Candidate Pipeline** - Application → Interview → Offer → Hire
4. **Messaging** - Communication between recruiters and candidates
5. **Onboarding** - New hire process
6. **Offboarding** - Exit process

---

## 📊 Database Schema Design

### 1. Job Listings & Management

```sql
-- Job postings
CREATE TABLE job_listings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    posted_by_person_id INTEGER REFERENCES persons(id), -- Recruiter
    title VARCHAR(200) NOT NULL,
    description TEXT,
    requirements TEXT,
    location_id INTEGER REFERENCES locations(id),
    employment_type VARCHAR(50), -- 'full-time', 'part-time', 'contract'
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    salary_currency VARCHAR(3), -- 'USD', 'EUR', etc.
    status VARCHAR(30) DEFAULT 'active', -- 'draft', 'active', 'filled', 'closed'
    posted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    filled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Skills required for job
CREATE TABLE job_skills (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES job_listings(id),
    skill_name VARCHAR(100),
    required BOOLEAN DEFAULT false, -- true = must have, false = nice to have
    years_required INTEGER
);
```

---

### 2. Recruiter Outreach & Candidate Pipeline

```sql
-- Recruiter reaching out to candidates
CREATE TABLE candidate_outreach (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES job_listings(id),
    candidate_person_id INTEGER REFERENCES persons(id),
    recruiter_person_id INTEGER REFERENCES persons(id),
    outreach_method VARCHAR(50), -- 'direct_message', 'email', 'linkedin'
    initial_message TEXT,
    outreach_status VARCHAR(50), -- 'sent', 'opened', 'responded', 'declined', 'interested'
    responded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Full application/candidate pipeline
CREATE TABLE candidate_applications (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES job_listings(id),
    candidate_person_id INTEGER REFERENCES persons(id),
    recruiter_person_id INTEGER REFERENCES persons(id),
    source VARCHAR(50), -- 'direct_apply', 'recruiter_outreach', 'referral'
    current_stage VARCHAR(50), -- 'applied', 'screening', 'interview', 'offer', 'hired', 'rejected'
    application_date TIMESTAMP DEFAULT NOW(),
    resume_url VARCHAR(500),
    cover_letter TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Track pipeline stage changes
CREATE TABLE application_stage_history (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES candidate_applications(id),
    from_stage VARCHAR(50),
    to_stage VARCHAR(50),
    changed_by_person_id INTEGER REFERENCES persons(id), -- Who moved them
    notes TEXT,
    changed_at TIMESTAMP DEFAULT NOW()
);
```

---

### 3. Interview Process

```sql
-- Interview scheduling
CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES candidate_applications(id),
    interview_type VARCHAR(50), -- 'phone_screen', 'technical', 'behavioral', 'final'
    scheduled_at TIMESTAMP,
    duration_minutes INTEGER,
    location VARCHAR(200), -- 'Zoom link: ...', 'Office: Room 301', etc.
    status VARCHAR(30), -- 'scheduled', 'completed', 'cancelled', 'no_show'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Interview participants (multiple interviewers)
CREATE TABLE interview_participants (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id),
    person_id INTEGER REFERENCES persons(id),
    role VARCHAR(50), -- 'interviewer', 'candidate', 'observer'
    attended BOOLEAN
);

-- Interview feedback
CREATE TABLE interview_feedback (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id),
    interviewer_person_id INTEGER REFERENCES persons(id),
    rating INTEGER, -- 1-5 scale
    technical_skills_score INTEGER,
    cultural_fit_score INTEGER,
    communication_score INTEGER,
    recommendation VARCHAR(50), -- 'strong_hire', 'hire', 'no_hire', 'strong_no_hire'
    notes TEXT,
    submitted_at TIMESTAMP DEFAULT NOW()
);
```

---

### 4. Messaging System

```sql
-- Conversations between recruiters and candidates
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES job_listings(id),
    candidate_person_id INTEGER REFERENCES persons(id),
    recruiter_person_id INTEGER REFERENCES persons(id),
    status VARCHAR(30), -- 'active', 'closed'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Individual messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    sender_person_id INTEGER REFERENCES persons(id),
    receiver_person_id INTEGER REFERENCES persons(id),
    message_text TEXT,
    attachment_urls TEXT[], -- Array of file URLs
    read_at TIMESTAMP,
    sent_at TIMESTAMP DEFAULT NOW()
);
```

---

### 5. Offer Management

```sql
-- Job offers
CREATE TABLE job_offers (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES candidate_applications(id),
    salary_amount DECIMAL(10,2),
    salary_currency VARCHAR(3),
    start_date DATE,
    benefits TEXT,
    offer_letter_url VARCHAR(500),
    status VARCHAR(50), -- 'draft', 'sent', 'accepted', 'declined', 'expired'
    sent_at TIMESTAMP,
    responded_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 6. Onboarding Process

```sql
-- New hire onboarding
CREATE TABLE employee_onboarding (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES persons(id),
    job_id INTEGER REFERENCES job_listings(id),
    start_date DATE,
    manager_person_id INTEGER REFERENCES persons(id),
    onboarding_status VARCHAR(50), -- 'pending', 'in_progress', 'completed'
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Onboarding tasks checklist
CREATE TABLE onboarding_tasks (
    id SERIAL PRIMARY KEY,
    onboarding_id INTEGER REFERENCES employee_onboarding(id),
    task_name VARCHAR(200),
    task_description TEXT,
    assigned_to_person_id INTEGER REFERENCES persons(id), -- HR, IT, Manager
    due_date DATE,
    status VARCHAR(30), -- 'pending', 'in_progress', 'completed'
    completed_at TIMESTAMP,
    notes TEXT
);
```

---

### 7. Offboarding Process

```sql
-- Employee exits
CREATE TABLE employee_offboarding (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES persons(id),
    termination_type VARCHAR(50), -- 'resignation', 'termination', 'retirement', 'layoff'
    last_working_day DATE,
    reason TEXT,
    initiated_by_person_id INTEGER REFERENCES persons(id),
    exit_interview_completed BOOLEAN DEFAULT false,
    offboarding_status VARCHAR(50), -- 'pending', 'in_progress', 'completed'
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Offboarding tasks checklist
CREATE TABLE offboarding_tasks (
    id SERIAL PRIMARY KEY,
    offboarding_id INTEGER REFERENCES employee_offboarding(id),
    task_name VARCHAR(200),
    task_description TEXT,
    assigned_to_person_id INTEGER REFERENCES persons(id),
    status VARCHAR(30), -- 'pending', 'completed'
    completed_at TIMESTAMP
);

-- Exit interview data
CREATE TABLE exit_interviews (
    id SERIAL PRIMARY KEY,
    offboarding_id INTEGER REFERENCES employee_offboarding(id),
    conducted_by_person_id INTEGER REFERENCES persons(id),
    satisfaction_rating INTEGER, -- 1-5
    would_recommend_company BOOLEAN,
    reason_for_leaving TEXT,
    feedback TEXT,
    conducted_at TIMESTAMP
);
```

---

## 🏗️ Application Logic (Backend/API)

### 1. Job Posting Module
**Endpoints needed:**
- `POST /api/jobs` - Create job posting
- `GET /api/jobs` - List all jobs (with filters)
- `GET /api/jobs/:id` - Get job details
- `PUT /api/jobs/:id` - Update job
- `DELETE /api/jobs/:id` - Close/delete job

**Business Logic:**
- Auto-expire jobs after X days
- Notify recruiter when job filled
- Send alerts when applications received

---

### 2. Recruiter Outreach Module
**Endpoints needed:**
- `POST /api/outreach` - Send initial message to candidate
- `GET /api/outreach/:jobId` - Get all outreach for a job
- `PUT /api/outreach/:id/status` - Update outreach status

**Business Logic:**
- Track open/read rates
- Prevent duplicate outreach to same candidate
- Auto-follow-up reminders

---

### 3. Application Pipeline Module
**Endpoints needed:**
- `POST /api/applications` - Submit application
- `GET /api/applications` - List applications (recruiter view)
- `PUT /api/applications/:id/stage` - Move candidate to next stage
- `GET /api/applications/:id/history` - View stage history

**Business Logic:**
- Auto-notify candidate when stage changes
- Calculate time-in-stage metrics
- Send reminders for stalled applications

---

### 4. Interview Module
**Endpoints needed:**
- `POST /api/interviews` - Schedule interview
- `PUT /api/interviews/:id` - Update interview
- `POST /api/interviews/:id/feedback` - Submit feedback
- `GET /api/interviews/:id/feedback` - View all feedback

**Business Logic:**
- Send calendar invites
- Send reminders 24h before interview
- Auto-collect feedback from all interviewers

---

### 5. Messaging Module
**Endpoints needed:**
- `POST /api/conversations` - Start conversation
- `POST /api/messages` - Send message
- `GET /api/conversations/:id/messages` - Get message history
- `PUT /api/messages/:id/read` - Mark as read

**Business Logic:**
- Real-time message delivery (WebSocket)
- Push notifications for new messages
- File attachment handling

---

### 6. Offer Module
**Endpoints needed:**
- `POST /api/offers` - Create offer
- `GET /api/offers/:id` - View offer
- `PUT /api/offers/:id/accept` - Accept offer
- `PUT /api/offers/:id/decline` - Decline offer

**Business Logic:**
- Generate offer letter PDF
- Track offer expiration
- Auto-trigger onboarding on acceptance

---

### 7. Onboarding Module
**Endpoints needed:**
- `POST /api/onboarding` - Start onboarding
- `GET /api/onboarding/:id/tasks` - Get task checklist
- `PUT /api/onboarding/tasks/:id/complete` - Complete task

**Business Logic:**
- Auto-create task checklist from template
- Send reminders for overdue tasks
- Notify manager of progress

---

### 8. Offboarding Module
**Endpoints needed:**
- `POST /api/offboarding` - Initiate offboarding
- `GET /api/offboarding/:id/tasks` - Get exit tasks
- `POST /api/exit-interviews` - Record exit interview

**Business Logic:**
- Auto-create exit tasks
- Disable system access on last day
- Archive employee data

---

## 📱 Frontend/App Requirements

### For Recruiters:
- Job posting dashboard
- Candidate search/browse
- Application pipeline (Kanban view)
- Interview scheduler
- Messaging inbox
- Offer management
- Analytics dashboard

### For Candidates:
- Job search/browse
- Application tracker
- Interview schedule
- Message inbox
- Offer review/accept
- Onboarding checklist

---

## 📊 Metrics This Enables

Once built, you can measure:
- ✅ Job Listings Growth
- ✅ Job Views
- ✅ Application Rate
- ✅ Time to Fill
- ✅ Interview-to-Offer ratio
- ✅ Offer Acceptance Rate
- ✅ Onboarding Completion Rate
- ✅ Turnover Rate
- ✅ Source of Hire effectiveness
- ✅ Recruiter performance

---

## ⏱️ Implementation Timeline Estimate

| Phase | Components | Effort | Timeline |
|-------|-----------|--------|----------|
| **Phase 1** | Job listings + Applications | High | 4-6 weeks |
| **Phase 2** | Interview scheduling + Feedback | Medium | 3-4 weeks |
| **Phase 3** | Messaging system | High | 4-6 weeks |
| **Phase 4** | Offers + Onboarding | Medium | 3-4 weeks |
| **Phase 5** | Offboarding | Low | 2-3 weeks |
| **Total** | - | - | **16-23 weeks (4-6 months)** |

---

## 🎯 MVP (Minimum Viable Product) - Phase 1 Only

**If you need to ship quickly, start with:**
1. Job listings (post, view, search)
2. Applications (apply, view status)
3. Basic messaging
4. Application stage tracking

**Skip for MVP:**
- Advanced interview scheduling
- Onboarding checklists
- Offboarding workflows
- Exit interviews

**MVP Timeline: 6-8 weeks**

---

## 💡 What to Say/Present

### Executive Summary:
"We need to build a complete hiring lifecycle system to track the full journey from job posting to employee exit. This includes job listings, recruiter outreach, application pipeline, interview management, messaging, offers, onboarding, and offboarding. The database requires 15+ new tables, the backend needs 40+ API endpoints, and the frontend needs both recruiter and candidate interfaces. This is a 4-6 month project for full implementation, or 6-8 weeks for an MVP covering just job postings, applications, and basic messaging."

---

*This is a major product initiative, not just analytics. It's essentially building an Applicant Tracking System (ATS) + Onboarding/Offboarding platform from scratch.*