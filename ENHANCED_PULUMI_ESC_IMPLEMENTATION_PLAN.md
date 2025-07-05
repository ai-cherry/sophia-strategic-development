# 🔐 Enhanced Sophia AI Pulumi ESC Secret Management Implementation Plan

## 📋 Executive Summary

**Mission:** Transform Sophia AI's secret management from a bypassed fallback system to a robust, enterprise-grade, fully automated Pulumi ESC-driven solution with 100% GitHub Organization Secrets integration.

**Current Critical Issues:**
- ❌ Broken Pulumi ESC authentication requiring bypass mechanisms
- ❌ Missing critical Python scripts (github_sync_bidirectional.py, get_secret.py)
- ❌ Inconsistent secret definitions across multiple configuration sources
- ❌ Security vulnerabilities with hardcoded fallbacks
- ❌ Limited secret loading (fallback vs full 200+ secrets)

**Target Outcome:**
- ✅ 100% automated GitHub Organization Secrets → Pulumi ESC → Applications pipeline
- ✅ Enterprise-grade security with audit trails and compliance
- ✅ Zero-downtime secret rotation and disaster recovery
- ✅ Complete observability and monitoring

## 🏗️ Enhanced Architecture Overview

```
GitHub Organization Secrets (ai-cherry) [Single Source of Truth]
           ↓ Automated Sync (Bidirectional)
    Pulumi ESC Environment (sophia-ai-production)
           ↓ Secure Runtime Injection
    Applications (Docker Secrets/K8s Secrets/Env Vars)
           ↓ Comprehensive Monitoring
    Audit Trail & Compliance Reporting
```

## 🚀 **PHASE 1: Foundation & Critical Fixes** (Week 1)

### **1.1 Root Cause Analysis & Authentication Fix**

#### Critical Issues to Resolve:
- Broken Pulumi ESC authentication
- Missing PULUMI_ACCESS_TOKEN permissions
- CLI version compatibility
- Non-functional secret retrieval scripts

### **1.2 Fix Security Configuration Issues**

**Current Problems in `backend/core/security_config.py`:**
- SecretType enum using `os.getenv()` instead of static strings
- SECRETS_REGISTRY using `os.getenv("JWT_SECRET")` as dictionary key
- Inconsistent secret naming conventions

## 🔄 **PHASE 2: Enhanced Security Configuration** (Week 1-2)

### **2.1 Complete Secret Management Infrastructure**

