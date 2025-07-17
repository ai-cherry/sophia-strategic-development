#!/usr/bin/env python3
"""
Update Namecheap DNS records for sophia-intel.ai domain
Automatically updates DNS based on deployed infrastructure IPs
"""

import argparse
import json
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List
import sys
import time

class NamecheapDNSUpdater:
    """Manages Namecheap DNS updates"""
    
    def __init__(self, api_key: str, api_user: str, username: str):
        self.api_key = api_key
        self.api_user = api_user
        self.username = username
        self.api_url = "https://api.namecheap.com/xml.response"
        
    def get_client_ip(self) -> str:
        """Get current public IP for API whitelisting"""
        response = requests.get('https://api.ipify.org')
        return response.text.strip()
    
    def get_current_records(self, domain: str) -> List[Dict]:
        """Get current DNS records for the domain"""
        sld, tld = domain.split('.')
        
        params = {
            'ApiUser': self.api_user,
            'ApiKey': self.api_key,
            'UserName': self.username,
            'Command': 'namecheap.domains.dns.getHosts',
            'ClientIp': self.get_client_ip(),
            'SLD': sld,
            'TLD': tld
        }
        
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.text)
        records = []
        
        for host in root.findall('.//host'):
            records.append({
                'name': host.get('Name', '@'),
                'type': host.get('Type'),
                'address': host.get('Address'),
                'ttl': host.get('TTL', '300')
            })
        
        return records
    
    def update_records(self, domain: str, new_records: List[Dict]) -> bool:
        """Update DNS records for the domain"""
        sld, tld = domain.split('.')
        
        # Start with base parameters
        params = {
            'ApiUser': self.api_user,
            'ApiKey': self.api_key,
            'UserName': self.username,
            'Command': 'namecheap.domains.dns.setHosts',
            'ClientIp': self.get_client_ip(),
            'SLD': sld,
            'TLD': tld
        }
        
        # Add each record to parameters
        for i, record in enumerate(new_records, 1):
            params[f'HostName{i}'] = record['name']
            params[f'RecordType{i}'] = record['type']
            params[f'Address{i}'] = record['address']
            params[f'TTL{i}'] = record.get('ttl', '300')
        
        response = requests.post(self.api_url, data=params)
        response.raise_for_status()
        
        # Check if update was successful
        root = ET.fromstring(response.text)
        api_response = root.find('.//ApiResponse')
        success = api_response is not None and api_response.get('Status') == 'OK'
        
        if success:
            print(f"✅ Successfully updated {len(new_records)} DNS records")
        else:
            print(f"❌ Failed to update DNS records")
            print(response.text)
        
        return success
    
    def update_sophia_dns(self, domain: str, vm_ips: Dict[str, str]) -> bool:
        """Update DNS records specifically for Sophia AI infrastructure"""
        
        # Get current records to preserve non-infrastructure records
        current_records = self.get_current_records(domain)
        
        # Define our infrastructure DNS mappings
        dns_mappings = {
            'main-api': ['@', 'api', 'dashboard', 'sophia'],
            'qdrant-primary': ['qdrant'],
            'redis-mem0-postgres': ['memory', 'redis', 'postgres']
        }
        
        # Build new records list
        new_records = []
        processed_names = set()
        
        # Add infrastructure records
        for purpose, ip in vm_ips.items():
            if purpose in dns_mappings:
                for hostname in dns_mappings[purpose]:
                    new_records.append({
                        'name': hostname,
                        'type': 'A',
                        'address': ip,
                        'ttl': '300'
                    })
                    processed_names.add(hostname)
        
        # Preserve non-infrastructure records (like MX, TXT, etc.)
        for record in current_records:
            if record['type'] != 'A' or record['name'] not in processed_names:
                new_records.append(record)
        
        # Update DNS
        print(f"📋 Updating {len(new_records)} DNS records for {domain}")
        for record in new_records:
            if record['type'] == 'A' and record['name'] in processed_names:
                print(f"  → {record['name']}.{domain} => {record['address']}")
        
        return self.update_records(domain, new_records)

def main():
    parser = argparse.ArgumentParser(description="Update Namecheap DNS records")
    parser.add_argument("--domain", required=True, help="Domain to update")
    parser.add_argument("--ips", required=True, help="JSON string or file path with VM IPs")
    parser.add_argument("--api-key", required=True, help="Namecheap API key")
    parser.add_argument("--api-user", required=True, help="Namecheap API user")
    parser.add_argument("--username", required=True, help="Namecheap username")
    parser.add_argument("--validate", action="store_true", help="Validate after update")
    
    args = parser.parse_args()
    
    # Parse IPs
    try:
        if args.ips.startswith('{'):
            # Direct JSON string
            vm_ips = json.loads(args.ips)
        else:
            # File path
            with open(args.ips, 'r') as f:
                vm_ips = json.load(f)
    except Exception as e:
        print(f"❌ Failed to parse IPs: {e}")
        sys.exit(1)
    
    # Create updater and update DNS
    updater = NamecheapDNSUpdater(args.api_key, args.api_user, args.username)
    
    print(f"🌐 Updating DNS records for {args.domain}")
    print(f"📡 VM IPs: {json.dumps(vm_ips, indent=2)}")
    
    success = updater.update_sophia_dns(args.domain, vm_ips)
    
    if success and args.validate:
        print("\n⏳ Waiting 30 seconds for DNS propagation...")
        time.sleep(30)
        
        # Validate DNS records
        print("\n🔍 Validating DNS records...")
        updated_records = updater.get_current_records(args.domain)
        
        for record in updated_records:
            if record['type'] == 'A':
                print(f"  ✓ {record['name']}.{args.domain} => {record['address']}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
