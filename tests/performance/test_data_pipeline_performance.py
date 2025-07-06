from locust import HttpUser, between, task


class SophiaAIUser(HttpUser):
    """
    Performance test user for simulating real-world usage of the Sophia AI API.
    This user will make requests to the main chat/query endpoint with different
    types of queries to test various data pipelines.
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """on_start is called when a user starts before any task is scheduled"""
        self.client.headers = {"Content-Type": "application/json"}
        # In a real scenario, you might want to handle authentication here
        # self.client.headers["Authorization"] = f"Bearer {self.get_auth_token()}"

    @task(3)  # This task will be picked 3 times more often than tasks with no weight
    def query_sales_data(self):
        """Simulates a user asking for sales data."""
        self.client.post(
            "/api/v1/chat",  # Assuming this is the chat endpoint
            json={
                "query": "Show me top deals this quarter",
                "context": {
                    "user_id": "performance_test_user",
                    "session_id": "sales-test",
                },
            },
        )

    @task(2)
    def query_marketing_data(self):
        """Simulates a user asking for marketing analytics."""
        self.client.post(
            "/api/v1/chat",
            json={
                "query": "What was the performance of our last email campaign?",
                "context": {
                    "user_id": "performance_test_user",
                    "session_id": "marketing-test",
                },
            },
        )

    @task(1)
    def query_general_knowledge(self):
        """Simulates a user asking a general question."""
        self.client.post(
            "/api/v1/chat",
            json={
                "query": "What are the company's goals for this year?",
                "context": {
                    "user_id": "performance_test_user",
                    "session_id": "general-test",
                },
            },
        )

    @task(1)
    def query_complex_data_synthesis(self):
        """Simulates a complex query that might require multiple data sources."""
        self.client.post(
            "/api/v1/chat",
            json={
                "query": "Compare sales performance in regions where we ran marketing campaigns vs regions where we did not.",
                "context": {
                    "user_id": "performance_test_user",
                    "session_id": "complex-test",
                },
            },
        )


# To run this test:
# 1. Make sure the Sophia AI backend is running.
# 2. Run locust from the command line:
#    locust -f tests/performance/test_data_pipeline_performance.py --host=http://localhost:8000
# 3. Open your browser to http://localhost:8089 and start the test.
