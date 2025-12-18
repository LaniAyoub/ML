# Production Deployment Guide

## 📋 Pre-Deployment Checklist

### 1. Infrastructure Requirements

**Minimum Server Specifications:**
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 20.04 LTS / 22.04 LTS
- **Network**: Static IP with open ports 80, 443

**Recommended for Production:**
- **CPU**: 8 cores
- **RAM**: 16 GB
- **Storage**: 100 GB SSD
- **Load Balancer**: Nginx/HAProxy
- **CDN**: CloudFlare/AWS CloudFront

### 2. Domain & SSL Setup

#### Purchase Domain
- Register domain from GoDaddy, Namecheap, or Google Domains
- Point DNS A record to your server IP

#### SSL Certificate (Let's Encrypt - Free)
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (runs twice daily)
sudo systemctl status certbot.timer
```

### 3. Server Setup

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Install monitoring tools
sudo apt install htop iotop nethogs
```

#### Firewall Configuration
```bash
# Enable UFW
sudo ufw enable

# Allow SSH (change 22 if using custom port)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow monitoring (restrict to your IP)
sudo ufw allow from YOUR_IP_ADDRESS to any port 9090 proto tcp
sudo ufw allow from YOUR_IP_ADDRESS to any port 3001 proto tcp

# Check status
sudo ufw status verbose
```

## 🚀 Deployment Steps

### Step 1: Clone Repository to Server

```bash
# SSH into server
ssh user@your-server-ip

# Clone repository
git clone https://github.com/ahmed-khalil-omrani/Churn_predection.git
cd Churn_predection
```

### Step 2: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with production values
nano .env
```

**Critical Variables to Change:**
```env
SECRET_KEY=<generate-with: openssl rand -hex 32>
API_KEY=<generate-with: openssl rand -hex 32>
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
GF_SECURITY_ADMIN_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
```

### Step 3: Update Configuration Files

#### Update `nginx/nginx.conf`
Replace `yourdomain.com` with your actual domain on lines:
- Line 51: `server_name yourdomain.com www.yourdomain.com;`
- Line 63: `server_name yourdomain.com www.yourdomain.com;`

#### Update `frontend/script.js`
```javascript
// Change from localhost to production domain
const API_BASE_URL = 'https://yourdomain.com/api';
```

### Step 4: Prepare SSL Certificates

**Option A: Let's Encrypt (Recommended)**
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate certificates (do this AFTER DNS is configured)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/*.pem
```

**Option B: Self-Signed (Testing Only)**
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out nginx/ssl/fullchain.pem \
    -subj "/CN=yourdomain.com"
```

### Step 5: Update Production Requirements

Add production dependencies to `requirements.txt`:
```bash
# Add these lines
gunicorn==21.2.0
redis==5.0.1
python-dotenv==1.0.0
sentry-sdk[fastapi]==1.39.0
slowapi==0.1.9
```

### Step 6: Build and Deploy

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 7: Verify Deployment

```bash
# Check all containers are running
docker-compose -f docker-compose.prod.yml ps

# Test API health
curl https://yourdomain.com/api/health

# Test SSL
curl -I https://yourdomain.com

# Check certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## 🔒 Security Hardening

### 1. API Security

#### Add Rate Limiting to FastAPI
Create `src/middleware/rate_limit.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

#### Add API Key Authentication
Update `src/predict_api.py`:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not os.getenv("API_KEY_ENABLED", "false").lower() == "true":
        return None
    
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### 2. Database Security (Optional)

If adding PostgreSQL for logging:
```bash
# In docker-compose.prod.yml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: churn_db
    POSTGRES_USER: churn_user
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### 3. Secrets Management

**Option A: Docker Secrets**
```bash
# Create secrets
echo "my-secret-api-key" | docker secret create api_key -

# Use in docker-compose
secrets:
  api_key:
    external: true
```

**Option B: HashiCorp Vault**
```bash
docker run -d --name=vault -p 8200:8200 vault:latest
```

### 4. Regular Updates

```bash
# Create update script
cat > update.sh << 'EOF'
#!/bin/bash
git pull
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --build
docker system prune -f
EOF

chmod +x update.sh

# Run weekly via cron
crontab -e
# Add: 0 2 * * 0 cd /path/to/Churn_predection && ./update.sh
```

## 📊 Monitoring & Alerting

### 1. Access Monitoring Dashboards

- **Prometheus**: https://yourdomain.com:9090
- **Grafana**: https://yourdomain.com:3001
- **API Docs**: https://yourdomain.com/api/docs

