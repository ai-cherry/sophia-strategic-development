#!/usr/bin/env python3
"""
Performance Analysis Script for Sophia AI Codebase
Analyzes resource utilization, bottlenecks, and optimization opportunities
"""

import os
import ast
import time
import psutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

class PerformanceAnalyzer:
    def __init__(self, codebase_path: str = "/home/ubuntu/sophia-main"):
        self.codebase_path = Path(codebase_path)
        self.analysis_results = {}
        
    def analyze_file_complexity(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual file complexity and potential bottlenecks"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Count different types of nodes
            complexity_metrics = {
                'lines_of_code': len(content.splitlines()),
                'functions': 0,
                'classes': 0,
                'loops': 0,
                'nested_loops': 0,
                'database_calls': 0,
                'async_functions': 0,
                'imports': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity_metrics['functions'] += 1
                    if any(isinstance(decorator, ast.Name) and decorator.id == 'async' 
                          for decorator in getattr(node, 'decorator_list', [])):
                        complexity_metrics['async_functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    complexity_metrics['classes'] += 1
                elif isinstance(node, (ast.For, ast.While)):
                    complexity_metrics['loops'] += 1
                elif isinstance(node, ast.Import):
                    complexity_metrics['imports'] += len(node.names)
                elif isinstance(node, ast.ImportFrom):
                    complexity_metrics['imports'] += len(node.names) if node.names else 1
            
            # Check for database-related patterns
            if 'execute_query' in content or 'SELECT' in content or 'INSERT' in content:
                complexity_metrics['database_calls'] = content.count('execute_query') + content.count('SELECT') + content.count('INSERT')
            
            return complexity_metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_codebase_structure(self) -> Dict[str, Any]:
        """Analyze overall codebase structure and identify hotspots"""
        backend_path = self.codebase_path / "backend"
        
        file_analysis = {}
        total_metrics = defaultdict(int)
        
        for py_file in backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            relative_path = py_file.relative_to(self.codebase_path)
            metrics = self.analyze_file_complexity(py_file)
            
            if 'error' not in metrics:
                file_analysis[str(relative_path)] = metrics
                for key, value in metrics.items():
                    total_metrics[key] += value
        
        # Calculate complexity scores
        complexity_scores = {}
        for file_path, metrics in file_analysis.items():
            if 'error' not in metrics:
                score = (
                    metrics['lines_of_code'] * 0.1 +
                    metrics['functions'] * 2 +
                    metrics['classes'] * 3 +
                    metrics['loops'] * 5 +
                    metrics['database_calls'] * 10
                )
                complexity_scores[file_path] = score
        
        # Find top complexity files
        top_complex_files = sorted(complexity_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_files': len(file_analysis),
            'total_metrics': dict(total_metrics),
            'top_complex_files': top_complex_files,
            'file_details': file_analysis
        }
    
    def analyze_resource_patterns(self) -> Dict[str, Any]:
        """Analyze resource usage patterns"""
        backend_path = self.codebase_path / "backend"
        
        patterns = {
            'connection_patterns': [],
            'cache_patterns': [],
            'async_patterns': [],
            'database_patterns': [],
            'memory_patterns': []
        }
        
        for py_file in backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                relative_path = py_file.relative_to(self.codebase_path)
                
                # Check for connection patterns
                if 'snowflake.connector.connect' in content:
                    patterns['connection_patterns'].append({
                        'file': str(relative_path),
                        'type': 'snowflake_connection',
                        'count': content.count('snowflake.connector.connect')
                    })
                
                # Check for cache patterns
                if 'cache' in content.lower():
                    patterns['cache_patterns'].append({
                        'file': str(relative_path),
                        'type': 'cache_usage',
                        'count': content.lower().count('cache')
                    })
                
                # Check for async patterns
                if 'async def' in content:
                    patterns['async_patterns'].append({
                        'file': str(relative_path),
                        'type': 'async_function',
                        'count': content.count('async def')
                    })
                
                # Check for database patterns
                db_operations = content.count('execute_query') + content.count('SELECT') + content.count('INSERT') + content.count('UPDATE')
                if db_operations > 0:
                    patterns['database_patterns'].append({
                        'file': str(relative_path),
                        'type': 'database_operations',
                        'count': db_operations
                    })
                
                # Check for memory patterns
                if 'global' in content or 'memory' in content.lower():
                    patterns['memory_patterns'].append({
                        'file': str(relative_path),
                        'type': 'memory_usage',
                        'global_count': content.count('global'),
                        'memory_count': content.lower().count('memory')
                    })
                
            except Exception as e:
                continue
        
        return patterns
    
    def generate_recommendations(self, structure_analysis: Dict, pattern_analysis: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Analyze top complex files
        if structure_analysis.get('top_complex_files'):
            top_file = structure_analysis['top_complex_files'][0]
            recommendations.append(f"🔴 HIGH PRIORITY: Refactor {top_file[0]} (complexity score: {top_file[1]:.1f})")
        
        # Analyze database patterns
        db_files = pattern_analysis.get('database_patterns', [])
        if db_files:
            high_db_files = [f for f in db_files if f['count'] > 10]
            if high_db_files:
                recommendations.append(f"🟡 MEDIUM PRIORITY: Optimize database access in {len(high_db_files)} files with >10 DB operations")
        
        # Analyze connection patterns
        conn_files = pattern_analysis.get('connection_patterns', [])
        if len(conn_files) > 5:
            recommendations.append(f"🟡 MEDIUM PRIORITY: Implement connection pooling - {len(conn_files)} files creating connections")
        
        # Analyze cache patterns
        cache_files = pattern_analysis.get('cache_patterns', [])
        if len(cache_files) < 5:
            recommendations.append("🟢 LOW PRIORITY: Increase caching usage - only found in few files")
        
        # Analyze async patterns
        async_files = pattern_analysis.get('async_patterns', [])
        total_files = structure_analysis.get('total_files', 0)
        async_ratio = len(async_files) / total_files if total_files > 0 else 0
        if async_ratio < 0.3:
            recommendations.append(f"🟡 MEDIUM PRIORITY: Increase async usage - only {async_ratio:.1%} of files use async")
        
        return recommendations

def main():
    analyzer = PerformanceAnalyzer()
    
    print("🔍 Starting Sophia AI Performance Analysis...")
    
    # Analyze codebase structure
    print("📊 Analyzing codebase structure...")
    structure_analysis = analyzer.analyze_codebase_structure()
    
    # Analyze resource patterns
    print("🔧 Analyzing resource patterns...")
    pattern_analysis = analyzer.analyze_resource_patterns()
    
    # Generate recommendations
    print("💡 Generating recommendations...")
    recommendations = analyzer.generate_recommendations(structure_analysis, pattern_analysis)
    
    # Print results
    print("\n" + "="*60)
    print("📈 SOPHIA AI PERFORMANCE ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📁 CODEBASE OVERVIEW:")
    print(f"   Total Python files: {structure_analysis['total_files']}")
    print(f"   Total lines of code: {structure_analysis['total_metrics']['lines_of_code']:,}")
    print(f"   Total functions: {structure_analysis['total_metrics']['functions']:,}")
    print(f"   Total classes: {structure_analysis['total_metrics']['classes']:,}")
    print(f"   Total database calls: {structure_analysis['total_metrics']['database_calls']:,}")
    
    print(f"\n🔥 TOP COMPLEX FILES:")
    for i, (file_path, score) in enumerate(structure_analysis['top_complex_files'][:5], 1):
        print(f"   {i}. {file_path} (score: {score:.1f})")
    
    print(f"\n🔧 RESOURCE USAGE PATTERNS:")
    print(f"   Files with database operations: {len(pattern_analysis['database_patterns'])}")
    print(f"   Files with connection patterns: {len(pattern_analysis['connection_patterns'])}")
    print(f"   Files with async patterns: {len(pattern_analysis['async_patterns'])}")
    print(f"   Files with cache usage: {len(pattern_analysis['cache_patterns'])}")
    
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"   {rec}")
    
    print("\n" + "="*60)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()
