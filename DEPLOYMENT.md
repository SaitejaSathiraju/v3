# 🚀 Deployment Guide

This guide covers deploying the Face Recognition System to various platforms.

## 📋 Prerequisites

Before deploying, ensure you have:
- Python 3.8+ installed
- All dependencies installed (`pip install -r requirements.txt`)
- Your photo collection organized in `static/photos/`
- Configured the `PHOTOS_ROOT` path in your application files

## 🖥️ Local Development

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/face-recognition-system.git
cd face-recognition-system

# Install dependencies
pip install -r requirements.txt

# Configure photo directory path in app.py or v4.py
# Edit PHOTOS_ROOT = "your/path/to/photos"

# Run the application
python app.py
# or
python v4.py
```

The application will be available at `http://localhost:5000`

## ☁️ Cloud Deployment

### Heroku Deployment

1. **Create Heroku App**
   ```bash
   heroku create your-face-recognition-app
   ```

2. **Add Buildpacks**
   ```bash
   heroku buildpacks:add heroku/python
   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
   ```

3. **Create Aptfile**
   ```bash
   echo "cmake" > Aptfile
   echo "libboost-all-dev" >> Aptfile
   ```

4. **Create Procfile**
   ```bash
   echo "web: gunicorn app:app" > Procfile
   ```

5. **Add gunicorn to requirements.txt**
   ```bash
   echo "gunicorn==21.2.0" >> requirements.txt
   ```

6. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Minimum t3.medium (2 vCPU, 4GB RAM)
   - Attach EBS volume for photos

2. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-dev
   sudo apt-get install cmake libboost-all-dev
   sudo apt-get install nginx
   ```

3. **Setup Application**
   ```bash
   git clone https://github.com/yourusername/face-recognition-system.git
   cd face-recognition-system
   pip3 install -r requirements.txt
   pip3 install gunicorn
   ```

4. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/face-recognition
   ```

   Add configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/face-recognition /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Run with Gunicorn**
   ```bash
   gunicorn --bind 127.0.0.1:8000 app:app
   ```

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       cmake \
       libboost-all-dev \
       && rm -rf /var/lib/apt/lists/*

   # Set working directory
   WORKDIR /app

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Create directories
   RUN mkdir -p static/photos static/results static/uploads

   # Expose port
   EXPOSE 5000

   # Run the application
   CMD ["python", "app.py"]
   ```

2. **Build and Run**
   ```bash
   docker build -t face-recognition .
   docker run -p 5000:5000 -v /path/to/photos:/app/static/photos face-recognition
   ```

### Google Cloud Platform (GCP)

1. **Create App Engine Configuration**
   Create `app.yaml`:
   ```yaml
   runtime: python39
   entrypoint: gunicorn -b :$PORT app:app

   instance_class: F2

   automatic_scaling:
     target_cpu_utilization: 0.6
     min_instances: 1
     max_instances: 10

   env_variables:
     PHOTOS_ROOT: "/app/static/photos"
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

## 🔧 Production Configuration

### Environment Variables

Create a `.env` file for production:
```env
FLASK_ENV=production
FLASK_DEBUG=False
PHOTOS_ROOT=/path/to/photos
MAX_WORKERS=4
CACHE_ENABLED=True
```

### Security Considerations

1. **HTTPS Setup**
   - Use Let's Encrypt for free SSL certificates
   - Configure Nginx to redirect HTTP to HTTPS

2. **File Upload Limits**
   ```python
   app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
   ```

3. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address

   limiter = Limiter(
       app,
       key_func=get_remote_address,
       default_limits=["200 per day", "50 per hour"]
   )
   ```

### Performance Optimization

1. **Database Optimization**
   ```python
   # Use connection pooling
   import sqlite3
   from contextlib import contextmanager

   @contextmanager
   def get_db_connection():
       conn = sqlite3.connect(FACE_CACHE_DB, timeout=20)
       conn.execute('PRAGMA journal_mode=WAL')
       yield conn
       conn.close()
   ```

2. **Memory Management**
   ```python
   # Clear cache periodically
   import schedule
   import time

   def clear_old_cache():
       # Remove cache entries older than 30 days
       pass

   schedule.every().day.at("02:00").do(clear_old_cache)
   ```

3. **Load Balancing**
   - Use multiple Gunicorn workers
   - Configure Nginx upstream

## 📊 Monitoring

### Health Checks

Add a health check endpoint:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

### Logging

Configure structured logging:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/face_recognition.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Face Recognition startup')
```

## 🔍 Troubleshooting Deployment

### Common Issues

1. **Memory Errors**
   - Increase instance size
   - Reduce parallel workers
   - Implement memory monitoring

2. **Timeout Issues**
   - Increase timeout limits
   - Implement async processing
   - Use background tasks

3. **File Permission Errors**
   - Check file ownership
   - Ensure proper directory permissions
   - Use absolute paths

### Performance Monitoring

1. **CPU Usage**
   ```bash
   htop
   ```

2. **Memory Usage**
   ```bash
   free -h
   ```

3. **Disk Usage**
   ```bash
   df -h
   ```

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer Setup**
   - Use AWS ALB or GCP Load Balancer
   - Configure health checks
   - Set up auto-scaling groups

2. **Database Scaling**
   - Use PostgreSQL instead of SQLite
   - Implement read replicas
   - Use connection pooling

3. **File Storage**
   - Use S3 or GCS for photo storage
   - Implement CDN for static files
   - Use distributed file systems

---

For more detailed deployment instructions, refer to the platform-specific documentation.
