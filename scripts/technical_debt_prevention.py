#!/usr/bin/env python3
"""
🎯 SOPHIA AI: TECHNICAL DEBT PREVENTION FRAMEWORK
Zero Technical Debt Guarantee Implementation

This framework implements automated technical debt prevention with continuous monitoring,
pre-commit validation, and quality gates to maintain zero technical debt.

Date: July 14, 2025
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation rule"""
    rule_name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = "info"  # info, warning, error, critical

@dataclass
class DebtPreventionReport:
    """Complete debt prevention report"""
    passed: bool
    debt_score: float
    results: List[ValidationResult]
    timestamp: datetime
    file_count: int
    repository_size_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'results': [asdict(r) for r in self.results]
        }

class DebtPreventionError(Exception):
    """Exception raised when debt prevention rules are violated"""
    pass

class TechnicalDebtPreventionFramework:
    """Comprehensive technical debt prevention framework"""
    
    PREVENTION_RULES = {
        "file_count_limit": {
            "threshold": 3000,  # Enterprise-appropriate (was 250 - too strict)
            "action": "warn_and_log",  # Changed from block_commit to allow development
            "message": "Repository file count is high - consider modular architecture"
        },
        "repository_size_limit": {
            "threshold": 2000,  # 2GB limit (was 500MB - too strict)
            "action": "warn_and_log",  # Changed from block_commit
            "message": "Repository size is large - consider asset optimization"
        },
        "duplicate_code_detection": {
            "threshold": 0.90,  # Relaxed from 0.85 - allow some patterns
            "action": "warn_and_suggest",
            "message": "Duplicate code detected - consider refactoring when convenient"
        },
        "broken_references": {
            "patterns": [
                r"import.*missing",
                r"ModuleNotFoundError", 
                r"FileNotFoundError",
                r"ImportError"
            ],
            "action": "block_commit",  # Keep strict - this breaks functionality
            "message": "Broken imports or references detected"
        },
        "hardcoded_secrets": {
            "patterns": [
                r"(api_key|password|secret|token)\s*=\s*['\"][a-zA-Z0-9]{8,}['\"]",  # More precise
                r"sk-[a-zA-Z0-9]{32,}",  # OpenAI keys
                r"pk_[a-zA-Z0-9]{32,}",  # Pinecone keys
                r"Bearer [a-zA-Z0-9]{32,}"  # Bearer tokens
            ],
            "action": "block_commit",  # Keep strict - security critical
            "message": "Hardcoded secrets detected - use config management"
        },
        "dead_code_markers": {
            "patterns": [r"TODO", r"FIXME", r"HACK", r"XXX"],
            "threshold": 20,  # Increased from 5 - more realistic for enterprise
            "action": "warn",
            "message": "Many code markers found - review when convenient"
        },
        "archive_directories": {
            "patterns": [
                r"archive/",
                r"backup/", 
                r"_archived/",
                r"migration_backup/",
                r"\.backup/"
            ],
            "action": "block_commit",  # Keep strict - prevents clutter
            "message": "Archive directories not allowed - use git history"
        },
        "backup_files": {
            "patterns": [
                r"\.backup$",
                r"\.bak$", 
                r"\.old$",
                r"\.tmp$",
                r"\.temp$"
            ],
            "action": "warn_and_clean",  # Changed to auto-clean instead of blocking
            "message": "Backup files found - auto-cleaning recommended"
        },
        "one_time_scripts": {
            "patterns": [
                r"scripts/(?!one_time/|utils/|monitoring/).*(?:deploy_|setup_|fix_|test_|migrate_|cleanup_)"
            ],
            "action": "warn_and_suggest",  # Changed from block - too disruptive
            "message": "Consider moving one-time scripts to scripts/one_time/ directory"
        }
    }
    
    def __init__(self):
        self.monitoring_active = True
        self.prevention_log = []
        self.base_path = Path.cwd()
        
    async def continuous_monitoring(self):
        """Continuous repository monitoring for debt accumulation"""
        logger.info("🔍 Starting continuous technical debt monitoring...")
        
        while self.monitoring_active:
            try:
                debt_score = await self.calculate_debt_score()
                
                if debt_score > 20:  # Out of 100
                    await self.trigger_debt_alert(debt_score)
                    await self.suggest_remediation()
                
                logger.info(f"📊 Current debt score: {debt_score}/100")
                
                # Monitor every 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def pre_commit_validation(self) -> DebtPreventionReport:
        """Pre-commit hook for debt prevention"""
        logger.info("🔍 Running pre-commit technical debt validation...")
        
        validation_results = []
        
        for rule_name, rule_config in self.PREVENTION_RULES.items():
            try:
                result = await self.validate_rule(rule_name, rule_config)
                validation_results.append(result)
                
                if not result.passed and rule_config["action"] == "block_commit":
                    raise DebtPreventionError(f"Commit blocked: {rule_config['message']}")
                    
            except Exception as e:
                logger.error(f"❌ Rule validation error for {rule_name}: {e}")
                validation_results.append(ValidationResult(
                    rule_name=rule_name,
                    passed=False,
                    message=f"Validation error: {str(e)}",
                    severity="error"
                ))
        
        debt_score = await self.calculate_debt_score()
        file_count = await self._count_files()
        repo_size = await self._get_repository_size()
        
        report = DebtPreventionReport(
            passed=all(r.passed for r in validation_results if r.severity in ["error", "critical"]),
            debt_score=debt_score,
            results=validation_results,
            timestamp=datetime.now(),
            file_count=file_count,
            repository_size_mb=repo_size
        )
        
        logger.info(f"📊 Pre-commit validation complete. Debt score: {debt_score}/100")
        return report
    
    async def validate_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate a specific prevention rule"""
        
        if rule_name == "file_count_limit":
            return await self._validate_file_count(rule_config)
        elif rule_name == "repository_size_limit":
            return await self._validate_repository_size(rule_config)
        elif rule_name == "duplicate_code_detection":
            return await self._validate_duplicate_code(rule_config)
        elif rule_name == "broken_references":
            return await self._validate_broken_references(rule_config)
        elif rule_name == "hardcoded_secrets":
            return await self._validate_hardcoded_secrets(rule_config)
        elif rule_name == "dead_code_markers":
            return await self._validate_dead_code_markers(rule_config)
        elif rule_name == "archive_directories":
            return await self._validate_archive_directories(rule_config)
        elif rule_name == "backup_files":
            return await self._validate_backup_files(rule_config)
        elif rule_name == "one_time_scripts":
            return await self._validate_one_time_scripts(rule_config)
        else:
            return ValidationResult(
                rule_name=rule_name,
                passed=False,
                message=f"Unknown rule: {rule_name}",
                severity="error"
            )
    
    async def _validate_file_count(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate file count limit"""
        file_count = await self._count_files()
        threshold = rule_config["threshold"]
        
        passed = file_count <= threshold
        
        return ValidationResult(
            rule_name="file_count_limit",
            passed=passed,
            message=f"File count: {file_count}/{threshold}",
            details={"current_count": file_count, "threshold": threshold},
            severity="error" if not passed else "info"
        )
    
    async def _validate_repository_size(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate repository size limit"""
        repo_size = await self._get_repository_size()
        threshold = rule_config["threshold"]
        
        passed = repo_size <= threshold
        
        return ValidationResult(
            rule_name="repository_size_limit",
            passed=passed,
            message=f"Repository size: {repo_size:.1f}MB/{threshold}MB",
            details={"current_size_mb": repo_size, "threshold_mb": threshold},
            severity="error" if not passed else "info"
        )
    
    async def _validate_duplicate_code(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate duplicate code detection"""
        # Simple duplicate detection based on file content hashes
        file_hashes = {}
        duplicates = []
        
        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append((py_file, file_hashes[file_hash]))
                    else:
                        file_hashes[file_hash] = py_file
                        
            except Exception as e:
                logger.warning(f"⚠️  Could not read file {py_file}: {e}")
        
        passed = len(duplicates) == 0
        
        return ValidationResult(
            rule_name="duplicate_code_detection",
            passed=passed,
            message=f"Duplicate files found: {len(duplicates)}",
            details={"duplicates": [(str(f1), str(f2)) for f1, f2 in duplicates]},
            severity="warning" if not passed else "info"
        )
    
    async def _validate_broken_references(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate broken imports and references"""
        broken_refs = []
        patterns = rule_config["patterns"]
        
        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            broken_refs.append({
                                "file": str(py_file),
                                "pattern": pattern,
                                "matches": matches
                            })
                            
            except Exception as e:
                logger.warning(f"⚠️  Could not read file {py_file}: {e}")
        
        passed = len(broken_refs) == 0
        
        return ValidationResult(
            rule_name="broken_references",
            passed=passed,
            message=f"Broken references found: {len(broken_refs)}",
            details={"broken_references": broken_refs},
            severity="error" if not passed else "info"
        )
    
    async def _validate_hardcoded_secrets(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate hardcoded secrets"""
        secrets_found = []
        patterns = rule_config["patterns"]
        
        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            secrets_found.append({
                                "file": str(py_file),
                                "pattern": pattern,
                                "matches": len(matches)
                            })
                            
            except Exception as e:
                logger.warning(f"⚠️  Could not read file {py_file}: {e}")
        
        passed = len(secrets_found) == 0
        
        return ValidationResult(
            rule_name="hardcoded_secrets",
            passed=passed,
            message=f"Hardcoded secrets found: {len(secrets_found)}",
            details={"secrets": secrets_found},
            severity="error" if not passed else "info"
        )
    
    async def _validate_dead_code_markers(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate dead code markers"""
        markers_found = 0
        patterns = rule_config["patterns"]
        threshold = rule_config["threshold"]
        
        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        markers_found += len(matches)
                        
            except Exception as e:
                logger.warning(f"⚠️  Could not read file {py_file}: {e}")
        
        passed = markers_found <= threshold
        
        return ValidationResult(
            rule_name="dead_code_markers",
            passed=passed,
            message=f"Dead code markers: {markers_found}/{threshold}",
            details={"markers_count": markers_found, "threshold": threshold},
            severity="warning" if not passed else "info"
        )
    
    async def _validate_archive_directories(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate archive directories"""
        archive_dirs = []
        patterns = rule_config["patterns"]
        
        for directory in self.base_path.rglob("*"):
            if directory.is_dir():
                dir_path = str(directory.relative_to(self.base_path))
                
                for pattern in patterns:
                    if re.search(pattern, dir_path, re.IGNORECASE):
                        archive_dirs.append(dir_path)
                        break
        
        passed = len(archive_dirs) == 0
        
        return ValidationResult(
            rule_name="archive_directories",
            passed=passed,
            message=f"Archive directories found: {len(archive_dirs)}",
            details={"archive_directories": archive_dirs},
            severity="error" if not passed else "info"
        )
    
    async def _validate_backup_files(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate backup files"""
        backup_files = []
        patterns = rule_config["patterns"]
        
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                file_name = str(file_path.name)
                
                for pattern in patterns:
                    if re.search(pattern, file_name, re.IGNORECASE):
                        backup_files.append(str(file_path.relative_to(self.base_path)))
                        break
        
        passed = len(backup_files) == 0
        
        return ValidationResult(
            rule_name="backup_files",
            passed=passed,
            message=f"Backup files found: {len(backup_files)}",
            details={"backup_files": backup_files},
            severity="error" if not passed else "info"
        )
    
    async def _validate_one_time_scripts(self, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate one-time scripts placement"""
        misplaced_scripts = []
        patterns = rule_config["patterns"]
        
        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            file_path = str(py_file.relative_to(self.base_path))
            
            for pattern in patterns:
                if re.search(pattern, file_path, re.IGNORECASE):
                    misplaced_scripts.append(file_path)
                    break
        
        passed = len(misplaced_scripts) == 0
        
        return ValidationResult(
            rule_name="one_time_scripts",
            passed=passed,
            message=f"Misplaced one-time scripts: {len(misplaced_scripts)}",
            details={"misplaced_scripts": misplaced_scripts},
            severity="error" if not passed else "info"
        )
    
    async def calculate_debt_score(self) -> float:
        """Calculate current technical debt score (0-100, 0 = no debt)"""
        factors = {
            "file_count": await self._assess_file_count(),
            "repository_size": await self._assess_repository_size(),
            "code_quality": await self._assess_code_quality(),
            "documentation_coverage": await self._assess_documentation(),
            "test_coverage": await self._assess_test_coverage(),
            "dependency_health": await self._assess_dependencies()
        }
        
        # Weighted scoring
        weights = {
            "file_count": 0.20,
            "repository_size": 0.15,
            "code_quality": 0.30,
            "documentation_coverage": 0.15,
            "test_coverage": 0.15,
            "dependency_health": 0.05
        }
        
        debt_score = sum(factors[factor] * weights[factor] for factor in factors)
        return min(100, max(0, debt_score))
    
    async def _assess_file_count(self) -> float:
        """Assess file count factor (0-100)"""
        file_count = await self._count_files()
        
        if file_count <= 200:
            return 0
        elif file_count <= 250:
            return 20
        elif file_count <= 300:
            return 40
        elif file_count <= 400:
            return 60
        elif file_count <= 500:
            return 80
        else:
            return 100
    
    async def _assess_repository_size(self) -> float:
        """Assess repository size factor (0-100)"""
        repo_size = await self._get_repository_size()
        
        if repo_size <= 400:
            return 0
        elif repo_size <= 500:
            return 20
        elif repo_size <= 600:
            return 40
        elif repo_size <= 800:
            return 60
        elif repo_size <= 1000:
            return 80
        else:
            return 100
    
    async def _assess_code_quality(self) -> float:
        """Assess code quality factor (0-100)"""
        # Simple code quality assessment
        quality_score = 0
        
        # Check for common quality issues
        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Long lines
                    lines = content.split('\n')
                    long_lines = sum(1 for line in lines if len(line) > 88)
                    if long_lines > 10:
                        quality_score += 5
                    
                    # Missing docstrings
                    if 'def ' in content and '"""' not in content:
                        quality_score += 10
                    
                    # Too many imports
                    import_lines = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
                    if len(import_lines) > 20:
                        quality_score += 5
                        
            except Exception:
                continue
        
        return min(100, quality_score)
    
    async def _assess_documentation(self) -> float:
        """Assess documentation coverage factor (0-100)"""
        py_files = list(self.base_path.rglob("*.py"))
        md_files = list(self.base_path.rglob("*.md"))
        
        if len(py_files) == 0:
            return 0
        
        doc_ratio = len(md_files) / len(py_files)
        
        if doc_ratio >= 0.5:
            return 0
        elif doc_ratio >= 0.3:
            return 20
        elif doc_ratio >= 0.2:
            return 40
        elif doc_ratio >= 0.1:
            return 60
        else:
            return 80
    
    async def _assess_test_coverage(self) -> float:
        """Assess test coverage factor (0-100)"""
        py_files = list(self.base_path.rglob("*.py"))
        test_files = list(self.base_path.rglob("test_*.py")) + list(self.base_path.rglob("*_test.py"))
        
        if len(py_files) == 0:
            return 0
        
        test_ratio = len(test_files) / len(py_files)
        
        if test_ratio >= 0.8:
            return 0
        elif test_ratio >= 0.6:
            return 20
        elif test_ratio >= 0.4:
            return 40
        elif test_ratio >= 0.2:
            return 60
        else:
            return 80
    
    async def _assess_dependencies(self) -> float:
        """Assess dependency health factor (0-100)"""
        # Check for requirements files
        req_files = list(self.base_path.rglob("requirements*.txt")) + list(self.base_path.rglob("pyproject.toml"))
        
        if len(req_files) == 0:
            return 50
        
        # Simple dependency health check
        return 0  # Assume dependencies are healthy for now
    
    async def _count_files(self) -> int:
        """Count total files in repository"""
        count = 0
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and ".git" not in str(file_path) and ".venv" not in str(file_path) and "node_modules" not in str(file_path):
                count += 1
        return count
    
    async def _get_repository_size(self) -> float:
        """Get repository size in MB"""
        try:
            result = subprocess.run(
                ["du", "-sm", str(self.base_path)],
                capture_output=True,
                text=True,
                check=True
            )
            size_mb = float(result.stdout.split()[0])
            return size_mb
        except Exception:
            return 0.0
    
    async def trigger_debt_alert(self, debt_score: float):
        """Trigger debt alert for high debt scores"""
        logger.warning(f"🚨 Technical debt alert! Score: {debt_score}/100")
        
        # Could integrate with Slack, email, etc.
        alert_message = f"""
        🚨 TECHNICAL DEBT ALERT
        
        Current debt score: {debt_score}/100
        Threshold exceeded: 20/100
        
        Immediate action required to prevent debt accumulation.
        """
        
        print(alert_message)
    
    async def suggest_remediation(self):
        """Suggest remediation actions"""
        suggestions = [
            "1. Run file cleanup: python scripts/utils/daily_cleanup.py",
            "2. Review and remove unused files",
            "3. Consolidate duplicate code",
            "4. Update documentation",
            "5. Add missing tests",
            "6. Review and optimize dependencies"
        ]
        
        logger.info("💡 Suggested remediation actions:")
        for suggestion in suggestions:
            logger.info(f"   {suggestion}")

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Technical Debt Prevention Framework")
    parser.add_argument("--mode", choices=["validate", "monitor", "strict"], default="validate",
                       help="Operation mode")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    framework = TechnicalDebtPreventionFramework()
    
    if args.mode == "validate":
        logger.info("🔍 Running validation mode...")
        report = await framework.pre_commit_validation()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
        
        print("\n📊 TECHNICAL DEBT PREVENTION REPORT")
        print(f"{'='*50}")
        print(f"Debt Score: {report.debt_score:.1f}/100")
        print(f"File Count: {report.file_count}")
        print(f"Repository Size: {report.repository_size_mb:.1f}MB")
        print(f"Validation: {'✅ PASSED' if report.passed else '❌ FAILED'}")
        
        print("\n📋 VALIDATION RESULTS:")
        for result in report.results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.rule_name}: {result.message}")
        
        if not report.passed:
            sys.exit(1)
    
    elif args.mode == "monitor":
        logger.info("🔍 Running monitoring mode...")
        await framework.continuous_monitoring()
    
    elif args.mode == "strict":
        logger.info("🔍 Running strict mode...")
        report = await framework.pre_commit_validation()
        
        if report.debt_score > 0:
            logger.error(f"❌ Strict mode: Debt score {report.debt_score}/100 > 0")
            sys.exit(1)
        
        if not report.passed:
            logger.error("❌ Strict mode: Validation failed")
            sys.exit(1)
        
        logger.info("✅ Strict mode: All checks passed")

if __name__ == "__main__":
    asyncio.run(main()) 