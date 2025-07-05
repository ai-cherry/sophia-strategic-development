#!/usr/bin/env python3
"""
Simple Codacy MCP Server
A lightweight code quality analysis server
"""

import ast
import logging
import re
from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simple Codacy MCP Server",
    description="Lightweight code quality analysis",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Code to analyze")
    filename: str = Field("snippet.py", description="Filename for context")
    language: str = Field("python", description="Programming language")


class CodeIssue(BaseModel):
    severity: str
    title: str
    description: str
    line_number: int
    suggestion: Optional[str] = None


class AnalysisResult(BaseModel):
    filename: str
    issues: list[CodeIssue]
    metrics: dict[str, Any]
    overall_score: float
    security_score: float


# Security patterns
SECURITY_PATTERNS = [
    {
        "pattern": r"eval\s*\(",
        "severity": "critical",
        "title": "Dangerous eval() usage",
        "description": "Use of eval() can lead to code injection",
        "suggestion": "Use ast.literal_eval() or avoid dynamic execution",
    },
    {
        "pattern": r"exec\s*\(",
        "severity": "critical",
        "title": "Dangerous exec() usage",
        "description": "Use of exec() can lead to code injection",
        "suggestion": "Avoid dynamic code execution",
    },
    {
        "pattern": r'password\s*=\s*["\'][^"\']+["\']',
        "severity": "high",
        "title": "Hardcoded password",
        "description": "Password is hardcoded in source code",
        "suggestion": "Use environment variables or secure config",
    },
    {
        "pattern": r'api_key\s*=\s*["\'][^"\']+["\']',
        "severity": "high",
        "title": "Hardcoded API key",
        "description": "API key is hardcoded in source code",
        "suggestion": "Use environment variables or secure config",
    },
    {
        "pattern": r"subprocess.*shell=True",
        "severity": "high",
        "title": "Shell injection risk",
        "description": "Using shell=True can lead to injection",
        "suggestion": "Use shell=False and pass arguments as list",
    },
    {
        "pattern": r"os\.system\s*\(",
        "severity": "medium",
        "title": "Unsafe system command",
        "description": "os.system() can be vulnerable",
        "suggestion": "Use subprocess.run() instead",
    },
    {
        "pattern": r"pickle\.loads?\s*\(",
        "severity": "medium",
        "title": "Unsafe deserialization",
        "description": "Pickle can execute arbitrary code",
        "suggestion": "Use JSON or other safe formats",
    },
]


def analyze_security(code: str, filename: str) -> list[CodeIssue]:
    """Analyze code for security issues"""
    issues = []
    lines = code.split("\n")

    for line_num, line in enumerate(lines, 1):
        for pattern_info in SECURITY_PATTERNS:
            if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                issues.append(
                    CodeIssue(
                        severity=pattern_info["severity"],
                        title=pattern_info["title"],
                        description=pattern_info["description"],
                        line_number=line_num,
                        suggestion=pattern_info.get("suggestion"),
                    )
                )

    return issues


def analyze_complexity(
    code: str, filename: str
) -> tuple[list[CodeIssue], dict[str, int]]:
    """Analyze code complexity"""
    issues = []
    metrics = {"functions": 0, "classes": 0, "total_complexity": 0}

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["functions"] += 1
                # Simple complexity calculation
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For)):
                        complexity += 1

                metrics["total_complexity"] += complexity

                if complexity > 10:
                    issues.append(
                        CodeIssue(
                            severity="medium",
                            title="High function complexity",
                            description=f"Function '{node.name}' has complexity {complexity}",
                            line_number=node.lineno,
                            suggestion="Consider breaking into smaller functions",
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1

    except SyntaxError as e:
        issues.append(
            CodeIssue(
                severity="critical",
                title="Syntax error",
                description=f"Syntax error: {e.msg}",
                line_number=e.lineno or 1,
            )
        )

    return issues, metrics


def calculate_scores(issues: list[CodeIssue]) -> tuple[float, float]:
    """Calculate overall and security scores"""
    # Count issues by severity
    severity_weights = {"critical": 25, "high": 15, "medium": 10, "low": 5, "info": 2}

    total_penalty = 0
    security_penalty = 0

    for issue in issues:
        penalty = severity_weights.get(issue.severity, 0)
        total_penalty += penalty
        if "security" in issue.title.lower() or "injection" in issue.title.lower():
            security_penalty += penalty

    overall_score = max(0, 100 - total_penalty)
    security_score = max(0, 100 - security_penalty)

    return overall_score, security_score


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Simple Codacy MCP Server",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "codacy",
    }


@app.post("/api/v1/analyze/code", response_model=AnalysisResult)
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code for quality issues"""
    try:
        # Security analysis
        security_issues = analyze_security(request.code, request.filename)

        # Complexity analysis
        complexity_issues, metrics = analyze_complexity(request.code, request.filename)

        # Combine all issues
        all_issues = security_issues + complexity_issues

        # Calculate scores
        overall_score, security_score = calculate_scores(all_issues)

        # Add line counts to metrics
        lines = request.code.split("\n")
        metrics["total_lines"] = len(lines)
        metrics["non_empty_lines"] = len([l for l in lines if l.strip()])

        return AnalysisResult(
            filename=request.filename,
            issues=all_issues,
            metrics=metrics,
            overall_score=overall_score,
            security_score=security_score,
        )

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/security/scan")
async def security_scan(request: CodeAnalysisRequest):
    """Dedicated security scan endpoint"""
    try:
        issues = analyze_security(request.code, request.filename)

        # Group by severity
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        return {
            "filename": request.filename,
            "total_issues": len(issues),
            "severity_breakdown": severity_counts,
            "issues": issues,
        }

    except Exception as e:
        logger.error(f"Security scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_stats():
    """Get server statistics"""
    return {
        "uptime": "running",
        "analyses_performed": 0,
        "patterns_available": len(SECURITY_PATTERNS),
        "supported_languages": ["python"],
    }


if __name__ == "__main__":
    port = 3008
    logger.info(f"🚀 Starting Simple Codacy MCP Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
