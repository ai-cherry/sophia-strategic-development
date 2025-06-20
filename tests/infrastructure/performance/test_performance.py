"""
Performance tests for infrastructure components
"""

import pytest
import time
import asyncio
import statistics
from typing import List, Dict, Any
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.performance
class TestPerformance:
    """
    Performance tests for infrastructure components.
    These tests verify that the infrastructure meets performance requirements.
    """
    
    def setup_method(self):
        """
        Set up the test environment before each test.
        """
        self.performance_thresholds = {
            "snowflake_query": 2.0,  # seconds
            "pinecone_search": 0.1,  # seconds
            "gong_webhook": 0.5,     # seconds
            "api_response": 0.2,     # seconds
        }
        self.test_results = {}
    
    @pytest.mark.asyncio
    async def test_snowflake_query_performance(self, mock_snowflake_client):
        """
        Test Snowflake query performance under various loads.
        """
        # Generate test data
        logger.info("Generating test data for Snowflake performance test...")
        mock_snowflake_client.insert_data("performance_test", 
            [{"id": i, "value": f"test-{i}", "timestamp": time.time()} 
             for i in range(10000)]
        )
        
        # Test single query performance
        query = "SELECT * FROM performance_test WHERE value LIKE 'test-%' LIMIT 1000"
        
        start_time = time.time()
        result = mock_snowflake_client.query(query)
        single_query_time = time.time() - start_time
        
        logger.info(f"Single query completed in {single_query_time:.3f} seconds")
        assert single_query_time < self.performance_thresholds["snowflake_query"], \
            f"Query took {single_query_time:.3f}s, exceeding threshold of {self.performance_thresholds['snowflake_query']}s"
        
        # Test concurrent query performance
        concurrent_queries = 10
        query_times = []
        
        async def run_query():
            start = time.time()
            mock_snowflake_client.query(query)
            return time.time() - start
        
        tasks = [run_query() for _ in range(concurrent_queries)]
        query_times = await asyncio.gather(*tasks)
        
        avg_query_time = statistics.mean(query_times)
        max_query_time = max(query_times)
        
        logger.info(f"Concurrent queries - Avg: {avg_query_time:.3f}s, Max: {max_query_time:.3f}s")
        
        # Even under load, queries should complete within reasonable time
        assert max_query_time < self.performance_thresholds["snowflake_query"] * 2, \
            f"Max query time {max_query_time:.3f}s exceeds acceptable threshold"
        
        self.test_results["snowflake_query"] = {
            "single_query_time": single_query_time,
            "avg_concurrent_time": avg_query_time,
            "max_concurrent_time": max_query_time
        }
    
    @pytest.mark.asyncio
    async def test_pinecone_vector_search_performance(self, mock_pinecone_client):
        """
        Test Pinecone vector search performance.
        """
        # Generate test vectors
        logger.info("Generating test vectors for Pinecone performance test...")
        vector_count = 10000
        mock_pinecone_client.generate_test_vectors(count=vector_count, index_name="performance-test")
        
        # Test single search performance
        search_vector = [0.1] * 128
        
        start_time = time.time()
        result = mock_pinecone_client.search(
            vector=search_vector,
            top_k=10,
            index_name="performance-test"
        )
        single_search_time = time.time() - start_time
        
        logger.info(f"Single search completed in {single_search_time:.3f} seconds")
        assert single_search_time < self.performance_thresholds["pinecone_search"], \
            f"Search took {single_search_time:.3f}s, exceeding threshold of {self.performance_thresholds['pinecone_search']}s"
        
        # Test batch search performance
        batch_size = 100
        search_times = []
        
        async def run_search():
            start = time.time()
            mock_pinecone_client.search(
                vector=search_vector,
                top_k=10,
                index_name="performance-test"
            )
            return time.time() - start
        
        tasks = [run_search() for _ in range(batch_size)]
        search_times = await asyncio.gather(*tasks)
        
        avg_search_time = statistics.mean(search_times)
        p95_search_time = statistics.quantiles(search_times, n=20)[18]  # 95th percentile
        
        logger.info(f"Batch searches - Avg: {avg_search_time:.3f}s, P95: {p95_search_time:.3f}s")
        
        # 95th percentile should still be within acceptable range
        assert p95_search_time < self.performance_thresholds["pinecone_search"] * 3, \
            f"P95 search time {p95_search_time:.3f}s exceeds acceptable threshold"
        
        self.test_results["pinecone_search"] = {
            "single_search_time": single_search_time,
            "avg_batch_time": avg_search_time,
            "p95_batch_time": p95_search_time
        }
    
    @pytest.mark.asyncio
    async def test_gong_webhook_processing_performance(self, mock_gong_client):
        """
        Test Gong webhook processing performance.
        """
        # Test single webhook processing
        test_payload = {
            "call_id": "perf-test-001",
            "duration": 300,
            "participants": ["user1", "user2"],
            "transcript": "Test transcript " * 100  # Simulate larger payload
        }
        
        start_time = time.time()
        result = mock_gong_client.send_test_data(test_payload)
        single_webhook_time = time.time() - start_time
        
        logger.info(f"Single webhook processed in {single_webhook_time:.3f} seconds")
        assert single_webhook_time < self.performance_thresholds["gong_webhook"], \
            f"Webhook processing took {single_webhook_time:.3f}s, exceeding threshold"
        
        # Test webhook burst performance
        burst_size = 50
        webhook_times = []
        
        async def send_webhook(call_id):
            payload = test_payload.copy()
            payload["call_id"] = f"perf-test-{call_id}"
            start = time.time()
            mock_gong_client.send_test_data(payload)
            return time.time() - start
        
        tasks = [send_webhook(i) for i in range(burst_size)]
        webhook_times = await asyncio.gather(*tasks)
        
        avg_webhook_time = statistics.mean(webhook_times)
        max_webhook_time = max(webhook_times)
        
        logger.info(f"Webhook burst - Avg: {avg_webhook_time:.3f}s, Max: {max_webhook_time:.3f}s")
        
        # System should handle bursts gracefully
        assert max_webhook_time < self.performance_thresholds["gong_webhook"] * 5, \
            f"Max webhook time {max_webhook_time:.3f}s during burst exceeds acceptable threshold"
        
        self.test_results["gong_webhook"] = {
            "single_webhook_time": single_webhook_time,
            "avg_burst_time": avg_webhook_time,
            "max_burst_time": max_webhook_time
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_pipeline_performance(self, mock_gong_client, mock_snowflake_client):
        """
        Test end-to-end data pipeline performance from Gong to Snowflake.
        """
        # Measure time from Gong webhook to data availability in Snowflake
        test_call_id = f"e2e-perf-{int(time.time())}"
        test_data = {
            "call_id": test_call_id,
            "duration": 600,
            "participants": ["user1", "user2", "user3"],
            "transcript": "Performance test transcript " * 50,
            "timestamp": time.time()
        }
        
        # Send data to Gong
        start_time = time.time()
        mock_gong_client.send_test_data(test_data)
        
        # Poll Snowflake for data availability
        max_wait_time = 10  # seconds
        poll_interval = 0.1  # seconds
        data_found = False
        
        while time.time() - start_time < max_wait_time:
            query = f"SELECT * FROM gong_calls WHERE call_id = '{test_call_id}'"
            result = mock_snowflake_client.query(query)
            
            if result:
                data_found = True
                break
            
            await asyncio.sleep(poll_interval)
        
        end_to_end_time = time.time() - start_time
        
        assert data_found, f"Data not found in Snowflake after {max_wait_time} seconds"
        logger.info(f"End-to-end pipeline completed in {end_to_end_time:.3f} seconds")
        
        # End-to-end should complete within reasonable time
        assert end_to_end_time < 5.0, f"Pipeline took {end_to_end_time:.3f}s, exceeding 5s threshold"
        
        self.test_results["e2e_pipeline"] = {
            "pipeline_time": end_to_end_time
        }
    
    @pytest.mark.asyncio
    async def test_scalability_limits(self, mock_snowflake_client, mock_pinecone_client):
        """
        Test infrastructure scalability limits.
        """
        logger.info("Testing infrastructure scalability limits...")
        
        # Test Snowflake with large dataset
        large_dataset_size = 100000
        logger.info(f"Testing Snowflake with {large_dataset_size} records...")
        
        # Insert data in batches
        batch_size = 10000
        insert_times = []
        
        for i in range(0, large_dataset_size, batch_size):
            batch_data = [
                {"id": j, "value": f"scale-test-{j}", "timestamp": time.time()}
                for j in range(i, min(i + batch_size, large_dataset_size))
            ]
            
            start = time.time()
            mock_snowflake_client.insert_data("scalability_test", batch_data)
            insert_times.append(time.time() - start)
        
        avg_insert_time = statistics.mean(insert_times)
        logger.info(f"Average batch insert time: {avg_insert_time:.3f}s")
        
        # Query performance on large dataset
        start = time.time()
        result = mock_snowflake_client.query(
            "SELECT COUNT(*) FROM scalability_test WHERE value LIKE 'scale-test-%'"
        )
        large_query_time = time.time() - start
        
        logger.info(f"Query on {large_dataset_size} records completed in {large_query_time:.3f}s")
        
        # Test Pinecone with large vector index
        large_vector_count = 50000
        logger.info(f"Testing Pinecone with {large_vector_count} vectors...")
        
        mock_pinecone_client.generate_test_vectors(
            count=large_vector_count,
            index_name="scalability-test"
        )
        
        # Search performance on large index
        search_vector = [0.1] * 128
        start = time.time()
        result = mock_pinecone_client.search(
            vector=search_vector,
            top_k=100,
            index_name="scalability-test"
        )
        large_index_search_time = time.time() - start
        
        logger.info(f"Search on {large_vector_count} vectors completed in {large_index_search_time:.3f}s")
        
        self.test_results["scalability"] = {
            "snowflake_records": large_dataset_size,
            "snowflake_query_time": large_query_time,
            "pinecone_vectors": large_vector_count,
            "pinecone_search_time": large_index_search_time
        }
        
        # Assert reasonable performance even at scale
        assert large_query_time < 10.0, f"Large dataset query exceeded 10s threshold"
        assert large_index_search_time < 1.0, f"Large index search exceeded 1s threshold"
    
    def test_generate_performance_report(self):
        """
        Generate a comprehensive performance test report.
        """
        if not self.test_results:
            pytest.skip("No performance test results to report")
        
        logger.info("\n" + "="*60)
        logger.info("PERFORMANCE TEST REPORT")
        logger.info("="*60)
        
        for test_name, results in self.test_results.items():
            logger.info(f"\n{test_name.upper()}:")
            for metric, value in results.items():
                if isinstance(value, float):
                    logger.info(f"  {metric}: {value:.3f}s")
                else:
                    logger.info(f"  {metric}: {value}")
        
        logger.info("\n" + "="*60)
        
        # Save report to file
        import json
        report_path = "tests/infrastructure/performance/performance_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Performance report saved to: {report_path}")
