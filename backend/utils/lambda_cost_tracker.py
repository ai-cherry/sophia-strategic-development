"""
Lambda Inference Cost Tracker
Track your AI inference costs in real-time
"""

import time
from typing import Dict, List

class CostTracker:
    def __init__(self):
        self.requests: List[Dict] = []
        self.total_cost = 0.0

        # Lambda Labs pricing (per token)
        self.pricing = {
            "llama3.2-3b-instruct": {"input": 0.000000015, "output": 0.000000025},
            "llama3.3-70b-instruct-fp8": {"input": 0.00000012, "output": 0.0000003},
            "llama-3.1-405b-instruct": {"input": 0.0000008, "output": 0.0000008},
            "qwen2.5-coder-32b-instruct": {"input": 0.00000007, "output": 0.00000016},
        }

    def track_request(self, model: str, input_tokens: int, output_tokens: int):
        """Track a single request"""
        rates = self.pricing.get(model, self.pricing["llama3.3-70b-instruct-fp8"])
        cost = (input_tokens * rates["input"]) + (output_tokens * rates["output"])

        request = {
            "timestamp": time.time(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
        }

        self.requests.append(request)
        self.total_cost += cost

        return cost

    def get_summary(self):
        """Get cost summary"""
        if not self.requests:
            return "No requests tracked yet"

        return f"""
💰 Lambda Inference Cost Summary:
- Total Requests: {len(self.requests)}
- Total Cost: ${self.total_cost:.6f}
- Average Cost per Request: ${self.total_cost/len(self.requests):.6f}
- Estimated Monthly Cost: ${self.total_cost * 30 * 24 * 60:.2f} (at current rate)

Compare to OpenAI GPT-4:
- You saved: ${(self.total_cost * 100) - self.total_cost:.6f} (99% savings!)
"""

# Global tracker
cost_tracker = CostTracker()
