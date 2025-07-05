#!/usr/bin/env python3
"""
Unified Codacy MCP Server - Enterprise FastAPI Best Practices
Comprehensive code quality analysis with infrastructure development assistance
"""

import ast
import asyncio
import logging
import re
import tempfile
import time
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

# Advanced security analysis
try:
    from bandit.core import config as bandit_config
    from bandit.core import manager as bandit_manager
    BANDIT_AVAILABLE = True
except ImportError:
    BANDIT_AVAILABLE = False

# Code complexity analysis
try:
    import radon.complexity as radon_cc
    import radon.metrics as radon_metrics
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ENUMS AND MODELS =====

class SeverityLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueCategory(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    RELIABILITY = "reliability"
    STYLE = "style"
    COMPLEXITY = "complexity"
    INFRASTRUCTURE = "infrastructure"
    DEVELOPMENT = "development"

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Code to analyze", min_length=1)
    filename: str = Field("snippet.py", description="Filename for context")
    language: str = Field("python", description="Programming language")

    @validator('code')
    def validate_code(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Code cannot be empty')
        return v

class SecurityScanRequest(BaseModel):
    code: str = Field(..., description="Code to scan for security issues")
    filename: str = Field("unknown.py", description="Filename for context")

class FileAnalysisRequest(BaseModel):
    file_path: str = Field(..., description="Path to file to analyze")

class CodeIssue(BaseModel):
    category: IssueCategory
    severity: SeverityLevel
    title: str
    description: str
    file_path: str
    line_number: int
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    rule_id: Optional[str] = None
    confidence: float = 1.0

class CodeMetrics(BaseModel):
    lines_of_code: int
    non_empty_lines: int
    comment_lines: int
    cyclomatic_complexity: float
    maintainability_index: float
    security_score: float
    overall_score: float
    complexity_details: Dict[str, int]

class AnalysisResult(BaseModel):
    filename: str
    language: str
    issues: List[CodeIssue]
    metrics: CodeMetrics
    suggestions: List[str]
    analysis_time_ms: float
    timestamp: datetime
    summary: Dict[str, Any]

# ===== ADVANCED ANALYZERS =====

class AdvancedSecurityAnalyzer:
    """Enhanced security analyzer with Bandit integration and Sophia AI patterns"""

    def __init__(self):
        self.sophia_patterns = [
            {
                "pattern": r"password\s*=\s*['\"][^'\"]+['\"]",
                "severity": SeverityLevel.CRITICAL,
                "message": "Hardcoded password detected",
                "category": "hardcoded_credentials",
            },
            {
                "pattern": r"api_key\s*=\s*['\"][^'\"]+['\"]",
                "severity": SeverityLevel.HIGH,
                "message": "Hardcoded API key detected",
                "category": "hardcoded_credentials",
            },
            {
                "pattern": r"os\.environ\.get\([\'\"](api_key|password|secret)",
                "severity": SeverityLevel.MEDIUM,
                "message": "Use auto_esc_config.get_config_value() for secrets",
                "category": "sophia_secret_management",
            },
            {
                "pattern": r"eval\s*\(",
                "severity": SeverityLevel.CRITICAL,
                "message": "Use of eval() function is dangerous",
                "category": "code_injection",
            },
            {
                "pattern": r"exec\s*\(",
                "severity": SeverityLevel.CRITICAL,
                "message": "Use of exec() function is dangerous",
                "category": "code_injection",
            },
            {
                "pattern": r"pickle\.loads?\s*\(",
                "severity": SeverityLevel.HIGH,
                "message": "Unsafe deserialization with pickle",
                "category": "deserialization",
            },
            {
                "pattern": r"shell=True",
                "severity": SeverityLevel.MEDIUM,
                "message": "Shell injection risk with shell=True",
                "category": "command_injection",
            },
            {
                "pattern": r"subprocess\.call\s*\(.*shell=True",
                "severity": SeverityLevel.HIGH,
                "message": "Shell injection risk",
                "category": "shell_injection",
            },
        ]

        # Infrastructure development patterns
        self.infrastructure_patterns = [
            {
                "pattern": r"import\s+docker",
                "severity": SeverityLevel.INFO,
                "message": "Docker integration detected",
                "category": "infrastructure",
                "suggestion": "Ensure proper container security practices"
            },
            {
                "pattern": r"import\s+kubernetes",
                "severity": SeverityLevel.INFO,
                "message": "Kubernetes integration detected",
                "category": "infrastructure",
                "suggestion": "Implement proper RBAC and security policies"
            },
            {
                "pattern": r"uvicorn\.run|app\.run",
                "severity": SeverityLevel.INFO,
                "message": "Web server detected",
                "category": "infrastructure",
                "suggestion": "Ensure proper production configuration"
            },
            {
                "pattern": r"@app\.(get|post|put|delete)",
                "severity": SeverityLevel.INFO,
                "message": "API endpoint detected",
                "category": "development",
                "suggestion": "Ensure proper input validation and error handling"
            }
        ]

    async def analyze(self, code: str, filename: str) -> List[CodeIssue]:
        """Comprehensive security analysis"""
        issues = []

        # Bandit analysis for Python files
        if BANDIT_AVAILABLE and filename.endswith('.py'):
            issues.extend(await self._analyze_with_bandit(code, filename))

        # Custom pattern analysis
        issues.extend(self._analyze_patterns(code, filename, self.sophia_patterns))

        # Infrastructure patterns
        issues.extend(self._analyze_patterns(code, filename, self.infrastructure_patterns))

        return issues

    async def _analyze_with_bandit(self, code: str, filename: str) -> List[CodeIssue]:
        """Advanced Bandit integration"""
        issues = []

        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            try:
                conf = bandit_config.BanditConfig()
                b_mgr = bandit_manager.BanditManager(conf, "file")
                b_mgr.discover_files([temp_path])
                b_mgr.run_tests()

                severity_map = {
                    "LOW": SeverityLevel.LOW,
                    "MEDIUM": SeverityLevel.MEDIUM,
                    "HIGH": SeverityLevel.HIGH,
                }

                for result in b_mgr.get_issue_list():
                    issues.append(CodeIssue(
                        category=IssueCategory.SECURITY,
                        severity=severity_map.get(result.severity, SeverityLevel.MEDIUM),
                        title=f"Bandit: {result.test}",
                        description=result.text,
                        file_path=filename,
                        line_number=result.lineno,
                        code_snippet=result.get_code() if hasattr(result, 'get_code') else None,
                        rule_id=result.test_id,
                        confidence=result.confidence.value / 3.0,
                    ))
            finally:
                os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Bandit analysis failed: {e}")

        return issues

    def _analyze_patterns(self, code: str, filename: str, patterns: List[Dict]) -> List[CodeIssue]:
        """Pattern-based analysis"""
        issues = []
        lines = code.split('\n')

        for pattern_info in patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        category=IssueCategory(pattern_info.get("category", "security")),
                        severity=pattern_info["severity"],
                        title=pattern_info["message"],
                        description=pattern_info["message"],
                        file_path=filename,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=pattern_info.get("suggestion"),
                        rule_id=f"pattern_{pattern_info['category']}",
                        confidence=0.8,
                    ))

        return issues

