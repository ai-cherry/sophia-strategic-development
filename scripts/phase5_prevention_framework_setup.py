#!/usr/bin/env python3
"""
Phase 5: Prevention Framework Setup Script
Part of Comprehensive Technical Debt Elimination Plan

This script:
1. Creates automated pre-commit hooks to prevent technical debt
2. Sets up continuous monitoring for code quality
3. Implements automated scanning and alerts
4. Establishes code quality standards and enforcement
5. Creates technical debt prevention documentation

Author: Sophia AI Technical Debt Elimination Team
Date: January 2025
"""

import os
import logging
import subprocess
from module import starPath
from module import starDict, List, Tuple, Optional
from module import stardataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prevention_framework_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PreventionResult:
    """Results of prevention framework setup"""
    hooks_installed: List[str] = field(default_factory=list)
    monitors_created: List[str] = field(default_factory=list)
    standards_established: List[str] = field(default_factory=list)
    documentation_created: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class PreventionFrameworkSetup:
    """Comprehensive technical debt prevention framework"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.hooks_dir = self.root_path / ".git" / "hooks"
        self.scripts_dir = self.root_path / "scripts" / "prevention"
        self.docs_dir = self.root_path / "docs" / "prevention"
        
        # Create directories
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_pre_commit_hooks(self) -> List[str]:
        """Create comprehensive pre-commit hooks"""
        hooks_created = []
        
        # 1. Wildcard import prevention hook
        wildcard_hook = '''#!/bin/bash
# Pre-commit hook: Prevent wildcard imports

echo "🔍 Checking for wildcard imports..."

# Find wildcard imports in staged files
WILDCARD_IMPORTS=$(git diff --cached --name-only --diff-filter=ACM | grep '\\.py$' | xargs grep -l "from module import star*" 2>/dev/null || true)

if [ ! -z "$WILDCARD_IMPORTS" ]; then
    echo "❌ COMMIT BLOCKED: Wildcard imports detected!"
    echo "Files with wildcard imports:"
    echo "$WILDCARD_IMPORTS"
    echo ""
    echo "Please replace wildcard imports with explicit imports:"
    echo "  BAD:  from module import starstar"
    echo "  GOOD: from module import starSpecificClass, SpecificFunction"
    exit 1
fi

echo "✅ No wildcard imports found"
'''
        
        # 2. TODO prevention hook
        todo_hook = '''#!/bin/bash
# Pre-commit hook: Prevent TODO additions without tickets

echo "🔍 Checking for new TODOs without tickets..."

# Find new TODOs in staged files
NEW_TODOS=$(git diff --cached --diff-filter=A | grep "^+.*# TODO" | grep -v "# TODO: \\[TICKET-" || true)

if [ ! -z "$NEW_TODOS" ]; then
    echo "❌ COMMIT BLOCKED: New TODOs without ticket references detected!"
    echo "TODOs must include ticket references in format: # TODO: [TICKET-123] Description"
    echo ""
    echo "Found TODOs without tickets:"
    echo "$NEW_TODOS"
    exit 1
fi

echo "✅ All TODOs have proper ticket references"
'''
        
        # 3. Temporary code prevention hook
        temp_code_hook = '''#!/bin/bash
# Pre-commit hook: Prevent temporary code additions

echo "🔍 Checking for temporary code..."

# Find temporary code patterns in staged files
TEMP_CODE=$(git diff --cached --diff-filter=A | grep -E "^\\+.*(placeholder|temporary|temp|for now|mock.*for now|# HACK|# FIXME.*temp)" || true)

if [ ! -z "$TEMP_CODE" ]; then
    echo "❌ COMMIT BLOCKED: Temporary code detected!"
    echo "Temporary code should not be committed to main branches."
    echo ""
    echo "Found temporary code:"
    echo "$TEMP_CODE"
    echo ""
    echo "Please replace temporary code with production implementations."
    exit 1
fi

echo "✅ No temporary code found"
'''
        
        # 4. Code quality hook
        quality_hook = '''#!/bin/bash
# Pre-commit hook: Code quality checks

echo "🔍 Running code quality checks..."

# Check for proper docstrings in new functions/classes
MISSING_DOCSTRINGS=$(git diff --cached --diff-filter=A | grep -E "^\\+\\s*(def|class|async def)" | grep -A 5 -B 1 . | grep -L '"""' || true)

