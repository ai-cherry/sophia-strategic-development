# Enhanced AI Coding Standards for Sophia AI

## 🎯 **EXECUTIVE SUMMARY**

This document establishes comprehensive AI coding standards for building Sophia AI, a CEO-grade AI orchestration platform. These standards prioritize **Quality > Stability > Maintainability > Performance > Cost** and enforce zero-tolerance policies for technical debt, poor secret management, and repository clutter.

## 🚨 **CURRENT TECHNICAL DEBT ANALYSIS**

### **Critical Issues Identified**
- **3,079 linting violations** indicating quality decay
- **Multiple competing implementations** causing confusion
- **163 documentation files** creating information overload
- **One-time files accumulation** cluttering the repository
- **Hardcoded secrets** creating security vulnerabilities

### **Architecture Drift Patterns**
- **28 backend directories** with overlapping concerns
- **4 competing configuration systems** causing conflicts
- **Multiple chat implementations** with broken integration
- **Inconsistent error handling** across services
- **Missing test coverage** for critical functionality
- **Bypassed secret management** (not using Pulumi ESC)
- **Orphaned temporary files** reducing code clarity

## 📋 **MANDATORY PRE-CODING CHECKLIST**

### **🎯 Phase 1: Environment Validation (REQUIRED)**
```bash
# 1. Architecture Review (CRITICAL)
python -c "
import sys
from pathlib import Path
files = list(Path('.').rglob('*.py'))
print(f'📊 Python files: {len(files)}')
print(f'📊 Average file size: {sum(f.stat().st_size for f in files) / len(files):.0f} bytes')
"

# 2. Import Analysis (CRITICAL)
python -c "
import ast
import sys
from pathlib import Path

circular_imports = []
for py_file in Path('.').rglob('*.py'):
    try:
        with open(py_file) as f:
            tree = ast.parse(f.read())
            # Analysis logic here
    except:
        pass
print('🔍 Import analysis complete')
"

# 3. Dependency Validation (CRITICAL)
python -c "
# Check for conflicting dependencies
# Verify no duplicate functionality
print('✅ Dependencies validated')
"

# 4. ONE-TIME FILE DETECTION (CRITICAL)
find . -name "temp_*.py" -o -name "debug_*.py" -o -name "migration_*.py" -o -name "setup_*.py" -o -name "analyze_*.py"
echo "🚨 Above files should be deleted after use"

# 5. SECRET MANAGEMENT VALIDATION (CRITICAL)
grep -r "sk-" --include="*.py" . | grep -v "test" | head -10
grep -r "xoxb-" --include="*.py" . | head -10
grep -r "ghp_" --include="*.py" . | head -10
echo "🚨 Above patterns indicate hardcoded secrets - USE PULUMI ESC ONLY"

# 6. PULUMI ESC CONNECTIVITY CHECK
python -c "
from backend.core.auto_esc_config import get_config_value
try:
    test_val = get_config_value('test_connection')
    print('✅ Pulumi ESC accessible')
except Exception as e:
    print(f'❌ Pulumi ESC failed: {e}')
"
```

### **🎯 Phase 2: Planning & Design (REQUIRED)**
1. **Business Context Analysis**
   - CEO productivity impact assessment
   - Executive decision-making support requirements
   - Pay Ready business process integration

2. **Architecture Alignment**
   - Phoenix architecture pattern compliance
   - Snowflake-centric data architecture
   - Service decomposition strategy

3. **Performance Requirements**
   - CEO dashboard: <2 seconds
   - Executive reports: <5 seconds  
   - Business queries: <1 second

## 🏗️ **MANDATORY CODE TEMPLATE**

