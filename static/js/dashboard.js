// Chart color palette
const colors = {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#48bb78',
    warning: '#ed8936',
    danger: '#f56565',
    info: '#4299e1',
    purple: '#9f7aea',
    pink: '#ed64a6',
    teal: '#38b2ac',
    cyan: '#0bc5ea'
};

const chartColors = [
    colors.primary, colors.secondary, colors.success, 
    colors.warning, colors.info, colors.purple, 
    colors.pink, colors.teal, colors.cyan
];

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatMonth(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
}

// API fetch helper
async function fetchData(endpoint) {
    try {
        const response = await fetch(`/api/${endpoint}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

// =============================================================================
// SUMMARY CARDS
// =============================================================================
async function loadSummaryCards() {
    const data = await fetchData('engagement/summary');
    if (!data) return;

    const cardsContainer = document.getElementById('summaryCards');
    cardsContainer.innerHTML = '';

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${item.metric}</h3>
            <div class="value">${item.value}</div>
        `;
        cardsContainer.appendChild(card);
    });
}

// =============================================================================
// GROWTH METRICS CHARTS
// =============================================================================

// New Users Monthly Chart
async function loadNewUsersMonthlyChart() {
    const data = await fetchData('new-users/monthly');
    if (!data || data.length === 0) {
        console.error('No data for new users chart');
        return;
    }
    
    console.log('New Users data:', data);

    const ctx = document.getElementById('newUsersMonthlyChart').getContext('2d');
    // Don't reverse if already in correct order
    const sortedData = [...data].reverse(); // Create copy to avoid mutation
    
    new Chart(ctx, {
        type: 'bar', // Use bar chart for better visibility with few data points
        data: {
            labels: sortedData.map(d => formatMonth(d.month)),
            datasets: [{
                label: 'New Users',
                data: sortedData.map(d => d.new_users),
                borderColor: colors.primary,
                backgroundColor: colors.primary + '33',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toLocaleString() + ' users';
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Growth Rate Chart
async function loadGrowthRateChart() {
    const data = await fetchData('growth-rate/monthly');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('growthRateChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.reverse().map(d => formatMonth(d.month)),
            datasets: [{
                label: 'Growth Rate %',
                data: data.map(d => d.growth_rate_pct || 0),
                backgroundColor: data.map(d => 
                    (d.growth_rate_pct || 0) >= 0 ? colors.success : colors.danger
                ),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Growth Rate: ' + (context.parsed.y || 0).toFixed(2) + '%';
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Growth Rate (%)',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// DAU Chart
async function loadDAUChart() {
    const data = await fetchData('active-users/daily');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('dauChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.reverse().map(d => formatDate(d.date)),
            datasets: [{
                label: 'Active Users',
                data: data.map(d => d.active_users),
                borderColor: colors.info,
                backgroundColor: colors.info + '33',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Active Users: ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Active Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// MAU Chart
async function loadMAUChart() {
    const data = await fetchData('active-users/monthly');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('mauChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.reverse().map(d => formatMonth(d.month)),
            datasets: [{
                label: 'Monthly Active Users',
                data: data.map(d => d.active_users),
                backgroundColor: colors.purple,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Active Users: ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Active Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// MAU by Country Chart
async function loadMAUByCountryChart() {
    const data = await fetchData('active-users/monthly-by-country');
    if (!data || data.length === 0) return;

    // Filter for October 2025 and aggregate by country
    const octData = data.filter(d => d.month.startsWith('2025-10'));
    const countryMap = {};
    
    octData.forEach(item => {
        if (!countryMap[item.country]) {
            countryMap[item.country] = 0;
        }
        countryMap[item.country] += item.active_users;
    });

    const countries = Object.keys(countryMap);
    const counts = Object.values(countryMap);

    const ctx = document.getElementById('mauByCountryChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: countries,
            datasets: [{
                label: 'Active Users by Country',
                data: counts,
                backgroundColor: chartColors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.x.toLocaleString() + ' users';
                        }
                    }
                }
            },
            scales: {
                x: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Active Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Country',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

// =============================================================================
// ENGAGEMENT CHARTS
// =============================================================================

// Post Frequency Chart
async function loadPostFrequencyChart() {
    const data = await fetchData('engagement/post-frequency');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('postFrequencyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.reverse().map(d => formatDate(d.post_date)),
            datasets: [{
                label: 'Posts Created',
                data: data.map(d => d.posts_created),
                borderColor: colors.warning,
                backgroundColor: colors.warning + '33',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Posts Created: ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Posts',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Engagement Rate Chart
async function loadEngagementRateChart() {
    const data = await fetchData('engagement/post-engagement-rate');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('engagementRateChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.content_type || 'Unknown'),
            datasets: [{
                label: 'Avg Comments per Post',
                data: data.map(d => parseFloat(d.avg_comments_per_post) || 0),
                backgroundColor: colors.success,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(2) + ' comments per post';
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Content Type',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Average Comments per Post',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    }
                }
            }
        }
    });
}

// Content Type Distribution Chart
async function loadContentTypeChart() {
    const data = await fetchData('engagement/content-analysis');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('contentTypeChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.type || 'Unknown'),
            datasets: [{
                data: data.map(d => d.post_count),
                backgroundColor: chartColors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { 
                    display: true,
                    position: 'right',
                    labels: {
                        font: { size: 12 },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value.toLocaleString() + ' posts (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Active Posters Chart
async function loadActivePostersChart() {
    const data = await fetchData('engagement/active-posters');
    if (!data || data.length === 0) return;

    const topTen = data.slice(0, 10);

    const ctx = document.getElementById('activePostersChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topTen.map(d => d.name),
            datasets: [{
                label: 'Engagement Score',
                data: topTen.map(d => d.engagement_score),
                backgroundColor: colors.primary,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Engagement Score: ' + context.parsed.x.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Engagement Score (Posts×3 + Comments×2)',
                        font: { size: 11, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'User Name',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

// =============================================================================
// PROFILE METRICS CHARTS
// =============================================================================

// Profile Completion Score Distribution
async function loadProfileCompletionChart() {
    const data = await fetchData('profile/completion-rate');
    if (!data || data.length === 0) return;

    // Group by score
    const scoreGroups = {};
    data.forEach(item => {
        const score = item.profile_completeness_score;
        scoreGroups[score] = (scoreGroups[score] || 0) + 1;
    });

    const scores = Object.keys(scoreGroups).sort((a, b) => a - b);
    const counts = scores.map(s => scoreGroups[s]);

    const ctx = document.getElementById('profileCompletionChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: scores.map(s => `Score ${s}/7`),
            datasets: [{
                label: 'Number of Users',
                data: counts,
                backgroundColor: colors.info,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toLocaleString() + ' users';
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Profile Completeness Score',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Profile Status Breakdown
async function loadProfileStatusChart() {
    const data = await fetchData('profile/completion-rate');
    if (!data || data.length === 0) return;

    // Count by status
    const statusGroups = {};
    data.forEach(item => {
        const status = item.profile_status;
        statusGroups[status] = (statusGroups[status] || 0) + 1;
    });

    const statuses = Object.keys(statusGroups);
    const counts = Object.values(statusGroups);

    const ctx = document.getElementById('profileStatusChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: statuses,
            datasets: [{
                data: counts,
                backgroundColor: [colors.success, colors.warning, colors.info],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { 
                    display: true,
                    position: 'right',
                    labels: {
                        font: { size: 12 },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value.toLocaleString() + ' users (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Profile Update Freshness
async function loadProfileFreshnessChart() {
    const data = await fetchData('profile/update-frequency');
    if (!data || data.length === 0) return;

    // Count by freshness status
    const freshnessGroups = {};
    data.forEach(item => {
        const status = item.profile_status;
        freshnessGroups[status] = (freshnessGroups[status] || 0) + 1;
    });

    const statuses = Object.keys(freshnessGroups);
    const counts = Object.values(freshnessGroups);

    const ctx = document.getElementById('profileFreshnessChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: statuses,
            datasets: [{
                label: 'Number of Profiles',
                data: counts,
                backgroundColor: [colors.success, colors.warning, colors.danger],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toLocaleString() + ' profiles';
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Profile Status',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Profiles',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// =============================================================================
// TOP POSTS TABLE
// =============================================================================
async function loadTopPostsTable() {
    const data = await fetchData('engagement/post-reach');
    if (!data || data.length === 0) {
        document.querySelector('#topPostsTable tbody').innerHTML = 
            '<tr><td colspan="6" style="text-align: center;">No data available</td></tr>';
        return;
    }

    const tbody = document.querySelector('#topPostsTable tbody');
    tbody.innerHTML = '';

    data.forEach(post => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${post.post_preview || 'N/A'}</td>
            <td>${post.author || 'Unknown'}</td>
            <td>${post.content_type || 'N/A'}</td>
            <td>${post.comment_count || 0}</td>
            <td>${post.unique_commenters || 0}</td>
            <td>${Math.floor(post.days_old) || 0}</td>
        `;
        tbody.appendChild(row);
    });
}

// =============================================================================
// INITIALIZE DASHBOARD
// =============================================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Loading ChemLink Analytics Dashboard...');

    // Load all components
    loadSummaryCards();
    
    // Growth metrics
    loadNewUsersMonthlyChart();
    loadGrowthRateChart();
    loadDAUChart();
    loadMAUChart();
    loadMAUByCountryChart();
    
    // Engagement metrics
    loadPostFrequencyChart();
    loadEngagementRateChart();
    loadContentTypeChart();
    loadActivePostersChart();
    
    // Profile metrics
    loadProfileCompletionChart();
    loadProfileStatusChart();
    loadProfileFreshnessChart();
    
    // Tables
    loadTopPostsTable();

    console.log('Dashboard loaded successfully!');
});