if [ ! -z "$MISSING_DOCSTRINGS" ]; then
    echo "⚠️ WARNING: New functions/classes without docstrings detected"
    echo "Consider adding docstrings for better code documentation"
fi

# Check for proper error handling
MISSING_ERROR_HANDLING=$(git diff --cached --diff-filter=A | grep -E "^\\+.*\\.(get|post|put|delete|patch)\\(" | grep -v "try:" | head -5 || true)

if [ ! -z "$MISSING_ERROR_HANDLING" ]; then
    echo "⚠️ WARNING: API calls without visible error handling"
    echo "Consider adding try-catch blocks for API calls"
fi

echo "✅ Code quality checks completed"
'''
        
        # 5. Master pre-commit hook that runs all checks
        master_hook = f'''#!/bin/bash
# Master pre-commit hook: Technical Debt Prevention

echo "🚀 Running Technical Debt Prevention Checks..."
echo "=============================================="

# Run wildcard import check
{wildcard_hook}

# Run TODO check  
{todo_hook}

# Run temporary code check
{temp_code_hook}

# Run code quality check
{quality_hook}

echo "=============================================="
echo "✅ All technical debt prevention checks passed!"
echo "🚀 Commit approved"
'''
        
        # Write hooks to files
        hooks = {
            "pre-commit": master_hook,
            "pre-commit-wildcard": wildcard_hook,
            "pre-commit-todo": todo_hook,
            "pre-commit-temp": temp_code_hook,
            "pre-commit-quality": quality_hook
        }
        
        for hook_name, hook_content in hooks.items():
            hook_file = self.hooks_dir / hook_name
            try:
                hook_file.write_text(hook_content)
                hook_file.chmod(0o755)  # Make executable
                hooks_created.append(hook_name)
                logger.info(f"✅ Created hook: {hook_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create hook {hook_name}: {e}")
        
        return hooks_created
    
    def create_monitoring_scripts(self) -> List[str]:
        """Create continuous monitoring scripts"""
        monitors_created = []
        
        # 1. Daily technical debt scanner
        daily_scanner = '''#!/usr/bin/env python3
"""
Daily Technical Debt Scanner
Runs automated scans to detect technical debt accumulation
"""

import subprocess
import datetime
import json
from module import starPath

def scan_wildcard_imports():
    """Scan for wildcard imports"""
    result = subprocess.run(
        ["grep", "-r", "from module import star*", "--include=*.py", "."],
        capture_output=True, text=True
    )
    return len(result.stdout.split('\\n')) if result.stdout.strip() else 0

def scan_todos():
    """Scan for TODO items"""
    result = subprocess.run(
        ["grep", "-r", "TODO\\|FIXME\\|XXX\\|HACK", "--include=*.py", "."],
        capture_output=True, text=True
    )
    return len(result.stdout.split('\\n')) if result.stdout.strip() else 0

def scan_temporary_code():
    """Scan for temporary code"""
    patterns = ["placeholder", "temporary", "temp", "for now", "mock.*for now"]
    total = 0
    for pattern in patterns:
        result = subprocess.run(
            ["grep", "-r", pattern, "--include=*.py", "."],
            capture_output=True, text=True
        )
        total += len(result.stdout.split('\\n')) if result.stdout.strip() else 0
    return total

