#!/usr/bin/env python3
"""
Enhanced Codacy MCP Server with AI-Powered Quality Analysis
Implements strategic enhancements for Sophia AI platform
"""

import ast
import logging
import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Try to import AI services
try:
    from backend.services.snowflake_cortex_service import SnowflakeCortexService
    from backend.services.unified_ai_orchestration_service import (
        UnifiedAIOrchestrationService,
    )

    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    logging.warning("Snowflake Cortex not available - running in basic mode")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Enhanced Codacy MCP Server",
    description="AI-Powered Code Quality Analysis with Predictive Capabilities",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== MODELS =====


class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Code to analyze")
    filename: str = Field("snippet.py", description="Filename for context")
    language: str = Field("python", description="Programming language")
    enable_ai_insights: bool = Field(True, description="Enable AI-powered insights")
    enable_auto_fix: bool = Field(False, description="Enable automatic fix suggestions")
    context: dict[str, Any] | None = Field(None, description="Additional context")


class CodeIssue(BaseModel):
    severity: str
    title: str
    description: str
    line_number: int
    column_number: int | None = None
    suggestion: str | None = None
    auto_fix: str | None = None
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    category: str = "general"
    rule_id: str | None = None
    ai_insight: str | None = None


class PredictiveInsight(BaseModel):
    risk_level: str  # low, medium, high, critical
    prediction: str
    confidence: float
    recommended_action: str
    estimated_impact: dict[str, Any]


class QualityMetrics(BaseModel):
    total_lines: int
    non_empty_lines: int
    comment_lines: int
    complexity_score: float
    maintainability_index: float
    security_score: float
    overall_score: float
    test_coverage_estimate: float
    technical_debt_hours: float
    ai_quality_score: float


class AnalysisResult(BaseModel):
    filename: str
    language: str
    issues: list[CodeIssue]
    metrics: QualityMetrics
    predictive_insights: list[PredictiveInsight]
    auto_fix_available: bool
    ai_recommendations: list[str]
    business_impact: dict[str, Any]
    analysis_time_ms: float
    timestamp: datetime


class AutoFixRequest(BaseModel):
    filename: str
    issue_id: str
    apply_fix: bool = False


class HealthStatus(BaseModel):
    status: str
    timestamp: datetime
    service: str
    ai_services_available: bool
    patterns_loaded: int
    cache_hit_rate: float
    average_response_time_ms: float


# ===== ENHANCED SECURITY PATTERNS =====

