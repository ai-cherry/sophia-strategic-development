#!/usr/bin/env python3
"""
AI Memory MCP Server Code Quality Analyzer
Comprehensive analysis tool for code quality, performance, and best practices
"""

import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import radon.complexity as radon_cc
import radon.metrics as radon_metrics
from radon.raw import analyze


@dataclass
class CodeQualityMetrics:
    """Comprehensive code quality metrics"""
    
    # File-level metrics
    file_path: str
    lines_of_code: int = 0
    logical_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    
    # Complexity metrics
    cyclomatic_complexity: float = 0.0
    cognitive_complexity: float = 0.0
    halstead_difficulty: float = 0.0
    maintainability_index: float = 0.0
    
    # Quality indicators
    docstring_coverage: float = 0.0
    type_hint_coverage: float = 0.0
    test_coverage: float = 0.0
    
    # Issues and violations
    syntax_errors: List[str] = field(default_factory=list)
    style_violations: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    performance_issues: List[str] = field(default_factory=list)
    
    # Dependencies and imports
    import_count: int = 0
    external_dependencies: Set[str] = field(default_factory=set)
    circular_imports: List[str] = field(default_factory=list)
    
    # Architecture metrics
    class_count: int = 0
    function_count: int = 0
    method_count: int = 0
    async_function_count: int = 0


@dataclass
class ArchitectureAnalysis:
    """Architecture and design pattern analysis"""
    
    design_patterns: List[str] = field(default_factory=list)
    solid_violations: List[str] = field(default_factory=list)
    coupling_score: float = 0.0
    cohesion_score: float = 0.0
    abstraction_level: str = "unknown"
    
    # MCP-specific analysis
    mcp_compliance: bool = False
    mcp_patterns: List[str] = field(default_factory=list)
    mcp_violations: List[str] = field(default_factory=list)


@dataclass
class PerformanceAnalysis:
    """Performance and optimization analysis"""
    
    async_usage: Dict[str, int] = field(default_factory=dict)
    database_queries: List[str] = field(default_factory=list)
    memory_usage_patterns: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    
    # AI/ML specific
    embedding_operations: List[str] = field(default_factory=list)
    vector_operations: List[str] = field(default_factory=list)
    model_loading_patterns: List[str] = field(default_factory=list)


