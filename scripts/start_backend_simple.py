#!/usr/bin/env python3
"""Simple Backend Starter for Sophia AI
Starts a minimal backend without Pulumi dependencies
"""

import subprocess
import sys
import time
from pathlib import Path

import requests

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_backend_exists():
    """Check if simplified backend exists"""
    backend_path = Path(__file__).parent.parent / "backend" / "main_simple.py"
    if not backend_path.exists():
        print(f"{YELLOW}⚠ Simplified backend not found. Creating it...{RESET}")
        create_simplified_backend()
    return True


def create_simplified_backend():
    """Create a simplified backend file"""
    backend_dir = Path(__file__).parent.parent / "backend"
    backend_dir.mkdir(exist_ok=True)

    simplified_backend = '''"""
Simplified Sophia AI Backend
Minimal FastAPI backend without Pulumi dependencies
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Executive Dashboard API",
    description="Simplified API for CEO Dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple auth check
def verify_admin_key(x_admin_key: str = Header(None)):
    """Verify admin key"""
    expected_key = os.getenv("SOPHIA_ADMIN_KEY", "sophia_admin_2024")
    if x_admin_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sophia AI Executive Dashboard API",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/health",
            "/api/executive/summary",
            "/api/executive/metrics",
            "/api/executive/alerts",
            "/api/executive/insights"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "database": "simulated",
            "ai_engine": "simulated"
        }
    }

@app.get("/api/executive/summary")
async def get_executive_summary(x_admin_key: str = Header(None)):
    """Get executive summary data"""
    verify_admin_key(x_admin_key)

    return {
        "timestamp": datetime.now().isoformat(),
        "company": "Pay Ready",
        "period": "Current Quarter",
        "revenue": {
            "current": 2500000,
            "target": 3000000,
            "growth": 0.15,
            "trend": "up"
        },
        "customers": {
            "total": 150,
            "new_this_month": 12,
            "churn_rate": 0.02,
            "satisfaction": 4.8
        },
        "operations": {
            "efficiency_score": 0.92,
            "cost_reduction": 0.08,
            "automation_rate": 0.78
        },
        "ai_insights": {
            "opportunities_identified": 5,
            "risks_detected": 2,
            "recommendations": 3,
            "accuracy_score": 0.94
        }
    }

@app.get("/api/executive/metrics")
async def get_executive_metrics(x_admin_key: str = Header(None)):
    """Get detailed metrics"""
    verify_admin_key(x_admin_key)

    return {
        "timestamp": datetime.now().isoformat(),
        "kpis": [
            {
                "id": "revenue_growth",
                "name": "Revenue Growth",
                "value": 15,
                "unit": "%",
                "trend": "up",
                "target": 12,
                "status": "exceeding"
            },
            {
                "id": "customer_satisfaction",
                "name": "Customer Satisfaction",
                "value": 4.8,
                "unit": "/5",
                "trend": "stable",
                "target": 4.5,
                "status": "on_track"
            },
            {
                "id": "operational_efficiency",
                "name": "Operational Efficiency",
                "value": 92,
                "unit": "%",
                "trend": "up",
                "target": 90,
                "status": "exceeding"
            },
            {
                "id": "ai_automation",
                "name": "AI Automation Rate",
                "value": 78,
                "unit": "%",
                "trend": "up",
                "target": 80,
                "status": "approaching"
            }
        ],
        "comparisons": {
            "vs_last_quarter": {
                "revenue": "+12%",
                "customers": "+8%",
                "efficiency": "+5%"
            },
            "vs_last_year": {
                "revenue": "+45%",
                "customers": "+32%",
                "efficiency": "+15%"
            }
        }
    }

@app.get("/api/executive/alerts")
async def get_executive_alerts(x_admin_key: str = Header(None)):
    """Get executive alerts"""
    verify_admin_key(x_admin_key)

    return {
        "timestamp": datetime.now().isoformat(),
        "alerts": [
            {
                "id": 1,
                "type": "opportunity",
                "priority": "high",
                "title": "High-value lead identified",
                "description": "AI detected a potential $500K opportunity with TechCorp Inc.",
                "action_required": "Schedule executive meeting",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": 2,
                "type": "risk",
                "priority": "medium",
                "title": "Customer churn risk detected",
                "description": "3 enterprise customers showing early churn indicators",
                "action_required": "Initiate retention protocol",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": 3,
                "type": "insight",
                "priority": "low",
                "title": "Market trend identified",
                "description": "Increasing demand for AI-powered analytics in retail sector",
                "action_required": "Review market strategy",
                "created_at": datetime.now().isoformat()
            }
        ],
        "summary": {
            "total": 3,
            "high_priority": 1,
            "medium_priority": 1,
            "low_priority": 1
        }
    }

@app.get("/api/executive/insights")
async def get_executive_insights(x_admin_key: str = Header(None)):
    """Get AI-generated insights"""
    verify_admin_key(x_admin_key)

    return {
        "timestamp": datetime.now().isoformat(),
        "insights": [
            {
                "category": "revenue",
                "insight": "Revenue growth is outpacing targets by 25%. Primary driver is enterprise segment.",
                "confidence": 0.92,
                "recommendations": [
                    "Increase enterprise sales team by 20%",
                    "Develop enterprise-specific features"
                ]
            },
            {
                "category": "operations",
                "insight": "AI automation has reduced operational costs by 15% this quarter.",
                "confidence": 0.88,
                "recommendations": [
                    "Expand automation to customer service",
                    "Implement predictive maintenance"
                ]
            },
            {
                "category": "market",
                "insight": "Competitor analysis shows 3-month window for market expansion.",
                "confidence": 0.85,
                "recommendations": [
                    "Launch targeted marketing campaign",
                    "Fast-track product roadmap"
                ]
            }
        ],
        "ai_performance": {
            "accuracy": 0.94,
            "predictions_made": 127,
            "successful_predictions": 119
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Sophia AI Backend on port {port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"Admin Key: {os.getenv('SOPHIA_ADMIN_KEY', 'sophia_admin_2024')}")
    uvicorn.run(app, host="0.0.0.0", port=port)
'''

    # Write the file
    backend_path = backend_dir / "main_simple.py"
    backend_path.write_text(simplified_backend)
    print(f"{GREEN}✓ Created simplified backend at {backend_path}{RESET}")


