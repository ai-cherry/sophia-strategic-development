#!/usr/bin/env python3
"""
Launch AI server in alternative region
"""

import time

import requests

API_KEY = "secret_sophia-july-25_989f13097e374c779f28629f5a1ac571.iH4OIeM78TWyzDiltkpLAzlPeaTw68HJ"
BASE_URL = "https://cloud.lambda.ai/api/v1"

# Try different regions and instance types
alternatives = [
    {"region": "us-west-2", "type": "gpu_1x_a100_sxm4", "name": "Arizona A100"},
    {"region": "us-east-1", "type": "gpu_1x_a100_sxm4", "name": "Virginia A100"},
    {"region": "us-south-1", "type": "gpu_1x_a100", "name": "Texas A100"},
    {"region": "us-west-1", "type": "gpu_1x_a100", "name": "California A100 PCIe"},
    {
        "region": "us-west-1",
        "type": "gpu_1x_h100_pcie",
        "name": "California H100 (if available)",
    },
]


for alt in alternatives:
    response = requests.post(
        f"{BASE_URL}/instance-operations/launch",
        auth=(API_KEY, ""),
        json={
            "region_name": alt["region"],
            "instance_type_name": alt["type"],
            "ssh_key_names": ["lambda_labs_key"],
            "name": "sophia-ai-prod",
            "quantity": 1,
        },
    )

    if response.status_code in [200, 201]:
        break
    else:
        error = response.json().get("error", {})
        time.sleep(1)
else:
    pass

# Check all instances
response = requests.get(f"{BASE_URL}/instances", auth=(API_KEY, ""))
if response.status_code == 200:
    for _inst in response.json()["data"]:
        pass
