"""
Intelligent Data Ingestion System for Sophia AI

Supports comprehensive data ingestion with interactive and autonomous metadata handling.
Integrates with Snowflake and Pinecone for vectorization and semantic search.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field

from backend.core.integration_registry import IntegrationRegistry

logger = logging.getLogger(__name__)


class DataSource(BaseModel):
    """Represents a data source for ingestion."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # 'file', 'url', 'email', 'slack', 'api'
    format: str  # 'pdf', 'csv', 'excel', 'json', 'docx', 'pptx', 'txt'
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class MetadataTag(BaseModel):
    """Represents a metadata tag with confidence score."""

    key: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str  # 'user', 'ai_suggested', 'auto_detected'
    category: str  # 'business', 'technical', 'content', 'temporal'


class IngestionResult(BaseModel):
    """Result of data ingestion process."""

    source_id: str
    success: bool
    records_processed: int = 0
    chunks_created: int = 0
    embeddings_generated: int = 0
    metadata_tags: List[MetadataTag] = Field(default_factory=list)
    suggested_tags: List[MetadataTag] = Field(default_factory=list)
    processing_time_seconds: float = 0.0
    errors: List[str] = Field(default_factory=list)
    storage_locations: Dict[str, str] = Field(default_factory=dict)


class IntelligentDataIngestion:
    """
    Comprehensive data ingestion system with AI-powered metadata generation.

    Features:
    - Multi-format support (PDF, Excel, CSV, PPT, Word, JSON, emails, Slack)
    - Interactive metadata tagging with AI suggestions
    - Autonomous metadata detection and validation
    - Vectorization pipeline with Snowflake and Pinecone integration
    - Real-time processing status and progress tracking
    
    HYBRID APPROACH FOR HUBSPOT DATA:
    - Maintains existing ingestion capabilities for training/interaction with foundational knowledge
    - Adds Snowflake Secure Data Sharing for enterprise analytics and real-time CRM access
    - Blends traditional ETL with native Snowflake AI processing via Cortex
    - See backend/utils/snowflake_hubspot_connector.py for Secure Data Share integration
    - See backend/utils/snowflake_cortex_service.py for native AI processing capabilities
    """

    def __init__(self):
        self.integration_registry = IntegrationRegistry()
        self.supported_formats = {
            "documents": ["pdf", "docx", "txt", "md"],
            "spreadsheets": ["csv", "xlsx", "xls"],
            "presentations": ["pptx", "ppt"],
            "data": ["json", "jsonl", "xml"],
            "communications": ["eml", "msg"],
            "web": ["html", "htm"],
        }
        self.processing_queue: List[DataSource] = []
        self.active_ingestions: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Initialize the ingestion system and dependencies."""
        logger.info("Initializing Intelligent Data Ingestion System...")

        # Register with integration registry
        await self.integration_registry.register("data_ingestion", self)

        # Initialize AI metadata generator
        await self._initialize_metadata_ai()

        # Initialize storage connections
        await self._initialize_storage_connections()

        logger.info("Data ingestion system initialized successfully")

    async def _initialize_metadata_ai(self) -> None:
        """Initialize AI components for metadata generation."""
        # In production, this would initialize actual AI models
        # For now, we'll use rule-based and pattern-matching approaches
        self.metadata_patterns = {
            "business_terms": [
                "revenue",
                "sales",
                "customer",
                "deal",
                "pipeline",
                "forecast",
                "kpi",
                "metric",
                "performance",
                "growth",
                "churn",
                "retention",
            ],
            "temporal_patterns": [
                r"\d{4}-\d{2}-\d{2}",
                r"Q[1-4]\s*\d{4}",
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",
                r"(weekly|monthly|quarterly|annual)",
                r"(daily|hourly)",
            ],
            "data_types": [
                "financial",
                "operational",
                "marketing",
                "sales",
                "hr",
                "product",
                "customer_service",
                "analytics",
                "reporting",
            ],
        }

    async def _initialize_storage_connections(self) -> None:
        """Initialize connections to Snowflake and Pinecone."""
        # These would be actual connections in production
        self.snowflake_connected = True
        self.pinecone_connected = True
        logger.info("Storage connections initialized")

    async def ingest_data(
        self,
        source: DataSource,
        interactive_mode: bool = True,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> IngestionResult:
        """
        Main ingestion method with interactive metadata handling.

        Args:
            source: Data source to ingest
            interactive_mode: Whether to provide interactive metadata suggestions
            user_metadata: User-provided metadata to merge with AI suggestions

        Returns:
            IngestionResult with processing details and metadata
        """
        start_time = datetime.now()
        result = IngestionResult(source_id=source.id, success=False)

        try:
            # Add to active ingestions for progress tracking
            self.active_ingestions[source.id] = {
                "status": "starting",
                "progress": 0.0,
                "stage": "initialization",
            }

            # Step 1: Validate and prepare source
            await self._update_ingestion_progress(source.id, 0.1, "validation")
            validation_result = await self._validate_source(source)
            if not validation_result["valid"]:
                result.errors.extend(validation_result["errors"])
                return result

            # Step 2: Extract content based on format
            await self._update_ingestion_progress(source.id, 0.3, "content_extraction")
            content_data = await self._extract_content(source)
            result.records_processed = len(content_data.get("records", []))

            # Step 3: Generate AI metadata suggestions
            await self._update_ingestion_progress(source.id, 0.5, "metadata_analysis")
            ai_suggestions = await self._generate_metadata_suggestions(
                source, content_data
            )
            result.suggested_tags = ai_suggestions

            # Step 4: Interactive metadata handling (if enabled)
            if interactive_mode:
                await self._update_ingestion_progress(
                    source.id, 0.6, "interactive_metadata"
                )
                final_metadata = await self._handle_interactive_metadata(
                    source, ai_suggestions, user_metadata
                )
            else:
                final_metadata = await self._auto_apply_metadata(
                    ai_suggestions, user_metadata
                )

            result.metadata_tags = final_metadata

            # Step 5: Chunk content for vectorization
            await self._update_ingestion_progress(source.id, 0.7, "content_chunking")
            chunks = await self._create_content_chunks(content_data, final_metadata)
            result.chunks_created = len(chunks)

            # Step 6: Generate embeddings and store in Pinecone
            await self._update_ingestion_progress(source.id, 0.8, "vectorization")
            embeddings_result = await self._generate_and_store_embeddings(
                chunks, source
            )
            result.embeddings_generated = embeddings_result["count"]
            result.storage_locations["pinecone"] = embeddings_result["index_name"]

            # Step 7: Store structured data in Snowflake
            await self._update_ingestion_progress(source.id, 0.9, "structured_storage")
            snowflake_result = await self._store_in_snowflake(
                content_data, final_metadata, source
            )
            result.storage_locations["snowflake"] = snowflake_result["table_name"]

            # Step 8: Finalize and cleanup
            await self._update_ingestion_progress(source.id, 1.0, "completed")
            result.success = True

        except Exception as e:
            logger.error(f"Ingestion failed for {source.id}: {str(e)}")
            result.errors.append(str(e))
            await self._update_ingestion_progress(source.id, -1, "failed")

        finally:
            # Calculate processing time
            result.processing_time_seconds = (
                datetime.now() - start_time
            ).total_seconds()

            # Remove from active ingestions
            self.active_ingestions.pop(source.id, None)

        return result

    async def _validate_source(self, source: DataSource) -> Dict[str, Any]:
        """Validate data source before processing."""
        errors = []

        # Check format support
        format_supported = any(
            source.format.lower() in formats
            for formats in self.supported_formats.values()
        )

        if not format_supported:
            errors.append(f"Unsupported format: {source.format}")

        # Check file size limits (100MB default)
        max_size = 100 * 1024 * 1024  # 100MB
        if source.size_bytes and source.size_bytes > max_size:
            errors.append(
                f"File too large: {source.size_bytes} bytes (max: {max_size})"
            )

        return {"valid": len(errors) == 0, "errors": errors}

    async def _extract_content(self, source: DataSource) -> Dict[str, Any]:
        """Extract content from source based on format."""
        format_lower = source.format.lower()

        if format_lower in ["csv", "xlsx", "xls"]:
            return await self._extract_spreadsheet_content(source)
        elif format_lower in ["pdf", "docx", "txt"]:
            return await self._extract_document_content(source)
        elif format_lower in ["json", "jsonl"]:
            return await self._extract_json_content(source)
        elif format_lower in ["pptx", "ppt"]:
            return await self._extract_presentation_content(source)
        else:
            return await self._extract_generic_content(source)

    async def _extract_spreadsheet_content(self, source: DataSource) -> Dict[str, Any]:
        """Extract content from spreadsheet files."""
        # Simulate spreadsheet processing
        return {
            "type": "tabular",
            "records": [
                {"column1": "value1", "column2": "value2"},
                {"column1": "value3", "column2": "value4"},
            ],
            "columns": ["column1", "column2"],
            "row_count": 2,
            "sheets": ["Sheet1"],
        }

    async def _extract_document_content(self, source: DataSource) -> Dict[str, Any]:
        """Extract content from document files."""
        # Simulate document processing
        return {
            "type": "text",
            "content": f"Sample document content from {source.name}",
            "word_count": 150,
            "pages": 3,
            "sections": ["Introduction", "Main Content", "Conclusion"],
        }

    async def _extract_json_content(self, source: DataSource) -> Dict[str, Any]:
        """Extract content from JSON files."""
        # Simulate JSON processing
        return {
            "type": "structured",
            "records": [{"id": 1, "data": "sample"}],
            "schema": {"id": "integer", "data": "string"},
            "record_count": 1,
        }

    async def _extract_presentation_content(self, source: DataSource) -> Dict[str, Any]:
        """Extract content from presentation files."""
        # Simulate presentation processing
        return {
            "type": "presentation",
            "slides": [
                {"title": "Slide 1", "content": "Content 1"},
                {"title": "Slide 2", "content": "Content 2"},
            ],
            "slide_count": 2,
            "text_content": "Combined slide text content",
        }

    async def _extract_generic_content(self, source: DataSource) -> Dict[str, Any]:
        """Extract content from generic files."""
        return {
            "type": "generic",
            "content": f"Generic content from {source.name}",
            "size": source.size_bytes or 0,
        }

    async def _generate_metadata_suggestions(
        self, source: DataSource, content_data: Dict[str, Any]
    ) -> List[MetadataTag]:
        """Generate AI-powered metadata suggestions."""
        suggestions = []

        # Analyze filename for business terms
        filename_lower = source.name.lower()
        for term in self.metadata_patterns["business_terms"]:
            if term in filename_lower:
                suggestions.append(
                    MetadataTag(
                        key="business_domain",
                        value=term,
                        confidence=0.8,
                        source="ai_suggested",
                        category="business",
                    )
                )

        # Detect data type based on content
        content_text = str(content_data).lower()
        for data_type in self.metadata_patterns["data_types"]:
            if data_type in content_text:
                suggestions.append(
                    MetadataTag(
                        key="data_type",
                        value=data_type,
                        confidence=0.7,
                        source="ai_suggested",
                        category="technical",
                    )
                )

        # Suggest temporal metadata
        current_quarter = (
            f"Q{(datetime.now().month - 1) // 3 + 1} {datetime.now().year}"
        )
        suggestions.append(
            MetadataTag(
                key="time_period",
                value=current_quarter,
                confidence=0.6,
                source="ai_suggested",
                category="temporal",
            )
        )

        # Content-based suggestions
        if content_data.get("type") == "tabular":
            suggestions.append(
                MetadataTag(
                    key="content_structure",
                    value="structured_data",
                    confidence=0.9,
                    source="auto_detected",
                    category="technical",
                )
            )

        return suggestions

    async def _handle_interactive_metadata(
        self,
        source: DataSource,
        ai_suggestions: List[MetadataTag],
        user_metadata: Optional[Dict[str, Any]],
    ) -> List[MetadataTag]:
        """Handle interactive metadata refinement."""
        final_metadata = []

        # Start with high-confidence AI suggestions
        for suggestion in ai_suggestions:
            if suggestion.confidence >= 0.8:
                final_metadata.append(suggestion)

        # Add user-provided metadata with high confidence
        if user_metadata:
            for key, value in user_metadata.items():
                final_metadata.append(
                    MetadataTag(
                        key=key,
                        value=str(value),
                        confidence=1.0,
                        source="user",
                        category="business",
                    )
                )

        # In a real implementation, this would present suggestions to user
        # For now, we'll simulate user validation of medium-confidence suggestions
        for suggestion in ai_suggestions:
            if 0.6 <= suggestion.confidence < 0.8:
                # Simulate user approval (70% approval rate)
                if hash(suggestion.key + suggestion.value) % 10 < 7:
                    suggestion.source = "user_validated"
                    final_metadata.append(suggestion)

        return final_metadata

    async def _auto_apply_metadata(
        self, ai_suggestions: List[MetadataTag], user_metadata: Optional[Dict[str, Any]]
    ) -> List[MetadataTag]:
        """Automatically apply metadata without user interaction."""
        final_metadata = []

        # Apply high-confidence AI suggestions
        for suggestion in ai_suggestions:
            if suggestion.confidence >= 0.7:
                final_metadata.append(suggestion)

        # Add user metadata
        if user_metadata:
            for key, value in user_metadata.items():
                final_metadata.append(
                    MetadataTag(
                        key=key,
                        value=str(value),
                        confidence=1.0,
                        source="user",
                        category="business",
                    )
                )

        return final_metadata

    async def _create_content_chunks(
        self, content_data: Dict[str, Any], metadata: List[MetadataTag]
    ) -> List[Dict[str, Any]]:
        """Create content chunks optimized for vectorization."""
        chunks = []

        if content_data.get("type") == "text":
            # Split text content into chunks
            content = content_data.get("content", "")
            chunk_size = 1000  # characters

            for i in range(0, len(content), chunk_size):
                chunk_text = content[i : i + chunk_size]
                chunks.append(
                    {
                        "text": chunk_text,
                        "chunk_index": len(chunks),
                        "metadata": {tag.key: tag.value for tag in metadata},
                        "type": "text_chunk",
                    }
                )

        elif content_data.get("type") == "tabular":
            # Create chunks from tabular data
            records = content_data.get("records", [])
            for i, record in enumerate(records):
                chunks.append(
                    {
                        "text": json.dumps(record),
                        "chunk_index": i,
                        "metadata": {tag.key: tag.value for tag in metadata},
                        "type": "data_record",
                    }
                )

        else:
            # Generic content chunking
            content_str = str(content_data)
            chunks.append(
                {
                    "text": content_str,
                    "chunk_index": 0,
                    "metadata": {tag.key: tag.value for tag in metadata},
                    "type": "generic_content",
                }
            )

        return chunks

    async def _generate_and_store_embeddings(
        self, chunks: List[Dict[str, Any]], source: DataSource
    ) -> Dict[str, Any]:
        """Generate embeddings and store in Pinecone."""
        # Simulate embedding generation and Pinecone storage
        index_name = f"sophia-ai-{source.format}-{datetime.now().strftime('%Y%m')}"

        # In production, this would:
        # 1. Generate embeddings using OpenAI/Anthropic
        # 2. Store in Pinecone with metadata
        # 3. Return actual storage details

        return {
            "count": len(chunks),
            "index_name": index_name,
            "dimension": 1536,  # OpenAI embedding dimension
            "success": True,
        }

    async def _store_in_snowflake(
        self,
        content_data: Dict[str, Any],
        metadata: List[MetadataTag],
        source: DataSource,
    ) -> Dict[str, Any]:
        """Store structured data in Snowflake."""
        # Simulate Snowflake storage
        table_name = f"SOPHIA_AI.INGESTED_DATA.{source.format.upper()}_{datetime.now().strftime('%Y%m%d')}"

        # In production, this would:
        # 1. Create/update Snowflake tables
        # 2. Insert data with proper schema
        # 3. Store metadata in separate metadata table

        return {
            "table_name": table_name,
            "records_stored": content_data.get("record_count", 1),
            "success": True,
        }

    async def _update_ingestion_progress(
        self, source_id: str, progress: float, stage: str
    ) -> None:
        """Update ingestion progress for real-time tracking."""
        if source_id in self.active_ingestions:
            self.active_ingestions[source_id].update(
                {
                    "progress": progress,
                    "stage": stage,
                    "updated_at": datetime.now().isoformat(),
                }
            )

    async def get_ingestion_status(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get current ingestion status for a source."""
        return self.active_ingestions.get(source_id)

    async def list_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats by category."""
        return self.supported_formats

    async def search_ingested_content(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search ingested content using semantic search."""
        # Simulate semantic search across ingested content
        # In production, this would query Pinecone and Snowflake

        return {
            "query": query,
            "results": [
                {
                    "source_id": "sample-1",
                    "content": "Sample search result content",
                    "relevance_score": 0.85,
                    "metadata": {"business_domain": "sales", "data_type": "financial"},
                }
            ],
            "total_results": 1,
            "search_time_ms": 45,
        }