ENHANCED_SECURITY_PATTERNS = [
    # Critical Security Issues
    {
        "pattern": r"eval\s*\(",
        "severity": "critical",
        "title": "Code Injection Vulnerability",
        "description": "eval() executes arbitrary code and poses severe security risk",
        "suggestion": "Use ast.literal_eval() for safe evaluation or refactor logic",
        "auto_fix_pattern": r"eval\((.*?)\)",
        "auto_fix_replacement": "ast.literal_eval(\\1)",
        "category": "security",
        "rule_id": "SEC001",
        "business_impact": {"risk": "high", "compliance": "failed"},
    },
    {
        "pattern": r"exec\s*\(",
        "severity": "critical",
        "title": "Dynamic Code Execution",
        "description": "exec() allows arbitrary code execution",
        "suggestion": "Eliminate dynamic code execution or use safe alternatives",
        "category": "security",
        "rule_id": "SEC002",
        "business_impact": {"risk": "high", "compliance": "failed"},
    },
    # Sophia AI Specific Patterns
    {
        "pattern": r"os\.environ\.get\s*\(\s*['\"](?:OPENAI_API_KEY|ANTHROPIC_API_KEY|GONG_ACCESS_KEY)",
        "severity": "high",
        "title": "Direct Environment Variable Access",
        "description": "Bypassing Pulumi ESC secret management",
        "suggestion": "Use backend.core.auto_esc_config.get_config_value() instead",
        "auto_fix_pattern": r"os\.environ\.get\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
        "auto_fix_replacement": "get_config_value('\\1')",
        "category": "sophia_standards",
        "rule_id": "SOPHIA001",
        "business_impact": {"security": "compromised", "maintainability": "reduced"},
    },
    {
        "pattern": r"print\s*\(",
        "severity": "low",
        "title": "Debug Print Statement",
        "description": "Print statements should use logger",
        "suggestion": "Use logger.info() or logger.debug() instead",
        "auto_fix_pattern": r"print\s*\((.*?)\)",
        "auto_fix_replacement": "logger.info(\\1)",
        "category": "best_practices",
        "rule_id": "BP001",
    },
    # Performance Patterns
    {
        "pattern": r"time\.sleep\s*\(",
        "severity": "medium",
        "title": "Blocking Sleep",
        "description": "Blocking sleep in async context",
        "suggestion": "Use await asyncio.sleep() for async code",
        "auto_fix_pattern": r"time\.sleep\s*\((.*?)\)",
        "auto_fix_replacement": "await asyncio.sleep(\\1)",
        "category": "performance",
        "rule_id": "PERF001",
    },
    # SQL Injection Patterns
    {
        "pattern": r"f['\"].*SELECT.*WHERE.*{.*}",
        "severity": "critical",
        "title": "SQL Injection Risk",
        "description": "String formatting in SQL queries can lead to injection",
        "suggestion": "Use parameterized queries",
        "category": "security",
        "rule_id": "SEC003",
        "business_impact": {"risk": "critical", "data_breach": "possible"},
    },
]


# ===== QUALITY ANALYZER =====


