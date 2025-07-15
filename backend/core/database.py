"""
Database configuration and session management for Sophia AI
Supports PostgreSQL with SQLAlchemy for user management and application data
"""

import os
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
from contextlib import contextmanager

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = None
engine = None
SessionLocal = None
Base = declarative_base()

def init_database():
    """Initialize database connection and configuration"""
    global DATABASE_URL, engine, SessionLocal
    
    try:
        # Get database configuration from Pulumi ESC
        db_host = get_config_value("postgres_host", "localhost")
        db_port = get_config_value("postgres_port", "5432")
        db_name = get_config_value("postgres_database", "sophia_ai")
        db_user = get_config_value("postgres_user", "sophia")
        db_password = get_config_value("postgres_password", "default_password")
        
        # Construct database URL
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Create engine with connection pooling
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Fallback to SQLite for development
        DATABASE_URL = "sqlite:///./sophia_ai.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.warning("⚠️ Using SQLite fallback database")
        return False

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session
    Ensures proper session management and cleanup
    """
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_session():
    """
    Context manager for database sessions outside FastAPI
    """
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        if engine is None:
            init_database()
        
        # Import all models to ensure they're registered
        from backend.models.user import User, UserActivity, UserSession, UserPreferences
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise

def check_database_health() -> dict:
    """Check database connection health"""
    try:
        if engine is None:
            init_database()
            
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            result.fetchone()
            
        return {
            "status": "healthy",
            "database_url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "sqlite",
            "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else "N/A",
            "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else "N/A"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": "unknown"
        }

# Initialize on import
if not engine:
    init_database() 