### 2. Set Up Grafana Alerts

1. Login to Grafana (https://yourdomain.com:3001)
2. Navigate to Alerting → Notification channels
3. Add Email/Slack/PagerDuty integration
4. Create alerts for:
   - API response time > 2s
   - Error rate > 5%
   - CPU usage > 80%
   - Memory usage > 90%

### 3. Log Management

```bash
# Centralized logging
docker-compose -f docker-compose.prod.yml logs --tail=100 -f

# Rotate logs (add to /etc/logrotate.d/churn-app)
/path/to/Churn_predection/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

### 4. Integrate Sentry for Error Tracking

```python
# In src/predict_api.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
    )
```

## 🔄 Backup Strategy

### 1. Automated Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/churn_app"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup models
tar -czf $BACKUP_DIR/models_$DATE.tar.gz models/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Backup database volumes
docker run --rm -v churn_predection_prometheus_data:/data \
    -v $BACKUP_DIR:/backup alpine \
    tar -czf /backup/prometheus_$DATE.tar.gz -C /data .

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/Churn_predection/backup.sh
```

### 2. Off-Site Backups

```bash
# Sync to S3 (install awscli first)
aws s3 sync /backups/churn_app s3://your-backup-bucket/churn-app/

# Or use rsync to remote server
rsync -avz /backups/churn_app user@backup-server:/backups/
```

## 🧪 Testing Production Deployment

### 1. Smoke Tests

```bash
# Test all endpoints
bash -c 'for endpoint in /health /metrics /model-info; do
    echo "Testing $endpoint"
    curl -s https://yourdomain.com/api$endpoint | jq
done'
```

### 2. Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API performance
ab -n 1000 -c 10 https://yourdomain.com/api/health

# Or use wrk
wrk -t12 -c400 -d30s https://yourdomain.com/api/health
```

### 3. Security Scan

```bash
# Install security scanner
pip install safety

# Check for vulnerabilities
safety check -r requirements.txt

# SSL test
testssl.sh https://yourdomain.com
```

## 📱 Client Usage Examples

### cURL
```bash
curl -X POST https://yourdomain.com/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 1,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.35,
    "TotalCharges": "70.35"
  }'
```

### Python
```python
import requests

response = requests.post(
    "https://yourdomain.com/api/predict",
    headers={"X-API-Key": "your-api-key"},
    json={
        "gender": "Female",
        "SeniorCitizen": 0,
        # ... rest of data
    }
)
print(response.json())
```

## 🚨 Troubleshooting

### Common Issues

**1. Containers Won't Start**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Check ports
sudo netstat -tulpn | grep -E ':80|:443|:8000'
```

**2. SSL Certificate Issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate expiry
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | \
    openssl x509 -noout -dates
```

**3. High Memory Usage**
```bash
# Check container stats
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Clear old logs
truncate -s 0 logs/*.log
```

**4. API Not Responding**
```bash
# Check API container
docker exec -it churn_api_prod bash

# Test internally
curl http://localhost:8000/health

# Check gunicorn workers
ps aux | grep gunicorn
```

## 📞 Support & Maintenance

### Monitoring Checklist (Daily)
- [ ] Check Grafana dashboards
- [ ] Review error logs
- [ ] Verify backup completion
- [ ] Check SSL certificate expiry (30 days warning)
- [ ] Monitor disk space

### Maintenance Windows
Schedule downtime for:
- Security updates (monthly)
- Model retraining (weekly/monthly)
- Database maintenance (monthly)
- Certificate renewal (automated, verify quarterly)

### Incident Response
1. Check monitoring alerts
2. Review logs: `docker-compose logs -f`
3. Rollback if needed: `git checkout <previous-commit>`
4. Document incident
5. Update runbook

## 🎯 Performance Optimization

### 1. Enable Caching
```python
# Add Redis caching in predict_api.py
import redis
cache = redis.Redis(host='redis', port=6379, db=0)

@app.post("/predict")
async def predict_churn(data: CustomerData):
    cache_key = hash(str(data.dict()))
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... prediction logic
    cache.setex(cache_key, 3600, json.dumps(result))
```

### 2. Database Connection Pooling
Use SQLAlchemy with connection pooling for production logging.

### 3. CDN Integration
Configure CloudFlare or AWS CloudFront for static assets.

### 4. Horizontal Scaling
```bash
# Scale API containers
docker-compose -f docker-compose.prod.yml up -d --scale api=4
```

---

**Deployment Date**: _________________
**Deployed By**: _________________
**Next Review**: _________________
