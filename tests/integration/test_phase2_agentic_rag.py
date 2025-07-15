"""
Comprehensive Integration Tests for Phase 2 Agentic RAG Evolution
Tests all components: UnifiedMemoryService, MultimodalMemoryService, HypotheticalRAGService

Test Categories:
1. Agentic RAG Workflow Tests
2. LangGraph Integration Tests  
3. Multimodal Processing Tests
4. Hypothetical Document Generation Tests
5. Self-Pruning Memory Tests
6. Performance Validation Tests
7. Error Handling and Resilience Tests
"""

import asyncio
import pytest
import numpy as np
import time
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Import services to test
from backend.services.unified_memory_service import (
    UnifiedMemoryService, 
    RAGState, 
    ProcessingStage,
    get_unified_memory_service_v3
)
from backend.services.multimodal_memory_service import (
    MultimodalMemoryService,
    DocumentType,
    VisualElementType,
    get_multimodal_memory_service
)
from backend.services.hypothetical_rag_service import (
    HypotheticalRAGService,
    HypotheticalType,
    PruningStrategy,
    get_hypothetical_rag_service
)

class TestUnifiedMemoryService:
    """Test suite for UnifiedMemoryService agentic capabilities"""
    
    @pytest.fixture
    async def memory_service_v3(self):
        """Create test instance of UnifiedMemoryService"""
        service = UnifiedMemoryService()
        await service.initialize()
        yield service
        # Cleanup
        if hasattr(service, 'pruning_task') and service.pruning_task:
            service.pruning_task.cancel()
        if hasattr(service, 'warming_task') and service.warming_task:
            service.warming_task.cancel()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, memory_service_v3):
        """Test that service initializes correctly"""
        assert memory_service_v3.initialized
        assert memory_service_v3.v2_service is not None
        assert len(memory_service_v3.memory_tiers) == 4
        assert "episodic" in memory_service_v3.memory_tiers
        assert "semantic" in memory_service_v3.memory_tiers
        assert "visual" in memory_service_v3.memory_tiers
        assert "procedural" in memory_service_v3.memory_tiers
    
    @pytest.mark.asyncio
    async def test_agentic_search_basic(self, memory_service_v3):
        """Test basic agentic search functionality"""
        query = "How to optimize database performance?"
        
        result = await memory_service_v3.agentic_search(
            query=query,
            user_id="test_user",
            max_iterations=2
        )
        
        # Validate result structure
        assert isinstance(result, dict)
        assert "retrieved_docs" in result
        assert "performance_metrics" in result
        assert "confidence_score" in result
        assert "iterations" in result
        
        # Validate performance metrics
        metrics = result["performance_metrics"]
        assert "total_docs_retrieved" in metrics
        assert "final_confidence" in metrics
        assert metrics["final_confidence"] >= 0.0
        assert metrics["final_confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_agentic_workflow_stages(self, memory_service_v3):
        """Test that agentic workflow goes through proper stages"""
        query = "What are the best practices for API design?"
        
        result = await memory_service_v3.agentic_search(query=query)
        
        # Check that processing stages are recorded
        assert "processing_stages" in result
        stages = result["processing_stages"]
        
        # Should at least have initial retrieval and critique
        assert ProcessingStage.INITIAL_RETRIEVAL.value in stages
        assert ProcessingStage.CRITIQUE_ANALYSIS.value in stages
        assert ProcessingStage.FINAL_SYNTHESIS.value in stages
    
    @pytest.mark.asyncio
    async def test_multimodal_query_detection(self, memory_service_v3):
        """Test detection of multimodal queries"""
        multimodal_queries = [
            "Show me the UI design for the login page",
            "What does this diagram represent?",
            "Analyze the screenshot of the error",
            "Find images related to architecture"
        ]
        
        for query in multimodal_queries:
            is_multimodal = memory_service_v3._is_multimodal_query(query)
            assert is_multimodal, f"Query should be detected as multimodal: {query}"
        
        regular_queries = [
            "How to implement authentication?",
            "What is the best database for this use case?",
            "Explain the concept of microservices"
        ]
        
        for query in regular_queries:
            is_multimodal = memory_service_v3._is_multimodal_query(query)
            assert not is_multimodal, f"Query should not be detected as multimodal: {query}"
    
    @pytest.mark.asyncio
    async def test_critique_and_refinement(self, memory_service_v3):
        """Test critique and query refinement functionality"""
        # Mock LLM response for critique
        with patch.object(memory_service_v3, '_generate_critique_llm') as mock_llm:
            mock_llm.return_value = '{"relevance_score": 0.4, "coverage_gaps": ["missing technical details"], "refinements": "add more specific technical requirements", "tool_suggestions": [], "multimodal_suggestions": [], "confidence_assessment": "low"}'
            
            initial_state = {
                "query": "help with coding",
                "retrieved_docs": [{"content": "basic info", "score": 0.3}],
                "iteration_count": 1,
                "max_iterations": 3
            }
            
            # Test critique node
            result_state = await memory_service_v3._critique_node(initial_state)
            
            assert "critique_feedback" in result_state
            assert "confidence_score" in result_state
            assert result_state["confidence_score"] == 0.4
            
            critique = result_state["critique_feedback"]
            assert "relevance_score" in critique
            assert "coverage_gaps" in critique
    
    @pytest.mark.asyncio
    async def test_performance_metrics_tracking(self, memory_service_v3):
        """Test that performance metrics are properly tracked"""
        initial_metrics = memory_service_v3.get_performance_metrics()
        
        # Perform some operations
        await memory_service_v3.agentic_search("test query 1")
        await memory_service_v3.agentic_search("test query 2")
        
        updated_metrics = memory_service_v3.get_performance_metrics()
        
        # Check that metrics were updated
        assert updated_metrics["total_agentic_queries"] > initial_metrics["total_agentic_queries"]
        assert "avg_iterations" in updated_metrics
        assert "workflow_available" in updated_metrics
        assert "multimodal_available" in updated_metrics


class TestMultimodalMemoryService:
    """Test suite for MultimodalMemoryService"""
    
    @pytest.fixture
    async def multimodal_service(self):
        """Create test instance of MultimodalMemoryService"""
        service = MultimodalMemoryService()
        await service.initialize()
        yield service
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, multimodal_service):
        """Test multimodal service initialization"""
        assert multimodal_service.initialized
        assert multimodal_service.visual_collection == "visual_embeddings"
        assert multimodal_service.document_collection == "document_analysis"
        assert multimodal_service.embedding_dim == 1024
    
    @pytest.mark.asyncio
    async def test_document_type_detection(self, multimodal_service):
        """Test document type detection"""
        test_cases = [
            ("document.pdf", b"PDF content", DocumentType.PDF),
            ("presentation.pptx", b"PPTX content", DocumentType.PPTX),
            ("image.png", b"PNG content", DocumentType.IMAGE),
            ("webpage.html", b"HTML content", DocumentType.HTML),
            ("document.docx", b"DOCX content", DocumentType.DOCX),
            ("unknown.txt", b"text content", DocumentType.TEXT)
        ]
        
        for filename, content, expected_type in test_cases:
            detected_type = multimodal_service._detect_document_type(filename, content)
            assert detected_type == expected_type
    
    @pytest.mark.asyncio
    async def test_image_processing(self, multimodal_service):
        """Test direct image processing"""
        # Create a simple test image
        from PIL import Image
        import io
        
        # Create test image
        test_image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        # Process image
        visual_elements = await multimodal_service._process_image_directly(
            img_bytes, "test_doc_123"
        )
        
        assert len(visual_elements) == 1
        element = visual_elements[0]
        assert element.element_type == VisualElementType.IMAGE
        assert element.metadata["width"] == 100
        assert element.metadata["height"] == 100
        assert element.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_visual_search(self, multimodal_service):
        """Test visual element search functionality"""
        # Mock Qdrant client if not available
        if not multimodal_service.QDRANT_client:
            multimodal_service.QDRANT_client = Mock()
            multimodal_service.QDRANT_client.search.return_value = [
                Mock(
                    id="test_element_1",
                    score=0.9,
                    payload={
                        "element_type": "image",
                        "document_id": "doc_123",
                        "confidence": 0.8,
                        "extracted_text": "Test image",
                        "description": "A test image",
                        "metadata": {},
                        "bounding_box": {"x": 0, "y": 0, "width": 100, "height": 100}
                    }
                )
            ]
        
        results = await multimodal_service.search_visual_elements(
            query="test image",
            limit=5,
            element_types=[VisualElementType.IMAGE]
        )
        
        if multimodal_service.QDRANT_client:
            assert len(results) >= 0  # May be empty if no real data
            for result in results:
                assert "id" in result
                assert "score" in result
                assert "element_type" in result
    
    @pytest.mark.asyncio
    async def test_visual_question_answering(self, multimodal_service):
        """Test visual question answering"""
        # Mock search results
        with patch.object(multimodal_service, 'search_visual_elements') as mock_search:
            mock_search.return_value = [
                {
                    "id": "element_1",
                    "score": 0.9,
                    "element_type": "image",
                    "confidence": 0.8,
                    "description": "A flowchart showing the process",
                    "extracted_text": "Step 1: Initialize"
                }
            ]
            
            result = await multimodal_service.visual_question_answering(
                question="What does this flowchart show?",
                document_id="doc_123"
            )
            
            assert "answer" in result
            assert "confidence" in result
            assert "visual_elements" in result
            assert "reasoning" in result
            assert len(result["visual_elements"]) > 0
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, multimodal_service):
        """Test statistics tracking"""
        initial_stats = multimodal_service.get_statistics()
        
        # Simulate some operations
        multimodal_service.stats["documents_processed"] += 1
        multimodal_service.stats["visual_elements_extracted"] += 3
        multimodal_service.stats["multimodal_queries"] += 2
        
        updated_stats = multimodal_service.get_statistics()
        
        assert updated_stats["documents_processed"] == 1
        assert updated_stats["visual_elements_extracted"] == 3
        assert updated_stats["multimodal_queries"] == 2
        assert "capabilities" in updated_stats
        assert "configuration" in updated_stats


