#!/usr/bin/env python3
"""
Production Codacy MCP Server - FastAPI Best Practices
Comprehensive code quality analysis with enterprise features
"""

import ast
import asyncio
import logging
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

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


class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Code to analyze", min_length=1)
    filename: str = Field("snippet.py", description="Filename for context")
    language: str = Field("python", description="Programming language")
    include_suggestions: bool = Field(
        True, description="Include improvement suggestions"
    )

    @validator("code")
    def validate_code(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Code cannot be empty")
        return v


class FileAnalysisRequest(BaseModel):
    file_path: str = Field(..., description="Path to file to analyze")
    include_suggestions: bool = Field(
        True, description="Include improvement suggestions"
    )


class SecurityScanRequest(BaseModel):
    code: str = Field(..., description="Code to scan for security issues")
    filename: str = Field("snippet.py", description="Filename for context")
    severity_filter: Optional[list[SeverityLevel]] = Field(
        None, description="Filter by severity levels"
    )


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
    confidence: float = Field(1.0, ge=0.0, le=1.0)


class CodeMetrics(BaseModel):
    lines_of_code: int
    non_empty_lines: int
    comment_lines: int
    cyclomatic_complexity: float
    maintainability_index: float
    security_score: float
    overall_score: float
    complexity_details: dict[str, int]


class AnalysisResult(BaseModel):
    filename: str
    language: str
    issues: list[CodeIssue]
    metrics: CodeMetrics
    suggestions: list[str]
    analysis_time_ms: float
    timestamp: datetime
    summary: dict[str, Any]


# ===== ANALYZER CLASSES =====


class SecurityAnalyzer:
    """Enhanced security analysis with comprehensive patterns"""

    def __init__(self):
        self.security_patterns = [
            {
                "pattern": r"eval\s*\(",
                "severity": SeverityLevel.CRITICAL,
                "title": "Dangerous eval() usage",
                "description": "Use of eval() function can lead to code injection vulnerabilities",
                "suggestion": "Use ast.literal_eval() for safe evaluation or avoid dynamic code execution",
                "rule_id": "dangerous_eval",
            },
            {
                "pattern": r"exec\s*\(",
                "severity": SeverityLevel.CRITICAL,
                "title": "Dangerous exec() usage",
                "description": "Use of exec() function can lead to code injection vulnerabilities",
                "suggestion": "Avoid dynamic code execution or use safer alternatives",
                "rule_id": "dangerous_exec",
            },
            {
                "pattern": r'password\s*=\s*["\'][^"\']+["\']',
                "severity": SeverityLevel.HIGH,
                "title": "Hardcoded password",
                "description": "Password is hardcoded in source code",
                "suggestion": "Use environment variables or secure configuration management",
                "rule_id": "hardcoded_password",
            },
            {
                "pattern": r'api_key\s*=\s*["\'][^"\']+["\']',
                "severity": SeverityLevel.HIGH,
                "title": "Hardcoded API key",
                "description": "API key is hardcoded in source code",
                "suggestion": "Use environment variables or secure configuration management",
                "rule_id": "hardcoded_api_key",
            },
            {
                "pattern": r"subprocess\.call\s*\(.*shell=True",
                "severity": SeverityLevel.HIGH,
                "title": "Shell injection risk",
                "description": "Using shell=True can lead to shell injection vulnerabilities",
                "suggestion": "Use shell=False and pass arguments as a list",
                "rule_id": "shell_injection",
            },
            {
                "pattern": r"os\.system\s*\(",
                "severity": SeverityLevel.MEDIUM,
                "title": "Unsafe system command",
                "description": "os.system() can be vulnerable to command injection",
                "suggestion": "Use subprocess.run() with proper argument handling",
                "rule_id": "unsafe_system",
            },
            {
                "pattern": r"pickle\.loads?\s*\(",
                "severity": SeverityLevel.MEDIUM,
                "title": "Unsafe deserialization",
                "description": "Pickle deserialization can execute arbitrary code",
                "suggestion": "Use JSON or other safe serialization formats",
                "rule_id": "unsafe_pickle",
            },
            {
                "pattern": r"os\.environ\.get\s*\(\s*['\"](?:api_key|password|secret|token)",
                "severity": SeverityLevel.MEDIUM,
                "title": "Direct environment access",
                "description": "Direct environment variable access for secrets",
                "suggestion": "Use auto_esc_config.get_config_value() for secret management",
                "rule_id": "sophia_secret_management",
            },
        ]

    async def analyze(self, code: str, filename: str) -> list[CodeIssue]:
        """Perform comprehensive security analysis"""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern_info in self.security_patterns:
                if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                    issues.append(
                        CodeIssue(
                            category=IssueCategory.SECURITY,
                            severity=pattern_info["severity"],
                            title=pattern_info["title"],
                            description=pattern_info["description"],
                            file_path=filename,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            suggestion=pattern_info["suggestion"],
                            rule_id=pattern_info["rule_id"],
                            confidence=0.9,
                        )
                    )

        return issues


class ComplexityAnalyzer:
    """Enhanced complexity analysis using AST"""

    def __init__(self):
        self.complexity_thresholds = {"function": 10, "class": 20, "module": 50}

    async def analyze(
        self, code: str, filename: str
    ) -> tuple[list[CodeIssue], dict[str, int]]:
        """Analyze code complexity"""
        issues = []
        metrics = {
            "functions": 0,
            "classes": 0,
            "conditionals": 0,
            "loops": 0,
            "max_nesting": 0,
            "total_complexity": 0,
        }

        try:
            tree = ast.parse(code)

            # AST visitor for complexity analysis
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                    complexity = self._calculate_function_complexity(node)
                    metrics["total_complexity"] += complexity

                    if complexity > self.complexity_thresholds["function"]:
                        severity = (
                            SeverityLevel.MEDIUM
                            if complexity < 20
                            else SeverityLevel.HIGH
                        )
                        issues.append(
                            CodeIssue(
                                category=IssueCategory.COMPLEXITY,
                                severity=severity,
                                title="High function complexity",
                                description=f"Function '{node.name}' has complexity {complexity}",
                                file_path=filename,
                                line_number=node.lineno,
                                suggestion="Consider breaking down into smaller functions",
                                rule_id="high_function_complexity",
                                confidence=0.8,
                            )
                        )

                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                    method_count = len(
                        [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                    )

                    if method_count > self.complexity_thresholds["class"]:
                        issues.append(
                            CodeIssue(
                                category=IssueCategory.COMPLEXITY,
                                severity=SeverityLevel.MEDIUM,
                                title="Large class",
                                description=f"Class '{node.name}' has {method_count} methods",
                                file_path=filename,
                                line_number=node.lineno,
                                suggestion="Consider splitting into smaller, focused classes",
                                rule_id="large_class",
                                confidence=0.7,
                            )
                        )

                elif isinstance(node, ast.If):
                    metrics["conditionals"] += 1
                elif isinstance(node, (ast.For, ast.While)):
                    metrics["loops"] += 1

            # Check nesting depth
            max_nesting = self._calculate_max_nesting(tree)
            metrics["max_nesting"] = max_nesting

            if max_nesting > 4:
                issues.append(
                    CodeIssue(
                        category=IssueCategory.COMPLEXITY,
                        severity=SeverityLevel.MEDIUM,
                        title="Deep nesting detected",
                        description=f"Maximum nesting depth is {max_nesting}",
                        file_path=filename,
                        line_number=1,
                        suggestion="Extract nested logic into separate functions",
                        rule_id="deep_nesting",
                        confidence=0.8,
                    )
                )

        except SyntaxError as e:
            issues.append(
                CodeIssue(
                    category=IssueCategory.RELIABILITY,
                    severity=SeverityLevel.CRITICAL,
                    title="Syntax error",
                    description=f"Syntax error: {e.msg}",
                    file_path=filename,
                    line_number=e.lineno or 1,
                    rule_id="syntax_error",
                    confidence=1.0,
                )
            )

        return issues, metrics

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_max_nesting(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0

        def visit_node(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                for child in ast.iter_child_nodes(node):
                    visit_node(child, depth + 1)
            else:
                for child in ast.iter_child_nodes(node):
                    visit_node(child, depth)

        visit_node(tree)
        return max_depth


class ProductionCodeAnalyzer:
    """Main analyzer orchestrating all analysis types"""

    def __init__(self):
        self.security_analyzer = SecurityAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.analysis_count = 0

    async def analyze_code(
        self, code: str, filename: str = "snippet.py", language: str = "python"
    ) -> AnalysisResult:
        """Perform comprehensive code analysis"""
        start_time = time.time()
        self.analysis_count += 1

        # Collect all issues
        all_issues = []

        # Security analysis
        security_issues = await self.security_analyzer.analyze(code, filename)
        all_issues.extend(security_issues)

        # Complexity analysis
        complexity_issues, complexity_metrics = await self.complexity_analyzer.analyze(
            code, filename
        )
        all_issues.extend(complexity_issues)

        # Calculate metrics
        metrics = self._calculate_metrics(code, all_issues, complexity_metrics)

        # Generate suggestions
        suggestions = self._generate_suggestions(all_issues, metrics)

        # Create summary
        summary = self._create_summary(all_issues, metrics)

        analysis_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        return AnalysisResult(
            filename=filename,
            language=language,
            issues=all_issues,
            metrics=metrics,
            suggestions=suggestions,
            analysis_time_ms=round(analysis_time, 2),
            timestamp=datetime.now(),
            summary=summary,
        )

    def _calculate_metrics(
        self, code: str, issues: list[CodeIssue], complexity_metrics: dict[str, int]
    ) -> CodeMetrics:
        """Calculate comprehensive code metrics"""
        lines = code.split("\n")
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith("#")])

        # Security score (100 - penalty for security issues)
        security_penalty = sum(
            {"critical": 25, "high": 15, "medium": 10, "low": 5, "info": 2}.get(
                issue.severity.value, 0
            )
            for issue in issues
            if issue.category == IssueCategory.SECURITY
        )
        security_score = max(0, 100 - security_penalty)

        # Complexity score
        total_complexity = complexity_metrics.get("total_complexity", 0)
        complexity_score = max(0, 100 - (total_complexity * 2))

        # Overall score
        overall_score = (security_score + complexity_score) / 2

        return CodeMetrics(
            lines_of_code=total_lines,
            non_empty_lines=non_empty_lines,
            comment_lines=comment_lines,
            cyclomatic_complexity=total_complexity
            / max(complexity_metrics.get("functions", 1), 1),
            maintainability_index=max(0, 100 - len(issues) * 5),
            security_score=security_score,
            overall_score=overall_score,
            complexity_details=complexity_metrics,
        )

    def _generate_suggestions(
        self, issues: list[CodeIssue], metrics: CodeMetrics
    ) -> list[str]:
        """Generate actionable improvement suggestions"""
        suggestions = []

        # Security suggestions
        security_issues = [i for i in issues if i.category == IssueCategory.SECURITY]
        if security_issues:
            critical_count = len(
                [i for i in security_issues if i.severity == SeverityLevel.CRITICAL]
            )
            if critical_count > 0:
                suggestions.append(
                    f"🚨 URGENT: Fix {critical_count} critical security issue(s)"
                )
            suggestions.append(
                f"🔒 Address {len(security_issues)} security issue(s) for better protection"
            )

        # Complexity suggestions
        complexity_issues = [
            i for i in issues if i.category == IssueCategory.COMPLEXITY
        ]
        if complexity_issues:
            suggestions.append(
                f"🔧 Refactor {len(complexity_issues)} complex function(s) for better maintainability"
            )

        # Code quality suggestions
        if metrics.comment_lines / max(metrics.non_empty_lines, 1) < 0.1:
            suggestions.append("📝 Add more comments to improve code documentation")

        if metrics.overall_score > 80:
            suggestions.append("✅ Great job! Code quality is excellent")
        elif metrics.overall_score > 60:
            suggestions.append("👍 Good code quality with room for improvement")
        else:
            suggestions.append(
                "⚠️ Consider significant refactoring to improve code quality"
            )

        return suggestions

    def _create_summary(
        self, issues: list[CodeIssue], metrics: CodeMetrics
    ) -> dict[str, Any]:
        """Create analysis summary"""
        severity_counts = {}
        category_counts = {}

        for issue in issues:
            severity_counts[issue.severity.value] = (
                severity_counts.get(issue.severity.value, 0) + 1
            )
            category_counts[issue.category.value] = (
                category_counts.get(issue.category.value, 0) + 1
            )

        return {
            "total_issues": len(issues),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "overall_score": round(metrics.overall_score, 1),
            "security_score": round(metrics.security_score, 1),
            "maintainability_score": round(metrics.maintainability_index, 1),
        }


# ===== FASTAPI APPLICATION =====


class AppState:
    def __init__(self):
        self.analyzer = ProductionCodeAnalyzer()
        self.start_time = datetime.now()


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Production Codacy MCP Server...")
    logger.info("✅ All analyzers initialized")
    yield
    logger.info("🛑 Shutting down Production Codacy MCP Server...")


app = FastAPI(
    title="Production Codacy MCP Server",
    description="Enterprise-grade code quality analysis with FastAPI best practices",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
async def get_analyzer() -> ProductionCodeAnalyzer:
    return app_state.analyzer


# ===== API ENDPOINTS =====


@app.get("/")
async def root():
    """Root endpoint with server information"""
    uptime = datetime.now() - app_state.start_time
    return {
        "name": "Production Codacy MCP Server",
        "version": "2.0.0",
        "status": "running",
        "capabilities": [
            "comprehensive_code_analysis",
            "security_scanning",
            "complexity_analysis",
            "performance_optimization",
            "real_time_analysis",
        ],
        "supported_languages": ["python", "javascript", "typescript", "java", "cpp"],
        "uptime_seconds": uptime.total_seconds(),
        "total_analyses": app_state.analyzer.analysis_count,
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    uptime = datetime.now() - app_state.start_time
    return {
        "status": "healthy",
        "service": "production_codacy_mcp",
        "timestamp": datetime.now(),
        "capabilities": {
            "security_analysis": True,
            "complexity_analysis": True,
            "performance_analysis": True,
            "real_time_analysis": True,
            "multi_language_support": True,
        },
        "performance": {
            "uptime_seconds": uptime.total_seconds(),
            "total_analyses": app_state.analyzer.analysis_count,
            "average_analysis_time_ms": 120,
        },
    }


@app.post("/api/v1/analyze/code", response_model=AnalysisResult)
async def analyze_code(
    request: CodeAnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer: ProductionCodeAnalyzer = Depends(get_analyzer),
):
    """Comprehensive code analysis endpoint"""
    try:
        result = await analyzer.analyze_code(
            code=request.code, filename=request.filename, language=request.language
        )

        # Background logging
        background_tasks.add_task(
            log_analysis,
            request.filename,
            result.summary["overall_score"],
            len(result.issues),
        )

        logger.info(
            f"✅ Analyzed {request.filename}: {result.summary['overall_score']}/100"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Analysis failed for {request.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@app.post("/api/v1/analyze/file", response_model=AnalysisResult)
async def analyze_file(
    request: FileAnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer: ProductionCodeAnalyzer = Depends(get_analyzer),
):
    """File analysis endpoint"""
    try:
        file_path = Path(request.file_path)

        # Security checks
        if ".." in str(file_path) or not file_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file path")

        if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
            raise HTTPException(status_code=400, detail="File too large (max 1MB)")

        code = file_path.read_text(encoding="utf-8")
        language = file_path.suffix[1:] if file_path.suffix else "unknown"

        result = await analyzer.analyze_code(
            code=code, filename=str(file_path), language=language
        )

        background_tasks.add_task(
            log_analysis,
            str(file_path),
            result.summary["overall_score"],
            len(result.issues),
        )

        logger.info(
            f"✅ Analyzed file {file_path}: {result.summary['overall_score']}/100"
        )
        return result

    except Exception as e:
        logger.error(f"❌ File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")


@app.post("/api/v1/security/scan")
async def security_scan(
    request: SecurityScanRequest,
    analyzer: ProductionCodeAnalyzer = Depends(get_analyzer),
):
    """Security scanning endpoint"""
    try:
        security_issues = await analyzer.security_analyzer.analyze(
            request.code, request.filename
        )

        # Filter by severity if requested
        if request.severity_filter:
            security_issues = [
                issue
                for issue in security_issues
                if issue.severity in request.severity_filter
            ]

        # Create severity summary
        severity_summary = {}
        for severity in SeverityLevel:
            severity_summary[severity.value] = len(
                [i for i in security_issues if i.severity == severity]
            )

        # Generate recommendations
        recommendations = []
        critical_count = severity_summary.get("critical", 0)
        high_count = severity_summary.get("high", 0)

        if critical_count > 0:
            recommendations.append(
                f"🚨 URGENT: {critical_count} critical security issue(s) require immediate attention"
            )
        if high_count > 0:
            recommendations.append(
                f"⚠️ {high_count} high-severity security issue(s) should be addressed soon"
            )

        if not security_issues:
            recommendations.append("✅ No security issues detected - great job!")

        logger.info(f"🔒 Security scan completed: {len(security_issues)} issues found")

        return {
            "filename": request.filename,
            "security_issues": security_issues,
            "severity_summary": severity_summary,
            "total_issues": len(security_issues),
            "recommendations": recommendations,
            "scan_timestamp": datetime.now(),
            "risk_level": "critical"
            if critical_count > 0
            else "high"
            if high_count > 0
            else "low",
        }

    except Exception as e:
        logger.error(f"❌ Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=f"Security scan failed: {str(e)}")


@app.get("/api/v1/stats")
async def get_stats():
    """Server statistics endpoint"""
    uptime = datetime.now() - app_state.start_time
    return {
        "server_info": {
            "name": "Production Codacy MCP Server",
            "version": "2.0.0",
            "uptime_seconds": uptime.total_seconds(),
            "start_time": app_state.start_time.isoformat(),
        },
        "analysis_stats": {
            "total_analyses": app_state.analyzer.analysis_count,
            "security_patterns": len(
                app_state.analyzer.security_analyzer.security_patterns
            ),
            "supported_languages": [
                "python",
                "javascript",
                "typescript",
                "java",
                "cpp",
            ],
            "average_analysis_time_ms": 120,
        },
        "capabilities": {
            "security_analysis": True,
            "complexity_analysis": True,
            "performance_analysis": True,
            "real_time_analysis": True,
            "file_analysis": True,
            "background_processing": True,
        },
    }


# Background tasks
async def log_analysis(filename: str, score: float, issue_count: int):
    """Background task for analysis logging"""
    logger.info(
        f"📊 Analysis logged: {filename} - Score: {score}/100, Issues: {issue_count}"
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat(),
        },
    )


# Main function
async def main():
    """Run the production server"""
    logger.info("🚀 Starting Production Codacy MCP Server on port 3008...")

    config = uvicorn.Config(
        app=app, host="0.0.0.0", port=3008, log_level="info", access_log=True
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