class AIMemoryCodeAnalyzer:
    """Comprehensive code analyzer for AI Memory MCP server"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.ai_memory_files = []
        self.analysis_results = {}
        
        # AI Memory specific patterns
        self.ai_memory_patterns = {
            'memory_operations': [
                r'store_memory', r'retrieve_memory', r'search_memory',
                r'update_memory', r'delete_memory'
            ],
            'embedding_operations': [
                r'generate_embedding', r'cosine_similarity', r'vector_search',
                r'embedding_model', r'text_embedding'
            ],
            'mcp_patterns': [
                r'@mcp\.tool', r'mcp\.server', r'Tool\(', r'TextContent',
                r'server\.list_tools', r'server\.call_tool'
            ],
            'async_patterns': [
                r'async def', r'await ', r'asyncio\.'
            ],
            'database_patterns': [
                r'SELECT', r'INSERT', r'UPDATE', r'DELETE',
                r'snowflake', r'redis', r'pinecone', r'weaviate'
            ]
        }
    
    def discover_ai_memory_files(self) -> List[Path]:
        """Discover all AI Memory related files"""
        ai_memory_files = []
        
        # Search patterns for AI Memory files
        search_patterns = [
            "**/ai_memory/**/*.py",
            "**/ai-memory/**/*.py", 
            "**/*ai_memory*.py",
            "**/enhanced_ai_memory*.py",
            "**/optimized_ai_memory*.py"
        ]
        
        for pattern in search_patterns:
            files = list(self.base_path.glob(pattern))
            ai_memory_files.extend(files)
        
        # Remove duplicates and sort
        self.ai_memory_files = sorted(list(set(ai_memory_files)))
        return self.ai_memory_files
    
    def analyze_file(self, file_path: Path) -> CodeQualityMetrics:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Initialize metrics
            metrics = CodeQualityMetrics(file_path=str(file_path))
            
            # Basic metrics using radon
            raw_metrics = analyze(content)
            metrics.lines_of_code = raw_metrics.loc
            metrics.logical_lines = raw_metrics.lloc
            metrics.comment_lines = raw_metrics.comments
            metrics.blank_lines = raw_metrics.blank
            
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, metrics)
            except SyntaxError as e:
                metrics.syntax_errors.append(f"Syntax error: {e}")
            
            # Complexity analysis
            self._analyze_complexity(content, metrics)
            
            # Pattern analysis
            self._analyze_patterns(content, metrics)
            
            # Import analysis
            self._analyze_imports(content, metrics)
            
            return metrics
            
        except Exception as e:
            metrics = CodeQualityMetrics(file_path=str(file_path))
            metrics.syntax_errors.append(f"Analysis error: {e}")
            return metrics
    
    def _analyze_ast(self, tree: ast.AST, metrics: CodeQualityMetrics):
        """Analyze AST for detailed code metrics"""
        
        class CodeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.classes = 0
                self.functions = 0
                self.methods = 0
                self.async_functions = 0
                self.docstrings = 0
                self.type_hints = 0
                self.total_functions = 0
            
            def visit_ClassDef(self, node):
                self.classes += 1
                if ast.get_docstring(node):
                    self.docstrings += 1
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                self.functions += 1
                self.total_functions += 1
                if ast.get_docstring(node):
                    self.docstrings += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    self.type_hints += 1
                self.generic_visit(node)
            
            def visit_AsyncFunctionDef(self, node):
                self.async_functions += 1
                self.total_functions += 1
                if ast.get_docstring(node):
                    self.docstrings += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    self.type_hints += 1
                self.generic_visit(node)
            
            def visit_MethodDef(self, node):
                self.methods += 1
                self.generic_visit(node)
        
        visitor = CodeVisitor()
        visitor.visit(tree)
        
        metrics.class_count = visitor.classes
        metrics.function_count = visitor.functions
        metrics.method_count = visitor.methods
        metrics.async_function_count = visitor.async_functions
        
        # Calculate coverage percentages
        if visitor.total_functions > 0:
            metrics.docstring_coverage = (visitor.docstrings / visitor.total_functions) * 100
            metrics.type_hint_coverage = (visitor.type_hints / visitor.total_functions) * 100
    
    def _analyze_complexity(self, content: str, metrics: CodeQualityMetrics):
        """Analyze code complexity"""
        try:
            # Cyclomatic complexity
            cc_results = radon_cc.cc_visit(content)
            if cc_results:
                total_complexity = sum(item.complexity for item in cc_results)
                metrics.cyclomatic_complexity = total_complexity / len(cc_results) if cc_results else 0
            
            # Maintainability index
            mi_results = radon_metrics.mi_visit(content, multi=True)
            if mi_results:
                metrics.maintainability_index = mi_results
                
        except Exception as e:
            metrics.performance_issues.append(f"Complexity analysis error: {e}")
    
    def _analyze_patterns(self, content: str, metrics: CodeQualityMetrics):
        """Analyze AI Memory specific patterns"""
        
        # Check for AI Memory patterns
        for pattern_type, patterns in self.ai_memory_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    if pattern_type not in metrics.external_dependencies:
                        metrics.external_dependencies.add(pattern_type)
        
        # Performance pattern analysis
        performance_issues = []
        
        # Check for synchronous operations in async context
        if re.search(r'async def.*\n.*(?!await)', content):
            performance_issues.append("Potential blocking operations in async functions")
        
        # Check for inefficient database queries
        if re.search(r'SELECT \*', content, re.IGNORECASE):
            performance_issues.append("SELECT * queries found - consider specific column selection")
        
        # Check for memory leaks in vector operations
        if re.search(r'\.vector.*(?!del)', content):
            performance_issues.append("Vector operations without explicit cleanup")
        
        metrics.performance_issues.extend(performance_issues)
    
    def _analyze_imports(self, content: str, metrics: CodeQualityMetrics):
        """Analyze import patterns and dependencies"""
        import_lines = re.findall(r'^(?:from|import)\s+([^\s]+)', content, re.MULTILINE)
        metrics.import_count = len(import_lines)
        
        # Identify external dependencies
        external_deps = set()
        for imp in import_lines:
            if not imp.startswith('.') and not imp in ['os', 'sys', 'json', 'datetime', 'typing']:
                external_deps.add(imp.split('.')[0])
        
        metrics.external_dependencies.update(external_deps)
    
    def analyze_architecture(self, files: List[Path]) -> ArchitectureAnalysis:
        """Analyze overall architecture and design patterns"""
        arch_analysis = ArchitectureAnalysis()
        
        # Analyze MCP compliance
        mcp_files = [f for f in files if 'mcp' in str(f).lower()]
        if mcp_files:
            arch_analysis.mcp_compliance = True
            arch_analysis.mcp_patterns.append("MCP server structure detected")
        
        # Check for design patterns
        all_content = ""
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_content += f.read() + "\n"
            except:
                continue
        
        # Detect design patterns
        patterns = []
        if re.search(r'class.*Handler', all_content):
            patterns.append("Handler Pattern")
        if re.search(r'class.*Service', all_content):
            patterns.append("Service Pattern")
        if re.search(r'class.*Repository', all_content):
            patterns.append("Repository Pattern")
        if re.search(r'@dataclass', all_content):
            patterns.append("Data Class Pattern")
        if re.search(r'async def.*await', all_content):
            patterns.append("Async/Await Pattern")
        
        arch_analysis.design_patterns = patterns
        
        return arch_analysis
    
    def analyze_performance(self, files: List[Path]) -> PerformanceAnalysis:
        """Analyze performance characteristics"""
        perf_analysis = PerformanceAnalysis()
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Async usage analysis
                async_funcs = len(re.findall(r'async def', content))
                await_calls = len(re.findall(r'await ', content))
                perf_analysis.async_usage[str(file_path)] = {
                    'async_functions': async_funcs,
                    'await_calls': await_calls
                }
                
                # Database query analysis
                db_queries = re.findall(r'(SELECT|INSERT|UPDATE|DELETE).*', content, re.IGNORECASE)
                perf_analysis.database_queries.extend(db_queries)
                
                # Embedding operations
                embedding_ops = re.findall(r'(embedding|vector|similarity).*', content, re.IGNORECASE)
                perf_analysis.embedding_operations.extend(embedding_ops)
                
            except:
                continue
        
        # Optimization opportunities
        opportunities = []
        if len(perf_analysis.database_queries) > 10:
            opportunities.append("Consider query optimization and caching")
        if sum(usage.get('async_functions', 0) for usage in perf_analysis.async_usage.values()) < 5:
            opportunities.append("Consider more async operations for I/O bound tasks")
        
        perf_analysis.optimization_opportunities = opportunities
        
        return perf_analysis
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        # Discover files
        files = self.discover_ai_memory_files()
        
        # Analyze each file
        file_analyses = {}
        for file_path in files:
            file_analyses[str(file_path)] = self.analyze_file(file_path)
        
        # Overall architecture analysis
        arch_analysis = self.analyze_architecture(files)
        
        # Performance analysis
        perf_analysis = self.analyze_performance(files)
        
        # Calculate overall metrics
        total_loc = sum(metrics.lines_of_code for metrics in file_analyses.values())
        avg_complexity = sum(metrics.cyclomatic_complexity for metrics in file_analyses.values()) / len(file_analyses) if file_analyses else 0
        total_issues = sum(len(metrics.syntax_errors) + len(metrics.style_violations) + len(metrics.security_issues) + len(metrics.performance_issues) for metrics in file_analyses.values())
        
        # Generate recommendations
        recommendations = self._generate_recommendations(file_analyses, arch_analysis, perf_analysis)
        
        return {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "files_analyzed": len(files),
                "analyzer_version": "1.0.0"
            },
            "summary": {
                "total_lines_of_code": total_loc,
                "average_complexity": round(avg_complexity, 2),
                "total_issues": total_issues,
                "overall_quality_score": self._calculate_quality_score(file_analyses)
            },
            "file_analyses": {str(k): self._serialize_metrics(v) for k, v in file_analyses.items()},
            "architecture_analysis": self._serialize_architecture(arch_analysis),
            "performance_analysis": self._serialize_performance(perf_analysis),
            "recommendations": recommendations
        }
    
    def _serialize_metrics(self, metrics: CodeQualityMetrics) -> Dict[str, Any]:
        """Serialize metrics to JSON-compatible format"""
        return {
            "file_path": metrics.file_path,
            "lines_of_code": metrics.lines_of_code,
            "logical_lines": metrics.logical_lines,
            "comment_lines": metrics.comment_lines,
            "blank_lines": metrics.blank_lines,
            "cyclomatic_complexity": metrics.cyclomatic_complexity,
            "cognitive_complexity": metrics.cognitive_complexity,
            "maintainability_index": metrics.maintainability_index,
            "docstring_coverage": metrics.docstring_coverage,
            "type_hint_coverage": metrics.type_hint_coverage,
            "syntax_errors": metrics.syntax_errors,
            "style_violations": metrics.style_violations,
            "security_issues": metrics.security_issues,
            "performance_issues": metrics.performance_issues,
            "import_count": metrics.import_count,
            "external_dependencies": list(metrics.external_dependencies),
            "class_count": metrics.class_count,
            "function_count": metrics.function_count,
            "method_count": metrics.method_count,
            "async_function_count": metrics.async_function_count
        }
    
    def _serialize_architecture(self, arch: ArchitectureAnalysis) -> Dict[str, Any]:
        """Serialize architecture analysis"""
        return {
            "design_patterns": arch.design_patterns,
            "solid_violations": arch.solid_violations,
            "coupling_score": arch.coupling_score,
            "cohesion_score": arch.cohesion_score,
            "abstraction_level": arch.abstraction_level,
            "mcp_compliance": arch.mcp_compliance,
            "mcp_patterns": arch.mcp_patterns,
            "mcp_violations": arch.mcp_violations
        }
    
    def _serialize_performance(self, perf: PerformanceAnalysis) -> Dict[str, Any]:
        """Serialize performance analysis"""
        return {
            "async_usage": perf.async_usage,
            "database_queries": perf.database_queries[:10],  # Limit for readability
            "memory_usage_patterns": perf.memory_usage_patterns,
            "optimization_opportunities": perf.optimization_opportunities,
            "embedding_operations": perf.embedding_operations[:10],
            "vector_operations": perf.vector_operations,
            "model_loading_patterns": perf.model_loading_patterns
        }
    
    def _calculate_quality_score(self, file_analyses: Dict[str, CodeQualityMetrics]) -> float:
        """Calculate overall quality score (0-100)"""
        if not file_analyses:
            return 0.0
        
        scores = []
        for metrics in file_analyses.values():
            # Base score
            score = 100.0
            
            # Deduct for issues
            score -= len(metrics.syntax_errors) * 20
            score -= len(metrics.style_violations) * 5
            score -= len(metrics.security_issues) * 15
            score -= len(metrics.performance_issues) * 10
            
            # Deduct for complexity
            if metrics.cyclomatic_complexity > 10:
                score -= (metrics.cyclomatic_complexity - 10) * 2
            
            # Add for good practices
            score += metrics.docstring_coverage * 0.1
            score += metrics.type_hint_coverage * 0.1
            
            scores.append(max(0, min(100, score)))
        
        return round(sum(scores) / len(scores), 2)
    
    def _generate_recommendations(self, file_analyses: Dict[str, CodeQualityMetrics], 
                                arch_analysis: ArchitectureAnalysis, 
                                perf_analysis: PerformanceAnalysis) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Code quality recommendations
        total_issues = sum(len(metrics.syntax_errors) + len(metrics.style_violations) + 
                          len(metrics.security_issues) + len(metrics.performance_issues) 
                          for metrics in file_analyses.values())
        
        if total_issues > 10:
            recommendations.append("HIGH PRIORITY: Address critical code quality issues (syntax errors, security vulnerabilities)")
        
        # Documentation recommendations
        avg_docstring_coverage = sum(metrics.docstring_coverage for metrics in file_analyses.values()) / len(file_analyses) if file_analyses else 0
        if avg_docstring_coverage < 70:
            recommendations.append("MEDIUM PRIORITY: Improve documentation coverage (currently {:.1f}%)".format(avg_docstring_coverage))
        
        # Type hint recommendations
        avg_type_coverage = sum(metrics.type_hint_coverage for metrics in file_analyses.values()) / len(file_analyses) if file_analyses else 0
        if avg_type_coverage < 80:
            recommendations.append("MEDIUM PRIORITY: Add type hints for better code maintainability (currently {:.1f}%)".format(avg_type_coverage))
        
        # Architecture recommendations
        if not arch_analysis.mcp_compliance:
            recommendations.append("HIGH PRIORITY: Ensure MCP protocol compliance for proper integration")
        
        # Performance recommendations
        recommendations.extend(perf_analysis.optimization_opportunities)
        
        # AI Memory specific recommendations
        recommendations.extend([
            "Consider implementing memory caching for frequently accessed embeddings",
            "Optimize vector similarity calculations with batch processing",
            "Implement proper error handling for external AI service calls",
            "Add comprehensive logging for memory operations debugging",
            "Consider implementing memory cleanup routines for long-running processes"
        ])
        
        return recommendations


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Memory MCP Server Code Quality Analyzer")
    parser.add_argument("--path", type=str, default=".", help="Base path to analyze")
    parser.add_argument("--output", type=str, default="ai_memory_analysis_report.json", help="Output report file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = AIMemoryCodeAnalyzer(Path(args.path))
    
    if args.verbose:
        print("🔍 Starting AI Memory MCP Server code quality analysis...")
        print(f"📁 Base path: {args.path}")
    
    # Generate comprehensive report
    report = analyzer.generate_comprehensive_report()
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("🎯 AI MEMORY MCP SERVER ANALYSIS SUMMARY")
    print("="*60)
    print(f"📊 Files analyzed: {report['analysis_metadata']['files_analyzed']}")
    print(f"📏 Total lines of code: {report['summary']['total_lines_of_code']:,}")
    print(f"🔄 Average complexity: {report['summary']['average_complexity']}")
    print(f"⚠️  Total issues: {report['summary']['total_issues']}")
    print(f"🏆 Overall quality score: {report['summary']['overall_quality_score']}/100")
    
    print(f"\n📋 Top recommendations:")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n📄 Full report saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

