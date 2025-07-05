#!/usr/bin/env python3
"""
Comprehensive Gong Webhook Diagnosis Script
"""

import socket
import ssl

import requests


def check_dns_resolution(domain):
    """Check DNS resolution for the domain"""
    try:
        # Get IP addresses
        ips = socket.gethostbyname_ex(domain)
        return ips[2]
    except socket.gaierror:
        return []


def check_ssl_certificate(domain):
    """Check SSL certificate for the domain"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                # Check if certificate covers the domain
                cert.get("subjectAltName", [])
                return True
    except Exception:
        return False


def check_server_connectivity(url):
    """Check if the server is reachable"""
    try:
        # Check health endpoint
        health_url = url.replace("/calls", "/health")

        requests.get(health_url, timeout=30, verify=True)
        return True
    except requests.exceptions.SSLError:
        return False
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False
    except Exception:
        return False


def test_webhook_endpoint(url):
    """Test the webhook endpoint with a simulated request"""
    try:
        # Send empty POST request (simulating Gong test)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Gong-Webhook-Test",
        }

        # Empty payload for test
        response = requests.post(url, json={}, headers=headers, timeout=30, verify=True)

        return response.status_code == 200

    except Exception:
        return False


def check_public_key_endpoint(base_url):
    """Check if the public key endpoint is accessible"""
    try:
        public_key_url = base_url.replace(
            "/webhook/gong/calls", "/webhook/gong/public-key"
        )

        response = requests.get(public_key_url, timeout=30, verify=True)

        return response.status_code == 200

    except Exception:
        return False


def check_ip_connectivity(ip):
    """Check if the IP is reachable"""
    try:
        # Try to connect to the IP on port 443
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((ip, 443))
        sock.close()

        return result == 0
    except Exception:
        return False


def main():
    """Run comprehensive diagnosis"""

    domain = "webhooks.sophia-intel.ai"
    webhook_url = f"https://{domain}/webhook/gong/calls"
    expected_ip = "34.74.88.2"

    # 1. DNS Resolution
    ips = check_dns_resolution(domain)

    if expected_ip in ips:
        pass
    else:
        pass

    # 2. SSL Certificate
    ssl_valid = check_ssl_certificate(domain)

    # 3. Direct IP Connectivity
    if ips:
        for ip in ips:
            check_ip_connectivity(ip)

    # 4. Server Connectivity
    server_reachable = check_server_connectivity(webhook_url)

    # 5. Webhook Endpoint Test
    webhook_works = test_webhook_endpoint(webhook_url) if server_reachable else False

    # 6. Public Key Endpoint
    if server_reachable:
        public_key_works = check_public_key_endpoint(webhook_url)
    else:
        public_key_works = False

    # Summary

    issues = []

    if not ips:
        issues.append("❌ DNS not resolving")
    elif expected_ip not in ips:
        issues.append(f"⚠️  DNS not pointing to expected IP {expected_ip}")

    if not ssl_valid:
        issues.append("❌ SSL certificate issues")

    if not server_reachable:
        issues.append("❌ Server not reachable")

    if server_reachable and not webhook_works:
        issues.append("❌ Webhook endpoint not returning 200 OK")

    if server_reachable and not public_key_works:
        issues.append("⚠️  Public key endpoint not accessible")

    if issues:
        for _issue in issues:
            pass
    else:
        pass


if __name__ == "__main__":
    main()
