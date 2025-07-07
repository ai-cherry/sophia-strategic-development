"""Database helpers for ai_memory_v2 MCP server."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Index
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector

from infrastructure.mcp_servers.ai_memory_v2.config import settings

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


class MemoryTable(Base):
    """SQLAlchemy model for memory entries."""
    __tablename__ = "memory_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    category = Column(String(50), nullable=False, default="general")
    metadata = Column(JSON, nullable=False, default={})
    tags = Column(ARRAY(String), nullable=False, default=[])
    source = Column(String(100), nullable=True)
    user_id = Column(String(100), nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_memory_category', 'category'),
        Index('idx_memory_user', 'user_id'),
        Index('idx_memory_created', 'created_at'),
        # Vector index will be created separately with pgvector
    )


async def get_engine() -> AsyncEngine:
    """Get or create the database engine."""
    global _engine
    
    if _engine is None:
        _engine = create_async_engine(
            settings.DB_DSN,
            pool_size=settings.DB_POOL_MIN,
            max_overflow=settings.DB_POOL_MAX - settings.DB_POOL_MIN,
            pool_pre_ping=True,
            echo=settings.LOG_LEVEL == "DEBUG"
        )
        logger.info("Created database engine")
    
    return _engine


async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory."""
    global _session_factory
    
    if _session_factory is None:
        engine = await get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Created session factory")
    
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    factory = await get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize the database."""
    engine = await get_engine()
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Create pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Create vector index for similarity search
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_embedding 
            ON memory_entries 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
    
    logger.info("Database initialized")


async def close_db() -> None:
    """Close database connections."""
    global _engine, _session_factory
    
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")


async def check_db_health() -> bool:
    """Check database health."""
    try:
        async with get_session() as session:
            result = await session.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
