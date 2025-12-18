// API Configuration
const API_BASE_URL = window.location.origin;

// Theme colors matching new design
const THEME_COLORS = {
    primary: '#2563eb',
    primaryDark: '#1e40af',
    secondary: '#10b981',
    accent: '#f59e0b',
    danger: '#ef4444',
    warning: '#f59e0b',
    success: '#10b981',
    lowRisk: '#10b981',
    mediumRisk: '#f59e0b',
    highRisk: '#ef4444'
};

let riskChart = null;
let probabilityChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    checkAPIHealth();
    loadMetrics();
    initializeCharts();
    setupFormSubmission();
    setupSidebarToggle();
    setupNavigation();
    
    // Auto-refresh metrics every 30 seconds
    setInterval(() => {
        loadMetrics();
    }, 30000);
});

// Sidebar toggle for mobile
function setupSidebarToggle() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
        });
    }
    
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        });
    }
}

// Navigation between pages
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Close mobile sidebar
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            if (sidebar) sidebar.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            
            // Handle page navigation
            const page = link.dataset.page;
            console.log(`Navigating to: ${page}`);
        });
    });
}

// Check API health status
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        const statusIndicator = document.getElementById('modelStatus');
        const statusText = document.getElementById('statusText');
        
        if (response.ok && data.model_loaded) {
            statusIndicator.classList.remove('offline');
            statusText.textContent = 'Model Active';
        } else {
            statusIndicator.classList.add('offline');
            statusText.textContent = 'Model Unavailable';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        const statusIndicator = document.getElementById('modelStatus');
        const statusText = document.getElementById('statusText');
        statusIndicator.classList.add('offline');
        statusText.textContent = 'API Offline';
    }
}

// Load metrics from API
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics`);
        const data = await response.json();
        
        // Update stats cards
        document.getElementById('totalPredictions').textContent = data.total_predictions || 0;
        document.getElementById('lowRisk').textContent = data.predictions_by_risk.low || 0;
        document.getElementById('mediumRisk').textContent = data.predictions_by_risk.medium || 0;
        document.getElementById('highRisk').textContent = data.predictions_by_risk.high || 0;
        
        // Update model info
        if (data.model_info) {
            document.getElementById('f1Score').textContent = 
                parseFloat(data.model_info.test_f1_score).toFixed(3) || '-';
            document.getElementById('rocAuc').textContent = 
                parseFloat(data.model_info.test_roc_auc).toFixed(3) || '-';
        }
        
        // Update charts
        updateRiskChart(data.predictions_by_risk);
        updateProbabilityGauge(data.average_churn_probability);
        
    } catch (error) {
        console.error('Failed to load metrics:', error);
    }
}

// Initialize charts
function initializeCharts() {
    // Risk Distribution Chart
    const riskCtx = document.getElementById('riskChart').getContext('2d');
    riskChart = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    THEME_COLORS.lowRisk,
                    THEME_COLORS.mediumRisk,
                    THEME_COLORS.highRisk
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            family: 'Inter',
                            size: 12,
                            weight: '500'
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                title: {
                    display: true,
                    text: 'Risk Distribution',
                    font: {
                        family: 'Inter',
                        size: 14,
                        weight: '600'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    // Probability Gauge Chart
    const probCtx = document.getElementById('probabilityGauge').getContext('2d');
    probabilityChart = new Chart(probCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Average Churn Probability',
                data: [],
                borderColor: THEME_COLORS.primary,
                backgroundColor: THEME_COLORS.primary + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: THEME_COLORS.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Probability Trend',
                    font: {
                        family: 'Inter',
                        size: 14,
                        weight: '600'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        font: {
                            family: 'Inter',
                            size: 11
                        },
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    },
                    grid: {
                        color: '#e2e8f0'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Update risk distribution chart
function updateRiskChart(riskData) {
    if (riskChart) {
        riskChart.data.datasets[0].data = [
            riskData.low || 0,
            riskData.medium || 0,
            riskData.high || 0
        ];
        riskChart.update();
    }
}

// Update probability gauge
function updateProbabilityGauge(avgProbability) {
    if (probabilityChart) {
        const now = new Date();
        const timeLabel = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // Keep last 10 data points
        if (probabilityChart.data.labels.length > 10) {
            probabilityChart.data.labels.shift();
            probabilityChart.data.datasets[0].data.shift();
        }
        
        probabilityChart.data.labels.push(timeLabel);
        probabilityChart.data.datasets[0].data.push(avgProbability || 0);
        probabilityChart.update();
    }
}

// Setup form submission
function setupFormSubmission() {
    const form = document.getElementById('predictionForm');
    const predictBtn = document.getElementById('predictBtn');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        showLoading(true);
        predictBtn.disabled = true;
        
        // Clear previous errors
        clearFormErrors();
        
        // Collect form data
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        try {
            const response = await fetch(`${API_BASE_URL}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Prediction failed');
            }
            
            const result = await response.json();
            displayPredictionResult(result);
            
            // Refresh metrics after prediction
            await loadMetrics();
            
        } catch (error) {
            console.error('Prediction error:', error);
            showError('Failed to get prediction: ' + error.message);
        } finally {
            showLoading(false);
            predictBtn.disabled = false;
        }
    });
}

