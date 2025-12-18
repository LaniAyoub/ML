# 🚀 PRODUCTION DEPLOYMENT - COMPLETE GUIDE

## What I've Done For You

I've created a **complete production-ready deployment setup** for your Churn Prediction application. Here's everything you need to know:

---

## 📦 NEW FILES CREATED (11 Files)

### 1. Environment & Configuration
- ✅ `.env.example` - Template with all production settings
- ✅ `.gitignore` - Excludes sensitive files from git
- ✅ `docker-compose.prod.yml` - Production orchestration with SSL, caching, monitoring

### 2. Docker & Infrastructure
- ✅ `Dockerfile.prod` - Optimized multi-stage production image
- ✅ `nginx/nginx.conf` - Full production Nginx with SSL, security headers, rate limiting

### 3. Security & Performance
- ✅ `src/security.py` - API key auth, rate limiting, security headers
- ✅ `src/cache.py` - Redis caching layer for predictions
- ✅ `requirements.prod.txt` - Production Python dependencies

### 4. Deployment Scripts
- ✅ `deploy.sh` - Automated Linux deployment script
- ✅ `deploy.ps1` - Automated Windows PowerShell deployment script

### 5. Documentation
- ✅ `docs/PRODUCTION_DEPLOYMENT.md` - **500+ line comprehensive guide**
- ✅ `PRODUCTION_GUIDE.md` - Quick reference summary
- ✅ `DEPLOYMENT_CHANGES.md` - Complete changelog and instructions

---

## 🔧 WHAT YOU NEED TO CHANGE

### **REQUIRED CHANGES:**

#### 1. Create `.env` File
```powershell
Copy-Item .env.example .env
# Then edit .env with your values
```

#### 2. Update `frontend\script.js` (Line 2)
```javascript
// CHANGE THIS:
const API_BASE_URL = 'http://localhost:8000';

// TO YOUR DOMAIN:
const API_BASE_URL = 'https://yourdomain.com/api';
```

#### 3. Update `nginx\nginx.conf` (Lines 51 & 63)
```nginx
# Replace with your actual domain:
server_name yourdomain.com www.yourdomain.com;
```

#### 4. Add Production Dependencies
Merge `requirements.prod.txt` into your `requirements.txt`:
```
gunicorn==21.2.0
redis==5.0.1
python-dotenv==1.0.0
slowapi==0.1.9
sentry-sdk[fastapi]==1.39.0
```

---

## 🎯 DEPLOYMENT OPTIONS

### **Option 1: Automated Deployment (RECOMMENDED)**

#### On Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

#### On Windows PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy.ps1 -Domain "yourdomain.com" -Email "admin@yourdomain.com"
```

### **Option 2: Manual Deployment**

```powershell
# 1. Create environment file
Copy-Item .env.example .env
# Edit .env with your production values

# 2. Build images
docker compose -f docker-compose.prod.yml build --no-cache

# 3. Start services
docker compose -f docker-compose.prod.yml up -d

# 4. Verify
docker compose -f docker-compose.prod.yml ps
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

---

## 🏗️ INFRASTRUCTURE REQUIREMENTS

### **Minimum Server Specs:**
- **CPU**: 4 vCPU
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS (or Windows Server)

### **Cloud Provider Options:**

| Provider | Instance Type | Monthly Cost |
|----------|--------------|--------------|
| **AWS** | EC2 t3.large | ~$60 |
| **Google Cloud** | n1-standard-2 | ~$50 |
| **DigitalOcean** | Droplet 8GB | $40 |
| **Azure** | B2s VM | ~$55 |
| **Linode** | Dedicated 8GB | $40 |

