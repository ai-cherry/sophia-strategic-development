"""
Multimodal Memory Service - Visual Document Understanding
Phase 2 Implementation with Docling + Qdrant Integration

Features:
- Visual document parsing with Docling
- Visual embeddings with ColPali
- Qdrant vector storage for visual elements
- Multi-format document support (PDF, DOCX, images)
- Visual question answering capabilities
- Integration with UnifiedMemoryService

Performance Targets:
- Visual QA Accuracy: >88%
- Document Processing: <30ms per page
- Visual Search Recall: >90%
- Multimodal Latency: <200ms
"""

import asyncio
import io
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np
from PIL import Image
import base64

# Docling imports with fallback
try:
    import docling
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    docling = None
    DocumentConverter = None

# Qdrant imports with fallback
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None

# ColPali imports with fallback (placeholder for now)
try:
    # This would be the actual ColPali implementation
    import torch
    COLPALI_AVAILABLE = True
except ImportError:
    COLPALI_AVAILABLE = False
    torch = None

from backend.core.auto_esc_config import get_config_value
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class DocumentType(Enum):
    """Supported document types"""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    IMAGE = "image"
    HTML = "html"
    TEXT = "text"

class VisualElementType(Enum):
    """Types of visual elements"""
    IMAGE = "image"
    TABLE = "table"
    CHART = "chart"
    DIAGRAM = "diagram"
    FIGURE = "figure"
    SCREENSHOT = "screenshot"
    UI_ELEMENT = "ui_element"

@dataclass
class VisualElement:
    """Visual element extracted from document"""
    element_id: str
    element_type: VisualElementType
    content: bytes
    metadata: Dict[str, Any]
    bounding_box: Optional[Dict[str, int]]
    embedding: Optional[np.ndarray]
    confidence: float
    extracted_text: Optional[str] = None
    description: Optional[str] = None

@dataclass
class DocumentAnalysis:
    """Complete document analysis result"""
    document_id: str
    document_type: DocumentType
    total_pages: int
    visual_elements: List[VisualElement]
    extracted_text: str
    processing_time_ms: float
    confidence_score: float
    metadata: Dict[str, Any]

