# ChemLink Analytics Dashboard

A comprehensive analytics dashboard for visualizing ChemLink platform metrics including user growth, engagement, and profile statistics.

## Features

### Growth Metrics
- **New Users**: Daily, weekly, and monthly user sign-ups (monthly shows rolling 12 months)
- **User Growth Rate**: Month-over-month growth percentages (rolling 12 months)
- **Daily Active Users (DAU)**: Users who posted or commented each day
- **Weekly Active Users (WAU)**: Active users aggregated by week
- **Monthly Active Users (MAU)**: Active users by month with country breakdown

### User Engagement Metrics
- **Post Frequency**: Daily posting activity trends
- **Post Engagement Rate**: Comments per post by content type
- **Content Type Distribution**: Breakdown of post types (text, link, image, etc.)
- **Active Posters**: Top contributors by engagement score (HIDDEN - contains PII)
- **Top Performing Posts**: Posts with highest engagement in last 30 days (HIDDEN - contains PII)

### Profile Metrics
- **Profile Completion Rate**: Distribution of profile completeness scores
- **Profile Status**: Breakdown of Finder-enabled vs Builder-only profiles
- **Profile Update Freshness**: How recently users updated their profiles

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (2 databases - Engagement Platform & ChemLink Service)
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Charts**: Chart.js 4.4.0

## Prerequisites

- Python 3.8+
- Access to PostgreSQL databases:
  - `engagement-platform-stg`
  - `chemlink-service-stg`

## Installation

1. **Navigate to the project directory**:
   ```bash
   cd chemlink-analytics-dashboard
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database configuration is already set** in `.env` file with connection details.

## Running the Dashboard

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Access the dashboard**:
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

The dashboard will automatically fetch data from both databases and display all metrics with interactive charts.

## Project Structure

```
chemlink-analytics-dashboard/
├── app.py                    # Flask application with API routes
├── db_config.py              # Database connection configuration
├── requirements.txt          # Python dependencies
├── .env                      # Database credentials
├── templates/
│   └── dashboard.html        # Main dashboard HTML
└── static/
    ├── css/
    │   └── styles.css        # Dashboard styling
    └── js/
        └── dashboard.js      # Chart rendering and data fetching
```

## API Endpoints

### Growth Metrics
- `GET /api/new-users/daily` - New user sign-ups today
- `GET /api/new-users/weekly` - Weekly new users
- `GET /api/new-users/monthly` - Monthly new users
- `GET /api/growth-rate/weekly` - Weekly growth rate
- `GET /api/growth-rate/monthly` - Monthly growth rate
- `GET /api/active-users/daily` - Daily active users
- `GET /api/active-users/weekly` - Weekly active users
- `GET /api/active-users/monthly` - Monthly active users
- `GET /api/active-users/monthly-by-country` - MAU by country

### Engagement Metrics
- `GET /api/engagement/post-frequency` - Daily posting activity
- `GET /api/engagement/post-engagement-rate` - Engagement by content type
- `GET /api/engagement/content-analysis` - Content type analysis
- `GET /api/engagement/active-posters` - Top active users
- `GET /api/engagement/post-reach` - Top performing posts
- `GET /api/engagement/summary` - Quick stats summary

### Profile Metrics
- `GET /api/profile/completion-rate` - Profile completion statistics
- `GET /api/profile/update-frequency` - Profile update frequency

## Database Schema

The dashboard queries two databases:

### engagement-platform-stg
- `persons` - User profiles
- `posts` - User posts
- `comments` - Post comments
- `locations` - Geographic data

### chemlink-service-stg
- `persons` - User profiles with career data
- `experiences` - Work experience
- `education` - Educational background
- `embeddings` - AI embeddings for finder
- `person_languages` - Language proficiency

## Customization

### Changing Chart Colors
Edit `static/js/dashboard.js` and modify the `colors` object at the top of the file.

### Adding New Metrics
1. Add a new route in `app.py`
2. Add SQL query to fetch the data
3. Create a chart function in `static/js/dashboard.js`
4. Add HTML container in `templates/dashboard.html`

## Notes

- The dashboard uses real-time data from staging databases
- All dates are displayed in user's local timezone
- Charts are responsive and work on mobile devices
- Data is cached in browser for better performance
- **Monthly metrics show rolling 12-month window** for relevance
- **PII elements are hidden via CSS** - can be unhidden by removing CSS rules in `static/css/styles.css`
- **Job-related references removed** from pain points to focus on core platform value

## Security

- Database credentials are stored in `.env` file (not committed to git)
- Flask CORS is enabled for development
- For production, ensure proper security measures are in place

## Support

For issues or questions, contact the ChemLink development team.
