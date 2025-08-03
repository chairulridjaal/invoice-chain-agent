# ☁️ Cloud Deployment Guide

## 🚀 Best Cloud Hosting Options for Invoice Chain Agent

### **Recommended Options (Tested & Reliable)**

---

## 1. 🌊 **DigitalOcean App Platform** (Recommended)

**Cost**: $5-12/month | **Setup Time**: 15 minutes | **Difficulty**: Beginner

### Why DigitalOcean?

- ✅ Simple GitHub integration
- ✅ Python-friendly environment
- ✅ Auto-scaling and SSL
- ✅ Reliable uptime
- ✅ Clear pricing

### Setup Steps:

1. **Create DigitalOcean Account**: [digitalocean.com](https://digitalocean.com)

2. **Prepare Your Repository**:

```bash
# Create requirements.txt in project root
cd /path/to/invoice-chain-agent
pip freeze > requirements.txt

# Create .do/app.yaml configuration
mkdir .do
```

3. **Create App Configuration** (`.do/app.yaml`):

```yaml
name: invoice-chain-agent
services:
  - name: backend
    source_dir: /
    github:
      repo: your-username/invoice-chain-agent
      branch: main
    run_command: cd backend && gunicorn wsgi:application --bind 0.0.0.0:$PORT
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: OPENAI_API_KEY
        value: your_openai_api_key
      - key: CANISTER_ID
        value: your_canister_id
      - key: ICP_NETWORK
        value: testnet
      - key: PORT
        value: "8080"
  - name: frontend
    source_dir: /frontend
    build_command: npm install && npm run build
    run_command: npx serve -s dist -p $PORT
    environment_slug: node-js
    instance_count: 1
    instance_size_slug: basic-xxs
```

4. **Deploy**:
   - Go to DigitalOcean Apps
   - Connect GitHub repo
   - Choose auto-deploy on push
   - Configure environment variables

**Monthly Cost**: ~$10 for both backend + frontend

---

## 2. ☁️ **Google Cloud Run** (Serverless)

**Cost**: $2-10/month (pay-per-use) | **Setup Time**: 20 minutes | **Difficulty**: Intermediate

### Why Google Cloud Run?

- ✅ Pay only when used
- ✅ Auto-scaling to zero
- ✅ Enterprise-grade infrastructure
- ✅ Docker-based deployment

### Setup Steps:

1. **Create Dockerfile**:

```dockerfile
# Backend Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY .env .

EXPOSE 8080
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8080"]
```

2. **Deploy with Cloud Run**:

```bash
# Install gcloud CLI
# Build and deploy
gcloud run deploy invoice-chain-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Set Environment Variables** in Cloud Run console

**Monthly Cost**: ~$5 for moderate usage

---

## 3. 🔵 **Azure Container Instances**

**Cost**: $5-15/month | **Setup Time**: 25 minutes | **Difficulty**: Intermediate

### Why Azure?

- ✅ Microsoft ecosystem integration
- ✅ Enterprise features
- ✅ Good Python support
- ✅ Container-based deployment

### Setup Steps:

1. **Create Azure Resource Group**
2. **Deploy Container**:

```bash
az container create \
  --resource-group invoice-agent \
  --name invoice-chain-agent \
  --image your-docker-image \
  --ports 8080 \
  --environment-variables \
    OPENAI_API_KEY=your_key \
    CANISTER_ID=your_canister
```

**Monthly Cost**: ~$12 with basic plan

---

## 4. ⚡ **AWS Elastic Beanstalk**

**Cost**: $5-20/month | **Setup Time**: 30 minutes | **Difficulty**: Intermediate

### Why AWS?

- ✅ Industry standard
- ✅ Highly scalable
- ✅ Extensive ecosystem
- ✅ Enterprise-ready

### Setup Steps:

1. **Install EB CLI**:

```bash
pip install awsebcli
```

2. **Initialize and Deploy**:

```bash
cd backend
eb init
eb create invoice-chain-agent
eb deploy
```

3. **Configure Environment Variables** in EB console

**Monthly Cost**: ~$15 with t3.micro instance

---

## 📋 **Quick Comparison**

| Platform             | Monthly Cost | Setup Time | Difficulty   | Best For                       |
| -------------------- | ------------ | ---------- | ------------ | ------------------------------ |
| **DigitalOcean**     | $5-12        | 15 min     | Beginner     | **Small to medium projects**   |
| **Google Cloud Run** | $2-10        | 20 min     | Intermediate | **Variable traffic**           |
| **Azure**            | $5-15        | 25 min     | Intermediate | **Enterprise/Microsoft stack** |
| **AWS**              | $5-20        | 30 min     | Intermediate | **High scalability needs**     |

---

## 🔧 **Pre-Deployment Checklist**

### 1. **Environment Variables Required**:

```env
OPENAI_API_KEY=your_openrouter_api_key
CANISTER_ID=your_icp_canister_id
ICP_NETWORK=testnet
PORT=8080
FLASK_ENV=production
```

### 2. **Files to Create**:

- [ ] `requirements.txt` in project root
- [ ] Production WSGI configuration
- [ ] Environment-specific configs
- [ ] Health check endpoints

### 3. **Optional Enhancements**:

- [ ] Custom domain setup
- [ ] SSL certificate configuration
- [ ] CDN for static assets
- [ ] Database connection (if needed)
- [ ] Monitoring and logging

---

## 🎯 **Recommended Deployment Flow**

### **For Beginners**: Start with **DigitalOcean App Platform**

1. Push your code to GitHub
2. Connect DigitalOcean to your repo
3. Configure environment variables
4. Deploy with auto-SSL and custom domain

### **For Cost Optimization**: Use **Google Cloud Run**

1. Containerize your application
2. Deploy to Cloud Run
3. Configure automatic scaling
4. Pay only for actual usage

### **For Enterprise**: Use **AWS Elastic Beanstalk**

1. Set up AWS account with proper IAM
2. Deploy via EB CLI
3. Configure auto-scaling groups
4. Set up monitoring and alerts

---

## 🔍 **Next Steps After Deployment**

1. **Test Your Deployed API**:

```bash
curl https://your-deployed-url.com/health
curl -X POST https://your-deployed-url.com/submit \
  -H "Content-Type: application/json" \
  -d '{"invoice_id": "TEST-001", "vendor_name": "Test Corp", "amount": 1000}'
```

2. **Set Up Monitoring**:

   - Configure uptime monitoring
   - Set up error logging
   - Monitor API response times

3. **Configure Domain** (Optional):

   - Point custom domain to your deployment
   - Set up SSL certificate
   - Configure CDN if needed

4. **Scale As Needed**:
   - Monitor usage patterns
   - Adjust instance sizes
   - Set up auto-scaling rules

---

**💡 Pro Tip**: Start with DigitalOcean App Platform for simplicity, then migrate to Google Cloud Run if you need more cost optimization or AWS if you need enterprise features.

All these platforms offer free tiers or credits for new users, so you can test before committing!