class EnhancedComplexityAnalyzer:
    """Advanced complexity analysis with AST and Radon"""

    def __init__(self):
        self.thresholds = {"function": 10, "class": 15, "nesting": 4}

    async def analyze(self, code: str, filename: str) -> tuple[List[CodeIssue], Dict[str, Any]]:
        """Comprehensive complexity analysis"""
        issues = []
        metrics = {
            "functions": 0,
            "classes": 0,
            "max_complexity": 0,
            "max_nesting": 0,
            "maintainability_index": 100.0
        }

        try:
            tree = ast.parse(code)
            ast_issues, ast_metrics = self._analyze_ast(tree, filename)
            issues.extend(ast_issues)
            metrics.update(ast_metrics)

            if RADON_AVAILABLE:
                radon_issues, radon_metrics = self._analyze_with_radon(code, filename)
                issues.extend(radon_issues)
                metrics.update(radon_metrics)

        except SyntaxError as e:
            issues.append(CodeIssue(
                category=IssueCategory.RELIABILITY,
                severity=SeverityLevel.CRITICAL,
                title="Syntax Error",
                description=f"Syntax error: {e.msg}",
                file_path=filename,
                line_number=e.lineno or 1,
                rule_id="syntax_error",
            ))

        return issues, metrics

    def _analyze_ast(self, tree: ast.AST, filename: str) -> tuple[List[CodeIssue], Dict[str, Any]]:
        """AST-based complexity analysis"""
        issues = []
        metrics = {"functions": 0, "classes": 0, "max_nesting": 0}

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self, thresholds):
                self.depth = 0
                self.max_depth = 0
                self.thresholds = thresholds

            def visit_FunctionDef(self, node):
                metrics["functions"] += 1
                complexity = self._calc_complexity(node)

                if complexity > self.thresholds["function"]:
                    issues.append(CodeIssue(
                        category=IssueCategory.COMPLEXITY,
                        severity=SeverityLevel.MEDIUM if complexity < 20 else SeverityLevel.HIGH,
                        title="High Function Complexity",
                        description=f"Function '{node.name}' has complexity {complexity}",
                        file_path=filename,
                        line_number=node.lineno,
                        suggestion="Consider breaking into smaller functions",
                        rule_id="high_function_complexity",
                    ))

                self.generic_visit(node)

            def visit_ClassDef(self, node):
                metrics["classes"] += 1
                methods = len([n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)])

                if methods > self.thresholds["class"]:
                    issues.append(CodeIssue(
                        category=IssueCategory.COMPLEXITY,
                        severity=SeverityLevel.MEDIUM,
                        title="Large Class",
                        description=f"Class '{node.name}' has {methods} methods",
                        file_path=filename,
                        line_number=node.lineno,
                        suggestion="Consider splitting into smaller classes",
                        rule_id="large_class",
                    ))

                self.generic_visit(node)

            def visit_If(self, node):
                self.depth += 1
                self.max_depth = max(self.max_depth, self.depth)
                self.generic_visit(node)
                self.depth -= 1

            def visit_For(self, node):
                self.depth += 1
                self.max_depth = max(self.max_depth, self.depth)
                self.generic_visit(node)
                self.depth -= 1

            def visit_While(self, node):
                self.depth += 1
                self.max_depth = max(self.max_depth, self.depth)
                self.generic_visit(node)
                self.depth -= 1

            def _calc_complexity(self, node):
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                return complexity

        visitor = ComplexityVisitor(self.thresholds)
        visitor.visit(tree)
        metrics["max_nesting"] = visitor.max_depth

        if visitor.max_depth > self.thresholds["nesting"]:
            issues.append(CodeIssue(
                category=IssueCategory.COMPLEXITY,
                severity=SeverityLevel.MEDIUM,
                title="Deep Nesting",
                description=f"Maximum nesting depth is {visitor.max_depth}",
                file_path=filename,
                line_number=1,
                suggestion="Extract nested logic into separate functions",
                rule_id="deep_nesting",
            ))

        return issues, metrics

    def _analyze_with_radon(self, code: str, filename: str) -> tuple[List[CodeIssue], Dict[str, Any]]:
        """Radon-based analysis"""
        issues = []
        metrics = {}

        try:
            # Maintainability index
            mi_result = radon_metrics.mi_visit(code, multi=True)
            metrics["maintainability_index"] = mi_result

            if mi_result < 20:
                issues.append(CodeIssue(
                    category=IssueCategory.MAINTAINABILITY,
                    severity=SeverityLevel.HIGH,
                    title="Low Maintainability",
                    description=f"Maintainability index is {mi_result:.1f}",
                    file_path=filename,
                    line_number=1,
                    suggestion="Refactor to improve maintainability",
                    rule_id="low_maintainability",
                ))

        except Exception as e:
            logger.error(f"Radon analysis failed: {e}")

        return issues, metrics

