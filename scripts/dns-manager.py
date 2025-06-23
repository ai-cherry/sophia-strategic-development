#!/usr/bin/env python3
"""
Sophia Intelligence Platform - DNS Management Script
Automated DNS management for sophia-intel.ai using Namecheap API
Integrates with Pulumi ESC for secret management and IP whitelisting
"""

import os
import sys
import json
import asyncio
import argparse
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import requests
import socket
from datetime import datetime

@dataclass
class DNSRecord:
    """DNS record configuration"""
    name: str
    record_type: str
    value: str
    ttl: int = 300

@dataclass
class IPContext:
    """IP context for API calls"""
    environment: str
    ip_address: str
    confidence: int
    details: str

class PulumiESCIntegration:
    """Integration with Pulumi ESC for configuration management"""
    
    def __init__(self, organization: str = "scoobyjava-org", project: str = "default", environment: str = "sophia-intelligence-platform"):
        self.organization = organization
        self.project = project
        self.environment = environment
        
    async def get_configuration(self) -> Dict:
        """Get configuration from Pulumi ESC"""
        try:
            cmd = [
                "pulumi", "config", "get", 
                "--stack", f"{self.organization}/{self.project}/{self.environment}",
                "--json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get Pulumi ESC configuration: {e}")
            print(f"Command: {' '.join(cmd)}")
            print(f"Error output: {e.stderr}")
            raise
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Pulumi ESC configuration: {e}")
            raise

    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get a specific secret from Pulumi ESC"""
        try:
            cmd = [
                "pulumi", "config", "get", secret_name,
                "--stack", f"{self.organization}/{self.project}/{self.environment}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
            
        except subprocess.CalledProcessError:
            print(f"⚠️  Secret '{secret_name}' not found in Pulumi ESC")
            return None

class IPContextDetector:
    """Detect execution context and determine appropriate IP"""
    
    def __init__(self, ip_addresses: Dict[str, str]):
        self.ip_addresses = ip_addresses
        
    def detect_context(self) -> IPContext:
        """Detect current execution context"""
        
        # Check for GitHub Actions
        if self._is_github_actions():
            return IPContext(
                environment="github_actions",
                ip_address=self.ip_addresses.get("github_actions", ""),
                confidence=95,
                details="GitHub Actions CI/CD environment detected"
            )
        
        # Check for Pulumi Cloud
        if self._is_pulumi_cloud():
            return IPContext(
                environment="pulumi_cloud", 
                ip_address=self.ip_addresses.get("pulumi_cloud", ""),
                confidence=90,
                details="Pulumi Cloud deployment environment detected"
            )
        
        # Default to Lambda Labs (local dev)
        return IPContext(
            environment="local_dev",
            ip_address=self.ip_addresses.get("lambda_labs", ""),
            confidence=85,
            details="Local development environment (Lambda Labs server)"
        )
    
    def _is_github_actions(self) -> bool:
        """Check if running in GitHub Actions"""
        indicators = [
            os.getenv("GITHUB_ACTIONS") == "true",
            os.getenv("CI") == "true" and os.getenv("GITHUB_REPOSITORY") is not None,
            os.getenv("GITHUB_RUN_ID") is not None,
            os.getenv("RUNNER_OS") is not None
        ]
        return sum(indicators) >= 3
    
    def _is_pulumi_cloud(self) -> bool:
        """Check if running in Pulumi Cloud"""
        indicators = [
            os.getenv("PULUMI_COMMAND") is not None,
            os.getenv("PULUMI_ORGANIZATION") is not None,
            os.getenv("PULUMI_STACK") is not None,
            os.getenv("KUBERNETES_SERVICE_HOST") is not None
        ]
        return sum(indicators) >= 2

class NamecheapDNSManager:
    """Namecheap DNS API management"""
    
    def __init__(self, api_user: str, api_key: str, username: str, client_ip: str, sandbox: bool = False):
        self.api_user = api_user
        self.api_key = api_key
        self.username = username
        self.client_ip = client_ip
        self.endpoint = "https://api.sandbox.namecheap.com/xml.response" if sandbox else "https://api.namecheap.com/xml.response"
        
    async def create_dns_record(self, domain: str, record: DNSRecord) -> bool:
        """Create or update a DNS record"""
        try:
            print(f"📝 Creating DNS record: {record.name}.{domain} → {record.value}")
            
            # Get current records
            current_records = await self.get_host_records(domain)
            
            # Update records list
            updated_records = self._update_record_in_list(current_records, record)
            
            # Set all records
            success = await self.set_host_records(domain, updated_records)
            
            if success:
                print(f"  ✅ Successfully created/updated DNS record")
            else:
                print(f"  ❌ Failed to create DNS record")
                
            return success
            
        except Exception as e:
            print(f"  ❌ Error creating DNS record: {e}")
            return False
    
    async def get_host_records(self, domain: str) -> List[DNSRecord]:
        """Get current host records for domain"""
        try:
            sld, tld = self._split_domain(domain)
            
            params = {
                "ApiUser": self.api_user,
                "ApiKey": self.api_key,
                "UserName": self.username,
                "Command": "namecheap.domains.dns.getHosts",
                "ClientIp": self.client_ip,
                "SLD": sld,
                "TLD": tld
            }
            
            response = requests.get(self.endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            records = []
            
            # Parse XML response
            for host in root.findall(".//host"):
                records.append(DNSRecord(
                    name=host.get("Name", ""),
                    record_type=host.get("Type", ""),
                    value=host.get("Address", ""),
                    ttl=int(host.get("TTL", "300"))
                ))
            
            return records
            
        except Exception as e:
            print(f"❌ Error getting host records: {e}")
            return []
    
    async def set_host_records(self, domain: str, records: List[DNSRecord]) -> bool:
        """Set all host records for domain"""
        try:
            sld, tld = self._split_domain(domain)
            
            params = {
                "ApiUser": self.api_user,
                "ApiKey": self.api_key,
                "UserName": self.username,
                "Command": "namecheap.domains.dns.setHosts",
                "ClientIp": self.client_ip,
                "SLD": sld,
                "TLD": tld
            }
            
            # Add each record
            for i, record in enumerate(records, 1):
                params[f"HostName{i}"] = record.name
                params[f"RecordType{i}"] = record.record_type
                params[f"Address{i}"] = record.value
                params[f"TTL{i}"] = record.ttl
            
            response = requests.get(self.endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            return root.get("Status") == "OK" and root.find(".//Errors") is None
            
        except Exception as e:
            print(f"❌ Error setting host records: {e}")
            return False
    
    def _split_domain(self, domain: str) -> Tuple[str, str]:
        """Split domain into SLD and TLD"""
        parts = domain.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid domain: {domain}")
        
        # Handle common TLDs
        if len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) == 3 and parts[1] in ["co", "com", "net", "org"]:
            return parts[0], ".".join(parts[1:])
        else:
            return parts[0], ".".join(parts[1:])
    
    def _update_record_in_list(self, existing_records: List[DNSRecord], new_record: DNSRecord) -> List[DNSRecord]:
        """Update or add record in existing records list"""
        # Remove existing record with same name and type
        filtered_records = [
            r for r in existing_records 
            if not (r.name == new_record.name and r.record_type == new_record.record_type)
        ]
        
        # Add new record
        filtered_records.append(new_record)
        return filtered_records

class SophiaDNSManager:
    """Main DNS management class for Sophia Intelligence Platform"""
    
    def __init__(self):
        self.pulumi_esc = PulumiESCIntegration()
        self.config = None
        self.dns_manager = None
        
    async def initialize(self):
        """Initialize DNS manager with Pulumi ESC configuration"""
        print("🚀 Initializing Sophia DNS Manager...")
        
        try:
            # Load configuration from Pulumi ESC
            print("📡 Loading configuration from Pulumi ESC...")
            self.config = await self.pulumi_esc.get_configuration()
            
            # Get secrets
            api_user = await self.pulumi_esc.get_secret("NAMECHEAP_API_USER")
            api_key = await self.pulumi_esc.get_secret("NAMECHEAP_API_KEY")
            username = await self.pulumi_esc.get_secret("NAMECHEAP_USERNAME")
            
            # Get IP addresses
            lambda_ip = await self.pulumi_esc.get_secret("LAMBDA_IP_ADDRESS")
            github_ip = await self.pulumi_esc.get_secret("GH_IP_ADDRESS")
            pulumi_ip = await self.pulumi_esc.get_secret("PULUMI_IP_ADDRESS")
            
            if not all([api_user, api_key, username, lambda_ip, github_ip, pulumi_ip]):
                raise ValueError("Missing required secrets in Pulumi ESC")
            
            # Detect IP context
            ip_addresses = {
                "lambda_labs": lambda_ip,
                "github_actions": github_ip,
                "pulumi_cloud": pulumi_ip
            }
            
            ip_detector = IPContextDetector(ip_addresses)
            context = ip_detector.detect_context()
            
            print(f"🔍 IP Context: {context.environment} ({context.ip_address}) - {context.details}")
            
            # Initialize Namecheap DNS manager
            self.dns_manager = NamecheapDNSManager(
                api_user=api_user,
                api_key=api_key,
                username=username,
                client_ip=context.ip_address,
                sandbox=False
            )
            
            print("✅ Sophia DNS Manager initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize DNS manager: {e}")
            raise
    
    async def setup_domain_records(self, domain: str = "sophia-intel.ai", server_ip: str = None):
        """Set up all DNS records for the domain"""
        if not self.dns_manager:
            await self.initialize()
        
        if not server_ip:
            server_ip = await self.pulumi_esc.get_secret("LAMBDA_IP_ADDRESS")
        
        print(f"🌐 Setting up DNS records for {domain} → {server_ip}")
        
        # Define all DNS records
        records = [
            DNSRecord("@", "A", server_ip),        # Root domain
            DNSRecord("api", "A", server_ip),      # API subdomain
            DNSRecord("webhooks", "A", server_ip), # Webhooks subdomain
            DNSRecord("dashboard", "A", server_ip),# Dashboard subdomain
            DNSRecord("sophia", "A", server_ip),   # Sophia subdomain
            DNSRecord("dev", "A", server_ip),      # Development subdomain
            DNSRecord("*", "A", server_ip)         # Wildcard subdomain
        ]
        
        success_count = 0
        for record in records:
            if await self.dns_manager.create_dns_record(domain, record):
                success_count += 1
        
        print(f"📊 DNS Setup Summary: {success_count}/{len(records)} records created successfully")
        return success_count == len(records)
    
    async def validate_dns_records(self, domain: str = "sophia-intel.ai", expected_ip: str = None):
        """Validate DNS record propagation"""
        if not expected_ip:
            expected_ip = await self.pulumi_esc.get_secret("LAMBDA_IP_ADDRESS")
        
        print(f"🔍 Validating DNS records for {domain}...")
        
        subdomains = ["", "api", "webhooks", "dashboard", "sophia", "dev"]
        results = []
        
        for subdomain in subdomains:
            hostname = f"{subdomain}.{domain}" if subdomain else domain
            
            try:
                # Resolve DNS
                ip_addresses = socket.gethostbyname_ex(hostname)[2]
                is_valid = expected_ip in ip_addresses
                
                result = {
                    "hostname": hostname,
                    "expected_ip": expected_ip,
                    "actual_ips": ip_addresses,
                    "is_valid": is_valid
                }
                
                results.append(result)
                
                status = "✅" if is_valid else "❌"
                print(f"  {status} {hostname} → {', '.join(ip_addresses)}")
                
            except socket.gaierror as e:
                result = {
                    "hostname": hostname,
                    "expected_ip": expected_ip,
                    "actual_ips": [],
                    "is_valid": False,
                    "error": str(e)
                }
                results.append(result)
                print(f"  ❌ {hostname} → DNS resolution failed: {e}")
        
        valid_count = sum(1 for r in results if r["is_valid"])
        print(f"📊 DNS Validation Summary: {valid_count}/{len(results)} records valid")
        
        return results

async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Sophia Intelligence Platform DNS Manager")
    parser.add_argument("action", choices=["setup", "validate", "status"], help="Action to perform")
    parser.add_argument("--domain", default="sophia-intel.ai", help="Domain to manage")
    parser.add_argument("--ip", help="Server IP address (uses Pulumi ESC if not specified)")
    
    args = parser.parse_args()
    
    dns_manager = SophiaDNSManager()
    
    try:
        if args.action == "setup":
            await dns_manager.setup_domain_records(args.domain, args.ip)
        elif args.action == "validate":
            await dns_manager.validate_dns_records(args.domain, args.ip)
        elif args.action == "status":
            await dns_manager.initialize()
            print("✅ DNS Manager is operational")
    
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 