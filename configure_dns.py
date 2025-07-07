#!/usr/bin/env python3
"""
Configure DNS for sophia-intel.ai using Namecheap API
Sets up proper DNS records for Vercel frontend and Lambda Labs backend
"""

import json
import os
import subprocess
import time

import requests

# Configuration
DOMAIN = "sophia-intel.ai"
DOMAIN_NAME = "sophia-intel"
TLD = "ai"
NAMECHEAP_API_KEY = os.getenv("NAMECHEAP_API_KEY", "d6913ec33b2c4d328be9cbb4db382eca")
NAMECHEAP_API_USER = "scoobyjava"  # You may need to update this
NAMECHEAP_CLIENT_IP = requests.get("https://api.ipify.org").text

# Load cluster config
with open("sophia_cluster_config.json") as f:
    cluster_config = json.load(f)

MASTER_IP = cluster_config["master"]["ip"]
WORKER_IPS = [w["ip"] for w in cluster_config["workers"]]


def get_vercel_domains():
    """Get Vercel deployment domains"""
    cmd = ["vercel", "ls", "--json", "--token", os.getenv("VERCEL_API_TOKEN")]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        deployments = json.loads(result.stdout)
        # Get the most recent production deployment
        for deployment in deployments:
            if deployment.get("target") == "production":
                return deployment.get("url")
    return None


def configure_namecheap_dns():
    """Configure DNS records via Namecheap API"""
    print("🌐 Configuring DNS for sophia-intel.ai...")

    # Get Vercel CNAME target
    vercel_domain = get_vercel_domains()
    if not vercel_domain:
        vercel_domain = "cname.vercel-dns.com"  # Default Vercel CNAME

    # DNS Records to create
    dns_records = [
        # Root domain - points to Vercel
        {"Type": "CNAME", "Name": "@", "Address": vercel_domain, "TTL": "1800"},
        # WWW - also points to Vercel
        {"Type": "CNAME", "Name": "www", "Address": vercel_domain, "TTL": "1800"},
        # App subdomain - points to Vercel
        {"Type": "CNAME", "Name": "app", "Address": vercel_domain, "TTL": "1800"},
        # API subdomain - points to Lambda Labs master
        {"Type": "A", "Name": "api", "Address": MASTER_IP, "TTL": "1800"},
        # Additional API records for load balancing
        {"Type": "A", "Name": "api", "Address": WORKER_IPS[0], "TTL": "1800"},
        {"Type": "A", "Name": "api", "Address": WORKER_IPS[1], "TTL": "1800"},
        # MCP services subdomains
        {"Type": "A", "Name": "mcp", "Address": MASTER_IP, "TTL": "1800"},
        # Monitoring subdomain
        {"Type": "A", "Name": "monitor", "Address": MASTER_IP, "TTL": "1800"},
        # Grafana subdomain
        {"Type": "A", "Name": "grafana", "Address": MASTER_IP, "TTL": "1800"},
    ]

    # Namecheap API endpoint
    api_url = "https://api.namecheap.com/xml.response"

    # Build the API request
    params = {
        "ApiUser": NAMECHEAP_API_USER,
        "ApiKey": NAMECHEAP_API_KEY,
        "UserName": NAMECHEAP_API_USER,
        "ClientIp": NAMECHEAP_CLIENT_IP,
        "Command": "namecheap.domains.dns.setHosts",
        "SLD": DOMAIN_NAME,
        "TLD": TLD,
    }

    # Add DNS records to params
    for i, record in enumerate(dns_records, 1):
        params[f"HostName{i}"] = record["Name"]
        params[f"RecordType{i}"] = record["Type"]
        params[f"Address{i}"] = record["Address"]
        params[f"TTL{i}"] = record["TTL"]

    # Make the API request
    response = requests.post(api_url, params=params)

    if response.status_code == 200:
        print("✅ DNS records configured successfully!")
        print("\nDNS Records:")
        for record in dns_records:
            print(
                f"  {record['Name']}.{DOMAIN} → {record['Address']} ({record['Type']})"
            )
    else:
        print(f"❌ Failed to configure DNS: {response.text}")
        return False

    return True


def configure_vercel_domain():
    """Add custom domain to Vercel project"""
    print("\n🔗 Configuring Vercel custom domain...")

    # Add domain to Vercel
    cmd = ["vercel", "domains", "add", DOMAIN, "--token", os.getenv("VERCEL_API_TOKEN")]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Added {DOMAIN} to Vercel")
    else:
        print(f"⚠️  Domain may already be configured: {result.stderr}")

    # Also add app subdomain
    cmd = [
        "vercel",
        "domains",
        "add",
        f"app.{DOMAIN}",
        "--token",
        os.getenv("VERCEL_API_TOKEN"),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Added app.{DOMAIN} to Vercel")


def main():
    print("�� DNS Configuration for Sophia AI")
    print("=" * 50)

    # Configure Namecheap DNS
    if not configure_namecheap_dns():
        print("❌ DNS configuration failed!")
        return

    # Configure Vercel domains
    configure_vercel_domain()

    print("\n🎉 DNS Configuration Complete!")
    print("=" * 50)
    print("Frontend URLs:")
    print(f"  https://{DOMAIN}")
    print(f"  https://www.{DOMAIN}")
    print(f"  https://app.{DOMAIN}")
    print("\nBackend URLs:")
    print(f"  https://api.{DOMAIN}")
    print(f"  https://mcp.{DOMAIN}")
    print(f"  https://monitor.{DOMAIN}")
    print(f"  https://grafana.{DOMAIN}")
    print("\n⏳ DNS propagation may take up to 48 hours")


if __name__ == "__main__":
    main()