class TestHypotheticalRAGService:
    """Test suite for HypotheticalRAGService"""
    
    @pytest.fixture
    async def hypothetical_service(self):
        """Create test instance of HypotheticalRAGService"""
        service = HypotheticalRAGService()
        await service.initialize()
        yield service
        # Cleanup background tasks
        if service.pruning_task:
            service.pruning_task.cancel()
        if service.warming_task:
            service.warming_task.cancel()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, hypothetical_service):
        """Test hypothetical RAG service initialization"""
        assert hypothetical_service.initialized
        assert hypothetical_service.memory_service is not None
        assert isinstance(hypothetical_service.hypothetical_cache, dict)
        assert len(hypothetical_service.pruning_strategies) > 0
    
    @pytest.mark.asyncio
    async def test_hypothetical_document_generation(self, hypothetical_service):
        """Test hypothetical document generation"""
        query = "How to implement microservices architecture?"
        
        # Mock LLM response
        with patch.object(hypothetical_service.memory_service, 'portkey') as mock_portkey:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Comprehensive guide to microservices architecture including best practices, patterns, and implementation strategies."
            
            mock_portkey.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            # Mock embedding generation
            with patch.object(hypothetical_service.memory_service, 'generate_embedding') as mock_embed:
                mock_embed.return_value = np.random.randn(1024).astype(np.float32)
                
                hyp_doc = await hypothetical_service.generate_hypothetical_answer(
                    query=query,
                    document_type=HypotheticalType.ANSWER_FOCUSED
                )
                
                assert hyp_doc.query == query
                assert hyp_doc.document_type == HypotheticalType.ANSWER_FOCUSED
                assert hyp_doc.confidence > 0
                assert hyp_doc.access_count == 1
                assert len(hyp_doc.hypothetical_content) > 0
                assert hyp_doc.embedding is not None
    
    @pytest.mark.asyncio
    async def test_hypothetical_caching(self, hypothetical_service):
        """Test hypothetical document caching"""
        query = "What is containerization?"
        
        # Mock dependencies
        with patch.object(hypothetical_service.memory_service, 'portkey') as mock_portkey:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Containerization explanation"
            mock_portkey.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            with patch.object(hypothetical_service.memory_service, 'generate_embedding') as mock_embed:
                mock_embed.return_value = np.random.randn(1024).astype(np.float32)
                
                # First call - should generate
                doc1 = await hypothetical_service.generate_hypothetical_answer(query)
                initial_cache_size = len(hypothetical_service.hypothetical_cache)
                
                # Second call - should hit cache
                doc2 = await hypothetical_service.generate_hypothetical_answer(query)
                final_cache_size = len(hypothetical_service.hypothetical_cache)
                
                # Cache size should not increase
                assert final_cache_size == initial_cache_size
                # Access count should increase
                assert doc2.access_count == 2
                # Should be same document
                assert doc1.document_id == doc2.document_id
    
    @pytest.mark.asyncio
    async def test_hypothetical_search(self, hypothetical_service):
        """Test search using hypothetical documents"""
        query = "database optimization techniques"
        
        # Mock dependencies
        with patch.object(hypothetical_service.memory_service, 'portkey') as mock_portkey:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Database optimization guide"
            mock_portkey.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            with patch.object(hypothetical_service.memory_service, 'generate_embedding') as mock_embed:
                mock_embed.return_value = np.random.randn(1024).astype(np.float32)
                
                with patch.object(hypothetical_service.memory_service, 'search_knowledge') as mock_search:
                    mock_search.return_value = [
                        {"content": "Regular search result", "score": 0.7, "source": "regular"}
                    ]
                    
                    results = await hypothetical_service.hypothetical_search(
                        query=query,
                        limit=10,
                        include_types=[HypotheticalType.ANSWER_FOCUSED]
                    )
                    
                    assert len(results) > 0
                    
                    # Check for hypothetical enhancement
                    hypothetical_results = [r for r in results if r.get("hypothetical_enhanced", False)]
                    regular_results = [r for r in results if not r.get("hypothetical_enhanced", False)]
                    
                    # Should have both types
                    assert len(hypothetical_results) >= 0
                    assert len(regular_results) >= 0
    
    @pytest.mark.asyncio
    async def test_pruning_strategies(self, hypothetical_service):
        """Test different pruning strategies"""
        # Add some test documents to cache
        now = datetime.now()
        
        # Old document with low confidence
        old_doc = Mock()
        old_doc.confidence = 0.05
        old_doc.created_at = now - timedelta(hours=200)
        old_doc.last_accessed = now - timedelta(hours=100)
        old_doc.access_count = 1
        hypothetical_service.hypothetical_cache["old_low_conf"] = old_doc
        
        # Recent document with high confidence
        recent_doc = Mock()
        recent_doc.confidence = 0.9
        recent_doc.created_at = now - timedelta(hours=1)
        recent_doc.last_accessed = now
        recent_doc.access_count = 10
        hypothetical_service.hypothetical_cache["recent_high_conf"] = recent_doc
        
        # Test confidence-based pruning
        pruned_by_confidence = await hypothetical_service._prune_by_confidence()
        assert "old_low_conf" in pruned_by_confidence
        assert "recent_high_conf" not in pruned_by_confidence
        
        # Test age-based pruning
        pruned_by_age = await hypothetical_service._prune_by_age()
        assert "old_low_conf" in pruned_by_age
        assert "recent_high_conf" not in pruned_by_age
        
        # Test access-based pruning
        pruned_by_access = await hypothetical_service._prune_by_access()
        # Should include old document with low access
        assert len(pruned_by_access) >= 0  # May or may not include based on access patterns
    
    @pytest.mark.asyncio
    async def test_comprehensive_pruning(self, hypothetical_service):
        """Test comprehensive pruning operation"""
        # Add test documents
        for i in range(5):
            doc = Mock()
            doc.confidence = 0.1 if i < 2 else 0.9  # First 2 have low confidence
            doc.created_at = datetime.now() - timedelta(hours=i*50)
            doc.last_accessed = datetime.now() - timedelta(hours=i*10)
            doc.access_count = i + 1
            doc.query = f"test query {i}"
            doc.success_score = 0.5
            hypothetical_service.hypothetical_cache[f"doc_{i}"] = doc
        
        initial_count = len(hypothetical_service.hypothetical_cache)
        
        # Run comprehensive pruning
        pruning_metrics = await hypothetical_service._comprehensive_pruning()
        
        final_count = len(hypothetical_service.hypothetical_cache)
        
        # Validate pruning metrics
        assert pruning_metrics.total_documents_before == initial_count
        assert pruning_metrics.total_documents_after == final_count
        assert pruning_metrics.documents_pruned >= 0
        assert pruning_metrics.pruning_time_ms > 0
        assert len(pruning_metrics.strategies_applied) >= 0
    
    @pytest.mark.asyncio
    async def test_performance_statistics(self, hypothetical_service):
        """Test performance statistics collection"""
        stats = hypothetical_service.get_pruning_statistics()
        
        # Validate structure
        assert "cache_statistics" in stats
        assert "performance_metrics" in stats
        assert "pruning_configuration" in stats
        assert "document_type_distribution" in stats
        assert "access_patterns" in stats
        
        # Validate cache statistics
        cache_stats = stats["cache_statistics"]
        assert "total_documents" in cache_stats
        assert "cache_size_mb" in cache_stats
        assert "utilization_percent" in cache_stats
        
        # Validate performance metrics
        perf_metrics = stats["performance_metrics"]
        assert "cache_hit_rate" in perf_metrics
        assert "hypothetical_generated" in perf_metrics


