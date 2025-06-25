#!/usr/bin/env python3
"""
Comprehensive Gong Webhook Diagnosis Script
"""

import socket
import ssl
import requests
from datetime import datetime

def check_dns_resolution(domain):
    """Check DNS resolution for the domain"""
    print(f"\n🔍 DNS Resolution Check for {domain}")
    print("=" * 60)
    try:
        # Get IP addresses
        ips = socket.gethostbyname_ex(domain)
        print("✅ DNS Resolution successful")
        print(f"   Hostname: {ips[0]}")
        print(f"   Aliases: {ips[1]}")
        print(f"   IP Addresses: {ips[2]}")
        return ips[2]
    except socket.gaierror as e:
        print(f"❌ DNS Resolution failed: {e}")
        return []

def check_ssl_certificate(domain):
    """Check SSL certificate for the domain"""
    print(f"\n🔒 SSL Certificate Check for {domain}")
    print("=" * 60)
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                print("✅ SSL Certificate valid")
                print(f"   Subject: {cert.get('subject', 'N/A')}")
                print(f"   Issuer: {cert.get('issuer', 'N/A')}")
                print(f"   Not Before: {cert.get('notBefore', 'N/A')}")
                print(f"   Not After: {cert.get('notAfter', 'N/A')}")
                
                # Check if certificate covers the domain
                san = cert.get('subjectAltName', [])
                print(f"   Subject Alternative Names: {san}")
                return True
    except Exception as e:
        print(f"❌ SSL Certificate check failed: {e}")
        return False

def check_server_connectivity(url):
    """Check if the server is reachable"""
    print("\n🌐 Server Connectivity Check")
    print("=" * 60)
    try:
        # Check health endpoint
        health_url = url.replace('/calls', '/health')
        print(f"Checking health endpoint: {health_url}")
        
        response = requests.get(health_url, timeout=30, verify=True)
        print(f"✅ Health endpoint responded with status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return True
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_webhook_endpoint(url):
    """Test the webhook endpoint with a simulated request"""
    print("\n🧪 Webhook Endpoint Test")
    print("=" * 60)
    try:
        # Send empty POST request (simulating Gong test)
        print(f"Sending POST request to: {url}")
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Gong-Webhook-Test'
        }
        
        # Empty payload for test
        response = requests.post(url, json={}, headers=headers, timeout=30, verify=True)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint returned 200 OK")
            return True
        else:
            print(f"⚠️  Webhook endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def check_public_key_endpoint(base_url):
    """Check if the public key endpoint is accessible"""
    print("\n🔑 Public Key Endpoint Check")
    print("=" * 60)
    try:
        public_key_url = base_url.replace('/webhook/gong/calls', '/webhook/gong/public-key')
        print(f"Checking public key endpoint: {public_key_url}")
        
        response = requests.get(public_key_url, timeout=30, verify=True)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Public key endpoint accessible")
            print(f"Public Key Preview: {response.text[:100]}...")
            return True
        else:
            print(f"⚠️  Public key endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Public key check failed: {e}")
        return False

def check_ip_connectivity(ip):
    """Check if the IP is reachable"""
    print("\n🖥️  Direct IP Connectivity Check")
    print("=" * 60)
    try:
        # Try to connect to the IP on port 443
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((ip, 443))
        sock.close()
        
        if result == 0:
            print(f"✅ Port 443 is open on {ip}")
            return True
        else:
            print(f"❌ Port 443 is closed on {ip}")
            return False
    except Exception as e:
        print(f"❌ IP connectivity check failed: {e}")
        return False

def main():
    """Run comprehensive diagnosis"""
    print("\n" + "=" * 80)
    print("🔧 GONG WEBHOOK COMPREHENSIVE DIAGNOSIS")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    domain = "webhooks.sophia-intel.ai"
    webhook_url = f"https://{domain}/webhook/gong/calls"
    expected_ip = "34.74.88.2"
    
    # 1. DNS Resolution
    ips = check_dns_resolution(domain)
    
    if expected_ip in ips:
        print(f"\n✅ DNS correctly resolves to expected IP: {expected_ip}")
    else:
        print(f"\n⚠️  WARNING: DNS does not resolve to expected IP {expected_ip}")
        print(f"   Current IPs: {ips}")
    
    # 2. SSL Certificate
    ssl_valid = check_ssl_certificate(domain)
    
    # 3. Direct IP Connectivity
    if ips:
        for ip in ips:
            check_ip_connectivity(ip)
    
    # 4. Server Connectivity
    server_reachable = check_server_connectivity(webhook_url)
    
    # 5. Webhook Endpoint Test
    if server_reachable:
        webhook_works = test_webhook_endpoint(webhook_url)
    else:
        print("\n⚠️  Skipping webhook test due to server unreachability")
        webhook_works = False
    
    # 6. Public Key Endpoint
    if server_reachable:
        public_key_works = check_public_key_endpoint(webhook_url)
    else:
        print("\n⚠️  Skipping public key check due to server unreachability")
        public_key_works = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 80)
    
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
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ All checks passed! Webhook should be ready for Gong.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
