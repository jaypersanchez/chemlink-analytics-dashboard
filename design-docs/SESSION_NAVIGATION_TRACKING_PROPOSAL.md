# Session & Navigation Tracking - Design Proposal

**Date:** October 30, 2025  
**Author:** Jay Persanchez  
**Status:** Proposal for Review  
**Purpose:** Enable session duration, page views, navigation patterns, and user journey analytics

---

## Executive Summary

Currently, we cannot track:
- ❌ Session duration (time on platform)
- ❌ Page views (which pages users visit)
- ❌ Click-through rates (what users interact with)
- ❌ Time-on-page (content engagement depth)
- ❌ Navigation patterns (user journeys)

This proposal outlines **two implementation approaches** with complete technical specifications, effort estimates, and dashboard integration patterns.

---

## Solution Comparison

| Aspect | **Option A: Google Analytics** | **Option B: Custom Backend Tracking** |
|--------|-------------------------------|---------------------------------------|
| **Implementation Time** | 1-2 days | 2-3 weeks |
| **Data Accuracy** | 90-95% | 95-99% |
| **Data Ownership** | Third-party (Google) | Full ownership |
| **Privacy Compliance** | GDPR concerns | Full control |
| **Real-time Data** | 24-48 hour delay | Instant |
| **Custom Metrics** | Limited | Unlimited |
| **Maintenance** | None (managed) | Ongoing |
| **Cost** | Free (GA4) | Server/storage costs |

---

## Option A: Google Analytics 4 (GA4) Integration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ChemLink Web App                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │              React/Vue Frontend                     │    │
│  │  • Google Analytics SDK (gtag.js)                  │    │
│  │  • Automatic page view tracking                    │    │
│  │  • Custom event tracking                           │    │
│  └─────────────────┬──────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────┘
                     │
                     ▼ (sends events)
         ┌───────────────────────────┐
         │   Google Analytics 4      │
         │   • Session tracking      │
         │   • Page view tracking    │
         │   • Event aggregation     │
         └───────────┬───────────────┘
                     │
                     ▼ (API query)
         ┌───────────────────────────┐
         │  GA4 Reporting API        │
         │  • Data export            │
         │  • Custom dimensions      │
         └───────────┬───────────────┘
                     │
                     ▼ (fetch data)
┌─────────────────────────────────────────────────────────────┐
│          ChemLink Analytics Dashboard (Flask)               │
│  • Fetch GA4 data via API                                   │
│  • Merge with production DB data                            │
│  • Render unified charts                                    │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### **1. Frontend Integration (UI Team)**

**Install Google Analytics:**
```bash
npm install react-ga4
# or
yarn add react-ga4
```

**Initialize in app root (e.g., `App.jsx`):**
```javascript
import ReactGA from 'react-ga4';

// Initialize GA4
ReactGA.initialize('G-XXXXXXXXXX'); // Your GA4 Measurement ID

function App() {
  // Track page views on route changes
  useEffect(() => {
    ReactGA.send({ hitType: "pageview", page: window.location.pathname });
  }, [location.pathname]);

  return <Router>{/* app routes */}</Router>;
}
```

**Track Custom Events:**
```javascript
// Track Finder searches
const handleFinderSearch = (query) => {
  ReactGA.event({
    category: 'Finder',
    action: 'Search',
    label: query,
    value: 1
  });
  
  // Existing search logic...
};

// Track collection creation
const handleCreateCollection = (name, privacy) => {
  ReactGA.event({
    category: 'Collections',
    action: 'Create',
    label: privacy, // 'public' or 'private'
    value: 1
  });
};

// Track profile views
const handleProfileView = (profileId) => {
  ReactGA.event({
    category: 'Profile',
    action: 'View',
    label: profileId,
    value: 1
  });
};
```

**Effort Estimate:**
- Initial setup: **2 hours**
- Event tracking integration: **4-6 hours**
- Testing: **2 hours**
- **Total UI effort: 1 day**

---

#### **2. Backend Integration (Flask Dashboard)**

**Install Google Analytics Data API:**
```bash
pip install google-analytics-data
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

**Create GA4 Service (`ga4_service.py`):**
```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import os

