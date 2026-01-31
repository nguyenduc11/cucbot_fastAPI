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
        database_name = os.getenv("DEFAULT_DATABASE_NAME", "cucbot_db")
    
    # Cache database instances
    if database_name not in db_manager._databases:
        db_manager._databases[database_name] = db_manager.client[database_name]
    
    return db_manager._databases[database_name]

# Convenience functions for specific databases
def get_main_database():
    """Get main application database"""
    main_db_name = os.getenv("MAIN_DATABASE_NAME", "cucbot_main")
    return get_database(main_db_name)

def get_user_database():
    """Get user data database"""
    user_db_name = os.getenv("USER_DATABASE_NAME", "cucbot_users")
    return get_database(user_db_name)

def get_analytics_database():
    """Get analytics database"""
    analytics_db_name = os.getenv("ANALYTICS_DATABASE_NAME", "cucbot_analytics")
    return get_database(analytics_db_name)

def get_content_database():
    """Get content/educational database"""
    content_db_name = os.getenv("CONTENT_DATABASE_NAME", "cucbot_content")
    return get_database(content_db_name)