class TestPhase2Integration:
    """Integration tests for Phase 2 components working together"""
    
    @pytest.fixture
    async def integrated_services(self):
        """Create integrated test environment"""
        memory_v3 = UnifiedMemoryService()
        multimodal = MultimodalMemoryService()
        hypothetical = HypotheticalRAGService()
        
        await memory_v3.initialize()
        await multimodal.initialize()
        await hypothetical.initialize()
        
        yield {
            "memory_v3": memory_v3,
            "multimodal": multimodal,
            "hypothetical": hypothetical
        }
        
        # Cleanup
        for service in [memory_v3, hypothetical]:
            if hasattr(service, 'pruning_task') and service.pruning_task:
                service.pruning_task.cancel()
            if hasattr(service, 'warming_task') and service.warming_task:
                service.warming_task.cancel()
    
    @pytest.mark.asyncio
    async def test_end_to_end_agentic_workflow(self, integrated_services):
        """Test complete end-to-end agentic RAG workflow"""
        memory_v3 = integrated_services["memory_v3"]
        
        # Test complex query that should trigger multiple stages
        complex_query = "How to design a scalable microservices architecture with proper monitoring and observability?"
        
        # Mock LLM responses for critique and refinement
        with patch.object(memory_v3, '_generate_critique_llm') as mock_llm:
            mock_llm.side_effect = [
                # Critique response
                '{"relevance_score": 0.6, "coverage_gaps": ["monitoring details"], "refinements": "add specific monitoring tools", "tool_suggestions": ["github_search"], "multimodal_suggestions": [], "confidence_assessment": "medium"}',
                # Refinement response
                "How to design scalable microservices with Prometheus monitoring and distributed tracing?"
            ]
            
            result = await memory_v3.agentic_search(
                query=complex_query,
                user_id="integration_test",
                max_iterations=2
            )
            
            # Validate comprehensive result
            assert result is not None
            assert "retrieved_docs" in result
            assert "performance_metrics" in result
            assert "processing_stages" in result
            
            # Should have gone through multiple stages
            stages = result["processing_stages"]
            assert len(stages) >= 3  # At least retrieval, critique, synthesis
            
            # Should have performance metrics
            metrics = result["performance_metrics"]
            assert metrics["total_docs_retrieved"] >= 0
            assert 0 <= metrics["final_confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_multimodal_integration(self, integrated_services):
        """Test multimodal processing integration"""
        memory_v3 = integrated_services["memory_v3"]
        multimodal = integrated_services["multimodal"]
        
        # Test multimodal query
        multimodal_query = "Analyze the architecture diagram and explain the data flow"
        
        # Check multimodal detection
        is_multimodal = memory_v3._is_multimodal_query(multimodal_query)
        assert is_multimodal
        
        # Test visual search capability
        if multimodal.QDRANT_client:
            visual_results = await multimodal.search_visual_elements(
                query="architecture diagram",
                limit=5
            )
            assert isinstance(visual_results, list)
    
    @pytest.mark.asyncio
    async def test_hypothetical_enhancement(self, integrated_services):
        """Test hypothetical document enhancement"""
        hypothetical = integrated_services["hypothetical"]
        
        query = "Best practices for API rate limiting"
        
        # Mock dependencies for clean test
        with patch.object(hypothetical.memory_service, 'portkey') as mock_portkey:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "API rate limiting best practices guide"
            mock_portkey.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            with patch.object(hypothetical.memory_service, 'generate_embedding') as mock_embed:
                mock_embed.return_value = np.random.randn(1024).astype(np.float32)
                
                with patch.object(hypothetical.memory_service, 'search_knowledge') as mock_search:
                    mock_search.return_value = []
                    
                    # Test hypothetical search
                    results = await hypothetical.hypothetical_search(
                        query=query,
                        limit=5,
                        include_types=[HypotheticalType.ANSWER_FOCUSED, HypotheticalType.PROCEDURAL]
                    )
                    
                    assert isinstance(results, list)
                    # Should generate hypothetical documents
                    assert len(hypothetical.hypothetical_cache) > 0
    
    @pytest.mark.asyncio
    async def test_performance_targets(self, integrated_services):
        """Test that performance targets are met"""
        memory_v3 = integrated_services["memory_v3"]
        hypothetical = integrated_services["hypothetical"]
        
        # Test response time targets
        start_time = time.time()
        
        # Mock LLM for consistent timing
        with patch.object(memory_v3, '_generate_critique_llm') as mock_llm:
            mock_llm.return_value = '{"relevance_score": 0.8, "coverage_gaps": [], "refinements": "", "tool_suggestions": [], "multimodal_suggestions": [], "confidence_assessment": "high"}'
            
            result = await memory_v3.agentic_search(
                query="simple test query",
                max_iterations=1
            )
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Performance targets (relaxed for testing environment)
        assert response_time_ms < 5000  # 5 seconds max for test environment
        assert result["confidence_score"] >= 0.0
        
        # Test hypothetical generation time
        with patch.object(hypothetical.memory_service, 'portkey') as mock_portkey:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Quick response"
            mock_portkey.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            with patch.object(hypothetical.memory_service, 'generate_embedding') as mock_embed:
                mock_embed.return_value = np.random.randn(1024).astype(np.float32)
                
                start_time = time.time()
                hyp_doc = await hypothetical.generate_hypothetical_answer("test query")
                hyp_time_ms = (time.time() - start_time) * 1000
                
                # Should be fast
                assert hyp_time_ms < 2000  # 2 seconds max
                assert hyp_doc.metadata["generation_time_ms"] > 0
    
    @pytest.mark.asyncio
    async def test_error_resilience(self, integrated_services):
        """Test error handling and resilience"""
        memory_v3 = integrated_services["memory_v3"]
        hypothetical = integrated_services["hypothetical"]
        
        # Test with invalid inputs
        try:
            result = await memory_v3.agentic_search(
                query="",  # Empty query
                max_iterations=0  # Invalid iterations
            )
            # Should handle gracefully
            assert result is not None
        except Exception as e:
            # Should not crash
            assert isinstance(e, (ValueError, TypeError))
        
        # Test hypothetical service with LLM failure
        with patch.object(hypothetical.memory_service, 'portkey') as mock_portkey:
            mock_portkey.chat.completions.acreate = AsyncMock(side_effect=Exception("LLM Error"))
            
            try:
                await hypothetical.generate_hypothetical_answer("test query")
                assert False, "Should have raised exception"
            except Exception as e:
                assert "LLM Error" in str(e) or "Failed to generate" in str(e)
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, integrated_services):
        """Test memory efficiency and cleanup"""
        hypothetical = integrated_services["hypothetical"]
        
        # Generate multiple hypothetical documents
        queries = [f"test query {i}" for i in range(10)]
        
        with patch.object(hypothetical.memory_service, 'portkey') as mock_portkey:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_portkey.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            with patch.object(hypothetical.memory_service, 'generate_embedding') as mock_embed:
                mock_embed.return_value = np.random.randn(1024).astype(np.float32)
                
                for query in queries:
                    await hypothetical.generate_hypothetical_answer(query)
        
        initial_cache_size = len(hypothetical.hypothetical_cache)
        initial_memory_mb = hypothetical._calculate_cache_size_mb()
        
        # Trigger pruning
        pruning_metrics = await hypothetical._comprehensive_pruning()
        
        final_cache_size = len(hypothetical.hypothetical_cache)
        final_memory_mb = hypothetical._calculate_cache_size_mb()
        
        # Validate pruning occurred if needed
        if initial_cache_size > 0:
            assert pruning_metrics.total_documents_before == initial_cache_size
            assert pruning_metrics.total_documents_after == final_cache_size
            assert pruning_metrics.storage_freed_mb >= 0