class GA4Service:
    def __init__(self):
        # Set up authentication
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account.json'
        self.client = BetaAnalyticsDataClient()
        self.property_id = "properties/YOUR_PROPERTY_ID"
    
    def get_session_metrics(self, start_date='30daysAgo', end_date='today'):
        """Get session duration and user metrics"""
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionDefaultChannelGroup")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="averageSessionDuration"),
                Metric(name="engagementRate"),
                Metric(name="newUsers")
            ]
        )
        
        response = self.client.run_report(request)
        return self._parse_response(response)
    
    def get_page_views(self, start_date='30daysAgo', end_date='today'):
        """Get page view analytics"""
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="pageTitle")
            ],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="averageTimeOnPage"),
                Metric(name="entrances"),
                Metric(name="exits")
            ]
        )
        
        response = self.client.run_report(request)
        return self._parse_response(response)
    
    def get_user_journey(self, start_date='30daysAgo', end_date='today'):
        """Get navigation patterns"""
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="landingPage"),
                Dimension(name="secondPage"),
                Dimension(name="exitPage")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="bounceRate")
            ]
        )
        
        response = self.client.run_report(request)
        return self._parse_response(response)
    
    def get_custom_events(self, event_name, start_date='30daysAgo', end_date='today'):
        """Get custom event data (Finder searches, collection creates, etc.)"""
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="eventName"),
                Dimension(name="customEvent:category"),
                Dimension(name="customEvent:label")
            ],
            metrics=[
                Metric(name="eventCount")
            ],
            dimension_filter={
                "filter": {
                    "field_name": "eventName",
                    "string_filter": {"value": event_name}
                }
            }
        )
        
        response = self.client.run_report(request)
        return self._parse_response(response)
    
    def _parse_response(self, response):
        """Parse GA4 API response into dict"""
        results = []
        for row in response.rows:
            result = {}
            for i, dimension_value in enumerate(row.dimension_values):
                dimension_name = response.dimension_headers[i].name
                result[dimension_name] = dimension_value.value
            
            for i, metric_value in enumerate(row.metric_values):
                metric_name = response.metric_headers[i].name
                result[metric_name] = float(metric_value.value)
            
            results.append(result)
        
        return results
```

**Add Flask API Endpoints (`app.py`):**
```python
from ga4_service import GA4Service

ga4 = GA4Service()

@app.route('/api/sessions/duration')
def session_duration():
    """Get average session duration over time"""
    data = ga4.get_session_metrics()
    return jsonify(data)

@app.route('/api/sessions/stats')
def session_stats():
    """Get session statistics"""
    data = ga4.get_session_metrics()
    
    # Calculate aggregates
    total_sessions = sum(d['sessions'] for d in data)
    avg_duration = sum(d['averageSessionDuration'] for d in data) / len(data)
    
    return jsonify({
        'total_sessions': total_sessions,
        'average_duration_seconds': avg_duration,
        'average_duration_minutes': round(avg_duration / 60, 2),
        'daily_breakdown': data
    })

@app.route('/api/pages/views')
def page_views():
    """Get page view analytics"""
    data = ga4.get_page_views()
    return jsonify(data)

@app.route('/api/pages/top')
def top_pages():
    """Get most visited pages"""
    data = ga4.get_page_views()
    sorted_data = sorted(data, key=lambda x: x['screenPageViews'], reverse=True)
    return jsonify(sorted_data[:20])

@app.route('/api/navigation/patterns')
def navigation_patterns():
    """Get user journey patterns"""
    data = ga4.get_user_journey()
    return jsonify(data)