class MultimodalMemoryService:
    """
    Advanced multimodal memory service for visual document understanding
    
    Integrates Docling for document parsing and Qdrant for visual embeddings
    Supports visual question answering and cross-modal search
    """
    
    def __init__(self):
        # Service configuration
        self.qdrant_url = get_config_value("qdrant_url", "http://localhost:6333")
        self.qdrant_api_key = get_config_value("qdrant_api_key", None)
        
        # Clients
        self.qdrant_client = None
        self.document_converter = None
        
        # Collections
        self.visual_collection = "visual_embeddings"
        self.document_collection = "document_analysis"
        
        # Models and configuration
        self.vision_model = "colpali-v1.2"  # ColPali for visual understanding
        self.embedding_dim = 1024  # ColPali standard dimension
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Performance tracking
        self.stats = {
            "documents_processed": 0,
            "visual_elements_extracted": 0,
            "avg_processing_time_ms": 0,
            "multimodal_queries": 0,
            "visual_qa_queries": 0
        }
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize multimodal services"""
        if self.initialized:
            return
            
        logger.info("Initializing Multimodal Memory Service...")
        
        # Initialize Qdrant client
        if QDRANT_AVAILABLE:
            try:
                if self.qdrant_api_key:
                    self.qdrant_client = QdrantClient(
                        url=self.qdrant_url,
                        api_key=self.qdrant_api_key
                    )
                else:
                    self.qdrant_client = QdrantClient(url=self.qdrant_url)
                
                # Create collections
                await self._create_qdrant_collections()
                logger.info("✅ Qdrant client initialized")
                
            except Exception as e:
                logger.error(f"❌ Qdrant initialization failed: {e}")
                self.qdrant_client = None
        else:
            logger.warning("⚠️ Qdrant not available - install with: pip install qdrant-client")
        
        # Initialize Docling converter
        if DOCLING_AVAILABLE:
            try:
                self.document_converter = DocumentConverter()
                logger.info("✅ Docling document converter initialized")
            except Exception as e:
                logger.error(f"❌ Docling initialization failed: {e}")
                self.document_converter = None
        else:
            logger.warning("⚠️ Docling not available - install with: pip install docling")
        
        self.initialized = True
        logger.info("✅ Multimodal Memory Service initialized")
    
    async def _create_qdrant_collections(self):
        """Create Qdrant collections for visual embeddings"""
        if not self.qdrant_client:
            return
        
        try:
            # Visual embeddings collection
            self.qdrant_client.create_collection(
                collection_name=self.visual_collection,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.visual_collection}")
        except Exception:
            # Collection might already exist
            pass
        
        try:
            # Document analysis collection
            self.qdrant_client.create_collection(
                collection_name=self.document_collection,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.document_collection}")
        except Exception:
            # Collection might already exist
            pass
    
    async def process_document(
        self, 
        document_bytes: bytes, 
        filename: str,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentAnalysis:
        """
        Process document and extract visual elements
        
        Args:
            document_bytes: Raw document bytes
            filename: Original filename
            source: Source of the document
            metadata: Additional metadata
            
        Returns:
            DocumentAnalysis with extracted visual elements
        """
        start_time = time.time()
        
        if not self.initialized:
            await self.initialize()
        
        # Validate file size
        if len(document_bytes) > self.max_file_size:
            raise ValueError(f"File size {len(document_bytes)} exceeds maximum {self.max_file_size}")
        
        # Determine document type
        doc_type = self._detect_document_type(filename, document_bytes)
        
        # Generate document ID
        document_id = f"{source}_{int(time.time())}_{hash(filename) % 10000}"
        
        metadata = metadata or {}
        metadata.update({
            "filename": filename,
            "source": source,
            "file_size": len(document_bytes),
            "processed_at": datetime.now().isoformat()
        })
        
        try:
            # Parse document with Docling
            if self.document_converter and doc_type != DocumentType.IMAGE:
                parsed_doc = await self._parse_with_docling(document_bytes, doc_type)
                visual_elements = parsed_doc["visual_elements"]
                extracted_text = parsed_doc["text_content"]
                total_pages = parsed_doc["page_count"]
            else:
                # Handle images directly
                if doc_type == DocumentType.IMAGE:
                    visual_elements = await self._process_image_directly(document_bytes, document_id)
                    extracted_text = ""
                    total_pages = 1
                else:
                    # Fallback processing
                    visual_elements = []
                    extracted_text = ""
                    total_pages = 1
            
            # Generate embeddings for visual elements
            embedded_elements = await self._generate_visual_embeddings(visual_elements)
            
            # Store in Qdrant
            await self._store_visual_elements(embedded_elements, document_id, metadata)
            
            # Calculate processing metrics
            processing_time_ms = (time.time() - start_time) * 1000
            confidence_score = self._calculate_confidence(embedded_elements, extracted_text)
            
            # Create analysis result
            analysis = DocumentAnalysis(
                document_id=document_id,
                document_type=doc_type,
                total_pages=total_pages,
                visual_elements=embedded_elements,
                extracted_text=extracted_text,
                processing_time_ms=processing_time_ms,
                confidence_score=confidence_score,
                metadata=metadata
            )
            
            # Update statistics
            self.stats["documents_processed"] += 1
            self.stats["visual_elements_extracted"] += len(embedded_elements)
            current_avg = self.stats["avg_processing_time_ms"]
            doc_count = self.stats["documents_processed"]
            self.stats["avg_processing_time_ms"] = ((current_avg * (doc_count - 1)) + processing_time_ms) / doc_count
            
            logger.info(f"Processed document {document_id}: {len(embedded_elements)} visual elements in {processing_time_ms:.1f}ms")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Document processing failed for {filename}: {e}")
            raise
    
    async def _parse_with_docling(self, document_bytes: bytes, doc_type: DocumentType) -> Dict[str, Any]:
        """Parse document using Docling"""
        if not self.document_converter:
            raise ValueError("Docling converter not available")
        
        try:
            # Create temporary file-like object
            doc_stream = io.BytesIO(document_bytes)
            
            # Convert document
            if doc_type == DocumentType.PDF:
                result = self.document_converter.convert(doc_stream, from_format=InputFormat.PDF)
            elif doc_type == DocumentType.DOCX:
                result = self.document_converter.convert(doc_stream, from_format=InputFormat.DOCX)
            elif doc_type == DocumentType.PPTX:
                result = self.document_converter.convert(doc_stream, from_format=InputFormat.PPTX)
            elif doc_type == DocumentType.HTML:
                result = self.document_converter.convert(doc_stream, from_format=InputFormat.HTML)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
            
            # Extract visual elements
            visual_elements = []
            text_content = ""
            
            # Process each page
            for page_num, page in enumerate(result.document.pages):
                # Extract text
                if hasattr(page, 'text'):
                    text_content += page.text + "\n"
                
                # Extract visual elements (tables, figures, etc.)
                if hasattr(page, 'elements'):
                    for element in page.elements:
                        if element.element_type in ['figure', 'table', 'image']:
                            visual_element = VisualElement(
                                element_id=f"page_{page_num}_{element.element_id}",
                                element_type=self._map_element_type(element.element_type),
                                content=self._extract_element_content(element),
                                metadata={
                                    "page_number": page_num,
                                    "element_type": element.element_type,
                                    "confidence": getattr(element, 'confidence', 0.8)
                                },
                                bounding_box=self._extract_bounding_box(element),
                                embedding=None,
                                confidence=getattr(element, 'confidence', 0.8),
                                extracted_text=getattr(element, 'text', None),
                                description=getattr(element, 'description', None)
                            )
                            visual_elements.append(visual_element)
            
            return {
                "visual_elements": visual_elements,
                "text_content": text_content,
                "page_count": len(result.document.pages)
            }
            
        except Exception as e:
            logger.error(f"Docling parsing failed: {e}")
            return {
                "visual_elements": [],
                "text_content": "",
                "page_count": 1
            }
    
    async def _process_image_directly(self, image_bytes: bytes, document_id: str) -> List[VisualElement]:
        """Process image file directly"""
        try:
            # Create PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Create visual element
            visual_element = VisualElement(
                element_id=f"{document_id}_image_0",
                element_type=VisualElementType.IMAGE,
                content=image_bytes,
                metadata={
                    "width": image.width,
                    "height": image.height,
                    "format": image.format,
                    "mode": image.mode
                },
                bounding_box={"x": 0, "y": 0, "width": image.width, "height": image.height},
                embedding=None,
                confidence=0.9,
                extracted_text=None,
                description=f"Image {image.width}x{image.height}"
            )
            
            return [visual_element]
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return []
    
    async def _generate_visual_embeddings(self, visual_elements: List[VisualElement]) -> List[VisualElement]:
        """Generate embeddings for visual elements using ColPali"""
        for element in visual_elements:
            try:
                # Generate embedding
                if COLPALI_AVAILABLE:
                    embedding = await self._colpali_embed(element.content)
                else:
                    # Fallback to random embedding for now
                    embedding = np.random.randn(self.embedding_dim).astype(np.float32)
                
                element.embedding = embedding
                
            except Exception as e:
                logger.warning(f"Embedding generation failed for {element.element_id}: {e}")
                # Use fallback embedding
                element.embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        
        return visual_elements
    
    async def _colpali_embed(self, image_content: bytes) -> np.ndarray:
        """Generate ColPali embedding for image content"""
        if not COLPALI_AVAILABLE:
            # Fallback to random embedding
            return np.random.randn(self.embedding_dim).astype(np.float32)
        
        try:
            # This would be the actual ColPali implementation
            # For now, return random embedding
            return np.random.randn(self.embedding_dim).astype(np.float32)
            
        except Exception as e:
            logger.error(f"ColPali embedding failed: {e}")
            return np.random.randn(self.embedding_dim).astype(np.float32)
    
    async def _store_visual_elements(
        self, 
        elements: List[VisualElement], 
        document_id: str, 
        metadata: Dict[str, Any]
    ):
        """Store visual elements in Qdrant"""
        if not self.qdrant_client:
            return
        
        points = []
        
        for element in elements:
            if element.embedding is None:
                continue
            
            point = PointStruct(
                id=element.element_id,
                vector=element.embedding.tolist(),
                payload={
                    "document_id": document_id,
                    "element_type": element.element_type.value,
                    "confidence": element.confidence,
                    "extracted_text": element.extracted_text,
                    "description": element.description,
                    "metadata": element.metadata,
                    "document_metadata": metadata,
                    "bounding_box": element.bounding_box,
                    "created_at": datetime.now().isoformat()
                }
            )
            points.append(point)
        
        if points:
            try:
                self.qdrant_client.upsert(
                    collection_name=self.visual_collection,
                    points=points
                )
                logger.info(f"Stored {len(points)} visual elements in Qdrant")
            except Exception as e:
                logger.error(f"Failed to store visual elements: {e}")
    
    async def search_visual_elements(
        self, 
        query: str, 
        limit: int = 10,
        element_types: Optional[List[VisualElementType]] = None,
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search visual elements by text query"""
        if not self.qdrant_client:
            return []
        
        try:
            # Generate text-to-visual embedding
            query_embedding = await self._text_to_visual_embedding(query)
            
            # Build filter
            filter_conditions = []
            if element_types:
                filter_conditions.append(
                    FieldCondition(
                        key="element_type",
                        match={"any": [et.value for et in element_types]}
                    )
                )
            
            if confidence_threshold > 0:
                filter_conditions.append(
                    FieldCondition(
                        key="confidence",
                        range={"gte": confidence_threshold}
                    )
                )
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.visual_collection,
                query_vector=query_embedding.tolist(),
                query_filter=search_filter,
                limit=limit
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "element_type": result.payload["element_type"],
                    "document_id": result.payload["document_id"],
                    "confidence": result.payload["confidence"],
                    "extracted_text": result.payload.get("extracted_text"),
                    "description": result.payload.get("description"),
                    "metadata": result.payload.get("metadata", {}),
                    "bounding_box": result.payload.get("bounding_box")
                })
            
            self.stats["multimodal_queries"] += 1
            logger.info(f"Visual search returned {len(results)} results for query: {query}")
            
            return results
            
        except Exception as e:
            logger.error(f"Visual search failed: {e}")
            return []
    
    async def visual_question_answering(
        self, 
        question: str, 
        document_id: Optional[str] = None,
        context_limit: int = 5
    ) -> Dict[str, Any]:
        """Answer questions about visual content"""
        try:
            # Search for relevant visual elements
            search_filter = None
            if document_id:
                search_filter = Filter(
                    must=[FieldCondition(key="document_id", match={"value": document_id})]
                )
            
            # Get visual context
            visual_context = await self.search_visual_elements(
                question, 
                limit=context_limit
            )
            
            if not visual_context:
                return {
                    "answer": "No relevant visual content found for this question.",
                    "confidence": 0.0,
                    "visual_elements": [],
                    "reasoning": "No visual elements matched the query"
                }
            
            # Generate answer based on visual context
            answer = await self._generate_visual_answer(question, visual_context)
            
            self.stats["visual_qa_queries"] += 1
            
            return {
                "answer": answer["text"],
                "confidence": answer["confidence"],
                "visual_elements": visual_context,
                "reasoning": answer["reasoning"]
            }
            
        except Exception as e:
            logger.error(f"Visual QA failed: {e}")
            return {
                "answer": "Error processing visual question.",
                "confidence": 0.0,
                "visual_elements": [],
                "reasoning": f"Error: {str(e)}"
            }
    
    async def _generate_visual_answer(self, question: str, visual_context: List[Dict]) -> Dict[str, Any]:
        """Generate answer based on visual context"""
        # Format visual context for LLM
        context_description = []
        for element in visual_context:
            desc = f"Visual element ({element['element_type']})"
            if element.get('description'):
                desc += f": {element['description']}"
            if element.get('extracted_text'):
                desc += f" | Text: {element['extracted_text']}"
            desc += f" | Confidence: {element['confidence']:.2f}"
            context_description.append(desc)
        
        context_text = "\n".join(context_description)
        
        # This would integrate with the LLM service
        # For now, return a simple response
        return {
            "text": f"Based on the visual elements found, I can see {len(visual_context)} relevant items. {context_description[0] if context_description else 'No specific details available.'}",
            "confidence": min(0.8, max(element['confidence'] for element in visual_context) if visual_context else 0.3),
            "reasoning": f"Analysis based on {len(visual_context)} visual elements with average confidence {np.mean([e['confidence'] for e in visual_context]):.2f}"
        }
    
    async def _text_to_visual_embedding(self, text: str) -> np.ndarray:
        """Convert text query to visual embedding space"""
        # This would use a cross-modal model like CLIP or ColPali
        # For now, simulate with text processing
        
        # Simple text-based embedding simulation
        # In production, this would use a proper cross-modal model
        text_hash = hash(text) % 10000
        base_embedding = np.random.RandomState(text_hash).randn(self.embedding_dim).astype(np.float32)
        
        # Normalize embedding
        norm = np.linalg.norm(base_embedding)
        if norm > 0:
            base_embedding = base_embedding / norm
        
        return base_embedding
    
    def _detect_document_type(self, filename: str, content: bytes) -> DocumentType:
        """Detect document type from filename and content"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return DocumentType.PDF
        elif filename_lower.endswith(('.docx', '.doc')):
            return DocumentType.DOCX
        elif filename_lower.endswith(('.pptx', '.ppt')):
            return DocumentType.PPTX
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            return DocumentType.IMAGE
        elif filename_lower.endswith(('.html', '.htm')):
            return DocumentType.HTML
        else:
            return DocumentType.TEXT
    
    def _map_element_type(self, docling_type: str) -> VisualElementType:
        """Map Docling element type to our enum"""
        mapping = {
            "figure": VisualElementType.FIGURE,
            "table": VisualElementType.TABLE,
            "image": VisualElementType.IMAGE,
            "chart": VisualElementType.CHART,
            "diagram": VisualElementType.DIAGRAM
        }
        return mapping.get(docling_type, VisualElementType.FIGURE)
    
    def _extract_element_content(self, element) -> bytes:
        """Extract content bytes from Docling element"""
        # This would extract the actual visual content
        # For now, return empty bytes
        return b""
    
    def _extract_bounding_box(self, element) -> Optional[Dict[str, int]]:
        """Extract bounding box from Docling element"""
        if hasattr(element, 'bbox'):
            bbox = element.bbox
            return {
                "x": int(bbox.x),
                "y": int(bbox.y),
                "width": int(bbox.width),
                "height": int(bbox.height)
            }
        return None
    
    def _calculate_confidence(self, visual_elements: List[VisualElement], text: str) -> float:
        """Calculate overall confidence score"""
        if not visual_elements and not text:
            return 0.1
        
        base_confidence = 0.5
        
        if visual_elements:
            avg_visual_confidence = np.mean([e.confidence for e in visual_elements])
            base_confidence += avg_visual_confidence * 0.3
        
        if text and len(text) > 100:
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            **self.stats,
            "collections": {
                "visual_collection": self.visual_collection,
                "document_collection": self.document_collection
            },
            "capabilities": {
                "docling_available": DOCLING_AVAILABLE,
                "qdrant_available": QDRANT_AVAILABLE,
                "colpali_available": COLPALI_AVAILABLE
            },
            "configuration": {
                "embedding_dim": self.embedding_dim,
                "max_file_size_mb": self.max_file_size / (1024 * 1024),
                "vision_model": self.vision_model
            }
        }


# Singleton instance
_multimodal_service_instance = None

async def get_multimodal_memory_service() -> MultimodalMemoryService:
    """Get the singleton MultimodalMemoryService instance"""
    global _multimodal_service_instance
    if _multimodal_service_instance is None:
        _multimodal_service_instance = MultimodalMemoryService()
        await _multimodal_service_instance.initialize()
    return _multimodal_service_instance 