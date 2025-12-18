# Churn Prediction - Quick Production Deployment Summary

## 🚀 What You Need to Do for Real Production Deployment

### 1. **Infrastructure Setup** (Choose One)

#### Option A: Cloud Provider (Recommended)
- **AWS**: Use EC2 (t3.large), RDS, ELB, Route53
- **Google Cloud**: Compute Engine, Cloud SQL, Load Balancer
- **Azure**: VM, Azure Database, Application Gateway
- **DigitalOcean**: Droplet ($40/month), Managed Database, Load Balancer

**Minimum Instance**: 4 vCPU, 8GB RAM, 50GB SSD

#### Option B: VPS Provider
- **Linode**, **Vultr**, **Hetzner**
- Cost: ~$40-80/month
- Manual setup required

#### Option C: Platform as a Service (Easiest)
- **Heroku**, **Railway**, **Render.com**, **Fly.io**
- Simplified deployment
- Higher cost per resource

### 2. **Domain & DNS** (~$15/year)
1. Buy domain from Namecheap/GoDaddy/Google Domains
2. Point DNS A record to your server IP
3. Add www CNAME record

### 3. **SSL Certificate** (Free with Let's Encrypt)
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 4. **Required Changes to Your Code**

#### A. Update `frontend/script.js` (Line 2)
```javascript
// CHANGE THIS:
const API_BASE_URL = 'http://localhost:8000';

// TO THIS:
const API_BASE_URL = 'https://yourdomain.com/api';
```

#### B. Update `nginx/nginx.conf` (Lines 51, 63)
```nginx
server_name yourdomain.com www.yourdomain.com;
```

#### C. Create `.env` file
```bash
cp .env.example .env
# Then edit .env with your production values
```

#### D. Add to `requirements.txt`
```
gunicorn==21.2.0
redis==5.0.1
python-dotenv==1.0.0
slowapi==0.1.9
sentry-sdk[fastapi]==1.39.0
```

#### E. Update `src/predict_api.py` - Add Security
```python
# Add at the top
import os
from dotenv import load_dotenv
load_dotenv()

# Add after CORS middleware
from src.security import setup_security, verify_api_key
setup_security(app)

# Protect prediction endpoint
@app.post("/predict", dependencies=[Depends(verify_api_key)])
async def predict_churn(data: CustomerData):
    # ... existing code
```

### 5. **Deployment Commands**

```bash
# On your server
git clone https://github.com/ahmed-khalil-omrani/Churn_predection.git
cd Churn_predection

# Run automated deployment script
chmod +x deploy.sh
./deploy.sh

# Or manual deployment
docker compose -f docker-compose.prod.yml up -d --build
```

### 6. **Security Hardening**

```bash
# Firewall setup
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Disable password SSH (use keys only)
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd

# Setup fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 7. **Monitoring Setup**

Access these URLs after deployment:
- **Grafana**: https://yourdomain.com:3001 (admin/your-password)
- **Prometheus**: https://yourdomain.com:9090
- **API Docs**: https://yourdomain.com/api/docs

Setup alerts in Grafana for:
- API errors > 5%
- Response time > 2s
- CPU > 80%
- Memory > 90%

### 8. **Backup Strategy**

```bash
# Create backup script (already provided in repo)
chmod +x backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/Churn_predection/backup.sh
```

### 9. **CI/CD Pipeline** (Optional but Recommended)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/Churn_predection
            git pull
            docker compose -f docker-compose.prod.yml up -d --build
```

## 📋 Pre-Deployment Checklist

- [ ] Server/VPS purchased and configured
- [ ] Domain name purchased
- [ ] DNS A record pointing to server
- [ ] SSL certificate generated
- [ ] `.env` file created with production values
- [ ] `frontend/script.js` updated with domain
- [ ] `nginx/nginx.conf` updated with domain
- [ ] Production requirements added
- [ ] Security files created (`src/security.py`, `src/cache.py`)
- [ ] Firewall configured
- [ ] SSH key authentication enabled
- [ ] Monitoring dashboards configured
- [ ] Backup script scheduled
- [ ] Load testing completed
- [ ] Documentation updated

## 💰 Estimated Costs

| Item | Monthly Cost |
|------|--------------|
| VPS (4 vCPU, 8GB) | $40-80 |
| Domain (annual/12) | $1-2 |
| SSL Certificate | $0 (Let's Encrypt) |
| Backup Storage (100GB) | $5-10 |
| **Total** | **$45-90/month** |

## 🎯 Deployment Timeline

- **Day 1**: Infrastructure setup, domain purchase
- **Day 2**: Code updates, testing locally
- **Day 3**: Deploy to production, SSL setup
- **Day 4**: Monitoring setup, load testing
- **Day 5**: Documentation, team training

## 🆘 Quick Troubleshooting

**Problem**: Can't access website
- Check DNS: `nslookup yourdomain.com`
- Check firewall: `sudo ufw status`
- Check containers: `docker ps`

**Problem**: SSL errors
- Renew certificate: `sudo certbot renew`
- Check certificate: `sudo certbot certificates`

**Problem**: API slow
- Check resources: `docker stats`
- Scale API: `docker compose -f docker-compose.prod.yml up -d --scale api=4`
- Enable Redis caching

**Problem**: Out of memory
- Increase swap: `sudo fallocate -l 4G /swapfile`
- Upgrade server instance
- Optimize model size

## 📞 Support Resources

- **Deployment Guide**: `docs/PRODUCTION_DEPLOYMENT.md` (comprehensive 500+ line guide)
- **Architecture**: `docs/ARCHITECTURE.md`
- **API Docs**: https://yourdomain.com/api/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Docker**: https://docs.docker.com

---

**Ready to deploy?** Run: `bash deploy.sh`

**Need help?** Check `docs/PRODUCTION_DEPLOYMENT.md` for detailed step-by-step instructions.