```

**Effort Estimate:**
- GA4 API setup & authentication: **4 hours**
- Service class implementation: **6 hours**
- Flask endpoint creation: **4 hours**
- Testing & debugging: **4 hours**
- **Total backend effort: 2-3 days**

---

#### **3. Dashboard UI (Chart Integration)**

**Add new charts to `dashboard.html`:**
```html
<!-- Session Duration Section -->
<section class="metrics-section category-sessions">
    <div class="category-header">
        <h2>⏱️ Session & Engagement Metrics</h2>
        <p class="category-description">Track time spent and user journeys</p>
    </div>
    
    <div class="chart-row">
        <div class="chart-container">
            <h3>Average Session Duration</h3>
            <div class="pain-point">
                <span class="pain-icon">💡</span>
                <span class="pain-text">Understand how long users stay engaged with the platform</span>
            </div>
            <canvas id="sessionDurationChart"></canvas>
        </div>
        <div class="chart-container">
            <h3>Sessions per User</h3>
            <div class="pain-point">
                <span class="pain-icon">💡</span>
                <span class="pain-text">Measure user retention and return frequency</span>
            </div>
            <canvas id="sessionsPerUserChart"></canvas>
        </div>
    </div>
    
    <div class="chart-row">
        <div class="chart-container full-width">
            <h3>Top Pages by Views</h3>
            <canvas id="topPagesChart"></canvas>
        </div>
    </div>
    
    <div class="chart-row">
        <div class="chart-container full-width">
            <h3>User Journey (Most Common Paths)</h3>
            <canvas id="userJourneyChart"></canvas>
        </div>
    </div>
</section>
```

**Add JavaScript chart functions (`dashboard.js`):**
```javascript
// Session Duration Chart
async function loadSessionDurationChart() {
    const data = await fetchData('sessions/duration');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('sessionDurationChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => formatDate(d.date)),
            datasets: [{
                label: 'Avg Duration (minutes)',
                data: data.map(d => (d.averageSessionDuration / 60).toFixed(2)),
                borderColor: colors.primary,
                backgroundColor: colors.primary + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Duration: ' + context.parsed.y + ' minutes';
                        }
                    }
                }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Minutes',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

// Top Pages Chart
async function loadTopPagesChart() {
    const data = await fetchData('pages/top');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('topPagesChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.pageTitle || d.pagePath),
            datasets: [{
                label: 'Page Views',
                data: data.map(d => d.screenPageViews),
                backgroundColor: colors.info + '80',
                borderColor: colors.info,
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bars
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Total Views'
                    }
                }
            }
        }
    });
}

// User Journey Sankey/Flow Chart
async function loadUserJourneyChart() {
    const data = await fetchData('navigation/patterns');
    if (!data || data.length === 0) return;

    // Transform data for Sankey diagram
    const nodes = [];
    const links = [];
    const nodeMap = new Map();
    
    data.forEach(row => {
        // Add nodes if not exists
        if (!nodeMap.has(row.landingPage)) {
            nodeMap.set(row.landingPage, nodes.length);
            nodes.push({ name: row.landingPage });
        }
        if (!nodeMap.has(row.secondPage)) {
            nodeMap.set(row.secondPage, nodes.length);
            nodes.push({ name: row.secondPage });
        }
        if (!nodeMap.has(row.exitPage)) {
            nodeMap.set(row.exitPage, nodes.length);
            nodes.push({ name: row.exitPage });
        }
        
        // Add links
        links.push({
            source: nodeMap.get(row.landingPage),
            target: nodeMap.get(row.secondPage),
            value: row.sessions
        });
        links.push({
            source: nodeMap.get(row.secondPage),
            target: nodeMap.get(row.exitPage),
            value: row.sessions
        });
    });
    
    // Use Chart.js Sankey plugin or custom visualization
    // Implementation depends on chosen library
}
```

**Effort Estimate:**
- HTML template updates: **2 hours**
- JavaScript chart functions: **6 hours**
- Styling & responsive design: **2 hours**
- Testing across browsers: **2 hours**
- **Total dashboard UI effort: 1-2 days**

---

### GA4 Dashboard Integration Summary

**What the Dashboard Will Show:**

1. **Session Duration Chart**
   - Line chart showing average session time over 30 days
   - Y-axis: Minutes, X-axis: Date
   - Tooltip: Exact duration per day

2. **Sessions per User**
   - Bar chart showing frequency distribution
   - Categories: 1 session, 2-5, 6-10, 11+ sessions
   - Shows user stickiness

3. **Top Pages by Views**
   - Horizontal bar chart (top 20 pages)
   - Shows most popular sections
   - Time on page as secondary metric

4. **User Journey Flow**
   - Sankey diagram showing page transitions
   - Landing → Second Page → Exit paths
   - Width represents traffic volume

5. **Engagement Rate**
   - Donut chart showing engaged vs bounced sessions
   - Definition: >10 seconds or 2+ page views

**Data Refresh:**
- GA4 data has 24-48 hour processing delay
- Dashboard should cache API responses (1 hour TTL)
- Display "Last updated" timestamp

---

## Option B: Custom Backend Tracking

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  ChemLink Web App (Frontend)                │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Custom Tracking SDK                       │    │
│  │  • Session initialization on app load              │    │
│  │  • Page view tracking on route change              │    │
│  │  • Event tracking on user interactions             │    │
│  │  • Heartbeat every 30 seconds (activity)           │    │
│  └─────────────────┬──────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────┘
                     │
                     ▼ (POST /api/tracking/*)
┌─────────────────────────────────────────────────────────────┐
│              ChemLink Backend API (Flask/Node)              │
│  ┌────────────────────────────────────────────────────┐    │
│  │          Tracking Endpoints                         │    │
│  │  POST /api/tracking/session/start                  │    │
│  │  POST /api/tracking/session/heartbeat              │    │
│  │  POST /api/tracking/session/end                    │    │
│  │  POST /api/tracking/pageview                       │    │
│  │  POST /api/tracking/event                          │    │
│  └─────────────────┬──────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────┘
                     │
                     ▼ (INSERT/UPDATE)
         ┌───────────────────────────┐
         │   PostgreSQL Database     │
         │  • user_sessions          │
         │  • page_views             │
         │  • user_events            │
         └───────────┬───────────────┘
                     │
                     ▼ (SELECT queries)
┌─────────────────────────────────────────────────────────────┐
│          ChemLink Analytics Dashboard (Flask)               │
│  • Query session data from production DB                    │
│  • Aggregate metrics                                        │
│  • Render charts with Chart.js                              │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```sql
-- Sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id BIGINT NOT NULL REFERENCES persons(id),
    session_key VARCHAR(64) UNIQUE NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (COALESCE(ended_at, last_activity_at) - started_at))
    ) STORED,
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(20), -- desktop, mobile, tablet
    browser VARCHAR(50),
    os VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_person_started (person_id, started_at DESC),
    INDEX idx_session_active (is_active, last_activity_at DESC),
    INDEX idx_started_date (DATE(started_at))
);

