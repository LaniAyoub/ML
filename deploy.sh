#!/bin/bash

# Production Deployment Script for Churn Prediction Application
# This script automates the deployment process

set -e  # Exit on error

echo "================================================"
echo "Churn Prediction - Production Deployment"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${DOMAIN:-yourdomain.com}"
EMAIL="${EMAIL:-admin@yourdomain.com}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed."
        exit 1
    fi
    
    # Check disk space (need at least 10GB free)
    FREE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [ "$FREE_SPACE" -lt 10485760 ]; then
        log_warn "Low disk space. At least 10GB recommended."
    fi
    
    log_info "Requirements check passed ✓"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Check if .env exists
    if [ ! -f .env ]; then
        log_info "Creating .env file from example..."
        cp .env.example .env
        
        # Generate random secrets
        SECRET_KEY=$(openssl rand -hex 32)
        API_KEY=$(openssl rand -hex 32)
        REDIS_PASSWORD=$(openssl rand -hex 16)
        GF_PASSWORD=$(openssl rand -base64 12)
        
        # Update .env with generated values
        sed -i "s/change-this-to-a-random-secret-key-in-production/$SECRET_KEY/" .env
        sed -i "s/your-secure-api-key-here/$API_KEY/" .env
        sed -i "s/change-this-password/$REDIS_PASSWORD/" .env
        sed -i "s/change-this-secure-password/$GF_PASSWORD/" .env
        
        log_info "Generated secure random keys ✓"
        log_warn "Please update the domain name in .env file"
        
        # Save credentials
        cat > .credentials << EOF
API_KEY=$API_KEY
GRAFANA_PASSWORD=$GF_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
Generated: $(date)
EOF
        chmod 600 .credentials
        log_info "Credentials saved to .credentials (keep this file secure!)"
    else
        log_info ".env file already exists ✓"
    fi
}

setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p nginx/ssl
    
    # Check if Let's Encrypt certificates exist
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        log_info "Found existing Let's Encrypt certificates"
        sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
        sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
        sudo chmod 644 nginx/ssl/*.pem
        log_info "SSL certificates copied ✓"
    else
        log_warn "No Let's Encrypt certificates found"
        read -p "Do you want to generate self-signed certificates for testing? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout nginx/ssl/privkey.pem \
                -out nginx/ssl/fullchain.pem \
                -subj "/CN=$DOMAIN/O=Churn Prediction/C=US"
            log_info "Self-signed certificates generated ✓"
            log_warn "Remember to replace with proper certificates in production!"
        fi
    fi
}

update_configs() {
    log_info "Updating configuration files..."
    
    # Update nginx.conf with domain
    if [ -f nginx/nginx.conf ]; then
        sed -i "s/yourdomain.com/$DOMAIN/g" nginx/nginx.conf
        log_info "Updated nginx.conf with domain: $DOMAIN ✓"
    fi
    
    # Update frontend script.js
    if [ -f frontend/script.js ]; then
        sed -i "s|http://localhost:8000|https://$DOMAIN/api|g" frontend/script.js
        log_info "Updated frontend API URL ✓"
    fi
}

build_images() {
    log_info "Building Docker images..."
    
    docker compose -f docker-compose.prod.yml build --no-cache
    
    if [ $? -eq 0 ]; then
        log_info "Docker images built successfully ✓"
    else
        log_error "Failed to build Docker images"
        exit 1
    fi
}

start_services() {
    log_info "Starting services..."
    
    docker compose -f docker-compose.prod.yml up -d
    
    if [ $? -eq 0 ]; then
        log_info "Services started successfully ✓"
    else
        log_error "Failed to start services"
        exit 1
    fi
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service status
    docker compose -f docker-compose.prod.yml ps
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Test API health
    if curl -f -k https://localhost/api/health &> /dev/null; then
        log_info "API health check passed ✓"
    else
        log_error "API health check failed"
        log_info "Checking logs..."
        docker compose -f docker-compose.prod.yml logs api --tail=50
    fi
    
    # Display access information
    echo ""
    echo "================================================"
    echo "Deployment Complete!"
    echo "================================================"
    echo ""
    echo "🌐 Access your application:"
    echo "   Frontend:    https://$DOMAIN"
    echo "   API Docs:    https://$DOMAIN/api/docs"
    echo "   Grafana:     https://$DOMAIN:3001"
    echo "   Prometheus:  https://$DOMAIN:9090"
    echo ""
    echo "🔑 Credentials saved in: .credentials"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Test the frontend at https://$DOMAIN"
    echo "   2. Check logs: docker compose -f docker-compose.prod.yml logs -f"
    echo "   3. Setup monitoring alerts in Grafana"
    echo "   4. Configure firewall rules"
    echo "   5. Setup automated backups"
    echo ""
}

cleanup() {
    log_info "Cleaning up old containers and images..."
    docker system prune -f
    log_info "Cleanup complete ✓"
}

# Main deployment flow
main() {
    log_info "Starting deployment process..."
    
    check_requirements
    setup_environment
    setup_ssl
    update_configs
    build_images
    start_services
    verify_deployment
    cleanup
    
    log_info "Deployment completed successfully! 🎉"
}

# Run main function
main
