# Industrial IDS Deployment Strategy
## Real-World Implementation Guide

---

## 1. Deployment Architecture Overview

### 1.1 System Components

```
Industrial Network
├── Data Collection Layer
│   ├── Event Log Aggregator
│   ├── Feature Extraction Service
│   └── Data Buffer/Queue
├── Processing Layer
│   ├── Autoencoder Service (Stage 1)
│   ├── Classifier Service (Stage 2)
│   └── Rule Engine
├── Alert Management Layer
│   ├── Alert Correlation
│   ├── Alert Prioritization
│   └── Notification System
└── Monitoring & Management
    ├── Performance Monitoring
    ├── Model Health Checks
    └── Configuration Management
```

### 1.2 Deployment Patterns

#### Pattern A: Edge Deployment (Recommended for Small-Medium Facilities)
- **Location**: On-premise server or industrial PC
- **Latency**: <10ms processing time
- **Advantages**: Real-time processing, network isolation
- **Requirements**: 4-core CPU, 8GB RAM, 100GB storage

#### Pattern B: Hybrid Deployment (Large Facilities)
- **Edge**: Real-time anomaly detection
- **Cloud**: Model training, analysis, storage
- **Advantages**: Scalable, centralized management
- **Requirements**: Edge gateway + cloud connectivity

#### Pattern C: Centralized Deployment (Corporate Networks)
- **Location**: Central data center
- **Latency**: 100-500ms (acceptable for monitoring)
- **Advantages**: Easier maintenance, resource sharing
- **Requirements**: Enterprise server infrastructure

---

## 2. Technical Implementation

### 2.1 Container-Based Deployment

#### Docker Compose Configuration
```yaml
version: '3.8'
services:
  # Data Collection Service
  data-collector:
    build: ./services/data-collector
    volumes:
      - /var/log/industrial:/app/logs:ro
      - ./config:/app/config:ro
    environment:
      - LOG_SOURCE=/app/logs/events.jsonl
      - BUFFER_SIZE=1000
    restart: unless-stopped

  # Feature Extraction Service
  feature-extractor:
    build: ./services/feature-extractor
    depends_on:
      - data-collector
    volumes:
      - ./models:/app/models:ro
      - ./config:/app/config:ro
    environment:
      - WINDOW_SIZE=90
      - STRIDE=20
    restart: unless-stopped

  # Autoencoder Service (Stage 1)
  autoencoder:
    build: ./services/autoencoder
    depends_on:
      - feature-extractor
    volumes:
      - ./models:/app/models:ro
      - ./config:/app/config:ro
    environment:
      - MODEL_PATH=/app/models/autoencoder.pt
      - THRESHOLD_PERCENTILE=75
    restart: unless-stopped

  # Classifier Service (Stage 2)
  classifier:
    build: ./services/classifier
    depends_on:
      - autoencoder
    volumes:
      - ./models:/app/models:ro
      - ./config:/app/config:ro
    environment:
      - MODEL_PATH=/app/models/classifier.pt
      - THRESHOLD=0.5
    restart: unless-stopped

  # Alert Management
  alert-manager:
    build: ./services/alert-manager
    depends_on:
      - classifier
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
    environment:
      - ALERT_WEBHOOK_URL=${ALERT_WEBHOOK_URL}
      - EMAIL_SMTP=${EMAIL_SMTP}
    restart: unless-stopped

  # Monitoring Dashboard
  dashboard:
    build: ./services/dashboard
    ports:
      - "8080:8080"
    depends_on:
      - alert-manager
    environment:
      - DATABASE_URL=sqlite:///./data/metrics.db
    restart: unless-stopped
```

### 2.2 Kubernetes Deployment (Enterprise Scale)

#### Namespace Configuration
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: industrial-ids
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ids-autoencoder
  namespace: industrial-ids
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ids-autoencoder
  template:
    metadata:
      labels:
        app: ids-autoencoder
    spec:
      containers:
      - name: autoencoder
        image: industrial-ids/autoencoder:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: MODEL_PATH
          value: "/models/autoencoder.pt"
        volumeMounts:
        - name: model-volume
          mountPath: /models
      volumes:
      - name: model-volume
        configMap:
          name: ids-models