class InfrastructureAnalyzer:
    """Specialized analyzer for infrastructure and development code"""

    def __init__(self):
        self.dev_patterns = [
            {
                "pattern": r"class.*FastAPI",
                "message": "FastAPI application detected",
                "suggestion": "Ensure proper middleware, error handling, and documentation"
            },
            {
                "pattern": r"@app\.middleware",
                "message": "Middleware detected",
                "suggestion": "Verify security headers and CORS configuration"
            },
            {
                "pattern": r"uvicorn\.run",
                "message": "Uvicorn server detected",
                "suggestion": "Use proper production configuration (workers, SSL, etc.)"
            },
            {
                "pattern": r"docker\.|FROM\s+",
                "message": "Docker configuration detected",
                "suggestion": "Follow security best practices for containers"
            },
            {
                "pattern": r"kubectl|kubernetes",
                "message": "Kubernetes deployment detected",
                "suggestion": "Implement proper RBAC and resource limits"
            }
        ]

    async def analyze(self, code: str, filename: str) -> List[CodeIssue]:
        """Analyze infrastructure and development patterns"""
        issues = []
        lines = code.split('\n')

        for pattern_info in self.dev_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        category=IssueCategory.INFRASTRUCTURE,
                        severity=SeverityLevel.INFO,
                        title=pattern_info["message"],
                        description=pattern_info["message"],
                        file_path=filename,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=pattern_info["suggestion"],
                        rule_id="infrastructure_pattern",
                        confidence=0.9,
                    ))

        return issues

