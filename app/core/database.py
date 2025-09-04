"""
Database configuration and connection management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from typing import AsyncGenerator

from app.core.config import settings

# PostgreSQL setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB setup
mongo_client: AsyncIOMotorClient = None
mongo_database = None

async def init_db():
    """Initialize database connections"""
    global mongo_client, mongo_database
    
    # Initialize MongoDB
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongo_database = mongo_client[settings.MONGODB_DATABASE]
    
    # Test MongoDB connection
    try:
        await mongo_client.admin.command('ping')
        print("✅ MongoDB connection established")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
    
    # Test PostgreSQL connection
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ PostgreSQL connection established")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")

def get_db():
    """Get PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_mongo_db():
    """Get MongoDB database instance"""
    return mongo_database

async def close_db():
    """Close database connections"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("🔌 Database connections closed")