// Display prediction result
function displayPredictionResult(result) {
    const resultCard = document.getElementById('resultCard');
    const resultDiv = document.getElementById('predictionResult');
    
    const prediction = result.churn_prediction;
    const probability = result.churn_probability;
    const riskLevel = result.risk_level;
    
    let riskClass = 'low';
    let riskText = 'Low Risk';
    let riskIcon = 'check-circle-fill';
    
    if (riskLevel === 'Medium') {
        riskClass = 'medium';
        riskText = 'Medium Risk';
        riskIcon = 'exclamation-triangle-fill';
    } else if (riskLevel === 'High') {
        riskClass = 'high';
        riskText = 'High Risk';
        riskIcon = 'x-circle-fill';
    }
    
    resultDiv.innerHTML = `
        <div class="text-center mb-4">
            <div class="risk-badge ${riskClass}">
                <i class="bi bi-${riskIcon}"></i>
                ${riskText}
            </div>
        </div>
        
        <div class="probability-display">
            <div class="probability-label">Churn Probability</div>
            <div class="probability-value">${(probability * 100).toFixed(1)}%</div>
        </div>
        
        <div class="row text-center mt-4">
            <div class="col-6">
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    Prediction
                </div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary);">
                    ${prediction === 1 ? 'Will Churn' : 'Will Stay'}
                </div>
            </div>
            <div class="col-6">
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    Confidence
                </div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary);">
                    ${(Math.max(probability, 1 - probability) * 100).toFixed(1)}%
                </div>
            </div>
        </div>
        
        <div style="margin-top: 1.5rem; padding: 1rem; background: var(--main-bg); border-radius: 8px;">
            <h5 style="font-size: 0.938rem; font-weight: 600; margin-bottom: 0.75rem;">
                Recommendation
            </h5>
            <p style="font-size: 0.875rem; color: var(--text-secondary); margin: 0;">
                ${getRecommendation(riskLevel)}
            </p>
        </div>
    `;
    
    resultCard.style.display = 'block';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Get recommendation based on risk level
function getRecommendation(riskLevel) {
    const recommendations = {
        'Low': 'Customer shows strong retention indicators. Continue providing excellent service and consider loyalty rewards.',
        'Medium': 'Customer shows some churn signals. Proactively reach out with personalized offers and address potential concerns.',
        'High': 'Immediate intervention recommended. Contact customer urgently with retention offers and investigate dissatisfaction factors.'
    };
    return recommendations[riskLevel] || 'Monitor customer engagement closely.';
}

// Show/hide loading overlay
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

// Show error message
function showError(message) {
    const resultCard = document.getElementById('resultCard');
    const resultDiv = document.getElementById('predictionResult');
    
    resultDiv.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <strong>Error:</strong> ${message}
        </div>
    `;
    
    resultCard.style.display = 'block';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Clear form errors
function clearFormErrors() {
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(control => {
        control.classList.remove('form-error');
    });
    
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.remove());
}

// Show form validation error
function showFormError(fieldName, message) {
    const field = document.querySelector(`[name="${fieldName}"]`);
    if (field) {
        field.classList.add('form-error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }
}