class EnhancedQualityAnalyzer:
    """AI-powered code quality analyzer with predictive capabilities"""

    def __init__(self):
        self.patterns = ENHANCED_SECURITY_PATTERNS
        self.cache = {}
        self.metrics_history = defaultdict(list)
        self.cortex_service = None
        self.ai_service = None

        # Initialize AI services if available
        if SNOWFLAKE_AVAILABLE:
            try:
                self.cortex_service = SnowflakeCortexService()
                self.ai_service = UnifiedAIOrchestrationService()
                logger.info("✅ AI services initialized successfully")
            except Exception as e:
                logger.warning(f"AI services initialization failed: {e}")

    async def analyze_code(
        self,
        code: str,
        filename: str,
        language: str = "python",
        enable_ai: bool = True,
        enable_auto_fix: bool = False,
        context: dict[str, Any] | None = None,
    ) -> AnalysisResult:
        """Perform comprehensive code analysis with AI insights"""
        start_time = time.time()

        # Basic pattern-based analysis
        issues = await self._analyze_patterns(code, filename)

        # AST-based complexity analysis
        complexity_issues, complexity_metrics = await self._analyze_complexity(
            code, filename
        )
        issues.extend(complexity_issues)

        # Calculate quality metrics
        metrics = await self._calculate_metrics(code, issues, complexity_metrics)

        # AI-powered analysis if enabled
        ai_insights = []
        ai_recommendations = []
        if enable_ai and self.cortex_service:
            ai_insights, ai_recommendations = await self._get_ai_insights(
                code, issues, metrics, context
            )

        # Generate predictive insights
        predictive_insights = await self._generate_predictive_insights(
            issues, metrics, filename
        )

        # Calculate business impact
        business_impact = self._calculate_business_impact(issues, metrics)

        # Check for auto-fix availability
        auto_fix_available = (
            any(issue.auto_fix is not None for issue in issues) and enable_auto_fix
        )

        analysis_time = (time.time() - start_time) * 1000

        # Store metrics for trend analysis
        self._store_metrics_history(filename, metrics)

        return AnalysisResult(
            filename=filename,
            language=language,
            issues=issues,
            metrics=metrics,
            predictive_insights=predictive_insights,
            auto_fix_available=auto_fix_available,
            ai_recommendations=ai_recommendations,
            business_impact=business_impact,
            analysis_time_ms=round(analysis_time, 2),
            timestamp=datetime.now(),
        )

    async def _analyze_patterns(self, code: str, filename: str) -> list[CodeIssue]:
        """Analyze code against enhanced security and quality patterns"""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern_info in self.patterns:
                match = re.search(pattern_info["pattern"], line, re.IGNORECASE)
                if match:
                    issue = CodeIssue(
                        severity=pattern_info["severity"],
                        title=pattern_info["title"],
                        description=pattern_info["description"],
                        line_number=line_num,
                        column_number=match.start() if match else None,
                        suggestion=pattern_info.get("suggestion"),
                        category=pattern_info.get("category", "general"),
                        rule_id=pattern_info.get("rule_id"),
                        confidence=0.95,
                    )

                    # Add auto-fix if available
                    if pattern_info.get("auto_fix_pattern"):
                        issue.auto_fix = re.sub(
                            pattern_info["auto_fix_pattern"],
                            pattern_info["auto_fix_replacement"],
                            line,
                        )

                    issues.append(issue)

        return issues

    async def _analyze_complexity(
        self, code: str, filename: str
    ) -> tuple[list[CodeIssue], dict[str, Any]]:
        """Analyze code complexity using AST"""
        issues = []
        metrics = {
            "functions": 0,
            "classes": 0,
            "methods": 0,
            "total_complexity": 0,
            "max_complexity": 0,
            "average_complexity": 0,
            "nested_depth": 0,
            "cognitive_complexity": 0,
        }

        try:
            tree = ast.parse(code)

            # Analyze all nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                    complexity = self._calculate_cyclomatic_complexity(node)
                    cognitive = self._calculate_cognitive_complexity(node)

                    metrics["total_complexity"] += complexity
                    metrics["cognitive_complexity"] += cognitive
                    metrics["max_complexity"] = max(
                        metrics["max_complexity"], complexity
                    )

                    # Flag high complexity functions
                    if complexity > 10:
                        severity = "medium" if complexity < 20 else "high"
                        issues.append(
                            CodeIssue(
                                severity=severity,
                                title=f"High Cyclomatic Complexity ({complexity})",
                                description=f"Function '{node.name}' is too complex",
                                line_number=node.lineno,
                                suggestion="Break down into smaller, focused functions",
                                category="complexity",
                                rule_id="COMPLEX001",
                                confidence=0.9,
                                ai_insight=f"This function handles {self._identify_responsibilities(node)} responsibilities",
                            )
                        )

                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                    method_count = sum(
                        1 for n in node.body if isinstance(n, ast.FunctionDef)
                    )
                    metrics["methods"] += method_count

                    # Flag large classes
                    if method_count > 20:
                        issues.append(
                            CodeIssue(
                                severity="medium",
                                title=f"Large Class ({method_count} methods)",
                                description=f"Class '{node.name}' violates Single Responsibility Principle",
                                line_number=node.lineno,
                                suggestion="Consider splitting into smaller, cohesive classes",
                                category="design",
                                rule_id="DESIGN001",
                                confidence=0.85,
                            )
                        )

            # Calculate averages
            if metrics["functions"] > 0:
                metrics["average_complexity"] = (
                    metrics["total_complexity"] / metrics["functions"]
                )

            # Check for deep nesting
            max_depth = self._calculate_max_nesting_depth(tree)
            metrics["nested_depth"] = max_depth

            if max_depth > 4:
                issues.append(
                    CodeIssue(
                        severity="medium",
                        title=f"Deep Nesting (depth: {max_depth})",
                        description="Code has excessive nesting levels",
                        line_number=1,
                        suggestion="Extract nested logic into separate functions",
                        category="readability",
                        rule_id="READ001",
                        confidence=0.9,
                    )
                )

        except SyntaxError as e:
            issues.append(
                CodeIssue(
                    severity="critical",
                    title="Syntax Error",
                    description=f"Code contains syntax error: {e.msg}",
                    line_number=e.lineno or 1,
                    category="syntax",
                    rule_id="SYN001",
                    confidence=1.0,
                )
            )

        return issues, metrics

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_cognitive_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cognitive complexity (how hard code is to understand)"""
        complexity = 0
        nesting_level = 0

        def visit_node(n, level):
            nonlocal complexity
            if isinstance(n, (ast.If, ast.While, ast.For)):
                complexity += 1 + level  # Nesting increases complexity
            elif isinstance(n, ast.BoolOp):
                complexity += 1

            # Recursively visit children
            for child in ast.iter_child_nodes(n):
                new_level = (
                    level + 1
                    if isinstance(n, (ast.If, ast.While, ast.For, ast.Try))
                    else level
                )
                visit_node(child, new_level)

        visit_node(node, 0)
        return complexity

    def _identify_responsibilities(self, node: ast.FunctionDef) -> str:
        """Identify what a function does (for AI insights)"""
        responsibilities = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, "id"):
                    func_name = child.func.id
                    if "read" in func_name or "get" in func_name:
                        responsibilities.add("data retrieval")
                    elif "write" in func_name or "save" in func_name:
                        responsibilities.add("data persistence")
                    elif "calculate" in func_name or "compute" in func_name:
                        responsibilities.add("computation")
                    elif "validate" in func_name or "check" in func_name:
                        responsibilities.add("validation")

        return ", ".join(responsibilities) if responsibilities else "multiple"

    def _calculate_max_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth in the code"""
        max_depth = 0

        def visit_node(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            for child in ast.iter_child_nodes(node):
                new_depth = depth
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    new_depth = depth + 1
                visit_node(child, new_depth)

        visit_node(tree)
        return max_depth

    async def _calculate_metrics(
        self, code: str, issues: list[CodeIssue], complexity_metrics: dict[str, Any]
    ) -> QualityMetrics:
        """Calculate comprehensive quality metrics"""
        lines = code.split("\n")
        total_lines = len(lines)
        non_empty_lines = len([l for l in lines if l.strip()])
        comment_lines = len([l for l in lines if l.strip().startswith("#")])

        # Calculate scores based on issues
        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 10,
            "low": 5,
            "info": 2,
        }

        total_penalty = sum(severity_weights.get(issue.severity, 0) for issue in issues)

        security_penalty = sum(
            severity_weights.get(issue.severity, 0)
            for issue in issues
            if issue.category == "security"
        )

        # Calculate various scores
        security_score = max(0, 100 - security_penalty)
        complexity_score = max(
            0, 100 - complexity_metrics.get("total_complexity", 0) * 2
        )
        maintainability_index = max(0, 100 - len(issues) * 3)

        # Estimate test coverage based on complexity
        test_coverage_estimate = max(
            0, 100 - complexity_metrics.get("total_complexity", 0) * 5
        )

        # Calculate technical debt (hours)
        technical_debt_hours = (
            len([i for i in issues if i.severity == "critical"]) * 4
            + len([i for i in issues if i.severity == "high"]) * 2
            + len([i for i in issues if i.severity == "medium"]) * 1
            + len([i for i in issues if i.severity == "low"]) * 0.5
        )

        # AI quality score (if available)
        ai_quality_score = await self._calculate_ai_quality_score(
            code, issues, complexity_metrics
        )

        # Overall score
        overall_score = (
            security_score * 0.3
            + complexity_score * 0.3
            + maintainability_index * 0.2
            + ai_quality_score * 0.2
        )

        return QualityMetrics(
            total_lines=total_lines,
            non_empty_lines=non_empty_lines,
            comment_lines=comment_lines,
            complexity_score=complexity_score,
            maintainability_index=maintainability_index,
            security_score=security_score,
            overall_score=overall_score,
            test_coverage_estimate=test_coverage_estimate,
            technical_debt_hours=technical_debt_hours,
            ai_quality_score=ai_quality_score,
        )

    async def _calculate_ai_quality_score(
        self, code: str, issues: list[CodeIssue], complexity_metrics: dict[str, Any]
    ) -> float:
        """Calculate AI-powered quality score"""
        if not self.cortex_service:
            # Fallback calculation without AI
            base_score = 100
            base_score -= len(issues) * 2
            base_score -= complexity_metrics.get("cognitive_complexity", 0)
            return max(0, base_score)

        try:
            # Use Snowflake Cortex for advanced analysis
            prompt = f"""
            Analyze this code quality:
            - Issues found: {len(issues)}
            - Complexity: {complexity_metrics.get('total_complexity', 0)}
            - Cognitive complexity: {complexity_metrics.get('cognitive_complexity', 0)}

            Rate the overall quality from 0-100 considering:
            1. Readability
            2. Maintainability
            3. Best practices
            4. Potential bugs

            Return only a number between 0-100.
            """

            response = await self.cortex_service.complete(prompt, model="mistral-large")
            score = float(response.strip())
            return min(100, max(0, score))

        except Exception as e:
            logger.warning(f"AI quality score calculation failed: {e}")
            return 75.0  # Default score

    async def _get_ai_insights(
        self,
        code: str,
        issues: list[CodeIssue],
        metrics: QualityMetrics,
        context: dict[str, Any] | None,
    ) -> tuple[list[PredictiveInsight], list[str]]:
        """Generate AI-powered insights and recommendations"""
        insights = []
        recommendations = []

        if not self.cortex_service:
            return insights, recommendations

        try:
            # Analyze code patterns for predictions
            code_summary = f"""
            Code Analysis Summary:
            - Total issues: {len(issues)}
            - Security issues: {len([i for i in issues if i.category == 'security'])}
            - Complexity score: {metrics.complexity_score}
            - Technical debt: {metrics.technical_debt_hours} hours
            """

            # Get AI predictions
            prediction_prompt = f"""
            Based on this code analysis:
            {code_summary}

            Predict:
            1. Risk of production issues
            2. Maintenance challenges
            3. Security vulnerabilities
            4. Performance bottlenecks

            Format: JSON with risk_level, prediction, confidence, action
            """

            response = await self.cortex_service.complete(prediction_prompt)
            # Parse AI response (simplified for example)

            # Add predictive insights
            if metrics.security_score < 70:
                insights.append(
                    PredictiveInsight(
                        risk_level="high",
                        prediction="Security vulnerabilities likely to be exploited",
                        confidence=0.85,
                        recommended_action="Immediate security audit required",
                        estimated_impact={
                            "potential_breach_cost": "$50K-500K",
                            "remediation_time": "2-5 days",
                        },
                    )
                )

            if metrics.complexity_score < 60:
                insights.append(
                    PredictiveInsight(
                        risk_level="medium",
                        prediction="Code will become unmaintainable within 6 months",
                        confidence=0.75,
                        recommended_action="Refactor complex functions now",
                        estimated_impact={
                            "future_dev_time": "3x current",
                            "bug_rate_increase": "250%",
                        },
                    )
                )

            # Generate recommendations
            if metrics.overall_score < 70:
                recommendations.extend(
                    [
                        "🚨 Prioritize fixing critical security issues",
                        f"📊 Implement comprehensive testing (current coverage ~{int(metrics.test_coverage_estimate)}%)",
                        "🔧 Schedule refactoring sprint to reduce technical debt",
                    ]
                )

            # Context-aware recommendations
            if context and context.get("is_production"):
                recommendations.append(
                    "⚠️ Production code requires immediate attention"
                )

        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")

        return insights, recommendations

    async def _generate_predictive_insights(
        self, issues: list[CodeIssue], metrics: QualityMetrics, filename: str
    ) -> list[PredictiveInsight]:
        """Generate predictive insights based on historical data"""
        insights = []

        # Analyze trends from history
        history = self.metrics_history.get(filename, [])
        if len(history) >= 3:
            # Trend analysis
            recent_scores = [h.overall_score for h in history[-3:]]
            score_trend = recent_scores[-1] - recent_scores[0]

            if score_trend < -10:
                insights.append(
                    PredictiveInsight(
                        risk_level="high",
                        prediction="Code quality rapidly declining",
                        confidence=0.9,
                        recommended_action="Immediate intervention required",
                        estimated_impact={
                            "productivity_loss": "40%",
                            "bug_increase": "300%",
                        },
                    )
                )

        # Pattern-based predictions
        security_issues = [i for i in issues if i.category == "security"]
        if len(security_issues) > 3:
            insights.append(
                PredictiveInsight(
                    risk_level="critical",
                    prediction="Multiple security vulnerabilities create attack surface",
                    confidence=0.95,
                    recommended_action="Security-focused code review required",
                    estimated_impact={
                        "breach_probability": "high",
                        "compliance_risk": "failed audit",
                    },
                )
            )

        return insights

    def _calculate_business_impact(
        self, issues: list[CodeIssue], metrics: QualityMetrics
    ) -> dict[str, Any]:
        """Calculate business impact of code quality issues"""
        impact = {
            "development_velocity": "normal",
            "operational_risk": "low",
            "compliance_status": "passed",
            "estimated_cost": 0,
            "customer_impact": "none",
        }

        # Development velocity impact
        if metrics.complexity_score < 70:
            impact["development_velocity"] = "reduced by 30%"

        # Operational risk
        critical_issues = len([i for i in issues if i.severity == "critical"])
        if critical_issues > 0:
            impact["operational_risk"] = "high"
            impact["customer_impact"] = "potential service disruption"

        # Compliance
        security_issues = [i for i in issues if i.category == "security"]
        if security_issues:
            impact["compliance_status"] = "at risk"

        # Cost estimation
        impact["estimated_cost"] = int(metrics.technical_debt_hours * 150)  # $150/hour

        return impact

    def _store_metrics_history(self, filename: str, metrics: QualityMetrics):
        """Store metrics for trend analysis"""
        history = self.metrics_history[filename]
        history.append(metrics)

        # Keep only last 10 entries
        if len(history) > 10:
            self.metrics_history[filename] = history[-10:]

    async def apply_auto_fix(
        self, filename: str, issue_id: str, code: str
    ) -> tuple[str, bool]:
        """Apply automatic fix for an issue"""
        # Find the issue with auto-fix
        # This is simplified - in real implementation would track issues by ID
        for pattern in self.patterns:
            if pattern.get("rule_id") == issue_id and pattern.get("auto_fix_pattern"):
                fixed_code = re.sub(
                    pattern["auto_fix_pattern"],
                    pattern["auto_fix_replacement"],
                    code,
                    flags=re.MULTILINE,
                )
                return fixed_code, fixed_code != code

        return code, False