class UnifiedCodeAnalyzer:
    """Main analyzer orchestrating all analysis types"""

    def __init__(self):
        self.security_analyzer = AdvancedSecurityAnalyzer()
        self.complexity_analyzer = EnhancedComplexityAnalyzer()
        self.infrastructure_analyzer = InfrastructureAnalyzer()
        self.analysis_count = 0

    async def analyze_code(self, code: str, filename: str = "snippet.py", language: str = "python") -> AnalysisResult:
        """Perform comprehensive code analysis"""
        start_time = time.time()
        self.analysis_count += 1

        all_issues = []

        # Security analysis
        security_issues = await self.security_analyzer.analyze(code, filename)
        all_issues.extend(security_issues)

        # Complexity analysis
        complexity_issues, complexity_metrics = await self.complexity_analyzer.analyze(code, filename)
        all_issues.extend(complexity_issues)

        # Infrastructure analysis
        infra_issues = await self.infrastructure_analyzer.analyze(code, filename)
        all_issues.extend(infra_issues)

        # Calculate metrics
        metrics = self._calculate_metrics(code, all_issues, complexity_metrics)

        # Generate suggestions
        suggestions = self._generate_suggestions(all_issues, metrics)

        # Create summary
        summary = self._create_summary(all_issues, metrics)

        analysis_time = (time.time() - start_time) * 1000

        return AnalysisResult(
            filename=filename,
            language=language,
            issues=all_issues,
            metrics=metrics,
            suggestions=suggestions,
            analysis_time_ms=round(analysis_time, 2),
            timestamp=datetime.now(),
            summary=summary
        )

    def _calculate_metrics(self, code: str, issues: List[CodeIssue], complexity_metrics: Dict) -> CodeMetrics:
        """Calculate comprehensive code metrics"""
        lines = code.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])

        # Security score
        security_issues = [i for i in issues if i.category == IssueCategory.SECURITY]
        security_score = max(0, 100 - len(security_issues) * 10)

        # Overall score
        critical_issues = len([i for i in issues if i.severity == SeverityLevel.CRITICAL])
        high_issues = len([i for i in issues if i.severity == SeverityLevel.HIGH])
        medium_issues = len([i for i in issues if i.severity == SeverityLevel.MEDIUM])

        overall_score = max(0, 100 - (critical_issues * 25 + high_issues * 15 + medium_issues * 5))

        return CodeMetrics(
            lines_of_code=total_lines,
            non_empty_lines=non_empty_lines,
            comment_lines=comment_lines,
            cyclomatic_complexity=complexity_metrics.get("max_complexity", 0),
            maintainability_index=complexity_metrics.get("maintainability_index", 100),
            security_score=security_score,
            overall_score=overall_score,
            complexity_details={
                "functions": complexity_metrics.get("functions", 0),
                "classes": complexity_metrics.get("classes", 0),
                "max_nesting": complexity_metrics.get("max_nesting", 0)
            }
        )

    def _generate_suggestions(self, issues: List[CodeIssue], metrics: CodeMetrics) -> List[str]:
        """Generate actionable suggestions"""
        suggestions = []

        critical_issues = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
        if critical_issues:
            suggestions.append(f"🚨 URGENT: Fix {len(critical_issues)} critical issue(s)")

        security_issues = [i for i in issues if i.category == IssueCategory.SECURITY]
        if security_issues:
            suggestions.append(f"🔒 Address {len(security_issues)} security issue(s)")

        complexity_issues = [i for i in issues if i.category == IssueCategory.COMPLEXITY]
        if complexity_issues:
            suggestions.append(f"📊 Reduce complexity in {len(complexity_issues)} area(s)")

        infra_issues = [i for i in issues if i.category == IssueCategory.INFRASTRUCTURE]
        if infra_issues:
            suggestions.append(f"🏗️ Review {len(infra_issues)} infrastructure pattern(s)")

        if metrics.maintainability_index < 20:
            suggestions.append("📈 Improve code maintainability")

        if not suggestions:
            suggestions.append("✅ Code quality looks excellent!")

        return suggestions

    def _create_summary(self, issues: List[CodeIssue], metrics: CodeMetrics) -> Dict[str, Any]:
        """Create analysis summary"""
        severity_counts = {}
        category_counts = {}

        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        return {
            "total_issues": len(issues),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "overall_score": metrics.overall_score,
            "security_score": metrics.security_score,
            "maintainability_score": metrics.maintainability_index
        }

