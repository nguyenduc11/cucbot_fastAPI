# Fly.io Deployment Guide for FastAPI

## Prerequisites

1. Install the Fly CLI:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Or download from: https://fly.io/docs/hands-on/install-flyctl/
   ```

2. Sign up and authenticate:
   ```bash
   fly auth signup  # Create account
   fly auth login   # Login to existing account
   ```

## Deployment Steps

### 1. Initialize Fly App (Optional - files already created)
```bash
cd d:\DUC\FastAPI\cucbot_fastAPI
fly launch --no-deploy  # This will create fly.toml if it doesn't exist
```

### 2. Set Environment Variables
```bash
# Set your MongoDB connection string
fly secrets set MONGODB_URL="your-mongodb-connection-string"

# Set database names
fly secrets set FLASK_WEB_DATABASE_NAME="flask_web"
fly secrets set AUTH_DATABASE_NAME="auth_db"
fly secrets set ENGLISH_DATABASE_NAME="english_grammar"
fly secrets set ESSAYS_MANAGEMENT_DATABASE_NAME="essays_management"
fly secrets set FLASHCARD_DATABASE_NAME="flashcard"
fly secrets set GRADE3_DATABASE_NAME="grade3"
```

### 3. Deploy the Application
```bash
fly deploy
```

### 4. Check Deployment Status
```bash
fly status
fly logs
```

### 5. Open Your App
```bash
fly open
# Or visit: https://cucbot-fastapi.fly.dev
```

## Configuration Details

### Dockerfile
- Uses Python 3.12 slim image
- Installs `uv` for dependency management
- Runs on port 8000
- Uses `uv run uvicorn` command

### fly.toml
- App name: `cucbot-fastapi`
- Region: Singapore (sin) - closest to Vietnam
- Auto-scaling: 0-1 machines
- Health check: `/health` endpoint
- Memory: 256MB, 1 shared CPU

### Health Check
The deployment uses your existing `/health` endpoint for monitoring.

## Post-Deployment

### Update CORS Origins
After deployment, update your CORS configuration in `app/main.py`:

```python
allow_origins=[
    "https://cucbot.vercel.app",
    "https://*.vercel.app",
    "https://cucbot-fastapi.fly.dev",  # Add your Fly.io domain
    "http://localhost:3000",
    "http://127.0.0.1:3000",
],
```

### Update Frontend API Configuration
Update your Next.js API configuration to use the new Fly.io URL:
```javascript
BASE_URLS: {
    development: 'http://localhost:8000',
    production: 'https://cucbot-fastapi.fly.dev',  // Update this
    local_nextjs: '/api'
}
```

## Useful Commands

```bash
# View logs
fly logs

# Scale app
fly scale count 1

# SSH into machine
fly ssh console

# Check app status
fly status

# Update secrets
fly secrets list
fly secrets set KEY=value

# Redeploy
fly deploy
```

## Cost Optimization

- The configuration uses auto-scaling (0-1 machines)
- Machines automatically stop when idle
- Uses minimal resources (256MB RAM, 1 shared CPU)
- Should fit within Fly.io's free tier limits
