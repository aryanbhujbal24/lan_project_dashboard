# 🚀 Deployment Guide

Complete guide for deploying the LAN Project Control Dashboard on various platforms.

## 📋 Table of Contents
1. [Local Deployment](#local-deployment)
2. [Streamlit Community Cloud (Free)](#streamlit-community-cloud)
3. [Heroku Deployment](#heroku-deployment)
4. [Docker Deployment](#docker-deployment)
5. [AWS Deployment](#aws-deployment)
6. [Azure Deployment](#azure-deployment)

---

## 🏠 Local Deployment

### Quick Start

```bash
# 1. Navigate to project directory
cd lan_project_dashboard

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
streamlit run app.py
```

### Access the Dashboard
- Open browser: `http://localhost:8501`
- The dashboard will auto-reload on code changes

### Running on Different Port
```bash
streamlit run app.py --server.port 8080
```

### Running in Production Mode
```bash
streamlit run app.py --server.headless true
```

---

## ☁️ Streamlit Community Cloud (Free)

**Best option for free hosting with zero configuration!**

### Prerequisites
- GitHub account
- Git installed locally

### Steps

1. **Push Code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/lan-dashboard.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud:**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign in with GitHub
- Click "New app"
- Select your repository
- Main file: `app.py`
- Click "Deploy"

3. **Configure Secrets (if needed):**
- Go to App settings → Secrets
- Add any API keys or sensitive data

4. **Custom Domain (Optional):**
- Available on Team and Enterprise plans
- Configure in app settings

### Features
✅ Free hosting  
✅ Automatic HTTPS  
✅ Easy updates (just push to GitHub)  
✅ Built-in monitoring  
✅ Community support

### Limitations
⚠️ Limited to 1GB RAM on free tier  
⚠️ App sleeps after inactivity  
⚠️ No custom domain on free tier

---

## 🔴 Heroku Deployment

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed

### Setup Files

**1. Create `Procfile`:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**2. Create `setup.sh`:**
```bash
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

**3. Update `requirements.txt`:**
Ensure all dependencies are listed with versions.

### Deployment Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create new app
heroku create your-app-name

# 3. Deploy
git init
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 4. Open app
heroku open
```

### Configuration

```bash
# Set environment variables
heroku config:set VARIABLE_NAME=value

# View logs
heroku logs --tail

# Scale dynos
heroku ps:scale web=1
```

### Cost
- **Free Tier:** 550 dyno hours/month, sleeps after 30 min
- **Hobby:** $7/month, no sleeping
- **Professional:** $25-500/month, advanced features

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t lan-dashboard .

# Run container
docker run -p 8501:8501 lan-dashboard

# Or use docker-compose
docker-compose up -d
```

### Deploy to Docker Hub

```bash
# Tag image
docker tag lan-dashboard yourusername/lan-dashboard:latest

# Push to Docker Hub
docker push yourusername/lan-dashboard:latest
```

---

## ☁️ AWS Deployment

### Option 1: AWS Elastic Beanstalk

**1. Install EB CLI:**
```bash
pip install awsebcli
```

**2. Initialize and Deploy:**
```bash
# Initialize
eb init -p python-3.9 lan-dashboard

# Create environment
eb create lan-dashboard-env

# Deploy updates
eb deploy

# Open application
eb open
```

**3. Configure Environment:**
```bash
# Set environment variables
eb setenv VARIABLE_NAME=value
```

### Option 2: AWS EC2

**1. Launch EC2 Instance:**
- Choose Amazon Linux 2 or Ubuntu
- Select t2.micro (free tier)
- Configure security group (allow port 8501)

**2. Connect and Setup:**
```bash
# SSH to instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python
sudo yum install python3 -y
# or
sudo apt install python3-pip -y

# Clone repository
git clone your-repo-url
cd lan_project_dashboard

# Install dependencies
pip3 install -r requirements.txt

# Run application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**3. Run as Service (systemd):**

Create `/etc/systemd/system/dashboard.service`:
```ini
[Unit]
Description=LAN Dashboard
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/lan_project_dashboard
ExecStart=/usr/local/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable dashboard
sudo systemctl start dashboard
sudo systemctl status dashboard
```

### Option 3: AWS Lightsail

1. Create Lightsail instance (Linux/Unix)
2. Use blueprint: "Amazon Linux 2"
3. Follow EC2 setup steps above
4. Configure networking to allow port 8501

### Cost Estimates
- **EC2 t2.micro:** Free tier eligible (750 hours/month for 12 months)
- **Elastic Beanstalk:** No additional charge (pay for underlying resources)
- **Lightsail:** Starting at $3.50/month

---

## 🌐 Azure Deployment

### Option 1: Azure App Service

**1. Install Azure CLI:**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**2. Deploy:**
```bash
# Login
az login

# Create resource group
az group create --name lan-dashboard-rg --location eastus

# Create app service plan
az appservice plan create --name lan-dashboard-plan --resource-group lan-dashboard-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group lan-dashboard-rg --plan lan-dashboard-plan --name lan-dashboard-app --runtime "PYTHON|3.9"

# Deploy code
az webapp up --name lan-dashboard-app --resource-group lan-dashboard-rg
```

**3. Configure:**
```bash
# Set startup command
az webapp config set --resource-group lan-dashboard-rg --name lan-dashboard-app --startup-file "streamlit run app.py --server.port 8000 --server.address 0.0.0.0"
```

### Option 2: Azure Container Instances

```bash
# Create container registry
az acr create --resource-group lan-dashboard-rg --name landashboardregistry --sku Basic

# Build and push image
az acr build --registry landashboardregistry --image lan-dashboard:v1 .

# Create container instance
az container create --resource-group lan-dashboard-rg --name lan-dashboard-container --image landashboardregistry.azurecr.io/lan-dashboard:v1 --cpu 1 --memory 1 --ports 8501 --dns-name-label lan-dashboard
```

---

## 🔒 Security Best Practices

### 1. Environment Variables
Never commit sensitive data. Use environment variables:

```python
import os
API_KEY = os.getenv('API_KEY')
```

### 2. Authentication
Add authentication for production:

```python
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == os.getenv("DASHBOARD_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # Your dashboard code here
    main()
```

### 3. HTTPS
- **Streamlit Cloud:** Automatic HTTPS
- **Heroku:** Automatic HTTPS
- **AWS/Azure:** Configure SSL certificate

### 4. Data Protection
- Encrypt sensitive data
- Use secure file storage
- Implement access controls

---

## 📊 Monitoring & Maintenance

### Logging

Add logging to your application:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Health Checks

Create health check endpoint:
```python
# In app.py
if st.sidebar.button("Health Check"):
    st.success("✅ Application is running")
    st.info(f"Last updated: {datetime.now()}")
```

### Performance Monitoring

- Use Streamlit's built-in performance monitoring
- Monitor resource usage (CPU, memory)
- Set up alerts for downtime

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/
    
    - name: Deploy to Streamlit Cloud
      run: |
        # Deployment handled automatically by Streamlit Cloud
        echo "Deployment triggered"
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Change port
streamlit run app.py --server.port 8502
```

**Module Not Found:**
```bash
pip install -r requirements.txt --upgrade
```

**Memory Issues:**
- Optimize data loading
- Use data caching
- Upgrade hosting plan

### Getting Help
- Check application logs
- Review error messages
- Consult platform documentation

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Test application locally
- [ ] Review security settings
- [ ] Set up environment variables
- [ ] Configure logging
- [ ] Test data loading
- [ ] Verify all dashboards work
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Document deployment process
- [ ] Set up CI/CD (optional)

---

**Need help?** Refer to the main README.md or check the platform-specific documentation.
