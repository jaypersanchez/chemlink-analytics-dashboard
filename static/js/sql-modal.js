// SQL Modal functionality

let sqlQueries = {};
let currentQueryCode = '';

// Load SQL queries on page load
async function loadSQLQueries() {
    try {
        const response = await fetch('/api/sql-queries');
        sqlQueries = await response.json();
        console.log('SQL queries loaded:', Object.keys(sqlQueries).length);
        
        // Add SQL buttons to all chart containers
        addSQLButtonsToCharts();
    } catch (error) {
        console.error('Error loading SQL queries:', error);
    }
}

// Add SQL buttons to each chart container
function addSQLButtonsToCharts() {
    // Map chart IDs to query IDs
    const chartToQueryMap = {
        'newUsersMonthlyChart': 'new_users_monthly',
        'growthRateChart': 'growth_rate_monthly',
        'dauChart': 'dau',
        'mauChart': 'mau',
        'mauByCountryChart': 'mau_by_country',
        'postFrequencyChart': 'post_frequency',
        'engagementRateChart': 'engagement_rate',
        'contentTypeChart': 'content_type',
        'activePostersChart': 'active_posters',
        'profileCompletionChart': 'profile_completion',
        'profileStatusChart': 'profile_completion', // Same query
        'profileFreshnessChart': 'profile_freshness',
        'activityByTypeMonthlyChart': 'activity_by_type_monthly',
        'activityDistributionChart': 'activity_distribution_current',
        'activityIntensityLevelsChart': 'activity_intensity_levels'
    };
    
    Object.entries(chartToQueryMap).forEach(([chartId, queryId]) => {
        const canvas = document.getElementById(chartId);
        if (canvas) {
            const container = canvas.closest('.chart-container');
            if (container && !container.querySelector('.sql-button')) {
                // Create SQL button
                const sqlButton = document.createElement('button');
                sqlButton.className = 'sql-button';
                sqlButton.innerHTML = '💾 SQL';
                sqlButton.onclick = () => showSQLModal(queryId);
                
                // Insert after h3 title
                const title = container.querySelector('h3');
                if (title) {
                    title.parentNode.insertBefore(sqlButton, title.nextSibling);
                }
            }
        }
    });
    
    // Add SQL button for top posts table
    const topPostsSection = document.querySelector('#topPostsTable');
    if (topPostsSection) {
        const container = topPostsSection.closest('.metrics-section');
        const h2 = container.querySelector('h2');
        if (h2 && !container.querySelector('.sql-button')) {
            const sqlButton = document.createElement('button');
            sqlButton.className = 'sql-button';
            sqlButton.innerHTML = '💾 View SQL';
            sqlButton.style.marginLeft = '15px';
            sqlButton.style.display = 'inline-block';
            sqlButton.onclick = () => showSQLModal('post_reach');
            h2.appendChild(sqlButton);
        }
    }
}

// Show SQL modal
function showSQLModal(queryId) {
    const queryData = sqlQueries[queryId];
    if (!queryData) {
        alert('SQL query not found for: ' + queryId);
        return;
    }
    
    // Set modal content
    document.getElementById('sqlModalTitle').textContent = queryData.name;
    document.getElementById('sqlDatabase').textContent = '📦 Database: ' + queryData.database;
    document.getElementById('sqlQueryCode').textContent = queryData.query;
    
    // Store current query for copy function
    currentQueryCode = queryData.query;
    
    // Show modal
    document.getElementById('sqlModal').style.display = 'flex';
}

// Close SQL modal
function closeSQLModal() {
    document.getElementById('sqlModal').style.display = 'none';
}

// Copy SQL to clipboard
async function copySQLToClipboard() {
    try {
        await navigator.clipboard.writeText(currentQueryCode);
        
        // Show feedback
        const btn = document.querySelector('.copy-sql-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copied!';
        btn.style.background = '#48bb78';
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
        }, 2000);
    } catch (error) {
        alert('Failed to copy to clipboard');
        console.error('Copy error:', error);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('sqlModal');
    if (event.target === modal) {
        closeSQLModal();
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeSQLModal();
    }
});

// Load queries when page loads
window.addEventListener('load', loadSQLQueries);