### **What You Need to Buy:**
1. ✅ **VPS/Server** - $40-80/month
2. ✅ **Domain Name** - $10-15/year (Namecheap, GoDaddy)
3. ✅ **SSL Certificate** - FREE (Let's Encrypt)

**Total Monthly Cost**: **$40-80** (plus $1-2 for domain)

---

## 📋 DEPLOYMENT STEPS (Step-by-Step)

### **STEP 1: Get Infrastructure**
1. Purchase a VPS from DigitalOcean, AWS, or Linode
2. Choose Ubuntu 20.04/22.04 LTS
3. Get a static IP address

### **STEP 2: Domain Setup**
1. Buy domain from Namecheap/GoDaddy
2. Point DNS A record to your server IP
3. Wait 5-30 minutes for DNS propagation

### **STEP 3: Server Setup**
```bash
# SSH into server
ssh root@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Clone repository
git clone https://github.com/ahmed-khalil-omrani/Churn_predection.git
cd Churn_predection
```

### **STEP 4: Configure Application**
```bash
# Create .env file
cp .env.example .env
nano .env  # Edit with your values

# Update domain in configs
sed -i 's/yourdomain.com/your-actual-domain.com/g' nginx/nginx.conf
sed -i 's/http:\/\/localhost:8000/https:\/\/your-actual-domain.com\/api/g' frontend/script.js
```

### **STEP 5: SSL Certificate (Let's Encrypt)**
```bash
# Install Certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone \
  -d your-actual-domain.com \
  -d www.your-actual-domain.com \
  --email your-email@example.com \
  --agree-tos

# Copy certificates
sudo cp /etc/letsencrypt/live/your-actual-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-actual-domain.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/*.pem
```

### **STEP 6: Deploy**
```bash
# Run automated deployment
chmod +x deploy.sh
./deploy.sh

# Or manual deployment
docker compose -f docker-compose.prod.yml up -d --build
```

### **STEP 7: Firewall Setup**
```bash
# Enable firewall
sudo ufw enable

# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Check status
sudo ufw status
```

### **STEP 8: Verify Deployment**
```bash
# Check containers
docker compose -f docker-compose.prod.yml ps

# Test API
curl https://your-actual-domain.com/api/health

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🔒 SECURITY FEATURES INCLUDED

✅ **SSL/TLS Encryption** - All traffic encrypted  
✅ **API Key Authentication** - Protect endpoints  
✅ **Rate Limiting** - 10 requests/sec per IP  
✅ **Security Headers** - XSS, CSRF, clickjacking protection  
✅ **Non-root Container** - Run as unprivileged user  
✅ **Firewall Rules** - Only necessary ports open  
✅ **Secret Management** - Environment variables  
✅ **Input Validation** - Pydantic models  

---

## 📊 MONITORING SETUP

### **Access Dashboards:**
- 🌐 **Frontend**: https://yourdomain.com
- 📚 **API Docs**: https://yourdomain.com/api/docs
- 📊 **Grafana**: https://yourdomain.com:3001
- 📈 **Prometheus**: https://yourdomain.com:9090

### **Default Credentials:**
Check `.credentials` file after running deployment script

### **Setup Alerts in Grafana:**
1. Login to Grafana (port 3001)
2. Go to Alerting → Notification channels
3. Add Email/Slack integration
4. Create alerts for:
   - API errors > 5%
   - Response time > 2s
   - CPU > 80%
   - Memory > 90%

---

## 🧪 TESTING YOUR DEPLOYMENT

### **Test API Health:**
```powershell
Invoke-RestMethod -Uri "https://yourdomain.com/api/health"
```

### **Test Prediction:**
```powershell
$body = @{
    gender = "Female"
    SeniorCitizen = 0
    Partner = "No"
    Dependents = "No"
    tenure = 1
    PhoneService = "Yes"
    MultipleLines = "No"
    InternetService = "Fiber optic"
    OnlineSecurity = "No"
    OnlineBackup = "No"
    DeviceProtection = "No"
    TechSupport = "No"
    StreamingTV = "No"
    StreamingMovies = "No"
    Contract = "Month-to-month"
    PaperlessBilling = "Yes"
    PaymentMethod = "Electronic check"
    MonthlyCharges = 70.35
    TotalCharges = "70.35"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "https://yourdomain.com/api/predict" `
  -Body $body `
  -ContentType "application/json" `
  -Headers @{"X-API-Key" = "your-api-key-from-env-file"}
```

### **Load Testing:**
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test performance
ab -n 1000 -c 10 https://yourdomain.com/api/health
```

---

## 🔄 MAINTENANCE & UPDATES

### **View Logs:**
```powershell
docker compose -f docker-compose.prod.yml logs -f
```

### **Restart Services:**
```powershell
docker compose -f docker-compose.prod.yml restart
```

### **Update Application:**
```powershell
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

### **Backup:**
```powershell
# Backup models
tar -czf backup_models.tar.gz models/

# Backup logs
tar -czf backup_logs.tar.gz logs/
```

---

## 🚨 TROUBLESHOOTING

### **Problem: Can't access website**
```bash
# Check DNS
nslookup yourdomain.com

# Check containers
docker ps

# Check logs
docker compose -f docker-compose.prod.yml logs api
```

### **Problem: SSL errors**
```bash
# Check certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Renew certificate
sudo certbot renew
```

### **Problem: Out of memory**
```bash
# Check resources
docker stats

# Restart services
docker compose -f docker-compose.prod.yml restart
```

---

## 📚 DOCUMENTATION FILES

| File | Description |
|------|-------------|
| **PRODUCTION_GUIDE.md** | Quick reference guide |
| **docs/PRODUCTION_DEPLOYMENT.md** | Complete 500+ line guide |
| **DEPLOYMENT_CHANGES.md** | All changes made |
| **README.md** | Project overview |
| **docs/ARCHITECTURE.md** | System architecture |

---

## ✅ PRE-DEPLOYMENT CHECKLIST

- [ ] VPS/Server purchased
- [ ] Domain name registered
- [ ] DNS A record configured
- [ ] `.env` file created
- [ ] Domain updated in `nginx/nginx.conf`
- [ ] Domain updated in `frontend/script.js`
- [ ] SSL certificate generated
- [ ] Firewall rules configured
- [ ] Docker installed on server
- [ ] Repository cloned to server
- [ ] Production dependencies added
- [ ] Services deployed and running
- [ ] Health check passing
- [ ] Monitoring dashboards accessible
- [ ] Backup strategy implemented

---

## 🎯 QUICK START COMMANDS

### **Deploy on Windows (PowerShell):**
```powershell
cd d:\Churn_predection
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy.ps1 -Domain "yourdomain.com"
```

### **Deploy on Linux/Mac:**
```bash
cd ~/Churn_predection
chmod +x deploy.sh
./deploy.sh
```

### **Manual Deploy:**
```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 📞 SUPPORT

**Need help?** Check these resources:
1. `docs/PRODUCTION_DEPLOYMENT.md` - Comprehensive guide
2. `PRODUCTION_GUIDE.md` - Quick reference
3. API Docs: `https://yourdomain.com/api/docs`
4. FastAPI Docs: https://fastapi.tiangolo.com
5. Docker Docs: https://docs.docker.com

---

## 🎉 YOU'RE READY!

All the files are created and ready to deploy. Just follow these 3 steps:

1. **Get Infrastructure** (VPS + Domain) - ~$40-50/month
2. **Run Deployment Script** - Automated setup
3. **Update Domain Settings** - 2 config files

**Estimated Setup Time**: 2-4 hours (including DNS propagation)

---

**Created**: December 18, 2025  
**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Next Review**: After first deployment  

**Questions?** Review `docs/PRODUCTION_DEPLOYMENT.md` for detailed instructions!
