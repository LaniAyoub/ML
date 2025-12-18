# Production Deployment Script for Windows PowerShell
# Churn Prediction Application

param(
    [string]$Domain = "yourdomain.com",
    [string]$Email = "admin@yourdomain.com"
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Churn Prediction - Production Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Functions
function Log-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Green
}

function Log-Warn($message) {
    Write-Host "[WARN] $message" -ForegroundColor Yellow
}

function Log-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

function Check-Requirements {
    Log-Info "Checking system requirements..."
    
    # Check Docker
    try {
        docker --version | Out-Null
        Log-Info "Docker installed ✓"
    } catch {
        Log-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    # Check Docker Compose
    try {
        docker compose version | Out-Null
        Log-Info "Docker Compose installed ✓"
    } catch {
        Log-Error "Docker Compose is not available."
        exit 1
    }
    
    # Check disk space
    $drive = Get-PSDrive C
    $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
    if ($freeSpaceGB -lt 10) {
        Log-Warn "Low disk space: $freeSpaceGB GB free. At least 10GB recommended."
    } else {
        Log-Info "Disk space: $freeSpaceGB GB free ✓"
    }
}

function Setup-Environment {
    Log-Info "Setting up environment..."
    
    # Check if .env exists
    if (-not (Test-Path .env)) {
        Log-Info "Creating .env file from example..."
        Copy-Item .env.example .env
        
        # Generate random secrets (Windows compatible)
        $SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        $API_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        $REDIS_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
        $GF_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 12 | ForEach-Object {[char]$_})
        
        # Update .env with generated values
        (Get-Content .env) -replace 'change-this-to-a-random-secret-key-in-production', $SECRET_KEY | Set-Content .env
        (Get-Content .env) -replace 'your-secure-api-key-here', $API_KEY | Set-Content .env
        (Get-Content .env) -replace 'change-this-password', $REDIS_PASSWORD | Set-Content .env
        (Get-Content .env) -replace 'change-this-secure-password', $GF_PASSWORD | Set-Content .env
        
        Log-Info "Generated secure random keys ✓"
        
        # Save credentials
        $credContent = @"
API_KEY=$API_KEY
GRAFANA_PASSWORD=$GF_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
Generated: $(Get-Date)
"@
        $credContent | Out-File -FilePath .credentials -Encoding UTF8
        Log-Info "Credentials saved to .credentials (keep this file secure!)"
    } else {
        Log-Info ".env file already exists ✓"
    }
}

function Setup-SSL {
    Log-Info "Setting up SSL certificates..."
    
    # Create SSL directory
    New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null
    
    # Generate self-signed certificate for testing
    Log-Warn "Generating self-signed certificates for testing..."
    Log-Warn "Replace with proper certificates in production!"
    
    # Use OpenSSL if available, otherwise warn
    try {
        & openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
            -keyout nginx\ssl\privkey.pem `
            -out nginx\ssl\fullchain.pem `
            -subj "/CN=$Domain/O=Churn Prediction/C=US" 2>$null
        
        Log-Info "Self-signed certificates generated ✓"
    } catch {
        Log-Warn "OpenSSL not found. You'll need to provide SSL certificates manually."
        Log-Warn "Place them in: nginx\ssl\fullchain.pem and nginx\ssl\privkey.pem"
    }
}

function Update-Configs {
    Log-Info "Updating configuration files..."
    
    # Update nginx.conf with domain
    if (Test-Path nginx\nginx.conf) {
        (Get-Content nginx\nginx.conf) -replace 'yourdomain.com', $Domain | Set-Content nginx\nginx.conf
        Log-Info "Updated nginx.conf with domain: $Domain ✓"
    }
    
    # Update frontend script.js
    if (Test-Path frontend\script.js) {
        (Get-Content frontend\script.js) -replace 'http://localhost:8000', "https://$Domain/api" | Set-Content frontend\script.js
        Log-Info "Updated frontend API URL ✓"
    }
}

function Build-Images {
    Log-Info "Building Docker images..."
    
    try {
        docker compose -f docker-compose.prod.yml build --no-cache
        Log-Info "Docker images built successfully ✓"
    } catch {
        Log-Error "Failed to build Docker images"
        throw
    }
}

function Start-Services {
    Log-Info "Starting services..."
    
    try {
        docker compose -f docker-compose.prod.yml up -d
        Log-Info "Services started successfully ✓"
    } catch {
        Log-Error "Failed to start services"
        throw
    }
    
    # Wait for services to be healthy
    Log-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 10
    
    # Check service status
    docker compose -f docker-compose.prod.yml ps
}

function Verify-Deployment {
    Log-Info "Verifying deployment..."
    
    # Test API health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Log-Info "API health check passed ✓"
        }
    } catch {
        Log-Error "API health check failed"
        Log-Info "Checking logs..."
        docker compose -f docker-compose.prod.yml logs api --tail=50
    }
    
    # Display access information
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "Deployment Complete!" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Access your application:" -ForegroundColor Green
    Write-Host "   Frontend:    https://$Domain"
    Write-Host "   API Docs:    https://$Domain/api/docs"
    Write-Host "   Grafana:     https://$Domain:3001"
    Write-Host "   Prometheus:  https://$Domain:9090"
    Write-Host ""
    Write-Host "🔑 Credentials saved in: .credentials" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Test the frontend at https://$Domain"
    Write-Host "   2. Check logs: docker compose -f docker-compose.prod.yml logs -f"
    Write-Host "   3. Setup monitoring alerts in Grafana"
    Write-Host "   4. Configure firewall rules"
    Write-Host "   5. Setup automated backups"
    Write-Host ""
}

function Cleanup {
    Log-Info "Cleaning up old containers and images..."
    docker system prune -f
    Log-Info "Cleanup complete ✓"
}

# Main deployment flow
try {
    Log-Info "Starting deployment process..."
    
    Check-Requirements
    Setup-Environment
    Setup-SSL
    Update-Configs
    Build-Images
    Start-Services
    Verify-Deployment
    Cleanup
    
    Log-Info "Deployment completed successfully! 🎉"
} catch {
    Log-Error "Deployment failed: $_"
    Log-Error "Check logs with: docker compose -f docker-compose.prod.yml logs"
    exit 1
}