-- Page views table
CREATE TABLE page_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES user_sessions(id),
    person_id BIGINT NOT NULL REFERENCES persons(id),
    page_url VARCHAR(500) NOT NULL,
    page_title VARCHAR(255),
    referrer VARCHAR(500),
    query_params JSONB,
    viewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exited_at TIMESTAMP,
    time_on_page_seconds INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (exited_at - viewed_at))
    ) STORED,
    scroll_depth_percent INTEGER, -- 0-100
    
    INDEX idx_session_views (session_id, viewed_at),
    INDEX idx_person_views (person_id, viewed_at DESC),
    INDEX idx_page_url (page_url),
    INDEX idx_viewed_date (DATE(viewed_at))
);

-- User events table (clicks, searches, interactions)
CREATE TABLE user_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES user_sessions(id),
    person_id BIGINT NOT NULL REFERENCES persons(id),
    page_view_id UUID REFERENCES page_views(id),
    event_type VARCHAR(50) NOT NULL, -- click, search, form_submit, etc.
    event_category VARCHAR(50), -- Finder, Collections, Profile, etc.
    event_action VARCHAR(100), -- Search, Create, Update, etc.
    event_label VARCHAR(255), -- Specific identifier
    element_id VARCHAR(100), -- DOM element clicked
    element_text VARCHAR(255), -- Button/link text
    metadata JSONB, -- Additional event data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_session_events (session_id, created_at),
    INDEX idx_person_events (person_id, created_at DESC),
    INDEX idx_event_type (event_type, created_at DESC),
    INDEX idx_event_category (event_category, created_at DESC)
);

-- Session summary materialized view (for fast queries)
CREATE MATERIALIZED VIEW session_metrics AS
SELECT 
    DATE(started_at) as date,
    COUNT(*) as total_sessions,
    COUNT(DISTINCT person_id) as unique_users,
    AVG(duration_seconds) as avg_duration_seconds,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_seconds) as median_duration_seconds,
    AVG(page_view_count) as avg_pages_per_session,
    COUNT(*) FILTER (WHERE page_view_count = 1) as bounce_sessions,
    COUNT(*) FILTER (WHERE duration_seconds > 600) as long_sessions, -- >10 min
    device_type,
    browser
