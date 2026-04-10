# Industrial IDS Deployment - Quick Start Guide

## Quick Deployment

### Step 0: Security Setup (Required)

**IMPORTANT**: Before deploying, configure your security credentials:

```bash
# Copy the environment template
cp deployment/.env.template deployment/.env

# Edit with your actual credentials
nano deployment/.env

# Set secure permissions (critical!)
chmod 600 deployment/.env
```

**Required Security Configuration:**
- `JWT_SECRET`: Generate strong random string (32+ chars)
- `GRAFANA_ADMIN_PASSWORD`: Change from default
- `EMAIL_PASS`: Your email service password
- `ALERT_WEBHOOK_URL`: Your alert webhook URL
- `API_KEY`: Your API integration key

**Generate Strong Passwords:**
```bash
# Generate JWT secret
openssl rand -hex 32

# Generate secure password
openssl rand -base64 12
```

⚠️ **Never commit .env file to version control!**

### Prerequisites
- Docker and Docker Compose installed
- Trained models in `outputs/models/` directory
- 8GB+ RAM, 4+ CPU cores recommended

### Step 1: Train Models (if not already done)
```bash
python run_pipeline.py --stage all
```

### Step 2: Deploy the System
```bash
# On Linux/Mac
./deployment/deploy.sh

# On Windows
bash deployment/deploy.sh
# or
docker-compose -f deployment/docker-compose.yml up -d
```

### Step 3: Verify Deployment
```bash
# Check service status
./deployment/deploy.sh status

# Test services
./deployment/deploy.sh test

# View logs
./deployment/deploy.sh logs
```

## 📊 Access Points

Once deployed, access the system at:

- **Main Dashboard**: http://localhost:8080
- **Grafana Monitoring**: http://localhost:3000 (admin/admin123)
- **Prometheus Metrics**: http://localhost:9090

## 🔧 Service Endpoints

- **Autoencoder**: http://localhost:8083
  - Health: `GET /health`
  - Predict: `POST /predict`
  - Metrics: `GET /metrics`

- **Classifier**: http://localhost:8084
  - Health: `GET /health`
  - Classify: `POST /classify`
  - Metrics: `GET /metrics`

- **Alert Manager**: http://localhost:8085
  - Health: `GET /health`
  - Alerts: `GET /alerts`

## 📝 Example API Usage

### Test Anomaly Detection
```bash
curl -X POST "http://localhost:8083/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "features": [0.1, 0.2, 0.3, ...],
       "timestamp": "2024-01-01T12:00:00Z"
     }'
```

### Test Malicious Classification
```bash
curl -X POST "http://localhost:8084/classify" \
     -H "Content-Type: application/json" \
     -d '{
       "features": [0.1, 0.2, 0.3, ...],
       "timestamp": "2024-01-01T12:00:00Z"
     }'
```

## 🛠️ Management Commands

```bash
# Stop all services
./deployment/deploy.sh stop

# Restart services
./deployment/deploy.sh restart

# View specific service logs
./deployment/deploy.sh logs autoencoder

# Cleanup everything
./deployment/deploy.sh cleanup
```

## 🔍 Monitoring

### Health Checks
```bash
# Check all services
curl http://localhost:8083/health
curl http://localhost:8084/health
curl http://localhost:8085/health
```

### Metrics
```bash
# View Prometheus metrics
curl http://localhost:8083/metrics
curl http://localhost:8084/metrics
```

## 🚨 Troubleshooting

### Common Issues

1. **Models not found**
   ```bash
   # Ensure models are trained
   python run_pipeline.py --stage all
   ```

2. **Port conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :8080
   # Stop conflicting services or change ports in docker-compose.yml
   ```

3. **Memory issues**
   ```bash
   # Check Docker resource limits
   docker system df
   # Clean up if needed
   docker system prune -f
   ```

4. **Services not starting**
   ```bash
   # View detailed logs
   docker-compose -f deployment/docker-compose.yml logs
   ```

### Performance Tuning

1. **Increase memory limits** in `docker-compose.yml`
2. **Adjust worker counts** in service configurations
3. **Optimize batch sizes** for your hardware

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale autoencoder service
docker-compose -f deployment/docker-compose.yml up -d --scale autoencoder=3
```

### Load Balancing
- Use nginx or HAProxy for load balancing
- Configure health checks for failover

## 🔐 Security

### Production Security
1. Change default passwords
2. Use HTTPS/SSL certificates
3. Configure firewall rules
4. Enable authentication
5. Set up network isolation

### Environment Variables
```bash
# Set up environment variables
export ALERT_WEBHOOK_URL="https://your-webhook-url"
export EMAIL_SMTP="smtp.yourcompany.com"
export EMAIL_USER="alerts@yourcompany.com"
export EMAIL_PASS="your-password"
export SLACK_WEBHOOK="https://hooks.slack.com/your-webhook"
```

## 📞 Support

For issues:
1. Check logs: `./deployment/deploy.sh logs`
2. Verify prerequisites
3. Check system resources
4. Review configuration files

## 🔄 Updates

### Updating Models
1. Train new models: `python run_pipeline.py --stage all`
2. Copy models to deployment directory
3. Restart services: `./deployment/deploy.sh restart`

### Updating Services
1. Pull latest code
2. Rebuild images: `./deployment/deploy.sh deploy`
3. Verify functionality: `./deployment/deploy.sh test`