```

---

## 3. Data Integration

### 3.1 Data Sources and Formats

#### Supported Data Sources
```python
# Event Log Sources
SOURCES = {
    'siemens_plc': {
        'format': 'jsonl',
        'fields': ['timestamp', 'device_id', 'event_type', 'value'],
        'parser': 'SiemensEventParser'
    },
    'rockwell_hmi': {
        'format': 'csv',
        'fields': ['time', 'station', 'alarm', 'priority'],
        'parser': 'RockwellEventParser'
    },
    'opcua_server': {
        'format': 'json',
        'fields': ['Timestamp', 'NodeId', 'Value', 'StatusCode'],
        'parser': 'OPCUAParser'
    },
    'modbus_gateway': {
        'format': 'binary',
        'fields': ['timestamp', 'slave_id', 'function_code', 'data'],
        'parser': 'ModbusParser'
    }
}
```

#### Real-time Data Pipeline
```python
class DataPipeline:
    def __init__(self, config):
        self.collectors = []
        self.feature_buffer = CircularBuffer(max_size=10000)
        self.processing_queue = Queue(maxsize=1000)
        
    async def start_collection(self):
        """Start real-time data collection from all sources"""
        for source_config in self.config['sources']:
            collector = DataCollector(source_config)
            self.collectors.append(collector)
            asyncio.create_task(collector.collect_events())
    
    async def process_events(self):
        """Process events in real-time"""
        while True:
            events = await self.processing_queue.get()
            features = self.extract_features(events)
            predictions = await self.predict(features)
            await self.handle_alerts(predictions)
```

### 3.2 Feature Extraction in Production

#### Real-time Feature Engineering
```python
class ProductionFeatureExtractor:
    def __init__(self, window_size=90, stride=20):
        self.window_size = window_size
        self.stride = stride
        self.feature_buffer = []
        
    def extract_realtime_features(self, new_events):
        """Extract features from incoming events"""
        self.feature_buffer.extend(new_events)
        
        # Maintain sliding window
        if len(self.feature_buffer) > self.window_size:
            self.feature_buffer = self.feature_buffer[-self.window_size:]
        
        if len(self.feature_buffer) == self.window_size:
            return self.compute_features(self.feature_buffer)
        return None
    
    def compute_features(self, events):
        """Compute 196-dimensional feature vector"""
        features = []
        
        # Temporal features
        features.extend(self.compute_temporal_stats(events))
        
        # Device-specific features
        features.extend(self.compute_device_features(events))
        
        # Network features
        features.extend(self.compute_network_features(events))
        
        # Control system features
        features.extend(self.compute_control_features(events))
        
        return np.array(features, dtype=np.float32)
```

---

## 4. Model Deployment

### 4.1 Model Serving with FastAPI

#### Autoencoder Service
```python
from fastapi import FastAPI, HTTPException
import torch
import numpy as np
from pydantic import BaseModel

app = FastAPI(title="Industrial IDS - Autoencoder Service")

class FeatureVector(BaseModel):
    features: List[float]
    timestamp: str

class AutoencoderService:
    def __init__(self):
        self.model = torch.load('/models/autoencoder.pt')
        self.model.eval()
        self.threshold = np.percentile([], 75)  # Load from training
    
    async def predict(self, features):
        """Get reconstruction error for anomaly detection"""
        with torch.no_grad():
            x = torch.tensor(features).float()
            recon, _ = self.model(x)
            error = ((x - recon) ** 2).mean().item()
            return {
                'reconstruction_error': error,
                'is_anomaly': error > self.threshold,
                'confidence': error / self.threshold
            }

autoencoder_service = AutoencoderService()

@app.post("/predict")
async def predict_anomaly(data: FeatureVector):
    try:
        result = await autoencoder_service.predict(data.features)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": True}
```

#### Classifier Service
```python
app = FastAPI(title="Industrial IDS - Classifier Service")