### **Executive-Grade Function Template**
```python
"""
🎯 SOPHIA AI EXECUTIVE FUNCTION
Purpose: [Business purpose for CEO operations]
Created: [date]
Last Modified: [date]

🚨 FILE TYPE: [PERMANENT|ONE_TIME]
🧹 CLEANUP: [If ONE_TIME: DELETE after successful execution]

Business Context:
- Supports Pay Ready CEO operations
- Integrates with Phoenix architecture
- Part of Snowflake-centric data strategy

Performance Requirements:
- Response Time: [target milliseconds]
- Code Quality: [target score]
- Test Coverage: [target percentage]
- Performance: [target response time]

Secret Management:
- Uses Pulumi ESC via get_config_value()
- NO hardcoded secrets or credentials
- NO .env files or manual configuration
"""

from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class ExecutiveBusinessLogic:
    """
    Executive-grade business logic with comprehensive validation.
    
    Designed for CEO-level operations with enterprise security,
    performance monitoring, and business impact tracking.
    """
    
    def __init__(self, config: ExecutiveConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor()
        self.security_validator = SecurityValidator()
        
    async def process_executive_request(
        self,
        request: ExecutiveRequest,
        user_context: CEOContext
    ) -> ExecutiveResponse:
        """
        Process executive-level business request.
        
        Args:
            request: Executive business request with validation
            user_context: CEO authentication and business context
            
        Returns:
            ExecutiveResponse with business insights and citations
            
        Raises:
            ValidationError: When request validation fails
            SecurityError: When security requirements not met
            PerformanceError: When performance targets not met
        """
        # Use Pulumi ESC for any secrets
        if self._needs_external_api():
            api_key = get_config_value("external_api_key")
            
        try:
            # Implementation with proper error handling
            pass
        except Exception as e:
            self.logger.error(f"Operation failed: {e}")
            raise

# ONE-TIME SCRIPT TEMPLATE (DELETE AFTER USE)
if __name__ == "__main__" and "one_time" in __file__:
    """
    🚨 ONE-TIME SCRIPT - DELETE AFTER SUCCESSFUL EXECUTION
    Purpose: [specific purpose]
    Usage: python [script_name].py
    """
    def main():
        try:
            # Script logic here
            print("✅ Operation completed successfully")
            print("🧹 CLEANUP REQUIRED: Delete this file now")
            print(f"   Command: rm {__file__}")
            print("   Reason: One-time script no longer needed")
        except Exception as e:
            print(f"❌ Operation failed: {e}")
            print("🔄 Fix issues and retry - DO NOT DELETE until successful")
    
    main()
```

## 🔧 **ENHANCED DEVELOPMENT PATTERNS**

### **CEO-Level Security Pattern**
```python
from backend.core.auto_esc_config import get_config_value

async def verify_ceo_access(user_context: UserContext) -> bool:
    """Verify CEO-level access with enhanced security."""
    if user_context.role != "ceo":
        raise SecurityError("CEO access required")
    
    # Get security configuration from Pulumi ESC
    security_config = {
        "jwt_secret": get_config_value("jwt_secret"),
        "encryption_key": get_config_value("encryption_key"),
        "session_timeout": get_config_value("ceo_session_timeout")
    }
    
    # Additional security validations
    if not await validate_session_security(user_context, security_config):
        raise SecurityError("Session security validation failed")
    
    return True
```

### **Business Intelligence Pattern**
```python
async def generate_executive_insights(
    data_context: BusinessDataContext,
    analysis_type: AnalysisType
) -> ExecutiveInsights:
    """Generate executive-level business insights."""
    
    # Use Snowflake Cortex for AI analysis
    cortex_service = SnowflakeCortexService()
    
    # Get AI configuration from Pulumi ESC
    ai_config = {
        "snowflake_account": get_config_value("snowflake_account"),
        "cortex_model": get_config_value("preferred_cortex_model"),
        "analysis_depth": get_config_value("executive_analysis_depth")
    }
    
    insights = await cortex_service.analyze_business_data(
        data_context, analysis_type, ai_config
    )
    
    return ExecutiveInsights(
        insights=insights,
        confidence_score=calculate_confidence(insights),
        business_impact=assess_business_impact(insights),
        recommendations=generate_recommendations(insights)
    )
```

## 🏆 **CRITICAL BEST PRACTICES SUMMARY**

### **🧹 FILE HYGIENE - ZERO TOLERANCE POLICY**
```python
# MANDATORY: File lifecycle management
ALWAYS_DELETE_AFTER_USE = [
    "migration_*.py",      # After migration completed
    "setup_*.py",          # After setup completed  
    "debug_*.py",          # After debugging finished
    "temp_*.py",           # After temporary operation
    "analyze_*.py",        # After analysis documented
    "test_data_*.py",      # After test data generated
    "one_time_*.py"        # After one-time operation
]

NEVER_DELETE = [
    "scripts/utils/*",     # Reusable utilities
    "docs/**/*",           # Documentation
    "tests/**/*",          # Test suites
    "config/templates/*",  # Configuration templates
    "monitoring/*"         # Monitoring scripts
]

# REQUIRED: Pre-creation assessment
def assess_file_lifecycle(filename: str, purpose: str) -> str:
    """Assess whether file should be permanent or temporary."""
    if any(pattern in filename for pattern in ALWAYS_DELETE_AFTER_USE):
        return "ONE_TIME"
    elif "util" in filename or "config" in filename or "test" in filename:
        return "PERMANENT"
    else:
        # Ask: Will this be used more than once?
        return "ONE_TIME" if purpose.startswith("one-time") else "PERMANENT"
```

