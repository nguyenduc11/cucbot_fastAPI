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

# Add CORS middleware to allow cross-origin requests
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

@app.get("/")
def read_root():
    return {"Message": "Hello World"}

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies MongoDB connection and lists databases"""
    try:
        # Test cluster connection
        from .database import db_manager
        await db_manager.client.admin.command('ping')
        
        # Get list of databases
        db_list = await db_manager.client.list_database_names()
        
        # Test specific database connections
        grade3_db = get_database("grade3")
        flashcard_db = get_database("flashcard")
        
        return {
            "status": "healthy", 
            "cluster": "connected",
            "available_databases": db_list,
            "configured_databases": {
                "grade3": "grade3",
                "flashcard": "flashcard"
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "cluster": "disconnected", "error": str(e)}
