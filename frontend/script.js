// API Configuration
const API_BASE_URL = 'https://library-production-9ee7.up.railway.app';

let riskChart = null;
let probabilityChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    checkAPIHealth();
    loadMetrics();
    initializeCharts();
    setupFormSubmission();
    
    // Auto-refresh metrics every 30 seconds
    setInterval(loadMetrics, 30000);
});

// Check API health status
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        const statusBadge = document.getElementById('modelStatus');
        const statusIcon = document.getElementById('statusIcon');
        
        if (data.model_loaded) {
            statusBadge.className = 'badge bg-success';
            statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Model Active';
        } else {
            statusBadge.className = 'badge bg-danger';
            statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Model Unavailable';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        const statusBadge = document.getElementById('modelStatus');
        statusBadge.className = 'badge bg-danger';
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> API Offline';
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
                parseFloat(data.model_info.test_f1_score).toFixed(4) || '-';
            document.getElementById('rocAuc').textContent = 
                parseFloat(data.model_info.test_roc_auc).toFixed(4) || '-';
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
                    '#10b981',
                    '#f59e0b',
                    '#ef4444'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Probability Gauge Chart
    const probCtx = document.getElementById('probabilityGauge').getContext('2d');
    probabilityChart = new Chart(probCtx, {
        type: 'doughnut',
        data: {
            labels: ['Churn Probability', 'Remaining'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [
                    '#2563eb',
                    '#e5e7eb'
                ],
                borderWidth: 0,
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            }
        }
    });
}

// Update risk chart
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
        const prob = (avgProbability * 100) || 0;
        probabilityChart.data.datasets[0].data = [prob, 100 - prob];
        probabilityChart.update();
    }
}

// Setup form submission
function setupFormSubmission() {
    const form = document.getElementById('predictionForm');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await makePrediction();
    });
}

// Make prediction
async function makePrediction() {
    const form = document.getElementById('predictionForm');
    const formData = new FormData(form);
    
    // Convert form data to JSON
    const data = {};
    formData.forEach((value, key) => {
        if (key === 'SeniorCitizen' || key === 'tenure') {
            data[key] = parseInt(value);
        } else if (key === 'MonthlyCharges') {
            data[key] = parseFloat(value);
        } else {
            data[key] = value;
        }
    });
    
    // Show loading spinner
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Prediction failed');
        }
        
        const result = await response.json();
        displayPredictionResult(result);
        
        // Refresh metrics
        await loadMetrics();
        
    } catch (error) {
        console.error('Prediction error:', error);
        showError('Prediction failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display prediction result
function displayPredictionResult(result) {
    const resultCard = document.getElementById('resultCard');
    const resultDiv = document.getElementById('predictionResult');
    
    const willChurn = result.churn_prediction === 1;
    const probability = (result.churn_probability * 100).toFixed(2);
    const riskLevel = result.risk_level;
    
    let riskBadgeClass = '';
    if (riskLevel === 'low') riskBadgeClass = 'risk-low';
    else if (riskLevel === 'medium') riskBadgeClass = 'risk-medium';
    else riskBadgeClass = 'risk-high';
    
    resultDiv.innerHTML = `
        <div class="text-center mb-4">
            <i class="bi bi-${willChurn ? 'x-circle' : 'check-circle'} text-${willChurn ? 'danger' : 'success'}" style="font-size: 4rem;"></i>
            <h3 class="mt-3">${willChurn ? 'High Churn Risk' : 'Low Churn Risk'}</h3>
            <p class="text-muted">Customer ID: ${result.customer_id}</p>
        </div>
        
        <div class="row mb-3">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>Churn Probability</span>
                    <strong>${probability}%</strong>
                </div>
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar bg-${riskLevel === 'low' ? 'success' : riskLevel === 'medium' ? 'warning' : 'danger'}" 
                         role="progressbar" 
                         style="width: ${probability}%" 
                         aria-valuenow="${probability}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        ${probability}%
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alert alert-${riskLevel === 'low' ? 'success' : riskLevel === 'medium' ? 'warning' : 'danger'} mb-3">
            <strong>Risk Level:</strong> 
            <span class="risk-badge ${riskBadgeClass}">
                ${riskLevel.toUpperCase()}
            </span>
        </div>
        
        <div class="card bg-light">
            <div class="card-body">
                <h6 class="card-title">Recommended Actions:</h6>
                <ul class="mb-0">
                    ${getRecommendations(riskLevel)}
                </ul>
            </div>
        </div>
        
        <small class="text-muted d-block mt-3">
            <i class="bi bi-clock"></i> Predicted at: ${new Date(result.timestamp).toLocaleString()}
        </small>
    `;
    
    resultCard.style.display = 'block';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Get recommendations based on risk level
function getRecommendations(riskLevel) {
    const recommendations = {
        low: [
            '<li>Continue monitoring customer engagement</li>',
            '<li>Maintain current service quality</li>',
            '<li>Consider loyalty rewards program</li>'
        ],
        medium: [
            '<li>Reach out for feedback survey</li>',
            '<li>Offer service upgrade or bundle deals</li>',
            '<li>Review customer support interactions</li>',
            '<li>Consider targeted retention campaign</li>'
        ],
        high: [
            '<li><strong>URGENT:</strong> Contact customer immediately</li>',
            '<li>Offer personalized retention incentives</li>',
            '<li>Schedule account review meeting</li>',
            '<li>Consider contract upgrade options</li>',
            '<li>Escalate to retention specialist team</li>'
        ]
    };
    
    return recommendations[riskLevel].join('');
}

// Show loading spinner
function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

// Hide loading spinner
function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

// Show error message
function showError(message) {
    alert(message);
}

// Export to CSV functionality
function exportPredictions() {
    // This would typically fetch all predictions and export to CSV
    alert('Export functionality would be implemented here');
}