FROM user_sessions us
LEFT JOIN (
    SELECT session_id, COUNT(*) as page_view_count
    FROM page_views
    GROUP BY session_id
) pv ON us.id = pv.session_id
WHERE started_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(started_at), device_type, browser;

-- Refresh materialized view daily
CREATE INDEX ON session_metrics (date DESC);
```

---

### Frontend Implementation (UI Team)

**Create tracking SDK (`tracking.js`):**
```javascript
class ChemLinkTracker {
    constructor(apiBaseUrl, userId) {
        this.apiBaseUrl = apiBaseUrl;
        this.userId = userId;
        this.sessionId = null;
        this.currentPageViewId = null;
        this.heartbeatInterval = null;
        this.pageStartTime = null;
        
        this.init();
    }
    
    async init() {
        // Start session
        this.sessionId = await this.startSession();
        
        // Set up event listeners
        this.setupPageViewTracking();
        this.setupEventTracking();
        this.setupHeartbeat();
        this.setupExitHandler();
    }
    
    async startSession() {
        const response = await fetch(`${this.apiBaseUrl}/tracking/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                person_id: this.userId,
                user_agent: navigator.userAgent,
                screen_resolution: `${window.screen.width}x${window.screen.height}`,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            })
        });
        
        const data = await response.json();
        return data.session_id;
    }
    
    setupPageViewTracking() {
        // Track initial page view
        this.trackPageView();
        
        // Track page changes (for SPAs)
        window.addEventListener('popstate', () => this.trackPageView());
        
        // Intercept router navigation (React Router example)
        const originalPushState = history.pushState;
        history.pushState = function(...args) {
            originalPushState.apply(this, args);
            window.dispatchEvent(new Event('pushstate'));
        };
        
        window.addEventListener('pushstate', () => this.trackPageView());
    }
    
    async trackPageView() {
        // End previous page view
        if (this.currentPageViewId && this.pageStartTime) {
            await this.endPageView();
        }
        
        // Start new page view
        this.pageStartTime = Date.now();
        
        const response = await fetch(`${this.apiBaseUrl}/tracking/pageview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: this.sessionId,
                person_id: this.userId,
                page_url: window.location.pathname,
                page_title: document.title,
                referrer: document.referrer,
                query_params: Object.fromEntries(new URLSearchParams(window.location.search))
            })
        });
        
        const data = await response.json();
        this.currentPageViewId = data.page_view_id;
    }
    
    async endPageView() {
        if (!this.currentPageViewId) return;
        
        const timeOnPage = Math.floor((Date.now() - this.pageStartTime) / 1000);
        const scrollDepth = this.getScrollDepth();
        
        await fetch(`${this.apiBaseUrl}/tracking/pageview/${this.currentPageViewId}/end`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                time_on_page_seconds: timeOnPage,
                scroll_depth_percent: scrollDepth
            })
        });
    }
    
    setupEventTracking() {
        // Track clicks on important elements
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-track]');
            if (target) {
                this.trackEvent({
                    event_type: 'click',
                    event_category: target.dataset.trackCategory,
                    event_action: target.dataset.trackAction,
                    event_label: target.dataset.trackLabel,
                    element_id: target.id,
                    element_text: target.textContent.trim().substring(0, 255)
                });
            }
        });
    }
    
    async trackEvent(eventData) {
        await fetch(`${this.apiBaseUrl}/tracking/event`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: this.sessionId,
                person_id: this.userId,
                page_view_id: this.currentPageViewId,
                ...eventData
            })
        });
    }
    
    setupHeartbeat() {
        // Send heartbeat every 30 seconds to track active session
        this.heartbeatInterval = setInterval(async () => {
            await fetch(`${this.apiBaseUrl}/tracking/session/heartbeat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
        }, 30000);
    }
    
    setupExitHandler() {
        window.addEventListener('beforeunload', () => {
            // End current page view
            if (this.currentPageViewId) {
                navigator.sendBeacon(
                    `${this.apiBaseUrl}/tracking/pageview/${this.currentPageViewId}/end`,
                    JSON.stringify({
                        time_on_page_seconds: Math.floor((Date.now() - this.pageStartTime) / 1000),
                        scroll_depth_percent: this.getScrollDepth()
                    })
                );
            }
            
            // End session
            navigator.sendBeacon(
                `${this.apiBaseUrl}/tracking/session/end`,
                JSON.stringify({ session_id: this.sessionId })
            );
            
            clearInterval(this.heartbeatInterval);
        });
    }
    
    getScrollDepth() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        return Math.round((scrollTop / scrollHeight) * 100);
    }
}

// Initialize tracker
const tracker = new ChemLinkTracker('/api', currentUser.id);

// Export for manual event tracking
export default tracker;
```

**Usage in React components:**
```javascript
import tracker from './tracking';

// Track Finder search
const handleFinderSearch = (query) => {
    tracker.trackEvent({
        event_type: 'search',
        event_category: 'Finder',
        event_action: 'Search',
        event_label: query,
        metadata: { query_length: query.length }
    });
    
    // Execute search...
};

// Track collection creation
const handleCreateCollection = (name, privacy) => {
    tracker.trackEvent({
        event_type: 'create',
        event_category: 'Collections',
        event_action: 'Create',
        event_label: privacy,
        metadata: { name, privacy }
    });
    
    // Create collection...
};
```

**Add tracking attributes to HTML:**
```html
<button 
    data-track 
    data-track-category="Profile"
    data-track-action="Edit"
    data-track-label="BasicInfo"
>
    Edit Profile
</button>

<a 
    href="/finder"
    data-track 
    data-track-category="Navigation"
    data-track-action="Click"
    data-track-label="FinderLink"
>
    Finder
</a>
```

**UI Effort Estimate:**
- Tracking SDK development: **8-12 hours**
- Integration into app: **8-12 hours**
- Testing & debugging: **6-8 hours**
- **Total UI effort: 3-4 days**

---

### Backend Implementation (Server Team)

**Create tracking service (`tracking_service.py`):**
```python
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from user_agent import parse
import ipaddress

tracking_bp = Blueprint('tracking', __name__)

class TrackingService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_session(self, person_id, user_agent_string, ip_address):
        """Create a new user session"""
        # Parse user agent
        ua = parse(user_agent_string)
        device_type = 'mobile' if ua.is_mobile else ('tablet' if ua.is_tablet else 'desktop')
        
        session_key = str(uuid.uuid4())
        
        query = """
            INSERT INTO user_sessions (
                person_id, session_key, ip_address, user_agent,
                device_type, browser, os, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, true)
            RETURNING id, session_key, started_at
        """
        
        result = self.db.execute(query, (
            person_id, session_key, ip_address, user_agent_string,
            device_type, ua.browser.family, ua.os.family
        ))
        
        return result[0]
    
    def update_session_heartbeat(self, session_id):
        """Update last activity timestamp"""
        query = """
            UPDATE user_sessions 
            SET last_activity_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND is_active = true
        """
        
        self.db.execute(query, (session_id,))
    
    def end_session(self, session_id):
        """Mark session as ended"""
        query = """
            UPDATE user_sessions 
            SET ended_at = CURRENT_TIMESTAMP,
                is_active = false,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        self.db.execute(query, (session_id,))
    
    def create_page_view(self, session_id, person_id, page_data):
        """Record a page view"""
        query = """
            INSERT INTO page_views (
                session_id, person_id, page_url, page_title,
                referrer, query_params
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, viewed_at
        """
        
        result = self.db.execute(query, (
            session_id, person_id, page_data['page_url'],
            page_data.get('page_title'), page_data.get('referrer'),
            page_data.get('query_params')
        ))
        
        return result[0]
    
    def end_page_view(self, page_view_id, time_on_page, scroll_depth):
        """Update page view with exit data"""
        query = """
            UPDATE page_views 
            SET exited_at = CURRENT_TIMESTAMP,
                scroll_depth_percent = %s
            WHERE id = %s
        """
        
        self.db.execute(query, (scroll_depth, page_view_id))
    
    def create_event(self, event_data):
        """Record a user event"""
        query = """
            INSERT INTO user_events (
                session_id, person_id, page_view_id,
                event_type, event_category, event_action,
                event_label, element_id, element_text, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """
        
        result = self.db.execute(query, (
            event_data['session_id'], event_data['person_id'],
            event_data.get('page_view_id'), event_data['event_type'],
            event_data.get('event_category'), event_data.get('event_action'),
            event_data.get('event_label'), event_data.get('element_id'),
            event_data.get('element_text'), event_data.get('metadata')
        ))
        
        return result[0]

# Initialize service
tracking_service = TrackingService(get_db_connection())

# API Endpoints
@tracking_bp.route('/tracking/session/start', methods=['POST'])
def start_session():
    """Start a new user session"""
    data = request.json
    ip_address = request.remote_addr
    
    session = tracking_service.create_session(
        person_id=data['person_id'],
        user_agent_string=data['user_agent'],
        ip_address=ip_address
    )
    
    return jsonify({
        'session_id': str(session['id']),
        'started_at': session['started_at'].isoformat()
    })

@tracking_bp.route('/tracking/session/heartbeat', methods=['POST'])
def session_heartbeat():
    """Update session activity"""
    data = request.json
    tracking_service.update_session_heartbeat(data['session_id'])
    return jsonify({'status': 'ok'})

@tracking_bp.route('/tracking/session/end', methods=['POST'])
def end_session():
    """End a user session"""
    data = request.json
    tracking_service.end_session(data['session_id'])
    return jsonify({'status': 'session_ended'})

@tracking_bp.route('/tracking/pageview', methods=['POST'])
def track_pageview():
    """Track a page view"""
    data = request.json
    page_view = tracking_service.create_page_view(
        session_id=data['session_id'],
        person_id=data['person_id'],
        page_data=data
    )
    
    return jsonify({
        'page_view_id': str(page_view['id']),
        'viewed_at': page_view['viewed_at'].isoformat()
    })

@tracking_bp.route('/tracking/pageview/<page_view_id>/end', methods=['PUT'])
def end_pageview(page_view_id):
    """Update page view with exit data"""
    data = request.json
    tracking_service.end_page_view(
        page_view_id=page_view_id,
        time_on_page=data.get('time_on_page_seconds'),
        scroll_depth=data.get('scroll_depth_percent')
    )
    return jsonify({'status': 'ok'})

@tracking_bp.route('/tracking/event', methods=['POST'])
def track_event():
    """Track a user event"""
    data = request.json
    event = tracking_service.create_event(data)
    
    return jsonify({
        'event_id': str(event['id']),
        'created_at': event['created_at'].isoformat()
    })

# Register blueprint
app.register_blueprint(tracking_bp, url_prefix='/api')
```

**Add analytics query endpoints (`analytics_service.py`):**
```python
@app.route('/api/sessions/duration')
def session_duration():
    """Get average session duration over time"""
    query = """
        SELECT 
            DATE(started_at) as date,
            COUNT(*) as total_sessions,
            AVG(duration_seconds) as avg_duration_seconds,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_seconds) as median_duration_seconds
        FROM user_sessions
        WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
          AND duration_seconds IS NOT NULL
        GROUP BY DATE(started_at)
        ORDER BY date DESC
    """
    
    results = execute_query(get_db_connection(), query)
    return jsonify(results)

@app.route('/api/sessions/stats')
def session_stats():
    """Get session statistics"""
    query = """
        SELECT 
            COUNT(*) as total_sessions,
            COUNT(DISTINCT person_id) as unique_users,
            AVG(duration_seconds) as avg_duration_seconds,
            AVG(duration_seconds) / 60 as avg_duration_minutes,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_seconds) as median_duration_seconds,
            COUNT(*) FILTER (WHERE duration_seconds < 30) as bounce_sessions,
            COUNT(*) FILTER (WHERE duration_seconds >= 600) as engaged_sessions
        FROM user_sessions
        WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
          AND is_active = false
    """
    
    results = execute_query(get_db_connection(), query)
    return jsonify(results[0] if results else {})

@app.route('/api/pages/views')
def page_views():
    """Get page view analytics"""
    query = """
        SELECT 
            page_url,
            page_title,
            COUNT(*) as total_views,
            COUNT(DISTINCT person_id) as unique_viewers,
            AVG(time_on_page_seconds) as avg_time_on_page,
            AVG(scroll_depth_percent) as avg_scroll_depth
        FROM page_views
        WHERE viewed_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY page_url, page_title
        ORDER BY total_views DESC
        LIMIT 50
    """
    
    results = execute_query(get_db_connection(), query)
    return jsonify(results)

@app.route('/api/navigation/patterns')
def navigation_patterns():
    """Get user journey patterns"""
    query = """
        WITH page_sequences AS (
            SELECT 
                session_id,
                page_url,
                LAG(page_url) OVER (PARTITION BY session_id ORDER BY viewed_at) as previous_page,
                LEAD(page_url) OVER (PARTITION BY session_id ORDER BY viewed_at) as next_page
            FROM page_views
            WHERE viewed_at >= CURRENT_DATE - INTERVAL '30 days'
        )
        SELECT 
            previous_page as from_page,
            page_url as to_page,
            COUNT(*) as transition_count
        FROM page_sequences
        WHERE previous_page IS NOT NULL
        GROUP BY previous_page, page_url
        HAVING COUNT(*) > 10
        ORDER BY transition_count DESC
        LIMIT 100
    """
    
    results = execute_query(get_db_connection(), query)
    return jsonify(results)

@app.route('/api/events/summary')
def events_summary():
    """Get event summary by category"""
    query = """
        SELECT 
            event_category,
            event_action,
            COUNT(*) as event_count,
            COUNT(DISTINCT person_id) as unique_users,
            COUNT(DISTINCT session_id) as unique_sessions
        FROM user_events
        WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY event_category, event_action
        ORDER BY event_count DESC
    """
    
    results = execute_query(get_db_connection(), query)
    return jsonify(results)
```

**Backend Effort Estimate:**
- Database schema & migrations: **8 hours**
- Tracking service implementation: **12-16 hours**
- API endpoints: **8-12 hours**
- Analytics query optimization: **6-8 hours**
- Testing & debugging: **8-12 hours**
- **Total backend effort: 5-7 days**

---

### Dashboard Integration (Same for Both Options)

The dashboard charts are **identical** regardless of whether you use GA4 or custom tracking. The only difference is the API endpoint data source.

**Charts to add:**
1. Session Duration (line chart)
2. Sessions per User (bar chart)
3. Top Pages by Views (horizontal bar)
4. User Journey Flow (Sankey diagram)
5. Device/Browser Breakdown (pie chart)
6. Engagement Rate (gauge/donut)

**Total dashboard effort: 1-2 days** (same for both options)

---

## Recommendation

### For Immediate Need (1-2 weeks):
**Use Google Analytics 4**
- Fastest implementation
- Industry-standard metrics
- No infrastructure changes
- Can migrate to custom later

### For Long-term Solution (2-4 weeks):
**Build Custom Tracking**
- Full data ownership
- Custom metrics & dimensions
- Real-time analytics
- Privacy-compliant
- Integrated with existing data

### Hybrid Approach (Recommended):
1. **Phase 1 (Week 1):** Implement GA4 for immediate visibility
2. **Phase 2 (Weeks 2-4):** Build custom tracking in parallel
3. **Phase 3 (Week 5):** Run both side-by-side for validation
4. **Phase 4 (Week 6+):** Transition fully to custom tracking

---

## Total Effort Summary

| Task | GA4 | Custom |
|------|-----|--------|
| **Frontend** | 1 day | 3-4 days |
| **Backend** | 2-3 days | 5-7 days |
| **Dashboard** | 1-2 days | 1-2 days |
| **Testing** | 1 day | 2-3 days |
| **Documentation** | 0.5 days | 1 day |
| **TOTAL** | **5-7 days** | **12-17 days** |

---

## Next Steps

1. **Get stakeholder approval** on approach (GA4 vs Custom vs Hybrid)
2. **Allocate resources** (frontend dev, backend dev, QA)
3. **Create implementation tickets** with detailed specs
4. **Set up tracking plan** (what events to track)
5. **Begin Phase 1** implementation

---

**Questions or Clarifications?**  
Contact: Jay Persanchez  
Date: October 30, 2025