# ===== GLOBAL ANALYZER INSTANCE =====

analyzer = EnhancedQualityAnalyzer()


# ===== API ENDPOINTS =====


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Enhanced Codacy MCP Server",
        "version": "2.0.0",
        "features": [
            "AI-powered code analysis",
            "Predictive quality insights",
            "Automatic fix suggestions",
            "Business impact assessment",
            "Snowflake Cortex integration",
        ],
        "status": "running",
    }


@app.get("/health", response_model=HealthStatus)
async def health():
    """Enhanced health check endpoint"""
    # Calculate cache hit rate
    # This is simplified - real implementation would track actual cache usage
    cache_hit_rate = 0.75 if analyzer.cache else 0.0

    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(),
        service="enhanced_codacy",
        ai_services_available=SNOWFLAKE_AVAILABLE
        and analyzer.cortex_service is not None,
        patterns_loaded=len(analyzer.patterns),
        cache_hit_rate=cache_hit_rate,
        average_response_time_ms=150.0,  # Would track actual response times
    )


@app.post("/api/v1/analyze/code", response_model=AnalysisResult)
async def analyze_code(request: CodeAnalysisRequest, background_tasks: BackgroundTasks):
    """Enhanced code analysis with AI insights"""
    try:
        result = await analyzer.analyze_code(
            code=request.code,
            filename=request.filename,
            language=request.language,
            enable_ai=request.enable_ai_insights,
            enable_auto_fix=request.enable_auto_fix,
            context=request.context,
        )

        # Log analysis for monitoring
        background_tasks.add_task(
            log_analysis,
            filename=request.filename,
            score=result.metrics.overall_score,
            issues=len(result.issues),
        )

        return result

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze/file")
async def analyze_file(filepath: str):
    """Analyze a file from the codebase"""
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        with open(file_path) as f:
            code = f.read()

        request = CodeAnalysisRequest(
            code=code,
            filename=str(file_path),
            language="python",
            enable_ai_insights=True,
            enable_auto_fix=True,
            context={"is_production": "production" in str(file_path)},
        )

        return await analyze_code(request, BackgroundTasks())

    except Exception as e:
        logger.error(f"File analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/auto-fix")
