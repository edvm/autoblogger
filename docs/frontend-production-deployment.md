# Frontend Production Deployment Guide

This guide provides detailed steps to deploy the AutoBlogger Next.js frontend on an Ubuntu 25 server.

## Prerequisites

- Ubuntu 25 server with root/sudo access
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

## Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Node.js 18+ and npm

```bash
# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be 18.x
npm --version
```

### 3. Install PM2 for Process Management

```bash
sudo npm install -g pm2
```

### 4. Install Nginx (Reverse Proxy)

```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 5. Install Docker (Alternative Deployment Method)

```bash
# Install Docker
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
```

## Deployment Methods

### Method 1: Native Node.js Deployment (Recommended)

#### 1. Create Application Directory

```bash
sudo mkdir -p /var/www/autoblogger-frontend
sudo chown -R $USER:$USER /var/www/autoblogger-frontend
```

#### 2. Clone and Build Application

```bash
cd /var/www/autoblogger-frontend
git clone <your-repository-url> .
cd frontend

# Install dependencies
npm ci --production=false

# Create production environment file
cp .env.local.example .env.local
nano .env.local
```

#### 3. Configure Environment Variables

Edit `.env.local`:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key
CLERK_SECRET_KEY=sk_test_your_secret_key

# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
# Or for local backend: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Production settings
NODE_ENV=production
```

#### 4. Build Application

```bash
npm run build
```

#### 5. Configure PM2

Create PM2 ecosystem file:

```bash
nano ecosystem.config.js
```

```javascript
module.exports = {
  apps: [{
    name: 'autoblogger-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/var/www/autoblogger-frontend/frontend',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    instances: 'max',
    exec_mode: 'cluster',
    watch: false,
    max_memory_restart: '1G',
    error_file: '/var/log/autoblogger-frontend-error.log',
    out_file: '/var/log/autoblogger-frontend-out.log',
    log_file: '/var/log/autoblogger-frontend.log',
    time: true
  }]
};
```

#### 6. Start Application with PM2

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Method 2: Docker Deployment

#### 1. Build Docker Image

```bash
cd /var/www/autoblogger-frontend/frontend
docker build -t autoblogger-frontend .
```

#### 2. Run Container

```bash
# Create environment file
cat > .env.production << EOF
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key
CLERK_SECRET_KEY=sk_test_your_secret_key
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
NODE_ENV=production
EOF

# Run container
docker run -d \
  --name autoblogger-frontend \
  --restart unless-stopped \
  -p 3000:3000 \
  --env-file .env.production \
  autoblogger-frontend
```

#### 3. Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    container_name: autoblogger-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      - NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Start with:
```bash
docker-compose up -d
```

## Nginx Configuration

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/autoblogger-frontend
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types
        text/css
        text/javascript
        text/xml
        text/plain
        text/x-component
        application/javascript
        application/x-javascript
        application/json
        application/xml
        application/rss+xml
        application/atom+xml
        font/truetype
        font/opentype
        application/vnd.ms-fontobject
        image/svg+xml;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # Proxy to Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/autoblogger-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Configuration with Let's Encrypt

### 1. Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Generate SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Auto-renewal

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Monitoring and Logging

### 1. Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/autoblogger-frontend
```

```
/var/log/autoblogger-frontend*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $USER $USER
    postrotate
        pm2 reloadLogs
    endscript
}
```

### 2. Health Check Script

```bash
nano /usr/local/bin/autoblogger-health-check.sh
```

```bash
#!/bin/bash
HEALTH_URL="http://localhost:3000"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
    echo "$(date): Health check failed. HTTP $RESPONSE"
    pm2 restart autoblogger-frontend
else
    echo "$(date): Health check passed"
fi
```

```bash
chmod +x /usr/local/bin/autoblogger-health-check.sh
```

### 3. Add to Crontab

```bash
crontab -e
```

Add:
```
*/5 * * * * /usr/local/bin/autoblogger-health-check.sh >> /var/log/autoblogger-health.log 2>&1
```

## Security Considerations

### 1. Firewall Configuration

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Environment Variables Security

- Never commit `.env.local` to version control
- Use restricted file permissions: `chmod 600 .env.local`
- Consider using external secret management services

### 3. Regular Updates

```bash
# Setup automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

## Deployment Automation

### 1. Deploy Script

```bash
nano deploy.sh
```

```bash
#!/bin/bash
set -e

echo "Starting deployment..."

# Pull latest code
git pull origin main

# Install dependencies
cd frontend
npm ci --production=false

# Build application
npm run build

# Restart PM2
pm2 restart autoblogger-frontend

# Wait for startup
sleep 10

# Health check
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Deployment successful!"
else
    echo "Deployment failed - health check failed"
    exit 1
fi
```

### 2. GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Frontend

on:
  push:
    branches: [ main ]
    paths: [ 'frontend/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /var/www/autoblogger-frontend
          ./deploy.sh
```

## Troubleshooting

### Common Issues

1. **Port 3000 already in use**
   ```bash
   sudo lsof -i :3000
   sudo kill -9 <PID>
   ```

2. **PM2 process not starting**
   ```bash
   pm2 logs autoblogger-frontend
   pm2 restart autoblogger-frontend
   ```

3. **Build failures**
   - Check Node.js version compatibility
   - Verify environment variables
   - Check disk space: `df -h`

4. **Nginx 502 errors**
   - Verify Next.js is running: `curl http://localhost:3000`
   - Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`

### Performance Optimization

1. **Enable Next.js caching**
   - Static assets are cached for 1 year
   - API routes can be cached with appropriate headers

2. **Database connections**
   - Use connection pooling
   - Implement proper error handling

3. **CDN Integration**
   - Consider using CloudFlare for static assets
   - Enable image optimization

## Maintenance

### Regular Tasks

1. **Weekly**
   - Check application logs
   - Monitor disk usage
   - Review SSL certificate expiry

2. **Monthly**
   - Update dependencies
   - Review security patches
   - Backup configuration files

3. **Quarterly**
   - Full security audit
   - Performance review
   - Capacity planning

This deployment guide provides a production-ready setup for the AutoBlogger Next.js frontend on Ubuntu 25.