class ClassifierService:
    def __init__(self):
        self.model = torch.load('/models/classifier.pt')
        self.model.eval()
        self.threshold = 0.5
    
    async def predict(self, features):
        """Classify anomaly as benign or malicious"""
        with torch.no_grad():
            x = torch.tensor(features).float()
            logits = self.model(x)
            probability = torch.sigmoid(logits).item()
            return {
                'malicious_probability': probability,
                'is_malicious': probability > self.threshold,
                'confidence': abs(probability - 0.5) * 2
            }

classifier_service = ClassifierService()

@app.post("/classify")
async def classify_anomaly(data: FeatureVector):
    if not data.features:
        raise HTTPException(status_code=400, detail="No features provided")
    
    result = await classifier_service.predict(data.features)
    return result
```

### 4.2 Model Versioning and Updates

#### Model Registry
```python
class ModelRegistry:
    def __init__(self, registry_path="/models"):
        self.registry_path = registry_path
        self.current_models = {}
        self.load_model_metadata()
    
    def register_model(self, model_type, model_path, metadata):
        """Register new model version"""
        version = metadata['version']
        model_info = {
            'path': model_path,
            'metadata': metadata,
            'performance': metadata['performance'],
            'registered_at': datetime.now()
        }
        
        # Save to registry
        registry_file = f"{self.registry_path}/{model_type}_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(model_info, f)
        
        # Update current if this is the best performing
        if self.is_best_model(model_type, model_info):
            self.current_models[model_type] = model_info
    
    def rollback_model(self, model_type, target_version):
        """Rollback to previous model version"""
        # Implementation for model rollback
        pass
```

---

## 5. Alert Management

### 5.1 Alert System Architecture

#### Alert Processing Pipeline
```python
class AlertManager:
    def __init__(self, config):
        self.alert_rules = config['alert_rules']
        self.notification_channels = []
        self.alert_history = []
        self.correlation_window = 300  # 5 minutes
        
    async def process_prediction(self, prediction):
        """Process model prediction and generate alerts"""
        if prediction['is_malicious']:
            alert = self.create_alert(prediction)
            
            # Check for alert correlation
            correlated_alerts = self.find_correlated_alerts(alert)
            
            if correlated_alerts:
                alert = self.merge_alerts(alert, correlated_alerts)
            
            # Apply suppression rules
            if not self.is_suppressed(alert):
                await self.send_alert(alert)
                self.alert_history.append(alert)
    
    def create_alert(self, prediction):
        """Create structured alert"""
        return {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(),
            'severity': self.calculate_severity(prediction),
            'confidence': prediction['confidence'],
            'attack_type': self.classify_attack_type(prediction),
            'source_device': prediction.get('device_id'),
            'description': self.generate_description(prediction),
            'recommended_actions': self.get_recommendations(prediction)
        }
```

### 5.2 Notification Channels

#### Multi-Channel Alert System
```python
class NotificationManager:
    def __init__(self, config):
        self.channels = {
            'email': EmailNotifier(config['email']),
            'sms': SMSNotifier(config['sms']),
            'slack': SlackNotifier(config['slack']),
            'webhook': WebhookNotifier(config['webhook']),
            'siren': SirenNotifier(config['siren'])
        }
    
    async def send_alert(self, alert):
        """Send alert through appropriate channels"""
        channels = self.select_channels(alert)
        
        tasks = []
        for channel_name in channels:
            channel = self.channels[channel_name]
            tasks.append(channel.send(alert))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def select_channels(self, alert):
        """Select notification channels based on alert severity"""
        if alert['severity'] == 'critical':
            return ['siren', 'sms', 'email', 'slack']
        elif alert['severity'] == 'high':
            return ['sms', 'email', 'slack']
        elif alert['severity'] == 'medium':
            return ['email', 'slack']
        else:
            return ['email']