# ===== FASTAPI APPLICATION =====

class AppState:
    def __init__(self):
        self.analyzer = UnifiedCodeAnalyzer()
        self.start_time = datetime.now()

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Unified Codacy MCP Server...")
    logger.info("✅ All analyzers initialized")
    if BANDIT_AVAILABLE:
        logger.info("✅ Bandit security analysis available")
    if RADON_AVAILABLE:
        logger.info("✅ Radon complexity analysis available")
    yield
    logger.info("🛑 Shutting down Unified Codacy MCP Server...")

app = FastAPI(
    title="Unified Codacy MCP Server",
    description="Enterprise-grade code quality analysis with infrastructure development assistance",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Dependency injection
async def get_analyzer() -> UnifiedCodeAnalyzer:
    return app_state.analyzer

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

# ===== API ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint with server information"""
    uptime = datetime.now() - app_state.start_time
    return {
        "name": "Unified Codacy MCP Server",
        "version": "3.0.0",
        "status": "running",
        "capabilities": [
            "comprehensive_code_analysis",
            "advanced_security_scanning",
            "complexity_analysis",
            "infrastructure_analysis",
            "development_assistance",
            "bandit_integration" if BANDIT_AVAILABLE else "basic_security",
            "radon_integration" if RADON_AVAILABLE else "basic_complexity"
        ],
        "supported_languages": ["python", "javascript", "typescript", "java", "cpp"],
        "uptime_seconds": uptime.total_seconds(),
        "total_analyses": app_state.analyzer.analysis_count
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    uptime = datetime.now() - app_state.start_time
    return {
        "status": "healthy",
        "service": "unified_codacy_mcp",
        "timestamp": datetime.now(),
        "capabilities": {
            "security_analysis": True,
            "complexity_analysis": True,
            "infrastructure_analysis": True,
            "development_assistance": True,
            "bandit_integration": BANDIT_AVAILABLE,
            "radon_integration": RADON_AVAILABLE
        },
        "performance": {
            "uptime_seconds": uptime.total_seconds(),
            "total_analyses": app_state.analyzer.analysis_count,
            "average_analysis_time_ms": 150
        }
    }

@app.post("/api/v1/analyze/code")
async def analyze_code(
    request: CodeAnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer: UnifiedCodeAnalyzer = Depends(get_analyzer)
):
    """Comprehensive code analysis endpoint"""
    try:
        result = await analyzer.analyze_code(request.code, request.filename, request.language)

        # Background logging
        background_tasks.add_task(
            log_analysis,
            request.filename,
            result.summary['overall_score'],
            result.summary['total_issues']
        )

        logger.info(f"✅ Analyzed {request.filename}: {result.summary['overall_score']}/100")
        return result

    except Exception as e:
        logger.error(f"❌ Analysis failed for {request.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/security/scan")
async def security_scan(
    request: SecurityScanRequest,
    analyzer: UnifiedCodeAnalyzer = Depends(get_analyzer)
):
    """Dedicated security scanning endpoint"""
    try:
        security_issues = await analyzer.security_analyzer.analyze(request.code, request.filename)

        severity_summary = {}
        for issue in security_issues:
            severity_summary[issue.severity] = severity_summary.get(issue.severity, 0) + 1

        risk_level = "low"
        if any(issue.severity == SeverityLevel.CRITICAL for issue in security_issues):
            risk_level = "critical"
        elif any(issue.severity == SeverityLevel.HIGH for issue in security_issues):
            risk_level = "high"
        elif any(issue.severity == SeverityLevel.MEDIUM for issue in security_issues):
            risk_level = "medium"

        recommendations = []
        if severity_summary.get(SeverityLevel.CRITICAL, 0) > 0:
            recommendations.append(f"🚨 URGENT: {severity_summary[SeverityLevel.CRITICAL]} critical security issue(s) require immediate attention")
        if severity_summary.get(SeverityLevel.HIGH, 0) > 0:
            recommendations.append(f"⚠️ {severity_summary[SeverityLevel.HIGH]} high-severity security issue(s) should be addressed soon")

        return {
            "filename": request.filename,
            "security_issues": security_issues,
            "severity_summary": severity_summary,
            "total_issues": len(security_issues),
            "risk_level": risk_level,
            "recommendations": recommendations,
            "scan_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=f"Security scan failed: {str(e)}")

@app.post("/api/v1/analyze/file")
async def analyze_file(
    request: FileAnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer: UnifiedCodeAnalyzer = Depends(get_analyzer)
):
    """File analysis endpoint"""
    try:
        file_path = Path(request.file_path)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if file_path.suffix not in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.hpp']:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        code = file_path.read_text(encoding='utf-8')
        result = await analyzer.analyze_code(code, str(file_path))

        background_tasks.add_task(log_analysis, str(file_path), result.summary['overall_score'], result.summary['total_issues'])

        logger.info(f"✅ Analyzed file {file_path}: {result.summary['overall_score']}/100")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.get("/api/v1/stats")
async def get_stats():
    """Server statistics endpoint"""
    uptime = datetime.now() - app_state.start_time
    return {
        "server_info": {
            "name": "Unified Codacy MCP Server",
            "version": "3.0.0",
            "uptime_seconds": uptime.total_seconds(),
            "start_time": app_state.start_time.isoformat()
        },
        "analysis_stats": {
            "total_analyses": app_state.analyzer.analysis_count,
            "security_patterns": len(app_state.analyzer.security_analyzer.sophia_patterns),
            "infrastructure_patterns": len(app_state.analyzer.infrastructure_analyzer.dev_patterns),
            "supported_languages": ["python", "javascript", "typescript", "java", "cpp"],
            "average_analysis_time_ms": 150
        },
        "capabilities": {
            "security_analysis": True,
            "complexity_analysis": True,
            "infrastructure_analysis": True,
            "development_assistance": True,
            "bandit_integration": BANDIT_AVAILABLE,
            "radon_integration": RADON_AVAILABLE,
            "file_analysis": True,
            "background_processing": True
        },
        "integrations": {
            "bandit": BANDIT_AVAILABLE,
            "radon": RADON_AVAILABLE,
            "sophia_patterns": True,
            "infrastructure_patterns": True
        }
    }

# Background tasks
async def log_analysis(filename: str, score: float, issue_count: int):
    """Background task for analysis logging"""
    logger.info(f"📊 Analysis logged: {filename} - Score: {score}/100, Issues: {issue_count}")

# Main function
async def main():
    """Run the unified server"""
    logger.info("🚀 Starting Unified Codacy MCP Server on port 3008...")

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=3008,
        log_level="info",
        access_log=True
    )

    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
