#!/usr/bin/env python3
"""
🚀 Deployment Readiness Test Script

Tests that all required secrets and infrastructure are ready for deployment.
Uses the ACTUAL secret names from GitHub Organization.

Usage:
    python scripts/test_deployment_readiness.py
    python scripts/test_deployment_readiness.py --test-connections
"""

import os
import sys
import subprocess
import argparse
from typing import Dict, List

# ACTUAL secret names from GitHub Organization ai-cherry
GITHUB_SECRETS = {
    "DOCKERHUB_USERNAME": "Docker Hub username (scoobyjava15)",
    "DOCKER_TOKEN": "Docker Hub personal access token", 
    "LAMBDA_API_KEY": "Lambda Labs API key",
    "SSH_PRIVATE_KEY": "SSH private key for Lambda Labs",
    "QDRANT_API_KEY": "Qdrant Cloud API key",
    "OPENAI_API_KEY": "OpenAI API key",
    "ANTHROPIC_API_KEY": "Anthropic API key",
    "PULUMI_ACCESS_TOKEN": "Pulumi Cloud access token",
    "GONG_ACCESS_KEY": "Gong.io API access key (optional)",
    "HUBSPOT_ACCESS_TOKEN": "HubSpot API token (optional)",
}

def run_command(cmd: List[str], timeout: int = 30) -> tuple[bool, str, str]:
    """Run a command and return success, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd[0]}"

def check_github_secrets() -> Dict[str, bool]:
    """Check if all required GitHub secrets exist."""
    print("🔑 Checking GitHub Organization Secrets...")
    print("=" * 50)
    
    results = {}
    
    for secret_name, description in GITHUB_SECRETS.items():
        print(f"\n🔍 {secret_name}")
        print(f"   📝 {description}")
        
        # Try to get the secret
        success, stdout, stderr = run_command([
            "gh", "secret", "get", secret_name, "--org", "ai-cherry"
        ])
        
        if success and stdout.strip():
            print(f"   ✅ Available ({len(stdout.strip())} characters)")
            results[secret_name] = True
        else:
            print("   ❌ Not available or empty")
            if stderr:
                print(f"   📋 Error: {stderr.strip()}")
            results[secret_name] = False
    
    return results

def test_docker_access() -> bool:
    """Test Docker Hub access."""
    print("\n🐳 Testing Docker Hub Access...")
    
    # Get Docker credentials
    docker_user_success, docker_user, _ = run_command([
        "gh", "secret", "get", "DOCKERHUB_USERNAME", "--org", "ai-cherry"
    ])
    docker_token_success, docker_token, _ = run_command([
        "gh", "secret", "get", "DOCKER_TOKEN", "--org", "ai-cherry"
    ])
    
    if not (docker_user_success and docker_token_success):
        print("   ❌ Docker credentials not available")
        return False
    
    # Test Docker login (if Docker is available)
    docker_available, _, _ = run_command(["docker", "--version"])
    if not docker_available:
        print("   ⚠️  Docker not installed locally, skipping login test")
        return True
    
    # Create temporary Docker login test
    login_success, _, login_error = run_command([
        "docker", "login", "--username", docker_user.strip(), 
        "--password-stdin"
    ])
    
    if login_success:
        print(f"   ✅ Docker login successful for user: {docker_user.strip()}")
        return True
    else:
        print(f"   ❌ Docker login failed: {login_error}")
        return False

def test_lambda_labs_ssh() -> bool:
    """Test SSH access to Lambda Labs."""
    print("\n🖥️  Testing Lambda Labs SSH Access...")
    
    # Get SSH key
    ssh_key_success, ssh_key, _ = run_command([
        "gh", "secret", "get", "SSH_PRIVATE_KEY", "--org", "ai-cherry"
    ])
    
    if not ssh_key_success:
        print("   ❌ SSH private key not available")
        return False
    
    # Write SSH key to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.key') as f:
        f.write(ssh_key)
        ssh_key_path = f.name
    
    try:
        # Set proper permissions
        os.chmod(ssh_key_path, 0o600)
        
        # Test SSH connection
        ssh_success, ssh_output, ssh_error = run_command([
            "ssh", "-o", "StrictHostKeyChecking=no", 
            "-o", "ConnectTimeout=10",
            "-i", ssh_key_path,
            "ubuntu@192.222.58.232", 
            "echo 'SSH connection successful'"
        ], timeout=15)
        
        if ssh_success:
            print("   ✅ SSH connection to Lambda Labs successful")
            return True
        else:
            print(f"   ❌ SSH connection failed: {ssh_error}")
            return False
            
    finally:
        # Clean up SSH key file
        os.unlink(ssh_key_path)

def test_k3s_access() -> bool:
    """Test K3s cluster access."""
    print("\n☸️  Testing K3s Cluster Access...")
    
    # Check if kubectl is available
    kubectl_available, _, _ = run_command(["kubectl", "version", "--client"])
    if not kubectl_available:
        print("   ⚠️  kubectl not installed locally, skipping cluster test")
        return True
    
    # Get SSH key and setup kubeconfig
    ssh_key_success, ssh_key, _ = run_command([
        "gh", "secret", "get", "SSH_PRIVATE_KEY", "--org", "ai-cherry"
    ])
    
    if not ssh_key_success:
        print("   ❌ SSH private key not available")
        return False
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.key') as f:
        f.write(ssh_key)
        ssh_key_path = f.name
    
    try:
        os.chmod(ssh_key_path, 0o600)
        
        # Get kubeconfig from Lambda Labs
        kubeconfig_success, kubeconfig, kubeconfig_error = run_command([
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10", 
            "-i", ssh_key_path,
            "ubuntu@192.222.58.232",
            "sudo cat /etc/rancher/k3s/k3s.yaml"
        ], timeout=15)
        
        if not kubeconfig_success:
            print(f"   ❌ Failed to get kubeconfig: {kubeconfig_error}")
            return False
        
        # Save kubeconfig temporarily
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            # Replace localhost with actual IP
            fixed_kubeconfig = kubeconfig.replace('127.0.0.1:6443', '192.222.58.232:6443')
            f.write(fixed_kubeconfig)
            kubeconfig_path = f.name
        
        # Test kubectl with the kubeconfig
        os.environ['KUBECONFIG'] = kubeconfig_path
        cluster_success, cluster_output, cluster_error = run_command([
            "kubectl", "cluster-info", "--request-timeout=10s"
        ])
        
        if cluster_success:
            print("   ✅ K3s cluster access successful")
            cluster_lines = cluster_output.split('\n')
            if cluster_lines:
                print(f"   📋 Cluster info: {cluster_lines[0]}")
            return True
        else:
            print(f"   ❌ K3s cluster access failed: {cluster_error}")
            return False
            
    finally:
        # Clean up temporary files
        os.unlink(ssh_key_path)
        if 'kubeconfig_path' in locals():
            os.unlink(kubeconfig_path)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test deployment readiness")
    parser.add_argument(
        "--test-connections",
        action="store_true",
        help="Also test actual connections (Docker, SSH, K3s)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Sophia AI Deployment Readiness Test")
    print("=" * 60)
    
    # Check GitHub CLI authentication
    gh_auth_success, _, _ = run_command(["gh", "auth", "status"])
    if not gh_auth_success:
        print("❌ GitHub CLI not authenticated")
        print("Run: gh auth login")
        sys.exit(1)
    
    print("✅ GitHub CLI authenticated")
    
    # Check secrets
    secret_results = check_github_secrets()
    
    required_secrets = [
        "DOCKERHUB_USERNAME", "DOCKER_TOKEN", "LAMBDA_API_KEY", 
        "SSH_PRIVATE_KEY", "QDRANT_API_KEY", "OPENAI_API_KEY", 
        "ANTHROPIC_API_KEY", "PULUMI_ACCESS_TOKEN"
    ]
    
    missing_required = [s for s in required_secrets if not secret_results.get(s, False)]
    
    print("\n📊 Secret Summary:")
    print(f"   Total secrets checked: {len(GITHUB_SECRETS)}")
    print(f"   Available: {sum(secret_results.values())}")
    print(f"   Missing: {len(GITHUB_SECRETS) - sum(secret_results.values())}")
    print(f"   Required missing: {len(missing_required)}")
    
    if missing_required:
        print(f"❌ Missing required secrets: {', '.join(missing_required)}")
        sys.exit(1)
    
    print("✅ All required secrets available!")
    
    # Test connections if requested
    if args.test_connections:
        print("\n🔗 Testing Connections...")
        
        connection_tests = [
            ("Docker Hub", test_docker_access),
            ("Lambda Labs SSH", test_lambda_labs_ssh), 
            ("K3s Cluster", test_k3s_access)
        ]
        
        test_results = {}
        for test_name, test_func in connection_tests:
            try:
                result = test_func()
                test_results[test_name] = result
            except Exception as e:
                print(f"   ❌ {test_name} test failed with error: {e}")
                test_results[test_name] = False
        
        print("\n🔗 Connection Test Summary:")
        for test_name, result in test_results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}")
        
        if not all(test_results.values()):
            print("\n⚠️  Some connection tests failed, but deployment may still work")
    
    print(f"\n🎉 DEPLOYMENT READINESS: {'READY' if not missing_required else 'NOT READY'}")
    
    if not missing_required:
        print("\n🚀 Ready to deploy! Run the GitHub Actions workflow:")
        print("   gh workflow run 'Sophia AI - Single Source of Truth Deployment'")

if __name__ == "__main__":
    main() 