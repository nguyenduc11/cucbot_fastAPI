# CORS Implementation for FastAPI Backend

## Problem
NetworkError when Vercel frontend tries to fetch from Render FastAPI backend due to missing CORS configuration.

## Solution: Add CORS Middleware to FastAPI

### 1. Update main.py
Add CORS middleware to allow cross-origin requests:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import connect_to_mongo, close_mongo_connection, get_database
from .routers import teacher_notes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cucbot.vercel.app",  # Your production Vercel domain
        "https://*.vercel.app",       # Vercel preview deployments
        "http://localhost:3000",      # Local development
        "http://127.0.0.1:3000",      # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(teacher_notes.router)
```

### 2. Render Deployment Steps
1. Update the FastAPI code with CORS middleware
2. Commit and push changes to trigger Render deployment
3. Verify deployment completes successfully
4. Test API endpoints directly on Render

### 3. Verification Steps
1. Test `/health` endpoint directly: `https://cucbotapi.onrender.com/health`
2. Test teacher notes endpoint: `https://cucbotapi.onrender.com/teacher_notes/recent`
3. Test from Vercel frontend - NetworkError should be resolved
4. Check browser developer tools for any remaining CORS errors

### 4. Environment Variables on Render
Ensure these are set:
- `MONGODB_URL`: Your MongoDB connection string
- `FLASK_WEB_DATABASE_NAME`: flask_web
- Other database names as needed

### 5. Alternative CORS Configuration (if needed)
For development, you can use wildcard origins:
```python
allow_origins=["*"]  # Only for development/testing
```

But for production, specify exact domains for security.
