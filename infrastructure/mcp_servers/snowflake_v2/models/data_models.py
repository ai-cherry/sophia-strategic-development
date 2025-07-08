"""
Data models for Snowflake V2 MCP Server
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for query execution"""

    query: str = Field(..., description="SQL query to execute")
    parameters: dict[str, Any] | None = Field(
        default=None, description="Query parameters"
    )
    fetch_results: bool = Field(default=True, description="Whether to fetch results")
    warehouse: str | None = Field(default=None, description="Warehouse to use")
    timeout: int | None = Field(default=300, description="Query timeout in seconds")


class QueryResponse(BaseModel):
    """Response model for query execution"""

    success: bool
    data: list[dict[str, Any]] | None = None
    row_count: int = 0
    execution_time: float = 0.0
    query_id: str | None = None
    error: str | None = None


class SchemaRequest(BaseModel):
    """Request model for schema creation"""

    name: str = Field(..., description="Schema name")
    database: str = Field(default="SOPHIA_AI_CORE", description="Database name")
    comment: str | None = Field(default=None, description="Schema comment")
    create_ai_tables: bool = Field(default=True, description="Create AI-ready tables")


class ColumnDefinition(BaseModel):
    """Column definition for table creation"""

    name: str
    type: str
    not_null: bool = False
    default: str | None = None
    comment: str | None = None


class TableRequest(BaseModel):
    """Request model for table creation"""

    name: str = Field(..., description="Table name")
    schema: str = Field(..., description="Schema name")
    database: str = Field(default="SOPHIA_AI_CORE", description="Database name")
    columns: list[dict[str, Any]] = Field(..., description="Column definitions")
    cluster_by: list[str] | None = Field(default=None, description="Clustering keys")
    add_ai_columns: bool = Field(default=True, description="Add AI-ready columns")
    comment: str | None = Field(default=None, description="Table comment")


class DataLoadRequest(BaseModel):
    """Request model for data loading"""

    target_table: str = Field(..., description="Target table for data load")
    source_type: str = Field(..., description="Source type (file, stage, table)")
    source_path: str = Field(..., description="Source path or location")
    file_format: str | None = Field(default="CSV", description="File format")
    options: dict[str, Any] | None = Field(default=None, description="Load options")
    transform_sql: str | None = Field(default=None, description="Transformation SQL")


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation"""

    table: str = Field(..., description="Table to update with embeddings")
    text_column: str = Field(..., description="Column containing text to embed")
    embedding_column: str = Field(
        default="ai_embeddings", description="Column to store embeddings"
    )
    model: str = Field(
        default="snowflake-arctic-embed-m-v2.0", description="Embedding model"
    )
    where_clause: str | None = Field(
        default=None, description="WHERE clause to filter rows"
    )
    batch_size: int = Field(default=1000, description="Batch size for processing")


class SearchRequest(BaseModel):
    """Request model for semantic search"""

    query: str = Field(..., description="Search query")
    table: str = Field(..., description="Table to search")
    embedding_column: str = Field(
        default="ai_embeddings", description="Embedding column"
    )
    return_columns: list[str] = Field(default=["*"], description="Columns to return")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold")
    limit: int = Field(default=10, description="Maximum results to return")


class OptimizationRequest(BaseModel):
    """Request model for performance optimization"""

    apply_clustering: bool = Field(default=True, description="Apply clustering keys")
    clustering_keys: dict[str, list[str]] = Field(
        default={}, description="Table: clustering keys"
    )
    analyze_tables: bool = Field(default=True, description="Analyze table statistics")
    tables_to_analyze: list[str] = Field(default=[], description="Tables to analyze")
    optimize_warehouse: bool = Field(
        default=False, description="Optimize warehouse settings"
    )


class WarehouseAction(BaseModel):
    """Warehouse management action"""

    action: str = Field(..., description="Action to perform (resume, suspend, resize)")
    warehouse: str | None = Field(default=None, description="Warehouse name")
    size: str | None = Field(default=None, description="New size for resize action")


class SystemStatus(BaseModel):
    """System status response"""

    timestamp: datetime
    connection: str
    current_context: dict[str, str]
    statistics: dict[str, Any]
    warehouses: list[dict[str, Any]] | None = None
    error: str | None = None


class AIProcessingResult(BaseModel):
    """Result of AI processing operations"""

    success: bool
    operation: str
    rows_processed: int = 0
    processing_time: float = 0.0
    metadata: dict[str, Any] | None = None
    error: str | None = None