#### Enhanced Bidirectional GitHub Sync Script
```python
# infrastructure/esc/github_sync_bidirectional.py
import os
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import asdict

class GitHubESCSyncManager:
    def __init__(self, org: str, github_token: str, pulumi_org: str, environment: str):
        self.org = org
        self.github_token = github_token
        self.pulumi_org = pulumi_org
        self.environment = environment
        self.logger = logging.getLogger(__name__)

        # GitHub API setup
        self.github_headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.github_api_base = f'https://api.github.com/orgs/{org}'

    def get_github_secrets(self) -> Dict[str, str]:
        """Retrieve all organization secrets from GitHub"""
        try:
            url = f'{self.github_api_base}/actions/secrets'
            response = requests.get(url, headers=self.github_headers, timeout=30)
            response.raise_for_status()

            secrets_data = response.json()
            secret_names = [secret['name'] for secret in secrets_data.get('secrets', [])]

            self.logger.info(f"Found {len(secret_names)} secrets in GitHub organization")
            return {name: "***PLACEHOLDER***" for name in secret_names}  # We can't read actual values

        except requests.RequestException as e:
            self.logger.error(f"Failed to retrieve GitHub secrets: {e}")
            return {}

    def get_pulumi_esc_secrets(self) -> Dict[str, any]:
        """Retrieve current secrets from Pulumi ESC"""
        try:
            env_path = f"{self.pulumi_org}/{self.environment}"
            result = subprocess.run(
                ["pulumi", "env", "get", env_path, "--show-secrets"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return json.loads(result.stdout).get("values", {})
            else:
                self.logger.error(f"Failed to get ESC environment: {result.stderr}")
                return {}

        except Exception as e:
            self.logger.error(f"Error retrieving ESC secrets: {e}")
            return {}

    def sync_github_to_esc(self, secret_mapping: Dict[str, str]) -> bool:
        """Sync specific secrets from GitHub to Pulumi ESC"""
        try:
            # Load current ESC environment
            current_esc = self.get_pulumi_esc_secrets()

            # Update with new mappings
            updated_count = 0
            for github_name, esc_key in secret_mapping.items():
                if github_name in self.get_github_secrets():
                    # Create ESC secret reference to GitHub Organization Secret
                    current_esc[esc_key] = f"fn::secret:github-org-{github_name.lower()}"
                    updated_count += 1

            # Update ESC environment
            env_path = f"{self.pulumi_org}/{self.environment}"

            # Create temporary file with updated config
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml_content = self._generate_esc_yaml(current_esc)
                f.write(yaml_content)
                temp_file = f.name

            try:
                result = subprocess.run(
                    ["pulumi", "env", "set", env_path, "--file", temp_file],
                    capture_output=True, text=True, timeout=60
                )

                if result.returncode == 0:
                    self.logger.info(f"Successfully synced {updated_count} secrets to ESC")
                    return True
                else:
                    self.logger.error(f"Failed to update ESC environment: {result.stderr}")
                    return False

            finally:
                os.unlink(temp_file)

        except Exception as e:
            self.logger.error(f"Error syncing GitHub to ESC: {e}")
            return False

    def _generate_esc_yaml(self, values: Dict[str, any]) -> str:
        """Generate ESC YAML configuration"""
        import yaml
        config = {
            "imports": [
                f"{self.pulumi_org}/consolidated"
            ],
            "values": values
        }
        return yaml.dump(config, default_flow_style=False)

    def validate_sync_status(self) -> Dict[str, str]:
        """Validate synchronization status between GitHub and ESC"""
        github_secrets = set(self.get_github_secrets().keys())
        esc_secrets = set(self.get_pulumi_esc_secrets().keys())

        return {
            "github_only": list(github_secrets - esc_secrets),
            "esc_only": list(esc_secrets - github_secrets),
            "common": list(github_secrets & esc_secrets),
            "sync_percentage": len(github_secrets & esc_secrets) / len(github_secrets) * 100 if github_secrets else 0
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync secrets between GitHub and Pulumi ESC")
    parser.add_argument("--direction", choices=["github-to-esc", "esc-to-github", "validate"],
                       default="github-to-esc", help="Sync direction")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--mapping-file", help="JSON file with secret name mappings")

    args = parser.parse_args()

    # Initialize sync manager
    sync_manager = GitHubESCSyncManager(
        org="ai-cherry",
        github_token=os.getenv("GITHUB_TOKEN"),
        pulumi_org=os.getenv("PULUMI_ORG", "scoobyjava-org"),
        environment=os.getenv("PULUMI_ENV", "sophia-ai-production")
    )

    if args.direction == "validate":
        status = sync_manager.validate_sync_status()
        print(json.dumps(status, indent=2))
    elif args.direction == "github-to-esc":
        # Load mapping file or use default
        mapping = {}
        if args.mapping_file and os.path.exists(args.mapping_file):
            with open(args.mapping_file) as f:
                mapping = json.load(f)

        if args.dry_run:
            print("Would sync the following mappings:")
            print(json.dumps(mapping, indent=2))
        else:
            success = sync_manager.sync_github_to_esc(mapping)
            exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## 🛡️ **PHASE 3: Security Hardening & Runtime Injection** (Week 2-3)

### **3.1 Enhanced Auto ESC Config**

#### Production-Ready Secret Loading
```python
# backend/core/enhanced_auto_esc_config.py
import os
import json
import subprocess
import logging
from functools import lru_cache
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import threading

class EnhancedESCConfigManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes
        self._last_refresh = None

        # Validate authentication on startup
        if not self._validate_esc_auth():
            self.logger.warning("Pulumi ESC authentication failed - falling back to environment variables")
            self.use_fallback = True
        else:
            self.use_fallback = False

    def _validate_esc_auth(self) -> bool:
        """Validate ESC authentication"""
        try:
            result = subprocess.run(["pulumi", "whoami"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    @lru_cache(maxsize=128)
    def get_config_value(self, key: str, default: Optional[str] = None, mask_logs: bool = True) -> Optional[str]:
        """
        Get configuration value with intelligent fallback strategy

        Priority:
        1. Pulumi ESC (for production/staging)
        2. Environment variables (for local dev)
        3. Default value (if provided)
        """
        # Check cache first
        cached_value = self._get_from_cache(key)
        if cached_value is not None:
            return cached_value

        value = None
        source = None

        # Try Pulumi ESC first (if authenticated)
        if not self.use_fallback:
            value = self._get_from_esc(key)
            if value is not None:
                source = "ESC"

        # Fallback to environment variables
        if value is None:
            value = os.getenv(key) or os.getenv(key.upper())
            if value is not None:
                source = "ENV"

        # Use default if provided
        if value is None and default is not None:
            value = default
            source = "DEFAULT"

        # Cache the result
        if value is not None:
            self._cache_value(key, value)

        # Log retrieval (with masking for secrets)
        log_value = "***MASKED***" if mask_logs and self._is_secret_key(key) else value
        if value is not None:
            self.logger.debug(f"Retrieved config '{key}' from {source}: {log_value}")
        else:
            self.logger.warning(f"Config '{key}' not found in any source")

        return value

    def _get_from_esc(self, key: str) -> Optional[str]:
        """Retrieve value from Pulumi ESC"""
        try:
            org = os.getenv("PULUMI_ORG", "scoobyjava-org")
            env = os.getenv("PULUMI_ENV", "sophia-ai-production")
            env_path = f"{org}/{env}"

            result = subprocess.run(
                ["pulumi", "env", "get", env_path, "--show-secrets"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                values = data.get("values", {})

                # Support nested key access
                return self._get_nested_value(values, key)
            else:
                self.logger.warning(f"ESC retrieval failed for '{key}': {result.stderr}")
                return None

        except Exception as e:
            self.logger.warning(f"Error retrieving '{key}' from ESC: {e}")
            return None

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """Get value from nested dictionary using dot notation"""
        # Try direct key first
        if key in data:
            return str(data[key]) if data[key] is not None else None

        # Try with dot notation (e.g., "sophia.ai.openai_api_key")
        keys = key.split('.')
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return str(current) if current is not None else None

    def _get_from_cache(self, key: str) -> Optional[str]:
        """Get value from cache if still valid"""
        with self._cache_lock:
            if (self._last_refresh and
                datetime.now() - self._last_refresh < self._cache_ttl and
                key in self._cache):
                return self._cache[key]
        return None

    def _cache_value(self, key: str, value: str):
        """Cache a value with timestamp"""
        with self._cache_lock:
            self._cache[key] = value
            self._last_refresh = datetime.now()

    def _is_secret_key(self, key: str) -> bool:
        """Determine if a key represents a secret value"""
        secret_indicators = [
            'password', 'secret', 'key', 'token', 'credential',
            'auth', 'api_key', 'access_token', 'private'
        ]
        key_lower = key.lower()
        return any(indicator in key_lower for indicator in secret_indicators)

    def refresh_cache(self):
        """Force refresh of the configuration cache"""
        with self._cache_lock:
            self._cache.clear()
            self._last_refresh = None
        self.logger.info("Configuration cache refreshed")

    def validate_required_secrets(self, required_keys: List[str]) -> Dict[str, bool]:
        """Validate that all required secrets are available"""
        results = {}
        missing_secrets = []

        for key in required_keys:
            value = self.get_config_value(key)
            is_valid = value is not None and value.strip() != ""
            results[key] = is_valid

            if not is_valid:
                missing_secrets.append(key)

        if missing_secrets:
            self.logger.error(f"Missing required secrets: {missing_secrets}")
        else:
            self.logger.info("All required secrets validated successfully")

        return results

    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of configuration status"""
        return {
            "esc_authenticated": not self.use_fallback,
            "cache_size": len(self._cache),
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None,
            "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60
        }

# Global instance
_config_manager = None

def get_config_manager() -> EnhancedESCConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = EnhancedESCConfigManager()
    return _config_manager

def get_config_value(key: str, default: Optional[str] = None, mask_logs: bool = True) -> Optional[str]:
    """Convenience function to get configuration value"""
    return get_config_manager().get_config_value(key, default, mask_logs)

def validate_required_secrets(required_keys: List[str]) -> Dict[str, bool]:
    """Convenience function to validate required secrets"""
    return get_config_manager().validate_required_secrets(required_keys)
```

## 🔄 **PHASE 4: CI/CD Integration & Automation** (Week 3-4)

### **4.1 GitHub Actions Workflows**

#### Secret Synchronization Workflow
```yaml
# .github/workflows/secret-sync.yml
name: Secret Synchronization

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:
    inputs:
      sync_direction:
        description: 'Sync direction'
        required: true
        default: 'github-to-esc'
        type: choice
        options:
          - github-to-esc
          - validate
      dry_run:
        description: 'Dry run mode'
        required: false
        default: false
        type: boolean

jobs:
  sync-secrets:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Pulumi CLI
        uses: pulumi/actions@v4
        with:
          pulumi-version: latest

      - name: Install dependencies
        run: |
          pip install -r infrastructure/requirements.txt

      - name: Authenticate with Pulumi
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: |
          pulumi login
          pulumi whoami

      - name: Validate authentication
        env:
          PULUMI_ORG: scoobyjava-org
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: |
          python infrastructure/esc/pulumi_auth_validator.py

      - name: Run secret synchronization
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          PULUMI_ORG: scoobyjava-org
          PULUMI_ENV: sophia-ai-production
        run: |
          python infrastructure/esc/github_sync_bidirectional.py \
            --direction ${{ github.event.inputs.sync_direction || 'github-to-esc' }} \
            ${{ github.event.inputs.dry_run == 'true' && '--dry-run' || '' }} \
            --mapping-file infrastructure/esc/secret_mappings.json

      - name: Generate sync report
        if: always()
        run: |
          python infrastructure/esc/github_sync_bidirectional.py --direction validate > sync_report.json
          cat sync_report.json

      - name: Upload sync report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: secret-sync-report
          path: sync_report.json

      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: 'Secret synchronization failed! Check workflow logs.'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🔍 **PHASE 5: Monitoring & Compliance** (Week 4-5)

### **5.1 Comprehensive Monitoring System**

#### Secret Management Monitoring
```python
# infrastructure/monitoring/secret_monitor.py
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import schedule
import time

@dataclass
class SecretHealthMetric:
    key: str
    status: str  # "healthy", "missing", "expired", "expiring"
    last_updated: Optional[datetime]
    days_until_rotation: Optional[int]
    source: str  # "esc", "env", "default"
    masked_value: str = "***MASKED***"

class SecretHealthMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []

    def check_secret_health(self) -> List[SecretHealthMetric]:
        """Comprehensive secret health check"""
        from backend.core.security_config import SecurityConfig
        from backend.core.enhanced_auto_esc_config import get_config_manager

        config_manager = get_config_manager()
        health_metrics = []

        for key, secret_config in SecurityConfig.SECRETS_REGISTRY.items():
            if isinstance(key, str):  # Skip invalid keys
                value = config_manager.get_config_value(key)

                # Determine status
                if value is None:
                    status = "missing"
                elif secret_config.rotation_enabled:
                    # Check rotation status (simplified - would need actual rotation tracking)
                    days_until = secret_config.rotation_days  # Placeholder
                    if days_until <= 7:
                        status = "expiring"
                    elif days_until <= 0:
                        status = "expired"
                    else:
                        status = "healthy"
                else:
                    status = "healthy"

                # Determine source
                source = "esc" if not config_manager.use_fallback else "env"

                metric = SecretHealthMetric(
                    key=key,
                    status=status,
                    last_updated=datetime.now(),
                    days_until_rotation=secret_config.rotation_days if secret_config.rotation_enabled else None,
                    source=source
                )

                health_metrics.append(metric)

        return health_metrics

    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        metrics = self.check_secret_health()

        # Categorize metrics
        healthy = [m for m in metrics if m.status == "healthy"]
        missing = [m for m in metrics if m.status == "missing"]
        expiring = [m for m in metrics if m.status == "expiring"]
        expired = [m for m in metrics if m.status == "expired"]

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_secrets": len(metrics),
                "healthy": len(healthy),
                "missing": len(missing),
                "expiring": len(expiring),
                "expired": len(expired),
                "health_percentage": len(healthy) / len(metrics) * 100 if metrics else 0
            },
            "details": {
                "missing_secrets": [m.key for m in missing],
                "expiring_secrets": [{"key": m.key, "days": m.days_until_rotation} for m in expiring],
                "expired_secrets": [m.key for m in expired]
            },
            "recommendations": self._generate_recommendations(missing, expiring, expired)
        }

        return report

    def _generate_recommendations(self, missing, expiring, expired) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if missing:
            recommendations.append(f"Add {len(missing)} missing secrets to GitHub Organization Secrets")

        if expired:
            recommendations.append(f"Immediately rotate {len(expired)} expired secrets")

        if expiring:
            recommendations.append(f"Schedule rotation for {len(expiring)} expiring secrets")

        return recommendations

    def send_alerts(self, report: Dict):
        """Send alerts for critical issues"""
        critical_issues = (
            report["summary"]["missing"] > 0 or
            report["summary"]["expired"] > 0 or
            report["summary"]["health_percentage"] < 90
        )

        if critical_issues:
            self.logger.error(f"CRITICAL: Secret health issues detected: {report['summary']}")
            # Here you would integrate with your alerting system (Slack, PagerDuty, etc.)

def main():
    """Main monitoring loop"""
    monitor = SecretHealthMonitor()

    # Schedule regular health checks
    schedule.every(1).hours.do(lambda: monitor.check_secret_health())
    schedule.every().day.at("09:00").do(lambda: monitor.send_alerts(monitor.generate_health_report()))

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
```

## 📋 **Implementation Checklist**

### **Phase 1: Foundation (Week 1)**
- [ ] Create `infrastructure/esc/pulumi_auth_validator.py`
- [ ] Create `infrastructure/esc/get_secret.py`
- [ ] Fix `backend/core/security_config.py` enum issues
- [ ] Test Pulumi ESC authentication end-to-end
- [ ] Validate secret retrieval from ESC

### **Phase 2: Security Configuration (Week 1-2)**
- [ ] Create `infrastructure/esc/github_sync_bidirectional.py`
- [ ] Create `backend/core/enhanced_auto_esc_config.py`
- [ ] Update all secret references to use enhanced config
- [ ] Create secret mapping configuration files
- [ ] Test bidirectional sync functionality

### **Phase 3: Runtime Security (Week 2-3)**
- [ ] Implement Docker Secrets integration for Lambda Labs
- [ ] Update application code for secure secret consumption
- [ ] Remove hardcoded fallbacks from auto_esc_config
- [ ] Test secure runtime injection
- [ ] Validate zero-secret-exposure in logs

### **Phase 4: CI/CD Automation (Week 3-4)**
- [ ] Create `.github/workflows/secret-sync.yml`
- [ ] Create automated rotation workflows
- [ ] Update deployment workflows for ESC integration
- [ ] Test complete CI/CD pipeline
- [ ] Validate automated secret deployment

### **Phase 5: Monitoring & Compliance (Week 4-5)**
- [ ] Create `infrastructure/monitoring/secret_monitor.py`
- [ ] Set up automated health reporting
- [ ] Implement alerting for critical issues
- [ ] Create compliance audit trail
- [ ] Document complete secret management process

## 🎯 **Success Criteria**

### **Technical Metrics**
- ✅ 100% of GitHub Organization Secrets synchronized to Pulumi ESC
- ✅ Zero hardcoded secrets in application code
- ✅ <30 second secret retrieval time
- ✅ 99.9% secret availability SLA
- ✅ Complete audit trail for all secret operations

### **Security Metrics**
- ✅ Zero secrets exposed in logs or environment variables
- ✅ Automated rotation for 100% of eligible secrets
- ✅ Real-time alerting for secret health issues
- ✅ Compliance with enterprise security standards
- ✅ Disaster recovery capability with <5 minute RTO

### **Operational Metrics**
- ✅ Zero manual secret management operations
- ✅ <2 hour deployment time with full secret validation
- ✅ Automated secret rotation without service disruption
- ✅ Complete observability into secret lifecycle
- ✅ Self-healing secret infrastructure

This enhanced implementation plan provides a comprehensive, enterprise-grade solution that transforms Sophia AI's secret management into a robust, automated, and secure system with complete GitHub Organization Secrets integration.
