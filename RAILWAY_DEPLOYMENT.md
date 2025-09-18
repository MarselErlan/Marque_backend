# Railway Deployment Configuration for Marque API

## 🚀 **Railway Deployment Setup**

This configuration will deploy your Marque Phone Authentication API to Railway with production-ready settings.

---

## 📁 **Required Files**

### 1. **railway.json** - Railway Configuration

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python marque_api_production.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. **Procfile** - Process Definition

```
web: python marque_api_production.py
```

### 3. **requirements.txt** - Production Dependencies

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
PyJWT==2.8.0
twilio==8.10.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.1
dependency-injector==4.41.0
```

### 4. **runtime.txt** - Python Version

```
python-3.11.4
```

---

## 🔧 **Environment Variables**

Set these in Railway dashboard:

### **Twilio Configuration**

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_VERIFY_SERVICE_SID=your_twilio_verify_service_sid_here
```

### **Security**

```
SECRET_KEY=your-super-secure-production-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### **Environment**

```
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
```

### **Database (if using)**

```
DATABASE_URL_MARQUE_KG=postgresql://user:password@host:port/db_kg
DATABASE_URL_MARQUE_US=postgresql://user:password@host:port/db_us

```

---

## 🚀 **Deployment Steps**

### **Step 1: Prepare Files**

1. Create `railway.json`
2. Create `Procfile`
3. Update `requirements.txt`
4. Create `runtime.txt`

### **Step 2: Railway Setup**

1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Create new project
4. Select your Marque repository

### **Step 3: Configure Environment**

1. Go to Variables tab
2. Add all environment variables
3. Set `PORT=8000` (Railway default)

### **Step 4: Deploy**

1. Railway will auto-deploy on push
2. Check logs for any issues
3. Test your deployed API

---

## 📱 **Production API Endpoints**

Once deployed, your API will be available at:

```
https://your-app-name.railway.app
```

### **Test Endpoints:**

- Health: `GET /health`
- Send SMS: `POST /api/v1/auth/send-verification`
- Verify: `POST /api/v1/auth/verify-code`
- Profile: `GET /api/v1/users/profile`

---

## 🔒 **Security Checklist**

- ✅ **Environment Variables**: All secrets in Railway
- ✅ **HTTPS**: Railway provides SSL
- ✅ **JWT Security**: Production secret key
- ✅ **Rate Limiting**: Built-in protection
- ✅ **Input Validation**: Comprehensive validation
- ✅ **Error Handling**: Structured responses

---

## 📊 **Monitoring**

Railway provides:

- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, network
- **Health Checks**: Automatic monitoring
- **Alerts**: Failure notifications

---

## 🎯 **Ready for Production!**

Your Marque API will be:

- 🌐 **Publicly accessible** via HTTPS
- 📱 **SMS verification** working globally
- 🔐 **Secure** with production settings
- 📊 **Monitored** with Railway metrics
- 🚀 **Auto-scaling** based on demand

**Deploy to Railway and go live!** 🎉
