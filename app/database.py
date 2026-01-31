import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class DatabaseManager:
    client: AsyncIOMotorClient = None
    
    def __init__(self):
        self.client = None
        self._databases = {}

# Global database manager instance
db_manager = DatabaseManager()

async def connect_to_mongo():
    """Create MongoDB client connection"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    print(f"Connecting to MongoDB cluster at: {mongodb_url}")
    
    # Create MongoDB client (connects to the cluster, not specific database)
    db_manager.client = AsyncIOMotorClient(mongodb_url)
    
    try:
        # Test the connection
        await db_manager.client.admin.command('ping')
        print("Successfully connected to MongoDB cluster")
        
        # List available databases for debugging
        db_list = await db_manager.client.list_database_names()
        print(f"Available databases: {db_list}")
        
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    if db_manager.client:
        db_manager.client.close()
        print("MongoDB connection closed")

def get_database(database_name: Optional[str] = None):
    """
    Get database instance by name
    
    Args:
        database_name: Name of the database. If None, uses default from env
    
    Returns:
        Database instance
    """
    if not db_manager.client:
        raise RuntimeError("Database client not initialized. Call connect_to_mongo() first.")
    
    # Use provided name or fall back to environment variable
    if database_name is None:
        database_name = os.getenv("GRADE3_DATABASE_NAME", "grade3")
    
    # Cache database instances
    if database_name not in db_manager._databases:
        db_manager._databases[database_name] = db_manager.client[database_name]
    
    return db_manager._databases[database_name]

# Convenience functions for specific databases
def get_auth_database():
    """Get authentication database"""
    auth_db_name = os.getenv("AUTH_DATABASE_NAME", "auth_db")
    return get_database(auth_db_name)

def get_english_database():
    """Get English grammar database"""
    english_db_name = os.getenv("ENGLISH_DATABASE_NAME", "english_grammar")
    return get_database(english_db_name)

def get_essays_database():
    """Get essays management database"""
    essays_db_name = os.getenv("ESSAYS_MANAGEMENT_DATABASE_NAME", "essays_management")
    return get_database(essays_db_name)

def get_flashcard_database():
    """Get flashcard database"""
    flashcard_db_name = os.getenv("FLASHCARD_DATABASE_NAME", "flashcard")
    return get_database(flashcard_db_name)

def get_flask_web_database():
    """Get flask web database"""
    flask_web_db_name = os.getenv("FLASK_WEB_DATABASE_NAME", "flask_web")
    return get_database(flask_web_db_name)

def get_grade3_database():
    """Get grade 3 educational database"""
    grade3_db_name = os.getenv("GRADE3_DATABASE_NAME", "grade3")
    return get_database(grade3_db_name)