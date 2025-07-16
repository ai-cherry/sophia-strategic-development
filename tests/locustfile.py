"""
Phase 4: Locust Load Testing
Tests 2000 qps with <0.5% error rate and <150ms P95

Date: July 12, 2025
"""

import json
import random
import time
from datetime import datetime

from locust import HttpUser, task, between, events

class SophiaAIUser(HttpUser):
    """Simulated user for Sophia AI platform"""
    
    wait_time = between(0.1, 0.5)  # Fast requests for high QPS
    
    def on_start(self):
        """Initialize user session"""
        self.user_id = f"user_{random.randint(1000, 9999)}"
        self.session_id = f"session_{int(time.time())}"
        self.modes = ["professional", "casual", "snarky", "ceo_roast"]
        
    @task(40)
    def chat_query(self):
        """Test chat endpoint - highest weight"""
        queries = [
            "Revenue trends?",
            "What are Q3 sales?",
            "Show me customer metrics",
            "Team performance update",
            "Market analysis summary"
        ]
        
        payload = {
            "message": random.choice(queries),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "mode": random.choice(self.modes),
            "include_trends": random.choice([True, False]),
            "include_video": random.choice([True, False])
        }
        
        with self.client.post(
            "/api/v4/chat/unified",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Check latency requirement
                if data.get("performance", {}).get("latency_ms", 999) > 150:
                    response.failure("Latency exceeded 150ms")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(20)
    def search_knowledge(self):
        """Test search endpoint"""
        search_terms = [
            "revenue growth",
            "customer acquisition",
            "product metrics",
            "employee satisfaction",
            "market trends"
        ]
        
        params = {
            "q": random.choice(search_terms),
            "limit": 10,
            "user_id": self.user_id
        }
        
        self.client.get("/api/v4/search", params=params)
    
    @task(10)
    def get_dashboard_metrics(self):
        """Test dashboard metrics endpoint"""
        self.client.get(f"/api/v4/dashboard/metrics?user_id={self.user_id}")
    
    @task(10)
    def get_session_summary(self):
        """Test session summary endpoint"""
        self.client.get(
            f"/api/v4/chat/session/{self.session_id}/summary",
            params={"user_id": self.user_id}
        )
    
    @task(5)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")
    
    @task(5)
    def streaming_chat(self):
        """Test streaming chat endpoint"""
        payload = {
            "message": "Quick status update",
            "user_id": self.user_id,
            "mode": "fast"
        }
        
        # Simulate SSE connection
        with self.client.post(
            "/api/v4/chat/stream",
            json=payload,
            stream=True,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Read some chunks
                for _ in range(5):
                    chunk = response.raw.read(1024)
                    if not chunk:
                        break
            else:
                response.failure(f"Stream failed: {response.status_code}")
    
    @task(10)
    def batch_operation(self):
        """Test batch operations"""
        records = [
            {
                "content": f"Test record {i}",
                "metadata": {"type": "test", "index": i}
            }
            for i in range(10)
        ]
        
        payload = {
            "records": records,
            "user_id": self.user_id
        }
        
        self.client.post("/api/v4/batch/ingest", json=payload)

class AdminUser(HttpUser):
    """Admin user for monitoring endpoints"""
    
    wait_time = between(5, 10)  # Less frequent
    
    @task
    def get_system_metrics(self):
        """Get system metrics"""
        self.client.get("/api/v4/admin/metrics")
    
    @task
    def get_performance_report(self):
        """Get performance report"""
        self.client.get("/api/v4/admin/performance")

# Custom event handlers for detailed reporting
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, **kwargs):
    """Track detailed request metrics"""
    if response_time > 150:
        print(f"⚠️  Slow request: {name} took {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test"""
    print("🚀 Starting Sophia AI load test")
    print("Target: 2000 QPS, <0.5% errors, <150ms P95")
    print("=" * 50)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate final report"""
    print("\n" + "=" * 50)
    print("📊 Load Test Results")
    print("=" * 50)
    
    # Calculate metrics
    stats = environment.stats
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    
    if total_requests > 0:
        error_rate = (total_failures / total_requests) * 100
        avg_response_time = stats.total.avg_response_time
        p95_response_time = stats.total.get_response_time_percentile(0.95)
        p99_response_time = stats.total.get_response_time_percentile(0.99)
        
        print(f"Total Requests: {total_requests:,}")
        print(f"Total Failures: {total_failures:,}")
        print(f"Error Rate: {error_rate:.2f}%")
        print(f"Average Response Time: {avg_response_time:.0f}ms")
        print(f"P95 Response Time: {p95_response_time:.0f}ms")
        print(f"P99 Response Time: {p99_response_time:.0f}ms")
        
        # Check if targets met
        print("\n📋 Target Validation:")
        print(f"Error Rate < 0.5%: {'✅' if error_rate < 0.5 else '❌'} ({error_rate:.2f}%)")
        print(f"P95 < 150ms: {'✅' if p95_response_time < 150 else '❌'} ({p95_response_time:.0f}ms)")
        
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_requests": total_requests,
            "total_failures": total_failures,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "targets_met": {
                "error_rate": error_rate < 0.5,
                "p95_latency": p95_response_time < 150
            }
        }
        
        with open("PHASE_4_LOAD_TEST_RESULTS.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\nDetailed results saved to: PHASE_4_LOAD_TEST_RESULTS.json")

# Configuration for running standalone
if __name__ == "__main__":
    # Run with: locust -f tests/locustfile.py --host=http://localhost:8000
    # For 2000 QPS: locust -f tests/locustfile.py --host=http://localhost:8000 -u 200 -r 50 --run-time 5m
    pass 