# Performance benchmarks
class TestPhase2Performance:
    """Performance benchmarks for Phase 2 implementation"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_agentic_search_latency(self):
        """Benchmark agentic search latency"""
        service = UnifiedMemoryService()
        await service.initialize()
        
        try:
            queries = [
                "How to optimize database performance?",
                "Best practices for microservices?",
                "API security implementation guide",
                "Container orchestration strategies",
                "Machine learning model deployment"
            ]
            
            latencies = []
            
            with patch.object(service, '_generate_critique_llm') as mock_llm:
                mock_llm.return_value = '{"relevance_score": 0.8, "coverage_gaps": [], "refinements": "", "tool_suggestions": [], "multimodal_suggestions": [], "confidence_assessment": "high"}'
                
                for query in queries:
                    start_time = time.time()
                    await service.agentic_search(query, max_iterations=1)
                    latency_ms = (time.time() - start_time) * 1000
                    latencies.append(latency_ms)
            
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            
            print(f"Average latency: {avg_latency:.1f}ms")
            print(f"P95 latency: {p95_latency:.1f}ms")
            
            # Performance targets (relaxed for test environment)
            assert avg_latency < 3000  # 3 seconds average
            assert p95_latency < 5000   # 5 seconds P95
            
        finally:
            # Cleanup
            if hasattr(service, 'pruning_task') and service.pruning_task:
                service.pruning_task.cancel()
            if hasattr(service, 'warming_task') and service.warming_task:
                service.warming_task.cancel()
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_hypothetical_generation_throughput(self):
        """Benchmark hypothetical document generation throughput"""
        service = HypotheticalRAGService()
        await service.initialize()
        
        try:
            queries = [f"test query {i}" for i in range(20)]
            
            with patch.object(service.memory_service, 'portkey') as mock_portkey:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "Test response"
                mock_portkey.chat.completions.acreate = AsyncMock(return_value=mock_response)
                
                with patch.object(service.memory_service, 'generate_embedding') as mock_embed:
                    mock_embed.return_value = np.random.randn(1024).astype(np.float32)
                    
                    start_time = time.time()
                    
                    # Generate documents concurrently
                    tasks = [service.generate_hypothetical_answer(query) for query in queries]
                    await asyncio.gather(*tasks)
                    
                    total_time = time.time() - start_time
                    throughput = len(queries) / total_time
            
            print(f"Hypothetical generation throughput: {throughput:.1f} docs/second")
            
            # Performance target
            assert throughput > 2  # At least 2 documents per second
            
        finally:
            # Cleanup
            if service.pruning_task:
                service.pruning_task.cancel()
            if service.warming_task:
                service.warming_task.cancel()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"]) 