```

---

## 6. Monitoring and Maintenance

### 6.1 System Health Monitoring

#### Health Check Service
```python
class HealthMonitor:
    def __init__(self):
        self.services = {
            'data_collector': ServiceHealth('data-collector', 8081),
            'feature_extractor': ServiceHealth('feature-extractor', 8082),
            'autoencoder': ServiceHealth('autoencoder', 8083),
            'classifier': ServiceHealth('classifier', 8084),
            'alert_manager': ServiceHealth('alert-manager', 8085)
        }
    
    async def check_all_services(self):
        """Check health of all services"""
        health_status = {}
        
        for service_name, service in self.services.items():
            status = await service.check_health()
            health_status[service_name] = status
        
        return {
            'overall_health': self.calculate_overall_health(health_status),
            'services': health_status,
            'timestamp': datetime.now()
        }
    
    def calculate_overall_health(self, health_status):
        """Calculate overall system health"""
        healthy_count = sum(1 for s in health_status.values() if s['status'] == 'healthy')
        total_count = len(health_status)
        
        if healthy_count == total_count:
            return 'healthy'
        elif healthy_count >= total_count * 0.8:
            return 'degraded'
        else:
            return 'unhealthy'
```

### 6.2 Performance Monitoring

#### Metrics Collection
```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'prediction_latency': [],
            'prediction_accuracy': [],
            'alert_rate': [],
            'system_resources': [],
            'model_drift': []
        }
    
    def record_prediction(self, latency, confidence, prediction_time):
        """Record prediction metrics"""
        self.metrics['prediction_latency'].append({
            'timestamp': prediction_time,
            'latency_ms': latency * 1000,
            'confidence': confidence
        })
    
    def record_system_resources(self):
        """Record system resource usage"""
        import psutil
        
        self.metrics['system_resources'].append({
            'timestamp': datetime.now(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        })
    
    def detect_model_drift(self, recent_predictions):
        """Detect model performance drift"""
        # Compare recent performance with baseline
        baseline_accuracy = 0.873  # From training
        recent_accuracy = self.calculate_accuracy(recent_predictions)
        
        drift_score = abs(recent_accuracy - baseline_accuracy) / baseline_accuracy
        
        if drift_score > 0.1:  # 10% performance degradation
            return {
                'drift_detected': True,
                'drift_score': drift_score,
                'recommendation': 'retrain_model'
            }
        
        return {'drift_detected': False, 'drift_score': drift_score}
```

---

## 7. Security Considerations

### 7.1 IDS Security Hardening

#### Security Measures
```python
class SecurityManager:
    def __init__(self, config):
        self.config = config
        self.encryption_key = self.load_encryption_key()
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive operational data"""
        from cryptography.fernet import Fernet
        f = Fernet(self.encryption_key)
        return f.encrypt(json.dumps(data).encode())
    
    def authenticate_request(self, request):
        """Authenticate API requests"""
        token = request.headers.get('Authorization')
        if not token:
            return False
        
        try:
            payload = jwt.decode(token, self.config['jwt_secret'], algorithms=['HS256'])
            return payload.get('role') in ['operator', 'admin']
        except jwt.InvalidTokenError:
            return False
    
    def validate_input(self, data):
        """Validate input data for injection attacks"""
        # Check for SQL injection patterns
        sql_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE']
        data_str = str(data).upper()
        
        for pattern in sql_patterns:
            if pattern in data_str:
                raise SecurityException(f"Potential SQL injection detected: {pattern}")
        
        # Check for XSS patterns
        xss_patterns = ['<script>', 'javascript:', 'onerror=']
        for pattern in xss_patterns:
            if pattern in data_str.lower():
                raise SecurityException(f"Potential XSS detected: {pattern}")
        
        return True
```

### 7.2 Access Control

#### Role-Based Access Control
```python
class AccessControl:
    ROLES = {
        'viewer': ['read_metrics', 'view_alerts'],
        'operator': ['read_metrics', 'view_alerts', 'acknowledge_alerts'],
        'admin': ['read_metrics', 'view_alerts', 'acknowledge_alerts', 
                  'manage_models', 'configure_system'],
        'super_admin': ['all_permissions']
    }
    
    def check_permission(self, user_role, required_permission):
        """Check if user has required permission"""
        user_permissions = self.ROLES.get(user_role, [])
        return required_permission in user_permissions or 'all_permissions' in user_permissions
    
    def require_role(self, required_role):
        """Decorator for role-based access control"""
        def decorator(func):
            async def wrapper(request, *args, **kwargs):
                user_role = await self.get_user_role(request)
                if not self.check_permission(user_role, required_role):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                return await func(request, *args, **kwargs)
            return wrapper
        return decorator
```

---

## 8. Deployment Checklist

### 8.1 Pre-Deployment Checklist

#### Infrastructure Preparation
- [ ] Server hardware meets requirements (8GB RAM, 4+ cores)
- [ ] Network connectivity to data sources
- [ ] Firewall rules configured for required ports
- [ ] SSL certificates installed for HTTPS
- [ ] Backup systems configured
- [ ] Monitoring systems in place

#### Software Installation
- [ ] Docker/Podman installed and running
- [ ] Kubernetes cluster (if using K8s deployment)
- [ ] Database systems installed (PostgreSQL/InfluxDB)
- [ ] Time synchronization (NTP) configured
- [ ] Log rotation configured

#### Model Deployment
- [ ] Trained models copied to production server
- [ ] Model validation completed
- [ ] Threshold values optimized for production
- [ ] Model versioning system configured
- [ ] A/B testing framework ready

### 8.2 Post-Deployment Verification

#### Functional Testing
- [ ] Data collection working from all sources
- [ ] Feature extraction producing correct vectors
- [ ] Autoencoder predictions within expected latency (<10ms)
- [ ] Classifier predictions accurate
- [ ] Alert generation working correctly
- [ ] Notification channels functioning

#### Performance Testing
- [ ] Load testing with realistic data volumes
- [ ] Memory usage within limits
- [ ] CPU usage under control
- [ ] Network bandwidth sufficient
- [ ] Database performance acceptable

#### Security Testing
- [ ] Authentication working correctly
- [ ] Authorization enforced properly
- [ ] Input validation preventing injections
- [ ] Data encryption working
- [ ] Audit logging functioning

---

## 9. Scaling and Optimization

### 9.1 Horizontal Scaling

#### Load Balancer Configuration
```nginx
upstream ids_backend {
    server ids-autoencoder-1:8083;
    server ids-autoencoder-2:8083;
    server ids-autoencoder-3:8083;
}

server {
    listen 80;
    server_name ids.company.com;
    
    location /api/autoencoder {
        proxy_pass http://ids_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 1s;
        proxy_send_timeout 1s;
        proxy_read_timeout 1s;
    }
}
```

### 9.2 Performance Optimization

#### Caching Strategy
```python
class PredictionCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = 60  # 1 minute
    
    async def get_cached_prediction(self, feature_hash):
        """Get cached prediction if available"""
        cached = await self.redis.get(f"pred:{feature_hash}")
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_prediction(self, feature_hash, prediction):
        """Cache prediction result"""
        await self.redis.setex(
            f"pred:{feature_hash}", 
            self.cache_ttl, 
            json.dumps(prediction)
        )
```

---

## 10. Troubleshooting Guide

### 10.1 Common Issues and Solutions

#### High Latency Issues
**Problem**: Prediction latency > 50ms
**Causes**: 
- Model loading on every request
- Insufficient CPU resources
- Network delays

**Solutions**:
- Pre-load models in memory
- Scale horizontally with load balancer
- Optimize network configuration

#### False Positive Spike
**Problem**: Sudden increase in false positives
**Causes**:
- Model drift
- Threshold misconfiguration
- Data quality issues

**Solutions**:
- Check model performance metrics
- Recalibrate thresholds
- Validate data sources

#### Memory Leaks
**Problem**: Memory usage continuously increasing
**Causes**:
- Feature buffer not clearing
- Model not properly garbage collected
- Connection leaks

**Solutions**:
- Implement circular buffers
- Restart services periodically
- Monitor connection pools

---

This deployment strategy provides a comprehensive roadmap for taking your IDS from prototype to production, addressing real-world industrial constraints and requirements.