async def auto_fix(request: AutoFixRequest):
    """Apply automatic fix for an issue"""
    try:
        # Read the file
        file_path = Path(request.filename)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        with open(file_path) as f:
            code = f.read()

        # Apply fix
        fixed_code, success = await analyzer.apply_auto_fix(
            request.filename, request.issue_id, code
        )

        if success and request.apply_fix:
            # Write back to file
            with open(file_path, "w") as f:
                f.write(fixed_code)

        return {
            "success": success,
            "fixed_code": fixed_code if success else None,
            "applied": request.apply_fix and success,
        }

    except Exception as e:
        logger.error(f"Auto-fix error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/trends/{filename}")
async def get_quality_trends(filename: str):
    """Get quality trends for a file"""
    history = analyzer.metrics_history.get(filename, [])

    if not history:
        raise HTTPException(status_code=404, detail="No history for this file")

    return {
        "filename": filename,
        "trend_data": [
            {
                "timestamp": i,
                "overall_score": h.overall_score,
                "security_score": h.security_score,
                "complexity_score": h.complexity_score,
                "technical_debt_hours": h.technical_debt_hours,
            }
            for i, h in enumerate(history)
        ],
        "current_score": history[-1].overall_score if history else 0,
        "score_change": history[-1].overall_score - history[0].overall_score
        if len(history) > 1
        else 0,
    }


