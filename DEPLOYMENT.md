# HƯỚNG DẪN TRIỂN KHAI HỆ THỐNG

## MỤC LỤC
1. [Tổng quan](#tổng-quan)
2. [Chuẩn bị môi trường](#chuẩn-bị-môi-trường)
3. [Triển khai Development](#triển-khai-development)
4. [Triển khai Staging](#triển-khai-staging)
5. [Triển khai Production](#triển-khai-production)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Backup & Recovery](#backup--recovery)
8. [Monitoring & Logging](#monitoring--logging)
9. [Troubleshooting](#troubleshooting)

---

## TỔNG QUAN

### Các môi trường

1. **Development (Local)**
   - Mục đích: Phát triển và test features mới
   - Database: MySQL local
   - Debug mode: ON
   - Logging: Console

2. **Staging**
   - Mục đích: QA testing, UAT
   - Database: MySQL server (staging DB)
   - Debug mode: OFF
   - Logging: BetterStack

3. **Production**
   - Mục đích: Hệ thống chính
   - Database: MySQL server (production DB)
   - Debug mode: OFF
   - Logging: BetterStack
   - High availability setup

---

## CHUẨN BỊ MÔI TRƯỜNG

### Yêu cầu Server

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 50GB SSD
- **OS**: Ubuntu 20.04+ LTS
- **Network**: Static IP, Port 80/443 open

#### Recommended (Production)
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disk**: 100GB+ SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: Load balancer, CDN

### Cài đặt Dependencies

#### 1. Update hệ thống
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Cài đặt Python 3.11
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

#### 3. Cài đặt MySQL 8.0
```bash
# Cài đặt MySQL Server
sudo apt install mysql-server -y

# Bảo mật MySQL
sudo mysql_secure_installation

# Tạo database và user
sudo mysql
```

```sql
CREATE DATABASE steam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'steam_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON steam.* TO 'steam_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 4. Cài đặt Redis
```bash
sudo apt install redis-server -y

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: supervised systemd
# Set: bind 127.0.0.1 (nếu chỉ dùng local)

# Restart Redis
sudo systemctl restart redis
sudo systemctl enable redis

# Test Redis
redis-cli ping
# Response: PONG
```

#### 5. Cài đặt Nginx
```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 6. Cài đặt Certbot (SSL)
```bash
sudo apt install certbot python3-certbot-nginx -y
```

---

## TRIỂN KHAI DEVELOPMENT

### Setup Local Development

```bash
# 1. Clone repository
git clone <repository-url>
cd bdu_steam

# 2. Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy và config .env
cp .env.example .env
nano .env

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

### Development với Docker

```bash
# 1. Chỉnh sửa docker-compose.yaml
nano docker-compose.yaml

# 2. Build và run
docker-compose up -d

# 3. Run migrations
docker-compose exec steam_backend python manage.py migrate

# 4. Create superuser
docker-compose exec steam_backend python manage.py createsuperuser

# 5. Xem logs
docker-compose logs -f steam_backend
```

---

## TRIỂN KHAI STAGING

### 1. Setup Server

```bash
# SSH vào server
ssh user@staging-server.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies (theo phần Chuẩn bị môi trường)
```

### 2. Clone và Setup Application

```bash
# Tạo user cho application
sudo useradd -m -s /bin/bash steam
sudo passwd steam

# Switch to steam user
sudo su - steam

# Clone repository
git clone <repository-url> ~/bdu_steam
cd ~/bdu_steam

# Checkout staging branch
git checkout staging

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Create .env file
nano .env
```

```bash
# Django Settings
DEBUG=False
SECRET_KEY=<generate-random-secret-key>
ALLOWED_HOSTS=staging.bdu.edu.vn,www.staging.bdu.edu.vn

# Database
DATABASE_ENGINE=mysql
DATABASE_NAME=steam_staging
DATABASE_USER=steam_user
DATABASE_PASSWORD=<secure-password>
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=
REDIS_PASSWORD=

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=staging@bdu.edu.vn
EMAIL_HOST_PASSWORD=<app-password>

# Logging
BETTERSTACK_LOG_TOKEN=<your-token>
BETTERSTACK_LOG_HOST=<your-host>

# Google Drive
GDRIVE_SERVICE_ACCOUNT_FILE=/home/steam/bdu_steam/service_account.json
GDRIVE_DEFAULT_FOLDER_ID=<folder-id>
```

### 4. Setup Database

```bash
# Run migrations
source venv/bin/activate
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Setup Gunicorn

```bash
# Test Gunicorn
gunicorn steam.wsgi:application --bind 0.0.0.0:8000

# Create Gunicorn systemd service
sudo nano /etc/systemd/system/gunicorn-steam.service
```

```ini
[Unit]
Description=Gunicorn daemon for BDU STEAM
After=network.target

[Service]
User=steam
Group=steam
WorkingDirectory=/home/steam/bdu_steam
Environment="PATH=/home/steam/bdu_steam/venv/bin"
ExecStart=/home/steam/bdu_steam/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/steam/bdu_steam/gunicorn.sock \
          --access-logfile /home/steam/bdu_steam/logs/access.log \
          --error-logfile /home/steam/bdu_steam/logs/error.log \
          --log-level info \
          steam.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
mkdir -p /home/steam/bdu_steam/logs

# Start và enable Gunicorn
sudo systemctl start gunicorn-steam
sudo systemctl enable gunicorn-steam

# Check status
sudo systemctl status gunicorn-steam
```

### 6. Setup Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/steam
```

```nginx
server {
    listen 80;
    server_name staging.bdu.edu.vn www.staging.bdu.edu.vn;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/steam/bdu_steam/staticfiles/;
    }

    location /media/ {
        alias /home/steam/bdu_steam/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/steam/bdu_steam/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/steam /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 7. Setup SSL (Let's Encrypt)

```bash
# Generate SSL certificate
sudo certbot --nginx -d staging.bdu.edu.vn -d www.staging.bdu.edu.vn

# Auto-renewal test
sudo certbot renew --dry-run
```

---

## TRIỂN KHAI PRODUCTION

### Checklist trước khi deploy

```bash
☐ Backup database hiện tại
☐ Test trên staging environment
☐ Review code changes
☐ Update dependencies
☐ Run migrations (test)
☐ Check environment variables
☐ Setup monitoring & alerts
☐ Prepare rollback plan
☐ Notify users về maintenance (nếu cần)
```

### Production Setup

**Tương tự Staging nhưng với một số điểm khác biệt:**

#### 1. Environment Variables

```bash
# .env cho production
DEBUG=False
SECRET_KEY=<very-secure-random-key>
ALLOWED_HOSTS=bdu.edu.vn,www.bdu.edu.vn,api.bdu.edu.vn

# Sử dụng production database
DATABASE_NAME=steam_production
DATABASE_PASSWORD=<very-secure-password>

# Production Redis (có thể có password)
REDIS_PASSWORD=<redis-password>

# Production email
EMAIL_HOST_USER=noreply@bdu.edu.vn
```

#### 2. Gunicorn Configuration (Production)

```ini
[Service]
# Increase workers (2 x CPU cores + 1)
ExecStart=/home/steam/bdu_steam/venv/bin/gunicorn \
          --workers 9 \
          --worker-class gevent \
          --worker-connections 1000 \
          --timeout 120 \
          --bind unix:/home/steam/bdu_steam/gunicorn.sock \
          --access-logfile /home/steam/bdu_steam/logs/access.log \
          --error-logfile /home/steam/bdu_steam/logs/error.log \
          --log-level warning \
          steam.wsgi:application

# Auto-restart on failure
Restart=always
RestartSec=3
```

#### 3. Nginx Configuration (Production)

```nginx
server {
    listen 80;
    server_name bdu.edu.vn www.bdu.edu.vn api.bdu.edu.vn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bdu.edu.vn www.bdu.edu.vn api.bdu.edu.vn;

    ssl_certificate /etc/letsencrypt/live/bdu.edu.vn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bdu.edu.vn/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 100M;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /home/steam/bdu_steam/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/steam/bdu_steam/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/steam/bdu_steam/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

#### 4. Database Optimization

```sql
-- Optimize MySQL for production
-- /etc/mysql/mysql.conf.d/mysqld.cnf

[mysqld]
max_connections = 200
innodb_buffer_pool_size = 2G
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 0
query_cache_type = 0
```

```bash
# Restart MySQL
sudo systemctl restart mysql
```

#### 5. Redis Configuration

```bash
# /etc/redis/redis.conf

# Set password
requirepass your_secure_redis_password

# Persistence
save 900 1
save 300 10
save 60 10000

# Max memory
maxmemory 1gb
maxmemory-policy allkeys-lru
```

```bash
# Restart Redis
sudo systemctl restart redis
```

---

## CI/CD PIPELINE

### GitHub Actions Workflow

Tạo file `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_steam
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
      
      redis:
        image: redis:6.0
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run migrations
        env:
          DATABASE_ENGINE: mysql
          DATABASE_NAME: test_steam
          DATABASE_USER: root
          DATABASE_PASSWORD: root
          DATABASE_HOST: 127.0.0.1
          DATABASE_PORT: 3306
          REDIS_HOST: 127.0.0.1
          REDIS_PORT: 6379
        run: |
          python manage.py migrate
      
      - name: Run tests
        env:
          DATABASE_ENGINE: mysql
          DATABASE_NAME: test_steam
          DATABASE_USER: root
          DATABASE_PASSWORD: root
          DATABASE_HOST: 127.0.0.1
          DATABASE_PORT: 3306
          REDIS_HOST: 127.0.0.1
          REDIS_PORT: 6379
        run: |
          python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to Production Server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USERNAME }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /home/steam/bdu_steam
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn-steam
            sudo systemctl reload nginx
```

### Setup GitHub Secrets

1. Vào GitHub repository
2. Settings → Secrets and variables → Actions
3. Thêm secrets:
   - `PROD_HOST`: IP hoặc domain của production server
   - `PROD_USERNAME`: SSH username
   - `PROD_SSH_KEY`: SSH private key

### Manual Deployment Script

Tạo file `deploy.sh`:

```bash
#!/bin/bash

set -e

echo "🚀 Starting deployment..."

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Restart Gunicorn
echo "🔄 Restarting Gunicorn..."
sudo systemctl restart gunicorn-steam

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo "✅ Deployment completed successfully!"
```

```bash
# Make executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

---

## BACKUP & RECOVERY

### Database Backup

#### Automatic Daily Backup

Tạo script `/home/steam/scripts/backup_db.sh`:

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/home/steam/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="steam_production"
DB_USER="steam_user"
DB_PASS="your_password"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/steam_${DATE}.sql.gz

# Remove old backups
find $BACKUP_DIR -name "steam_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: steam_${DATE}.sql.gz"
```

```bash
# Make executable
chmod +x /home/steam/scripts/backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
```

```
0 2 * * * /home/steam/scripts/backup_db.sh >> /home/steam/logs/backup.log 2>&1
```

#### Manual Backup

```bash
# Backup database
mysqldump -u steam_user -p steam_production > steam_backup_$(date +%Y%m%d).sql

# Compress backup
gzip steam_backup_$(date +%Y%m%d).sql
```

#### Restore Database

```bash
# Extract backup
gunzip steam_backup_20250101.sql.gz

# Restore database
mysql -u steam_user -p steam_production < steam_backup_20250101.sql
```

### Application Backup

```bash
# Backup application files
tar -czf ~/backups/app/steam_app_$(date +%Y%m%d).tar.gz \
    -C /home/steam \
    --exclude='bdu_steam/venv' \
    --exclude='bdu_steam/__pycache__' \
    --exclude='bdu_steam/.git' \
    bdu_steam
```

### Media Files Backup

```bash
# Backup media files to Google Drive or S3
rclone sync /home/steam/bdu_steam/media/ gdrive:steam_backups/media/
```

---

## MONITORING & LOGGING

### System Monitoring

#### Setup Prometheus & Grafana (Optional)

```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar -xzf prometheus-2.40.0.linux-amd64.tar.gz
sudo mv prometheus-2.40.0.linux-amd64 /opt/prometheus

# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
```

#### Monitoring với BetterStack

Hệ thống đã được cấu hình logging với BetterStack. Kiểm tra logs tại:
https://logs.betterstack.com

### Application Monitoring

#### Health Check Monitoring

```bash
# Setup monitoring với simple bash script
nano /home/steam/scripts/health_check.sh
```

```bash
#!/bin/bash

HEALTH_URL="https://api.bdu.edu.vn/health/"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Check health endpoint
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
    # Send alert to Slack
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"🚨 Health check failed! HTTP Status: $RESPONSE\"}" \
        $SLACK_WEBHOOK
    
    echo "$(date): Health check failed - HTTP $RESPONSE" >> /home/steam/logs/health_check.log
else
    echo "$(date): Health check passed" >> /home/steam/logs/health_check.log
fi
```

```bash
# Add to crontab (every 5 minutes)
*/5 * * * * /home/steam/scripts/health_check.sh
```

### Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/steam
```

```
/home/steam/bdu_steam/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 steam steam
    sharedscripts
    postrotate
        systemctl reload gunicorn-steam > /dev/null 2>&1 || true
    endscript
}
```

---

## TROUBLESHOOTING

### Common Issues

#### 1. Gunicorn không start

```bash
# Check logs
sudo journalctl -u gunicorn-steam -n 50

# Check Gunicorn socket
ls -la /home/steam/bdu_steam/gunicorn.sock

# Check permissions
sudo chown -R steam:steam /home/steam/bdu_steam

# Restart service
sudo systemctl restart gunicorn-steam
```

#### 2. Nginx 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status gunicorn-steam

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check Nginx config
sudo nginx -t

# Check socket connection
sudo -u www-data curl --unix-socket /home/steam/bdu_steam/gunicorn.sock http://localhost/health/
```

#### 3. Database connection errors

```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u steam_user -p -h localhost steam_production

# Check max connections
mysql -u root -p -e "SHOW VARIABLES LIKE 'max_connections';"

# Check current connections
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
```

#### 4. Redis connection errors

```bash
# Check Redis is running
sudo systemctl status redis

# Test connection
redis-cli ping

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

#### 5. Static files không load

```bash
# Collect static files lại
cd /home/steam/bdu_steam
source venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R steam:steam /home/steam/bdu_steam/staticfiles
```

### Performance Issues

#### High CPU Usage

```bash
# Check processes
top -u steam

# Check Gunicorn workers
ps aux | grep gunicorn

# Reduce workers nếu cần
sudo nano /etc/systemd/system/gunicorn-steam.service
# Giảm --workers

sudo systemctl daemon-reload
sudo systemctl restart gunicorn-steam
```

#### High Memory Usage

```bash
# Check memory
free -h

# Check MySQL memory
mysql -u root -p -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';"

# Optimize MySQL config
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Giảm innodb_buffer_pool_size

sudo systemctl restart mysql
```

#### Slow Database Queries

```bash
# Enable slow query log
mysql -u root -p

SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';

# Analyze slow queries
sudo mysqldumpslow /var/log/mysql/slow-query.log
```

### Emergency Procedures

#### Rollback Deployment

```bash
# Go to application directory
cd /home/steam/bdu_steam

# Checkout previous commit
git log --oneline -10  # Find commit hash
git checkout <previous-commit-hash>

# Restore database từ backup
mysql -u steam_user -p steam_production < /home/steam/backups/database/steam_YYYYMMDD.sql

# Restart services
sudo systemctl restart gunicorn-steam
sudo systemctl reload nginx
```

#### Complete System Recovery

```bash
# 1. Stop services
sudo systemctl stop gunicorn-steam
sudo systemctl stop nginx

# 2. Restore database
mysql -u steam_user -p steam_production < /path/to/backup.sql

# 3. Restore application
cd /home/steam
tar -xzf backups/app/steam_app_YYYYMMDD.tar.gz

# 4. Start services
sudo systemctl start gunicorn-steam
sudo systemctl start nginx

# 5. Verify
curl -I https://api.bdu.edu.vn/health/
```

---

## SECURITY BEST PRACTICES

### 1. Firewall Setup

```bash
# Install UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### 2. Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
```

```bash
# Start Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

### 3. Regular Security Updates

```bash
# Setup unattended upgrades
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 4. SSH Hardening

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 22
```

```bash
# Restart SSH
sudo systemctl restart sshd
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-30  
**For Support**: support@bdu.edu.vn

