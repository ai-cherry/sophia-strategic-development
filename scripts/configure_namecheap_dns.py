#!/usr/bin/env python3
"""
Configure Namecheap DNS for sophia-intel.ai
Run this after whitelisting your IP address
"""

import requests
import sys

def configure_dns():
    # Credentials
    api_key = "d6913ec33b2c4d328be9cbb4db382eca"
    api_user = "scoobyjava"
    
    # Get current IP
    try:
        client_ip = requests.get('https://api.ipify.org').text.strip()
        print(f"Your IP: {client_ip}")
    except:
        print("❌ Could not get IP address")
        return False
    
    # DNS records to set
    records = [
        {'Type': 'A', 'Name': '@', 'Address': '76.76.21.21'},
        {'Type': 'A', 'Name': 'www', 'Address': '76.76.21.21'},
        {'Type': 'A', 'Name': 'api', 'Address': '192.222.58.232'},
        {'Type': 'CNAME', 'Name': 'dashboard', 'Address': 'cname.vercel-dns.com.'},
        {'Type': 'A', 'Name': 'docs', 'Address': '76.76.21.21'},
        {'Type': 'A', 'Name': 'grafana', 'Address': '192.222.58.232'},
    ]
    
    # Build API parameters
    params = {
        'ApiUser': api_user,
        'ApiKey': api_key,
        'UserName': api_user,
        'ClientIp': client_ip,
        'Command': 'namecheap.domains.dns.setHosts',
        'SLD': 'sophia-intel',
        'TLD': 'ai'
    }
    
    # Add all records to params
    for i, record in enumerate(records, 1):
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
        for r in records:
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