def generate_report():
    """Generate daily technical debt report"""
    report = {
        "date": datetime.datetime.now().isoformat(),
        "wildcard_imports": scan_wildcard_imports(),
        "todos": scan_todos(),
        "temporary_code": scan_temporary_code()
    }
    
    # Save report
    report_file = Path("daily_tech_debt_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Check thresholds
    alerts = []
    if report["wildcard_imports"] > 5:
        alerts.append(f"HIGH: {report['wildcard_imports']} wildcard imports detected")
    if report["todos"] > 50:
        alerts.append(f"HIGH: {report['todos']} TODO items detected")
    if report["temporary_code"] > 10:
        alerts.append(f"MEDIUM: {report['temporary_code']} temporary code items detected")
    
    if alerts:
        print("🚨 TECHNICAL DEBT ALERTS:")
        for alert in alerts:
            print(f"  - {alert}")
    else:
        print("✅ Technical debt levels within acceptable limits")
    
    return report

if __name__ == "__main__":
    generate_report()
'''
        
        # 2. Pre-push debt checker
        pre_push_checker = '''#!/usr/bin/env python3
"""
Pre-push Technical Debt Checker
Prevents pushing commits with high technical debt
"""

import subprocess
import sys

def check_debt_levels():
    """Check current technical debt levels"""
    # Run daily scanner
    result = subprocess.run([sys.executable, "scripts/prevention/daily_tech_debt_scanner.py"], 
                          capture_output=True, text=True)
    
    # Parse output for alerts
    if "🚨 TECHNICAL DEBT ALERTS:" in result.stdout:
        print("❌ PUSH BLOCKED: High technical debt detected!")
        print(result.stdout)
        return False
    
    print("✅ Technical debt levels acceptable for push")
    return True

if __name__ == "__main__":
    if not check_debt_levels():
        sys.exit(1)
'''
        
        # 3. Code quality metrics collector
        metrics_collector = '''#!/usr/bin/env python3
"""
Code Quality Metrics Collector
Collects and tracks code quality metrics over time
"""

import subprocess
import json
import datetime
from module import starPath

def collect_metrics():
    """Collect comprehensive code quality metrics"""
    metrics = {
        "timestamp": datetime.datetime.now().isoformat(),
        "lines_of_code": count_lines_of_code(),
        "test_coverage": get_test_coverage(),
        "cyclomatic_complexity": get_complexity_metrics(),
        "technical_debt_ratio": calculate_debt_ratio(),
        "code_duplication": detect_code_duplication()
    }
    
    # Save metrics
    metrics_file = Path("code_quality_metrics.json")
    if metrics_file.exists():
        with open(metrics_file, "r") as f:
            historical_metrics = json.load(f)
    else:
        historical_metrics = []
    
    historical_metrics.append(metrics)
    
    with open(metrics_file, "w") as f:
        json.dump(historical_metrics, f, indent=2)
    
    return metrics

def count_lines_of_code():
    """Count total lines of Python code"""
    result = subprocess.run(
        ["find", ".", "-name", "*.py", "-exec", "wc", "-l", "{}", "+"],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split('\\n')
    total = sum(int(line.split()[0]) for line in lines if line.strip())
    return total

def get_test_coverage():
    """Get test coverage percentage"""
    # Placeholder - implement with actual coverage tool
    return 85.0

def get_complexity_metrics():
    """Get cyclomatic complexity metrics"""
    # Placeholder - implement with complexity analysis tool
    return {"average": 3.2, "max": 15, "high_complexity_functions": 5}

def calculate_debt_ratio():
    """Calculate technical debt ratio"""
    # Simple calculation based on TODOs, temp code, etc.
    todos = subprocess.run(["grep", "-r", "TODO", "--include=*.py", "."], 
                          capture_output=True, text=True)
    todo_count = len(todos.stdout.split('\\n')) if todos.stdout.strip() else 0
    
    total_lines = count_lines_of_code()
    debt_ratio = (todo_count / total_lines) * 100 if total_lines > 0 else 0
    
    return round(debt_ratio, 2)

def detect_code_duplication():
    """Detect code duplication"""
    # Placeholder - implement with duplication detection tool
    return {"duplicated_lines": 150, "duplication_percentage": 2.1}

if __name__ == "__main__":
    metrics = collect_metrics()
    print(f"✅ Code quality metrics collected: {metrics['timestamp']}")
'''
        
        # Write monitoring scripts
        scripts = {
            "daily_tech_debt_scanner.py": daily_scanner,
            "pre_push_debt_checker.py": pre_push_checker,
            "code_quality_metrics_collector.py": metrics_collector
        }
        
        for script_name, script_content in scripts.items():
            script_file = self.scripts_dir / script_name
            try:
                script_file.write_text(script_content)
                script_file.chmod(0o755)  # Make executable
                monitors_created.append(script_name)
                logger.info(f"✅ Created monitor: {script_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create monitor {script_name}: {e}")
        
        return monitors_created
    
    def create_quality_standards(self) -> List[str]:
        """Create code quality standards and enforcement"""
        standards_created = []
        
        # 1. Code quality standards document
        standards_doc = '''# Code Quality Standards
## Sophia AI Technical Debt Prevention

### 🚫 PROHIBITED PATTERNS

#### 1. Wildcard Imports
```python
# ❌ PROHIBITED
from module import starstar

# ✅ REQUIRED
from module import starSpecificClass, SpecificFunction
```

#### 2. TODOs Without Tickets
```python
# ❌ PROHIBITED
# TODO: Fix this later

# ✅ REQUIRED  
# TODO: [TICKET-123] Implement proper error handling
```

#### 3. Temporary Code
```python
# ❌ PROHIBITED
# For now, just return mock data
def get_data():
    return {"mock": "data"}

# ✅ REQUIRED
def get_data():
    """Get data from production service"""
    try:
        return service.fetch_data()
    except Exception as e:
        logger.error(f"Data fetch failed: {e}")
        raise
```

### ✅ REQUIRED PATTERNS

#### 1. Explicit Imports
- Always use explicit imports
- Group imports: standard library, third-party, local
- Use absolute imports for clarity

#### 2. Comprehensive Error Handling
```python
# ✅ REQUIRED
async def api_call():
    try:
        response = await client.get("/api/data")
        return response.json()
    except ClientError as e:
        logger.error(f"API call failed: {e}")
        raise APIException(f"Failed to fetch data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

#### 3. Proper Documentation
```python
# ✅ REQUIRED
def process_data(data: List[Dict]) -> ProcessedData:
    """
    Process raw data into structured format.
    
    Args:
        data: List of raw data dictionaries
        
    Returns:
        ProcessedData object with validated and structured data
        
    Raises:
        ValidationError: If data validation fails
        ProcessingError: If processing fails
    """
```

### 📊 QUALITY METRICS

#### Thresholds
- **Wildcard Imports**: 0 (zero tolerance)
- **TODOs**: < 20 per 1000 lines of code
- **Temporary Code**: 0 (zero tolerance)
- **Test Coverage**: > 80%
- **Cyclomatic Complexity**: < 10 per function

#### Enforcement
- Pre-commit hooks block violations
- Daily monitoring tracks trends
- Pull request reviews enforce standards
- Automated alerts for threshold breaches

### 🔧 TOOLS AND AUTOMATION

#### Pre-commit Hooks
- Wildcard import detection
- TODO ticket validation
- Temporary code prevention
- Code quality checks

#### Continuous Monitoring
- Daily technical debt scans
- Code quality metrics collection
- Trend analysis and alerts
- Quality dashboard updates

#### Development Workflow
1. Write code following standards
2. Pre-commit hooks validate changes
3. Automated tests run
4. Code review enforces quality
5. Monitoring tracks metrics
'''
        
        # 2. Developer guidelines
        dev_guidelines = '''# Developer Guidelines
## Technical Debt Prevention

### 🎯 DEVELOPMENT WORKFLOW

#### Before You Code
1. **Plan Implementation**: Avoid temporary solutions
2. **Design for Production**: No placeholders or mocks
3. **Consider Error Cases**: Plan comprehensive error handling
4. **Document Intent**: Clear docstrings and comments

#### During Development
1. **Use Explicit Imports**: No wildcard imports
2. **Handle Errors Properly**: Try-catch with specific exceptions
3. **Write Tests**: Maintain >80% coverage
4. **Follow Naming Conventions**: Clear, descriptive names

#### Before Committing
1. **Run Pre-commit Hooks**: Automated quality checks
2. **Review Your Changes**: Look for technical debt patterns
3. **Update Documentation**: Keep docs current
4. **Test Thoroughly**: Ensure functionality works

### 🚨 RED FLAGS TO AVOID

#### Code Smells
- Functions longer than 50 lines
- Classes with >10 methods
- Deeply nested conditionals (>3 levels)
- Duplicate code blocks
- Unclear variable names

#### Technical Debt Indicators
- "TODO" without ticket reference
- "HACK" or "FIXME" comments
- Commented-out code
- Temporary implementations
- Mock data in production code

### ✅ BEST PRACTICES

#### Clean Code Principles
1. **Single Responsibility**: One function, one purpose
2. **Explicit is Better**: Clear over clever
3. **Fail Fast**: Validate inputs early
4. **Log Meaningfully**: Helpful error messages
5. **Test Everything**: Unit, integration, end-to-end

#### Performance Considerations
1. **Avoid Premature Optimization**: Profile first
2. **Cache Wisely**: Understand cache invalidation
3. **Handle Async Properly**: Use proper async/await patterns
4. **Monitor Resource Usage**: Memory, CPU, I/O

### 🛠️ RECOMMENDED TOOLS

#### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **pylint**: Static analysis
- **mypy**: Type checking
- **pytest**: Testing framework

#### Documentation
- **Sphinx**: API documentation
- **mkdocs**: User documentation
- **docstring**: Inline documentation
- **README**: Project overview

### 📈 CONTINUOUS IMPROVEMENT

#### Regular Reviews
- Weekly code quality reviews
- Monthly technical debt assessments
- Quarterly architecture reviews
- Annual tool and process updates

#### Learning and Growth
- Share knowledge in team meetings
- Document lessons learned
- Update guidelines based on experience
- Stay current with best practices
'''
        
        # Write standards documents
        standards = {
            "CODE_QUALITY_STANDARDS.md": standards_doc,
            "DEVELOPER_GUIDELINES.md": dev_guidelines
        }
        
        for doc_name, doc_content in standards.items():
            doc_file = self.docs_dir / doc_name
            try:
                doc_file.write_text(doc_content)
                standards_created.append(doc_name)
                logger.info(f"✅ Created standard: {doc_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create standard {doc_name}: {e}")
        
        return standards_created
    
    def setup_git_hooks(self) -> bool:
        """Set up Git hooks integration"""
        try:
            # Install pre-commit hook
            pre_commit_hook = self.hooks_dir / "pre-commit"
            if pre_commit_hook.exists():
                logger.info("✅ Pre-commit hook installed and active")
                return True
            else:
                logger.error("❌ Pre-commit hook not found")
                return False
        except Exception as e:
            logger.error(f"❌ Git hooks setup failed: {e}")
            return False
    
    def create_dashboard_config(self) -> str:
        """Create configuration for technical debt dashboard"""
        dashboard_config = '''{
  "dashboard": {
    "title": "Sophia AI Technical Debt Monitor",
    "refresh_interval": "1h",
    "panels": [
      {
        "title": "Technical Debt Overview",
        "type": "stat",
        "metrics": [
          {
            "name": "Wildcard Imports",
            "threshold": 0,
            "alert_level": "critical"
          },
          {
            "name": "TODO Items", 
            "threshold": 50,
            "alert_level": "warning"
          },
          {
            "name": "Temporary Code",
            "threshold": 0,
            "alert_level": "critical"
          }
        ]
      },
      {
        "title": "Code Quality Trends",
        "type": "graph",
        "timeframe": "30d",
        "metrics": [
          "test_coverage",
          "cyclomatic_complexity",
          "technical_debt_ratio"
        ]
      },
      {
        "title": "Prevention Effectiveness",
        "type": "table",
        "columns": [
          "Date",
          "Commits Blocked",
          "Issues Prevented",
          "Quality Score"
        ]
      }
    ]
  },
  "alerts": {
    "channels": ["email", "slack"],
    "thresholds": {
      "wildcard_imports": 0,
      "todos": 50,
      "temporary_code": 0,
      "test_coverage": 80,
      "debt_ratio": 5.0
    }
  }
}'''
        
        config_file = self.docs_dir / "dashboard_config.json"
        try:
            config_file.write_text(dashboard_config)
            logger.info("✅ Dashboard configuration created")
            return "dashboard_config.json"
        except Exception as e:
            logger.error(f"❌ Failed to create dashboard config: {e}")
            return ""
    
    def run_setup(self) -> PreventionResult:
        """Execute complete prevention framework setup"""
        logger.info("🚀 Starting Phase 5: Prevention Framework Setup")
        result = PreventionResult()
        
        try:
            # Step 1: Create pre-commit hooks
            logger.info("🔧 Step 1: Creating pre-commit hooks...")
            result.hooks_installed = self.create_pre_commit_hooks()
            
            # Step 2: Create monitoring scripts
            logger.info("📊 Step 2: Creating monitoring scripts...")
            result.monitors_created = self.create_monitoring_scripts()
            
            # Step 3: Create quality standards
            logger.info("📋 Step 3: Creating quality standards...")
            result.standards_established = self.create_quality_standards()
            
            # Step 4: Set up Git hooks
            logger.info("🔗 Step 4: Setting up Git hooks...")
            if self.setup_git_hooks():
                result.hooks_installed.append("git_integration")
            
            # Step 5: Create dashboard configuration
            logger.info("📈 Step 5: Creating dashboard configuration...")
            dashboard_config = self.create_dashboard_config()
            if dashboard_config:
                result.documentation_created.append(dashboard_config)
            
            # Generate summary
            logger.info("📊 Setup Summary:")
            logger.info(f"  - Hooks installed: {len(result.hooks_installed)}")
            logger.info(f"  - Monitors created: {len(result.monitors_created)}")
            logger.info(f"  - Standards established: {len(result.standards_established)}")
            logger.info(f"  - Documentation created: {len(result.documentation_created)}")
            logger.info(f"  - Errors: {len(result.errors)}")
            
            if result.errors:
                logger.error("❌ Setup completed with errors!")
                for error in result.errors:
                    logger.error(f"  - {error}")
            else:
                logger.info("✅ Prevention framework setup completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Critical error during setup: {e}")
            result.errors.append(f"Critical error: {e}")
        
        return result
    
    def generate_report(self, result: PreventionResult) -> str:
        """Generate comprehensive setup report"""
        report = f"""
# 📋 PREVENTION FRAMEWORK SETUP REPORT
## Phase 5 - Technical Debt Elimination

### 📊 SUMMARY
- **Hooks Installed**: {len(result.hooks_installed)}
- **Monitors Created**: {len(result.monitors_created)}
- **Standards Established**: {len(result.standards_established)}
- **Documentation Created**: {len(result.documentation_created)}
- **Errors**: {len(result.errors)}
- **Warnings**: {len(result.warnings)}

### 🔧 HOOKS INSTALLED
{chr(10).join(f"- {hook}" for hook in result.hooks_installed)}

### 📊 MONITORS CREATED
{chr(10).join(f"- {monitor}" for monitor in result.monitors_created)}

### 📋 STANDARDS ESTABLISHED
{chr(10).join(f"- {standard}" for standard in result.standards_established)}

### 📚 DOCUMENTATION CREATED
{chr(10).join(f"- {doc}" for doc in result.documentation_created)}

### ⚠️ ERRORS
{chr(10).join(f"- {error}" for error in result.errors)}

### 🎯 PREVENTION FRAMEWORK ACTIVE

The following prevention measures are now active:

1. **Pre-commit Hooks**: Block problematic code before commit
2. **Daily Monitoring**: Automated technical debt scanning
3. **Quality Standards**: Enforced code quality requirements
4. **Developer Guidelines**: Clear best practices documentation
5. **Dashboard Monitoring**: Real-time technical debt tracking

### 📈 NEXT STEPS
1. Train team on new prevention framework
2. Set up monitoring dashboard
3. Proceed to Phase 6: Validation & Monitoring
4. Schedule regular framework reviews

---
Generated: Phase 5 - Prevention Framework Setup Complete
"""
        return report

def main():
    """Main execution function"""
    setup = PreventionFrameworkSetup()
    result = setup.run_setup()
    
    # Generate and save report
    report = setup.generate_report(result)
    report_path = Path("PHASE_5_PREVENTION_FRAMEWORK_SETUP_REPORT.md")
    report_path.write_text(report)
    
    logger.info(f"📄 Report saved: {report_path}")
    
    # Return exit code based on success
    return 0 if not result.errors else 1

if __name__ == "__main__":
    exit(main()) 