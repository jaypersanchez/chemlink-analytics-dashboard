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

function formatHour(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', hour12: true });
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
    const sortedData = [...data].reverse();
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(d => formatMonth(d.month)),
            datasets: [{
                label: 'Growth Rate %',
                data: sortedData.map(d => d.growth_rate_pct !== null ? d.growth_rate_pct : 0),
                backgroundColor: sortedData.map(d => 
                    (d.growth_rate_pct !== null && d.growth_rate_pct >= 0) ? colors.success : 
                    (d.growth_rate_pct !== null && d.growth_rate_pct < 0) ? colors.danger : 
                    '#ccc'
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

// Login velocity chart (Kratos sessions)
async function loadLoginVelocityChart() {
    const data = await fetchData('auth/login-velocity/hourly');
    if (!data || data.length === 0) return;

    const canvas = document.getElementById('loginVelocityChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const sortedData = [...data].reverse();

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(d => formatHour(d.hour_bucket)),
            datasets: [{
                label: 'Sign-ins Started',
                data: sortedData.map(d => d.sessions_started),
                borderColor: colors.info,
                backgroundColor: colors.info + '33',
                borderWidth: 3,
                fill: true,
                tension: 0.35,
                pointRadius: 3
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
                            return `${context.dataset.label}: ${context.parsed.y.toLocaleString()} users`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Hour of Day (last 24h)',
                        font: { size: 12, weight: 'bold' },
                        color: '#1f2933'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Sign-ins Started per Hour',
                        font: { size: 12, weight: 'bold' },
                        color: '#1f2933'
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

// Unique authenticated identities (Kratos)
async function loadUniqueIdentitiesChart() {
    const data = await fetchData('auth/unique-identities/daily');
    if (!data || data.length === 0) return;

    const canvas = document.getElementById('uniqueIdentitiesChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const sortedData = [...data].reverse();

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(d => formatDate(d.day_bucket)),
            datasets: [{
                label: 'Unique Authenticated Users',
                data: sortedData.map(d => d.unique_identities),
                borderColor: colors.success,
                backgroundColor: colors.success + '22',
                borderWidth: 3,
                tension: 0.35,
                pointRadius: 3,
                fill: true
            }, {
                label: 'Sign-ins Started',
                data: sortedData.map(d => d.sessions_started),
                borderColor: colors.info,
                borderDash: [6, 4],
                fill: false,
                borderWidth: 2,
                tension: 0.25,
                pointRadius: 0
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
                            const label = context.dataset.label || '';
                            return `${label}: ${context.parsed.y.toLocaleString()} users`;
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date (Last 30 Days)',
                        font: { size: 12, weight: 'bold' },
                        color: '#1f2933'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Unique Authenticated Users / Sign-ins',
                        font: { size: 12, weight: 'bold' },
                        color: '#1f2933'
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
                borderWidth: 0,
                barPercentage: data.length === 1 ? 0.3 : 0.8,  // Narrower bars for single data points
                categoryPercentage: 0.9
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

    // Check if all engagement rates are 0
    const hasEngagement = data.some(d => parseFloat(d.avg_comments_per_post) > 0);
    
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
                    min: 0,
                    max: hasEngagement ? undefined : 1,  // Force max to 1 if no engagement to show scale
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
// TALENT MARKETPLACE INTELLIGENCE CHARTS  
// =============================================================================
async function loadTopCompaniesChart() {
    const data = await fetchData('talent/top-companies');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('topCompaniesChart');
    if (!ctx) return;

    const top10 = data.slice(0, 10);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(d => d.company_name || 'Unknown'),
            datasets: [{
                label: 'User Count',
                data: top10.map(d => d.user_count),
                backgroundColor: 'rgba(0, 150, 136, 0.7)',
                borderColor: '#00796b',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return '🏢 Top Companies\n' + context[0].label;
                        },
                        afterBody: function(context) {
                            const index = context[0].dataIndex;
                            const item = top10[index];
                            return [
                                `Total Experiences: ${item.total_experiences}`,
                                `Countries: ${item.countries || 'N/A'}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Users',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Company',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

async function loadTopRolesChart() {
    const data = await fetchData('talent/top-roles');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('topRolesChart');
    if (!ctx) return;

    const top10 = data.slice(0, 10);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(d => d.role_title || 'Unknown'),
            datasets: [{
                label: 'User Count',
                data: top10.map(d => d.user_count),
                backgroundColor: 'rgba(63, 81, 181, 0.7)',
                borderColor: '#3f51b5',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return '💼 Top Roles\n' + context[0].label;
                        },
                        afterBody: function(context) {
                            const index = context[0].dataIndex;
                            const item = top10[index];
                            return [
                                `Companies: ${item.companies_count}`,
                                `Avg Years: ${item.avg_years_in_role ? Math.round(item.avg_years_in_role * 10) / 10 : 'N/A'}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Users',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Role',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

async function loadEducationDistributionChart() {
    const data = await fetchData('talent/education-distribution');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('educationDistributionChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.degree_type || 'Unknown'),
            datasets: [{
                data: data.map(d => d.user_count),
                backgroundColor: [
                    'rgba(156, 39, 176, 0.8)',
                    'rgba(63, 81, 181, 0.8)',
                    'rgba(0, 150, 136, 0.8)',
                    'rgba(255, 152, 0, 0.8)',
                    'rgba(244, 67, 54, 0.8)',
                    'rgba(103, 58, 183, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return '🎓 Education Distribution\n' + context[0].label;
                        },
                        afterLabel: function(context) {
                            const item = data[context.dataIndex];
                            return `Schools: ${item.schools_count}`;
                        }
                    }
                }
            }
        }
    });
}

async function loadGeographicDistributionChart() {
    const data = await fetchData('talent/geographic-distribution');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('geographicDistributionChart');
    if (!ctx) return;

    const top10 = data.slice(0, 10);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(d => d.country),
            datasets: [{
                label: 'Users',
                data: top10.map(d => d.user_count),
                backgroundColor: 'rgba(33, 150, 243, 0.7)',
                borderColor: '#1976d2',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return '🌍 Geographic Distribution\n' + context[0].label;
                        },
                        afterBody: function(context) {
                            const index = context[0].dataIndex;
                            const item = top10[index];
                            return [
                                `Companies: ${item.companies_count}`,
                                `Percentage: ${item.percentage}%`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Country',
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

async function loadTopSkillsProjectsChart() {
    const data = await fetchData('talent/top-skills-projects');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('topSkillsProjectsChart');
    if (!ctx) return;

    const top10 = data.slice(0, 10);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(d => d.project_name || 'Unnamed Project'),
            datasets: [{
                label: 'Users with This Project',
                data: top10.map(d => d.user_count),
                backgroundColor: 'rgba(255, 152, 0, 0.7)',
                borderColor: '#f57c00',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return '🛠️ Top Skills & Projects\n' + context[0].label;
                        },
                        afterBody: function(context) {
                            const index = context[0].dataIndex;
                            const item = top10[index];
                            return item.project_description || 'No description';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Users',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Project/Skill',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

// =============================================================================
// FUNNEL ANALYTICS
// =============================================================================

// Account Creation Funnel
async function loadAccountFunnelChart() {
    const data = await fetchData('funnel/account-creation');
    if (!data || data.length === 0) return;

    const row = data[0];
    const total = row.total_accounts;

    // Define funnel stages with labels and values
    const stages = [
        { label: 'Account Created', value: total },
        { label: 'Basic Info', value: row.step_basic_info },
        { label: 'Added Headline', value: row.step_headline },
        { label: 'Added Location', value: row.step_location },
        { label: 'Added Company', value: row.step_company },
        { label: 'Linked LinkedIn', value: row.step_linkedin },
        { label: 'Enabled Finder', value: row.step_finder_enabled }
    ];

    const ctx = document.getElementById('accountFunnelChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stages.map(s => s.label),
            datasets: [{
                label: 'Users Remaining',
                data: stages.map(s => s.value),
                backgroundColor: [
                    '#667eea',
                    '#764ba2', 
                    '#48bb78',
                    '#ed8936',
                    '#4299e1',
                    '#9f7aea',
                    '#ed64a6'
                ],
                borderWidth: 0
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.x;
                            const pct = ((value / total) * 100).toFixed(1);
                            const dropPct = (100 - pct).toFixed(1);
                            return [
                                `Users: ${value.toLocaleString()}`,
                                `Completion: ${pct}%`,
                                `Drop-off: ${dropPct}%`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
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
                },
                y: {
                    title: {
                        display: true,
                        text: 'Onboarding Stage',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });

    // Load pyramid chart with same data
    loadAccountFunnelPyramidChart(stages, total);
}

// Account Creation Funnel Pyramid Chart (Custom Canvas Drawing)
function loadAccountFunnelPyramidChart(stages, total) {
    const canvas = document.getElementById('accountFunnelPyramidChart');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions based on container
    const container = canvas.parentElement;
    canvas.width = container.clientWidth - 40;
    canvas.height = 400;
    
    const width = canvas.width;
    const height = canvas.height;
    
    const maxValue = Math.max(...stages.map(s => s.value));
    
    // Calculate dimensions
    const padding = 60;
    const funnelHeight = height - (padding * 2);
    const stageHeight = funnelHeight / stages.length;
    const maxWidth = width - (padding * 2);
    
    // Colors matching bar chart
    const stageColors = [
        '#667eea',
        '#764ba2', 
        '#48bb78',
        '#ed8936',
        '#4299e1',
        '#9f7aea',
        '#ed64a6'
    ];
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw funnel stages
    stages.forEach((stage, index) => {
        const y = padding + (index * stageHeight);
        const stageWidth = (stage.value / maxValue) * maxWidth;
        
        // Calculate widths for trapezoid effect
        let topWidth = stageWidth;
        let bottomWidth = stageWidth;
        
        if (index < stages.length - 1) {
            bottomWidth = (stages[index + 1].value / maxValue) * maxWidth;
        }
        
        const topX = (width - topWidth) / 2;
        const bottomX = (width - bottomWidth) / 2;
        
        // Draw trapezoid
        ctx.fillStyle = stageColors[index];
        ctx.strokeStyle = stageColors[index];
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        ctx.moveTo(topX, y);
        ctx.lineTo(topX + topWidth, y);
        ctx.lineTo(bottomX + bottomWidth, y + stageHeight);
        ctx.lineTo(bottomX, y + stageHeight);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Draw stage label
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(stage.label, width / 2, y + stageHeight / 2 - 12);
        
        // Draw count
        ctx.font = '13px Arial';
        ctx.fillText(stage.value.toLocaleString() + ' users', width / 2, y + stageHeight / 2 + 6);
        
        // Draw percentage
        const percentage = ((stage.value / total) * 100).toFixed(1);
        ctx.font = '12px Arial';
        ctx.fillStyle = '#e0e0e0';
        ctx.fillText(percentage + '%', width / 2, y + stageHeight / 2 + 22);
    });
    
    // Make canvas responsive
    window.addEventListener('resize', () => {
        loadAccountFunnelPyramidChart(stages, total);
    });
}

// =============================================================================
// FINDER SEARCH ANALYTICS
// =============================================================================

// Finder Search Volume Chart
async function loadFinderSearchesChart() {
    const data = await fetchData('finder/searches');
    if (!data || !data.search_timeline || data.search_timeline.length === 0) return;

    const ctx = document.getElementById('finderSearchesChart').getContext('2d');
    const sortedData = [...data.search_timeline].reverse();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(d => formatMonth(d.month)),
            datasets: [{
                label: 'Searches',
                data: sortedData.map(d => d.searches),
                borderColor: colors.info,
                backgroundColor: colors.info + '33',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Searches: ' + context.parsed.y.toLocaleString();
                        }
                    }
                },
                title: {
                    display: true,
                    text: `Total: ${data.total_searches} Searches`,
                    color: '#ffffff',
                    font: { size: 14, weight: 'bold' }
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
                        text: 'Number of Searches',
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

// Search Intent Distribution Chart
async function loadFinderIntentsChart() {
    const data = await fetchData('finder/searches');
    if (!data || !data.searches_by_intent || data.searches_by_intent.length === 0) return;

    const ctx = document.getElementById('finderIntentsChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.searches_by_intent.map(d => d.intent),
            datasets: [{
                label: 'Searches',
                data: data.searches_by_intent.map(d => d.search_count),
                backgroundColor: chartColors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = data.total_searches;
                            const value = context.parsed.x;
                            const pct = ((value / total) * 100).toFixed(1);
                            return 'Searches: ' + value.toLocaleString() + ' (' + pct + '%)';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Searches',
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
                        text: 'Search Intent',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

// Finder Engagement Rate Chart
async function loadFinderEngagementChart() {
    const data = await fetchData('finder/engagement');
    if (!data) return;

    const ctx = document.getElementById('finderEngagementChart').getContext('2d');
    
    // Show vote types breakdown
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.votes_by_type.map(d => d.vote_type),
            datasets: [{
                data: data.votes_by_type.map(d => d.vote_count),
                backgroundColor: [
                    colors.success,
                    colors.danger,
                    colors.warning,
                    colors.info
                ],
                borderWidth: 2,
                borderColor: '#1a1d29'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#cccccc',
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = data.total_votes;
                            const pct = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' (' + pct + '%)';
                        }
                    }
                },
                title: {
                    display: true,
                    text: `${data.engagement_rate_pct}% Engagement Rate (${data.active_users} Active Users)`,
                    color: '#ffffff',
                    font: { size: 13, weight: 'bold' }
                }
            }
        }
    });
}

// =============================================================================
// COLLECTIONS FEATURE ENGAGEMENT
// =============================================================================

// Profile Additions to Collections Chart
async function loadProfileAdditionsChart() {
    const data = await fetchData('collections/profile-additions');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('profileAdditionsChart').getContext('2d');
    const sortedData = [...data].reverse();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(d => formatMonth(d.month)),
            datasets: [{
                label: 'Profiles Added',
                data: sortedData.map(d => d.profiles_added),
                borderColor: colors.success,
                backgroundColor: colors.success + '33',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Profiles Added: ' + context.parsed.y.toLocaleString();
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
                        text: 'Profiles Added',
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

// Collections Created Chart
async function loadCollectionsCreatedChart() {
    const data = await fetchData('collections/created');
    if (!data) return;

    const ctx = document.getElementById('collectionsCreatedChart').getContext('2d');
    
    // Show privacy breakdown as doughnut chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.privacy_breakdown.map(d => d.privacy_type || 'Unknown'),
            datasets: [{
                data: data.privacy_breakdown.map(d => d.count),
                backgroundColor: [
                    colors.primary,
                    colors.secondary,
                    colors.warning,
                    colors.info
                ],
                borderWidth: 2,
                borderColor: '#1a1d29'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#cccccc',
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = data.total_count;
                            const pct = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' (' + pct + '%)';
                        }
                    }
                },
                title: {
                    display: true,
                    text: `Total: ${data.total_count} Collections`,
                    color: '#ffffff',
                    font: { size: 14, weight: 'bold' }
                }
            }
        }
    });
}

// Collections Shared Chart
async function loadCollectionsSharedChart() {
    const data = await fetchData('collections/shared');
    if (!data) return;

    const ctx = document.getElementById('collectionsSharedChart').getContext('2d');
    
    // Show access type breakdown
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.access_type_breakdown.map(d => d.access_type || 'Unknown'),
            datasets: [{
                label: 'Collaborations',
                data: data.access_type_breakdown.map(d => d.share_count),
                backgroundColor: [
                    colors.success,
                    colors.warning,
                    colors.info,
                    colors.danger
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Shares: ' + context.parsed.y.toLocaleString();
                        }
                    }
                },
                title: {
                    display: true,
                    text: `${data.shared_collections_count} Collections Shared (${data.total_shares} Total Collaborations)`,
                    color: '#ffffff',
                    font: { size: 13, weight: 'bold' }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Access Type',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Shares',
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

// DAU Comprehensive Chart  
async function loadDAUComprehensiveChart() {
    const data = await fetchData('active-users/daily-comprehensive');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('dauComprehensiveChart').getContext('2d');
    const sortedData = [...data].reverse();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(d => formatDate(d.date)),
            datasets: [{
                label: 'Active Users',
                data: sortedData.map(d => d.active_users),
                borderColor: colors.purple,
                backgroundColor: colors.purple + '20',
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
                        text: 'Active Users',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

// MAU Comprehensive Chart
async function loadMAUComprehensiveChart() {
    const data = await fetchData('active-users/monthly-comprehensive');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('mauComprehensiveChart').getContext('2d');
    const sortedData = [...data].reverse();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(d => formatMonth(d.month)),
            datasets: [{
                label: 'Active Users',
                data: sortedData.map(d => d.active_users),
                borderColor: colors.teal,
                backgroundColor: colors.teal + '20',
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
                        text: 'Active Users',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

// Active Users by Type (Standard vs Finder)
async function loadActiveUsersByTypeChart() {
    const data = await fetchData('active-users/by-user-type');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('activeUsersByTypeChart').getContext('2d');
    
    // Group data by month
    const months = [...new Set(data.map(d => d.month))].sort();
    const userTypes = [...new Set(data.map(d => d.user_type))];
    
    const datasets = userTypes.map((type, index) => {
        const typeData = months.map(month => {
            const row = data.find(d => d.month === month && d.user_type === type);
            return row ? row.active_users : 0;
        });
        
        return {
            label: type,
            data: typeData,
            backgroundColor: index === 0 ? colors.primary + '80' : colors.warning + '80',
            borderColor: index === 0 ? colors.primary : colors.warning,
            borderWidth: 2
        };
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months.map(m => formatMonth(m)),
            datasets: datasets
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
                    },
                    stacked: false
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Active Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    stacked: false
                }
            }
        }
    });
}

// Collections by Privacy (Public vs Private)
async function loadCollectionsPrivacyChart() {
    const data = await fetchData('collections/created-by-privacy');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('collectionsPrivacyChart').getContext('2d');
    
    // Group data by month
    const months = [...new Set(data.map(d => d.month))].sort();
    const privacyTypes = [...new Set(data.map(d => d.privacy_type))];
    
    const datasets = privacyTypes.map((type, index) => {
        const typeData = months.map(month => {
            const row = data.find(d => d.month === month && d.privacy_type === type);
            return row ? row.collections_created : 0;
        });
        
        const colorMap = {
            'public': colors.success,
            'private': colors.info,
            'Not Set': '#999'
        };
        const color = colorMap[type.toLowerCase()] || chartColors[index];
        
        return {
            label: type,
            data: typeData,
            backgroundColor: color + '80',
            borderColor: color,
            borderWidth: 2
        };
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months.map(m => formatMonth(m)),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toLocaleString() + ' collections';
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
                    },
                    stacked: true
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Collections Created',
                        font: { size: 12, weight: 'bold' }
                    },
                    stacked: true
                }
            }
        }
    });
}

// =============================================================================
// ACTIVITY TYPE ANALYTICS
// =============================================================================

// Activity by Type Monthly Chart
async function loadActivityByTypeMonthlyChart() {
    const data = await fetchData('activity/by-type-monthly');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('activityByTypeMonthlyChart').getContext('2d');
    
    // Group data by month
    const months = [...new Set(data.map(d => d.month))].sort();
    const activityTypes = [...new Set(data.map(d => d.activity_type))];
    
    const datasets = activityTypes.map((type, index) => {
        const typeData = months.map(month => {
            const row = data.find(d => d.month === month && d.activity_type === type);
            return row ? row.unique_users : 0;
        });
        
        const colorMap = {
            'post': colors.primary,
            'comment': colors.success
        };
        const color = colorMap[type.toLowerCase()] || chartColors[index];
        
        return {
            label: type.charAt(0).toUpperCase() + type.slice(1) + 's',
            data: typeData,
            backgroundColor: color + '80',
            borderColor: color,
            borderWidth: 2
        };
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months.reverse().map(m => formatMonth(m)),
            datasets: datasets
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
                    },
                    stacked: true
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Unique Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    stacked: true,
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

// Activity Distribution Chart (Donut)
async function loadActivityDistributionChart() {
    const data = await fetchData('activity/distribution-current');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('activityDistributionChart').getContext('2d');
    
    const labels = data.map(d => d.activity_type.charAt(0).toUpperCase() + d.activity_type.slice(1) + 's');
    const values = data.map(d => d.unique_users);
    const percentages = data.map(d => d.percentage);
    
    const colorMap = {
        'Posts': colors.primary,
        'Comments': colors.success
    };
    const backgroundColors = labels.map(label => colorMap[label] || chartColors[labels.indexOf(label)]);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors,
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
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const percentage = percentages[context.dataIndex];
                            return label + ': ' + value.toLocaleString() + ' users (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Activity Intensity Levels Chart
async function loadActivityIntensityLevelsChart() {
    const data = await fetchData('activity/intensity-levels');
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('activityIntensityLevelsChart').getContext('2d');
    
    // Group data by month
    const months = [...new Set(data.map(d => d.month))].sort();
    const intensityLevels = ['Power User (20+)', 'Active User (10-19)', 'Regular User (5-9)', 'Casual User (1-4)'];
    
    const datasets = intensityLevels.map((level, index) => {
        const levelData = months.map(month => {
            const row = data.find(d => d.month === month && d.intensity_level === level);
            return row ? row.user_count : 0;
        });
        
        const colorMap = {
            'Power User (20+)': colors.danger,
            'Active User (10-19)': colors.warning,
            'Regular User (5-9)': colors.info,
            'Casual User (1-4)': colors.success
        };
        const color = colorMap[level] || chartColors[index];
        
        return {
            label: level,
            data: levelData,
            backgroundColor: color + '80',
            borderColor: color,
            borderWidth: 2
        };
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months.reverse().map(m => formatMonth(m)),
            datasets: datasets
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
                    },
                    stacked: true
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Users',
                        font: { size: 12, weight: 'bold' }
                    },
                    stacked: true,
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
// INITIALIZE DASHBOARD
// =============================================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Loading ChemLink Analytics Dashboard...');

    // Load all components
    loadSummaryCards();
    
    // Growth metrics
    loadNewUsersMonthlyChart();
    loadGrowthRateChart();
    loadLoginVelocityChart();
    loadUniqueIdentitiesChart();
    loadDAUChart();
    loadMAUChart();
    loadMAUByCountryChart();
    loadDAUComprehensiveChart();
    loadMAUComprehensiveChart();
    loadActiveUsersByTypeChart();
    
    // Engagement metrics
    loadPostFrequencyChart();
    loadEngagementRateChart();
    loadContentTypeChart();
    loadActivePostersChart();
    
    // Activity type analytics
    loadActivityByTypeMonthlyChart();
    loadActivityDistributionChart();
    loadActivityIntensityLevelsChart();
    
    // Funnel analytics
    loadAccountFunnelChart();
    
    // Finder search analytics
    loadFinderSearchesChart();
    loadFinderIntentsChart();
    loadFinderEngagementChart();
    
    // Collections feature engagement
    loadProfileAdditionsChart();
    loadCollectionsCreatedChart();
    loadCollectionsSharedChart();
    loadCollectionsPrivacyChart();
    
    // Profile metrics
    loadProfileCompletionChart();
    loadProfileStatusChart();
    loadProfileFreshnessChart();
    
    // Talent marketplace intelligence
    loadTopCompaniesChart();
    loadTopRolesChart();
    loadEducationDistributionChart();
    loadGeographicDistributionChart();
    loadTopSkillsProjectsChart();
    
    // Tables
    loadTopPostsTable();

    console.log('Dashboard loaded successfully!');
});