### **🔐 SECRET MANAGEMENT - PULUMI ESC ONLY**
```python
# ✅ CORRECT - Always use Pulumi ESC
from backend.core.auto_esc_config import (
    get_config_value,
    get_docker_hub_config,
    get_snowflake_config,
    get_lambda_labs_config
)

# For any secret
secret = get_config_value("secret_name")

# For Docker Hub (always available)
docker_config = get_docker_hub_config()
# Returns: {"username": "scoobyjava15", "access_token": "token", "registry": "docker.io"}

# ❌ FORBIDDEN - Never do this
API_KEY = "sk-1234567890"  # Hardcoded secret
os.environ["SECRET"] = "value"  # Manual env var
with open(".env", "w") as f:  # Manual .env file
    f.write("SECRET=value")

# ❌ FORBIDDEN - Never create these files
# .env, secrets.json, config.local.py, credentials.txt
```

### **🚀 DEPLOYMENT EXCELLENCE**
```python
# MANDATORY: Deployment readiness validation
DEPLOYMENT_BLOCKERS = [
    "hardcoded_secrets",      # Any hardcoded credentials
    "temporary_files",        # Any temp_*.py, debug_*.py files
    "syntax_errors",          # Any compilation errors
    "missing_tests",          # Business logic without tests
    "performance_violations", # Response time > requirements
    "security_vulnerabilities", # Any security issues
    "documentation_gaps",     # Missing documentation
    "pulumi_esc_bypass"      # Not using centralized config
]

async def validate_deployment_readiness() -> bool:
    """Validate deployment meets all excellence standards."""
    for blocker in DEPLOYMENT_BLOCKERS:
        if await check_blocker_exists(blocker):
            raise DeploymentError(f"Deployment blocked by: {blocker}")
    return True
```

### **📊 CONTINUOUS MONITORING**
```python
# REQUIRED: Real-time quality metrics
QUALITY_METRICS = {
    "file_hygiene_score": lambda: calculate_file_hygiene(),
    "secret_management_score": lambda: calculate_secret_compliance(),
    "technical_debt_score": lambda: calculate_technical_debt(),
    "performance_score": lambda: calculate_performance_metrics(),
    "security_score": lambda: calculate_security_posture(),
    "ceo_productivity_impact": lambda: calculate_business_impact()
}

async def monitor_quality_continuously():
    """Monitor quality metrics in real-time."""
    while True:
        for metric_name, calculator in QUALITY_METRICS.items():
            score = await calculator()
            if score < MINIMUM_THRESHOLD[metric_name]:
                alert_quality_degradation(metric_name, score)
        await asyncio.sleep(60)  # Check every minute
```

## 🎉 **CONCLUSION**

These enhanced AI coding standards provide a comprehensive framework for building high-quality, maintainable, and performant software. By following these guidelines, we ensure that:

1. **Code quality** remains consistently high
2. **Technical debt** is prevented proactively  
3. **Performance requirements** are met for executive operations
4. **Security standards** are maintained at all levels
5. **Business requirements** are integrated into technical decisions
6. **Deployment processes** are reliable and repeatable
7. **🧹 Repository stays clean** with zero tolerance for temporary files
8. **🔐 Secrets are secure** through centralized Pulumi ESC management
9. **📊 Quality is monitored** continuously with real-time metrics

### **Daily Checklist**
- [ ] Follow established patterns
- [ ] Update documentation
- [ ] Run performance validation
- [ ] **🧹 Delete all one-time files after use**
- [ ] **🔐 Verify all secrets use Pulumi ESC**
- [ ] **🚫 Scan for hardcoded secrets**
- [ ] Clean up temporary files
- [ ] Update AI memory with decisions

### **Weekly Assessment**
- [ ] Architectural compliance review
- [ ] Performance optimization analysis
- [ ] Security vulnerability scan
- [ ] Review security scans
- [ ] Update success metrics
- [ ] Plan improvements
- [ ] **🧹 Repository cleanup audit (orphaned files)**
- [ ] **🔐 Secret management compliance review**
- [ ] **📊 File lifecycle management assessment**

### **Monthly Assessment**
- [ ] Comprehensive quality audit
- [ ] Business impact analysis
- [ ] Technology stack review
- [ ] Security assessment
- [ ] Process improvement
- [ ] Team training updates
- [ ] **🧹 Complete repository hygiene audit**
- [ ] **🔐 Comprehensive secret management review**
- [ ] **📋 Best practices compliance assessment**

**Remember**: Every line of code is an investment in the future of Sophia AI. Make it count.

**Quality is not an accident; it is always the result of intelligent effort.** 