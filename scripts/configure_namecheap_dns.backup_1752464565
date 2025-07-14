#!/usr/bin/env python3
"""
Configure Namecheap DNS for sophia-intel.ai
Run this after whitelisting your IP address
"""

import os
import sys
import requests
from typing import Dict, List

# Namecheap API configuration
NAMECHEAP_API_USER = os.getenv('NAMECHEAP_API_USER', 'lynnmusil')
NAMECHEAP_API_KEY = os.getenv('NAMECHEAP_API_KEY')
NAMECHEAP_CLIENT_IP = os.getenv('NAMECHEAP_CLIENT_IP')

# Domain configuration
DOMAIN = 'sophia-intel.ai'
SLD = 'sophia-intel'
TLD = 'ai'

# DNS Records to configure
DNS_RECORDS = [
    # Main domain and www to Lambda Labs
    {'Type': 'A', 'Name': '@', 'Address': '192.222.58.232'},
    {'Type': 'A', 'Name': 'www', 'Address': '192.222.58.232'},
    
    # API subdomain to Lambda Labs backend
    {'Type': 'A', 'Name': 'api', 'Address': '192.222.58.232'},
    
    # Webhooks subdomain to Lambda Labs
    {'Type': 'A', 'Name': 'webhooks', 'Address': '192.222.58.232'},
    
    # Monitoring subdomains
    {'Type': 'A', 'Name': 'grafana', 'Address': '192.222.58.232'},
    
    # Dashboard to Vercel (will be configured later)
    # {'Type': 'CNAME', 'Name': 'dashboard', 'Address': 'cname.vercel-dns.com'},
    
    # Documentation (future)
    # {'Type': 'A', 'Name': 'docs', 'Address': '76.76.21.21'},
]

def configure_dns():
    # Get current IP
    try:
        client_ip = requests.get('https://api.ipify.org').text.strip()
        print(f"Your IP: {client_ip}")
    except:
        print("❌ Could not get IP address")
        return False
    
    # Build API parameters
    params = {
        'ApiUser': NAMECHEAP_API_USER,
        'ApiKey': NAMECHEAP_API_KEY,
        'UserName': NAMECHEAP_API_USER,
        'ClientIp': client_ip,
        'Command': 'namecheap.domains.dns.setHosts',
        'SLD': SLD,
        'TLD': TLD
    }
    
    # Add all records to params
    for i, record in enumerate(DNS_RECORDS, 1):
        params[f'HostName{i}'] = record['Name']
        params[f'RecordType{i}'] = record['Type']
        params[f'Address{i}'] = record['Address']
        params[f'TTL{i}'] = '1800'
    
    print("\n🌐 Configuring DNS records...")
    
    # Make API call
    url = "https://api.namecheap.com/xml.response"
    response = requests.post(url, data=params)
    
    if '<ApiResponse Status="OK"' in response.text:
        print("\n✅ DNS records configured successfully!")
        print("\nRecords set:")
        for r in DNS_RECORDS:
            if r['Name'] == '@':
                print(f"   {r['Type']} sophia-intel.ai → {r['Address']}")
            else:
                print(f"   {r['Type']} {r['Name']}.sophia-intel.ai → {r['Address']}")
        return True
    else:
        print("\n❌ DNS configuration failed!")
        if "Invalid request IP" in response.text:
            print(f"\n⚠️  You need to whitelist your IP ({client_ip}) in Namecheap:")
            print("1. Log into Namecheap.com")
            print("2. Go to Profile → Tools → API Access")
            print(f"3. Add IP: {client_ip}")
            print("4. Save and run this script again")
        else:
            print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Sophia AI DNS Configuration")
    print("==============================")
    
    if configure_dns():
        print("\n✅ Next steps:")
        print("1. Wait 5-30 minutes for DNS propagation")
        print("2. Go to Vercel dashboard and add sophia-intel.ai domain")
        print("3. Your site will be live at https://sophia-intel.ai")
    else:
        sys.exit(1) 