#!/usr/bin/env python3
"""
Quick Lambda Labs Status Checker
Check the status of all Lambda Labs instances quickly.
"""

import subprocess

INSTANCES = {
    "production": "104.171.202.103",
    "ai-core": "192.222.58.232",
    "mcp-servers": "104.171.202.117",
    "data-pipeline": "104.171.202.134",
    "development": "155.248.194.183",
}


def check_instance(name, ip):
    """Check instance status"""
    try:
        # Test SSH
        ssh_cmd = (
            f"ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@{ip} 'echo OK'"
        )
        ssh_result = subprocess.run(
            ssh_cmd, check=False, shell=True, capture_output=True, text=True, timeout=10
        )

        if ssh_result.returncode != 0:
            return f"❌ {name} ({ip}): SSH FAILED"

        # Test HTTP service
        http_cmd = f"ssh ubuntu@{ip} 'curl -s -m 5 http://localhost:8000/health || echo \"NO_SERVICE\"'"
        http_result = subprocess.run(
            http_cmd,
            check=False,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if "healthy" in http_result.stdout or "OK" in http_result.stdout:
            return f"✅ {name} ({ip}): OPERATIONAL"
        elif "NO_SERVICE" in http_result.stdout:
            return f"⚠️ {name} ({ip}): SSH OK, NO SERVICE"
        else:
            return f"🔄 {name} ({ip}): SSH OK, SERVICE STARTING"

    except Exception as e:
        return f"❌ {name} ({ip}): ERROR - {str(e)[:30]}"


def main():
    """Check all instances"""
    print("🔍 LAMBDA LABS STATUS CHECK")
    print("=" * 50)

    operational_count = 0
    total_count = len(INSTANCES)

    for name, ip in INSTANCES.items():
        status = check_instance(name, ip)
        print(status)
        if "✅" in status:
            operational_count += 1

    print("=" * 50)
    print(f"📊 Status: {operational_count}/{total_count} instances operational")

    if operational_count >= 3:
        print("🎉 DEPLOYMENT SUCCESSFUL!")
    elif operational_count >= 1:
        print("🔄 DEPLOYMENT IN PROGRESS...")
    else:
        print("⚠️ DEPLOYMENT ISSUES DETECTED")


if __name__ == "__main__":
    main()