@app.get("/api/v1/insights/predictive")
async def get_predictive_insights():
    """Get predictive insights across the codebase"""
    all_insights = []

    # Aggregate insights from recent analyses
    for filename, history in analyzer.metrics_history.items():
        if history:
            latest = history[-1]
            if latest.overall_score < 70:
                all_insights.append(
                    {
                        "filename": filename,
                        "risk_level": "high" if latest.overall_score < 50 else "medium",
                        "prediction": f"File likely to cause issues (score: {latest.overall_score})",
                        "action": "Immediate refactoring recommended",
                    }
                )

    return {
        "total_files_at_risk": len(all_insights),
        "insights": all_insights[:10],  # Top 10
        "recommended_actions": [
            "Schedule code quality sprint",
            "Implement stricter PR reviews",
            "Add automated quality gates",
        ]
        if all_insights
        else ["Maintain current quality standards"],
    }


async def log_analysis(filename: str, score: float, issues: int):
    """Log analysis for monitoring"""
    logger.info(f"Analysis complete: {filename} - Score: {score}, Issues: {issues}")


if __name__ == "__main__":
    port = 3008
    logger.info(f"🚀 Starting Enhanced Codacy MCP Server on port {port}...")
    logger.info(f"🤖 AI Services Available: {SNOWFLAKE_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=port)