def check_port_available(port=8000):
    """Check if port is available"""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", port))
    sock.close()
    return result != 0


def start_backend():
    """Start the backend server"""
    print(f"\n{BLUE}=== Starting Sophia AI Backend ==={RESET}")

    # Check if backend exists
    check_backend_exists()

    # Check if port is available
    if not check_port_available(8000):
        print(f"{YELLOW}⚠ Port 8000 is already in use{RESET}")
        print(
            "Either a backend is already running or another service is using the port"
        )
        print("\nTo check what's running:")
        print("  lsof -i :8000")
        print("\nTo kill existing process:")
        print("  kill $(lsof -t -i:8000)")
        return False

    # Start the backend
    backend_dir = Path(__file__).parent.parent / "backend"
    cmd = [sys.executable, "main_simple.py"]

    print(f"{BLUE}Starting backend server...{RESET}")
    process = subprocess.Popen(
        cmd, cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Wait for server to start
    print("Waiting for server to start", end="")
    for i in range(10):
        time.sleep(1)
        print(".", end="", flush=True)
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print(f"\n{GREEN}✓ Backend server is running!{RESET}")
                return True
        except:
            pass

    print(f"\n{RED}✗ Backend failed to start{RESET}")
    return False


def test_endpoints():
    """Test backend endpoints"""
    print(f"\n{BLUE}=== Testing Backend Endpoints ==={RESET}")

    endpoints = [
        ("Health Check", "http://localhost:8000/health", None),
        ("Root", "http://localhost:8000/", None),
        (
            "Executive Summary",
            "http://localhost:8000/api/executive/summary",
            {"X-Admin-Key": "sophia_admin_2024"},
        ),
        (
            "Executive Metrics",
            "http://localhost:8000/api/executive/metrics",
            {"X-Admin-Key": "sophia_admin_2024"},
        ),
        (
            "Executive Alerts",
            "http://localhost:8000/api/executive/alerts",
            {"X-Admin-Key": "sophia_admin_2024"},
        ),
        (
            "Executive Insights",
            "http://localhost:8000/api/executive/insights",
            {"X-Admin-Key": "sophia_admin_2024"},
        ),
    ]

    all_passed = True
    for name, url, headers in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"{GREEN}✓ {name}: OK{RESET}")
            else:
                print(f"{RED}✗ {name}: Status {response.status_code}{RESET}")
                all_passed = False
        except Exception as e:
            print(f"{RED}✗ {name}: {str(e)}{RESET}")
            all_passed = False

    return all_passed


def print_usage():
    """Print usage information"""
    print(f"\n{BLUE}=== Backend is Running! ==={RESET}")
    print(
        """
API Endpoints:
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
- Executive Summary: http://localhost:8000/api/executive/summary
- Executive Metrics: http://localhost:8000/api/executive/metrics
- Executive Alerts: http://localhost:8000/api/executive/alerts
- Executive Insights: http://localhost:8000/api/executive/insights

Authentication:
- Header: X-Admin-Key
- Value: sophia_admin_2024

Test with curl:
curl -H "X-Admin-Key: sophia_admin_2024" http://localhost:8000/api/executive/summary

Next Steps:
1. Open Retool and create a new app
2. Add REST API resource:
   - Base URL: http://localhost:8000
   - Headers: X-Admin-Key = sophia_admin_2024
3. Build your dashboard!

To stop the server:
- Press Ctrl+C in this terminal
- Or run: kill $(lsof -t -i:8000)
"""
    )


def main():
    """Main function"""
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Sophia AI Simple Backend Starter{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

    # Start backend
    if start_backend():
        # Test endpoints
        if test_endpoints():
            print(f"\n{GREEN}✓ All tests passed!{RESET}")

        # Print usage
        print_usage()

        # Keep running
        print(f"\n{YELLOW}Backend is running. Press Ctrl+C to stop.{RESET}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Stopping backend...{RESET}")
    else:
        print(f"\n{RED}Failed to start backend{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
