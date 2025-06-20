"""
LlamaIndex Integration for Sophia AI

This module provides document intelligence capabilities using LlamaIndex.
It enables advanced document processing, chunking, and indexing for the
Hybrid RAG Architecture.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from datetime import datetime

# Secret management
from infrastructure.esc.llamaindex_secrets import get_llamaindex_secrets

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.vector_stores.weaviate import WeaviateVectorStore

# Sophia AI imports
from backend.knowledge_base.vector_store import VectorStoreManager
from backend.knowledge_base.chunking import ChunkingStrategy
from backend.knowledge_base.metadata_store import MetadataStore
from backend.config.settings import settings
from backend.core.comprehensive_memory_manager import comprehensive_memory_manager, MemoryRequest, MemoryOperationType


# Configure logging
logger = logging.getLogger(__name__)

class BusinessEntityExtractor:
    """Extract business entities from document nodes."""
    
    async def aextract(self, nodes):
        """Extract business entities asynchronously."""
        # This is a placeholder for actual implementation
        # In a real implementation, this would use NER or other techniques
        for node in nodes:
            node.metadata["business_entities"] = ["Pay Ready", "Apartment", "Lease"]
        return nodes

class ComplianceExtractor:
    """Extract compliance-related information from document nodes."""
    
    async def aextract(self, nodes):
        """Extract compliance information asynchronously."""
        # This is a placeholder for actual implementation
        for node in nodes:
            node.metadata["compliance_topics"] = ["Fair Housing", "ADA Compliance"]
        return nodes

class FinancialDataExtractor:
    """Extract financial data from document nodes."""
    
    async def aextract(self, nodes):
        """Extract financial data asynchronously."""
        # This is a placeholder for actual implementation
        for node in nodes:
            node.metadata["financial_data"] = {
                "contains_financial_info": True,
                "currency_mentioned": ["USD"],
                "payment_terms_present": True
            }
        return nodes

class LlamaIndexProcessor:
    """
    Process documents with LlamaIndex for advanced document intelligence.
    
    This class provides document processing, chunking, indexing, and querying
    capabilities using LlamaIndex. It integrates with Sophia AI's existing
    vector stores and knowledge base.
    """
    
    def __init__(self):
        """Initialize the LlamaIndex processor."""
        # Get secrets from Pulumi ESC
        self.secrets = get_llamaindex_secrets()
        
        self.pinecone_store = self._setup_pinecone()
        self.weaviate_store = self._setup_weaviate()
        self.document_parser = self._setup_document_parser()
        self.extractors = self._setup_extractors()
        self.metadata_store = MetadataStore()
        
        # Configure LlamaIndex settings
        Settings.embed_model = settings.llm.embedding_model
        Settings.llm = settings.llm.default_model
        
        # Set API key from Pulumi ESC
        if "LLAMA_API_KEY" in self.secrets:
            os.environ["LLAMA_API_KEY"] = self.secrets["LLAMA_API_KEY"]
            logger.info("LLAMA_API_KEY set from Pulumi ESC")
        
        logger.info("LlamaIndex processor initialized")
    
    def _setup_pinecone(self) -> PineconeVectorStore:
        """Setup Pinecone vector store."""
        try:
            import pinecone
            
            # Initialize Pinecone with API key from Pulumi ESC if available
            api_key = self.secrets.get("LLAMAINDEX_PINECONE_API_KEY", settings.vector_db.pinecone_api_key)
            pinecone.init(
                api_key=api_key,
                environment=settings.vector_db.pinecone_environment
            )
            
            # Get or create index
            index_name = settings.vector_db.pinecone_index
            dimension = 1536  # Default for OpenAI embeddings
            
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine"
                )
            
            # Create vector store
            # Replaced pinecone.Index with ComprehensiveMemoryManager
            # Original: index = pinecone.Index(index_name)
            index = comprehensive_memory_manager
            return PineconeVectorStore(pinecone_index=index)
            
        except Exception as e:
            logger.error(f"Failed to setup Pinecone: {e}")
            # Return a mock store for development
            return None
    
    def _setup_weaviate(self) -> WeaviateVectorStore:
        """Setup Weaviate vector store."""
        try:
            import weaviate
            
            # Create Weaviate client with API key from Pulumi ESC if available
            api_key = self.secrets.get("LLAMAINDEX_WEAVIATE_API_KEY", settings.vector_db.weaviate_api_key)
            client = weaviate.Client(
                url=settings.vector_db.weaviate_url,
                auth_client_secret=weaviate.AuthApiKey(
                    api_key=api_key
                ) if api_key else None
            )
            
            # Create vector store
            return WeaviateVectorStore(
                weaviate_client=client,
                index_name="SophiaDocuments"
            )
            
        except Exception as e:
            logger.error(f"Failed to setup Weaviate: {e}")
            # Return a mock store for development
            return WeaviateVectorStore()
    
    def _setup_document_parser(self):
        """Setup advanced document parsing with LlamaIndex."""
        return SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=200,
            paragraph_separator="\n\n",
            secondary_chunking_regex="[.!?]+",
        )
    
    def _setup_extractors(self):
        """Setup metadata extractors."""
        return [
            TitleExtractor(nodes=5),
            QuestionsAnsweredExtractor(questions=3),
            BusinessEntityExtractor(),
            ComplianceExtractor(),
            FinancialDataExtractor()
        ]
    
    async def process_document(self, document: Union[str, Document, Dict], 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process document with full LlamaIndex pipeline.
        
        Args:
            document: The document to process. Can be a string, Document object, or dict.
            context: Additional context for processing.
            
        Returns:
            Dict containing processing results and metadata.
        """
        context = context or {}
        
        try:
            # Convert to Document if needed
            if isinstance(document, str):
                doc = Document(text=document)
            elif isinstance(document, dict):
                doc = Document(
                    text=document.get("text", ""),
                    metadata=document.get("metadata", {})
                )
            else:
                doc = document
            
            # Add processing metadata
            doc.metadata["processed_at"] = datetime.utcnow().isoformat()
            doc.metadata["processor"] = "llamaindex"
            
            # Parse document into nodes
            nodes = self.document_parser.get_nodes_from_documents([doc])
            
            # Extract metadata
            for extractor in self.extractors:
                nodes = await extractor.aextract(nodes)
            
            # Create vector indices
            pinecone_index = VectorStoreIndex.from_vector_store(
                self.pinecone_store, nodes=nodes
            )
            
            weaviate_index = VectorStoreIndex.from_vector_store(
                self.weaviate_store, nodes=nodes
            )
            
            # Store in knowledge base
            await self._store_in_knowledge_base(nodes, context)
            
            return {
                'status': 'success',
                'processed_nodes': len(nodes),
                'pinecone_index_id': pinecone_index.index_id,
                'weaviate_index_id': weaviate_index.index_id,
                'metadata': {
                    'title': nodes[0].metadata.get('title', 'Untitled Document'),
                    'questions_answered': nodes[0].metadata.get('questions_answered', []),
                    'business_entities': nodes[0].metadata.get('business_entities', []),
                    'compliance_topics': nodes[0].metadata.get('compliance_topics', []),
                    'financial_data': nodes[0].metadata.get('financial_data', {})
                }
            }
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _store_in_knowledge_base(self, nodes, context: Dict[str, Any]):
        """Store processed nodes in the knowledge base."""
        # This is a placeholder for actual implementation
        # In a real implementation, this would store the nodes in the knowledge base
        logger.info(f"Storing {len(nodes)} nodes in knowledge base")
        return True
    
    async def query_documents(self, query: str, context: Dict[str, Any] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Query documents using LlamaIndex retrieval.
        
        Args:
            query: The query string.
            context: Additional context for querying.
            
        Yields:
            Dict containing query results.
        """
        context = context or {}
        
        try:
            # Query Pinecone
            pinecone_results = await self._query_pinecone_index(query, context)
            
            # Query Weaviate
            weaviate_results = await self._query_weaviate_index(query, context)
            
            # Unified ranking across vector stores
            unified_results = await self._rank_across_sources(
                pinecone_results, weaviate_results
            )
            
            # Stream results with metadata
            for result in unified_results:
                yield {
                    'type': 'document_result',
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {}),
                    'score': result.get('score', 0.0),
                    'source': result.get('source', 'unknown')
                }
        except Exception as e:
            logger.error(f"Document querying failed: {e}")
            yield {
                'type': 'error',
                'error': str(e)
            }
    
    async def _query_pinecone_index(self, query: str, context: Dict[str, Any]) -> List[Dict]:
        """Query Pinecone index."""
        # This is a placeholder for actual implementation
        # In a real implementation, this would query the Pinecone index
        return [
            {
                'content': 'Pinecone result 1',
                'metadata': {'source': 'pinecone', 'document_id': '123'},
                'score': 0.95,
                'source': 'pinecone'
            },
            {
                'content': 'Pinecone result 2',
                'metadata': {'source': 'pinecone', 'document_id': '456'},
                'score': 0.85,
                'source': 'pinecone'
            }
        ]
    
    async def _query_weaviate_index(self, query: str, context: Dict[str, Any]) -> List[Dict]:
        """Query Weaviate index."""
        # This is a placeholder for actual implementation
        # In a real implementation, this would query the Weaviate index
        return [
            {
                'content': 'Weaviate result 1',
                'metadata': {'source': 'weaviate', 'document_id': '789'},
                'score': 0.92,
                'source': 'weaviate'
            },
            {
                'content': 'Weaviate result 2',
                'metadata': {'source': 'weaviate', 'document_id': '012'},
                'score': 0.82,
                'source': 'weaviate'
            }
        ]
    
    async def _rank_across_sources(self, pinecone_results: List[Dict], 
                                  weaviate_results: List[Dict]) -> List[Dict]:
        """Rank results across different vector stores."""
        # Combine results
        all_results = pinecone_results + weaviate_results
        
        # Sort by score
        sorted_results = sorted(all_results, key=lambda x: x.get('score', 0.0), reverse=True)
        
        return sorted_results

class LlamaIndexIntegration:
    async def initialize(self):
        logger.warning("Using placeholder LlamaIndex integration.")
        pass

    async def process_query(self, query: str, context: dict):
        logger.warning("Using placeholder LlamaIndex integration.")
        return {"data": "LlamaIndex placeholder response", "query": query}

llamaindex_integration = LlamaIndexIntegration()
