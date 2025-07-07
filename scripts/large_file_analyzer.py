#!/usr/bin/env python3
"""
Large File Analysis & Refactoring Strategy Script
Analyzes Sophia AI codebase for files violating Single Responsibility Principle

Based on the comprehensive requirements for identifying and analyzing large files
that exceed 500 lines and create technical debt hotspots.
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess

@dataclass
class FileAnalysis:
    """Analysis results for a single file"""
    file_path: str
    line_count: int
    file_type: str
    size_bytes: int
    complexity_score: int
    srp_violations: List[str]
    problem_areas: List[str]
    recommendations: List[str]
    risk_impact_score: int
    priority: str  # 'Critical', 'High', 'Medium', 'Low'

class LargeFileAnalyzer:
    """Comprehensive large file analyzer for Sophia AI codebase"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.large_files: List[FileAnalysis] = []
        self.excluded_dirs = {'.git', '.venv', 'external', '__pycache__', 'node_modules', '.pytest_cache'}
        self.line_threshold = 500
        
    def scan_repository(self) -> List[FileAnalysis]:
        """Scan repository for large files exceeding threshold"""
        print("🔍 Scanning repository for large files...")
        
        for file_path in self._get_all_files():
            if self._should_analyze_file(file_path):
                line_count = self._count_lines(file_path)
                if line_count > self.line_threshold:
                    analysis = self._analyze_file(file_path, line_count)
                    self.large_files.append(analysis)
                    print(f"📄 Found large file: {file_path} ({line_count} lines)")
        
        # Sort by risk/impact score
        self.large_files.sort(key=lambda x: x.risk_impact_score, reverse=True)
        
        print(f"✅ Analysis complete: {len(self.large_files)} large files identified")
        return self.large_files
    
    def _get_all_files(self) -> List[Path]:
        """Get all files in repository excluding specified directories"""
        all_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)
        
        return all_files
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if file should be analyzed"""
        # Skip binary files and certain extensions
        skip_extensions = {'.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', '.bin', 
                          '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz'}
        
        if file_path.suffix.lower() in skip_extensions:
            return False
        
        # Only analyze text-based files
        analyze_extensions = {'.py', '.tsx', '.ts', '.js', '.jsx', '.json', '.yaml', 
                            '.yml', '.md', '.sql', '.sh', '.bash', '.txt', '.csv'}
        
        return file_path.suffix.lower() in analyze_extensions or file_path.suffix == ''
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def _analyze_file(self, file_path: Path, line_count: int) -> FileAnalysis:
        """Perform comprehensive analysis of a large file"""
        relative_path = str(file_path.relative_to(self.project_root))
        file_type = self._determine_file_type(file_path)
        size_bytes = file_path.stat().st_size
        
        # Perform type-specific analysis
        if file_type == 'Python':
            analysis_result = self._analyze_python_file(file_path)
        elif file_type == 'TypeScript/React':
            analysis_result = self._analyze_typescript_file(file_path)
        elif file_type == 'JSON':
            analysis_result = self._analyze_json_file(file_path)
        elif file_type == 'Markdown':
            analysis_result = self._analyze_markdown_file(file_path)
        elif file_type == 'SQL':
            analysis_result = self._analyze_sql_file(file_path)
        else:
            analysis_result = self._analyze_generic_file(file_path)
        
        complexity_score = analysis_result['complexity_score']
        srp_violations = analysis_result['srp_violations']
        problem_areas = analysis_result['problem_areas']
        recommendations = analysis_result['recommendations']
        
        # Calculate risk/impact score
        risk_impact_score = self._calculate_risk_score(
            line_count, complexity_score, len(srp_violations), file_type
        )
        
        # Determine priority
        priority = self._determine_priority(risk_impact_score)
        
        return FileAnalysis(
            file_path=relative_path,
            line_count=line_count,
            file_type=file_type,
            size_bytes=size_bytes,
            complexity_score=complexity_score,
            srp_violations=srp_violations,
            problem_areas=problem_areas,
            recommendations=recommendations,
            risk_impact_score=risk_impact_score,
            priority=priority
        )
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine the type of file for analysis"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.py':
            return 'Python'
        elif suffix in {'.tsx', '.ts'}:
            return 'TypeScript/React'
        elif suffix in {'.js', '.jsx'}:
            return 'JavaScript/React'
        elif suffix == '.json':
            return 'JSON'
        elif suffix in {'.yaml', '.yml'}:
            return 'YAML'
        elif suffix == '.md':
            return 'Markdown'
        elif suffix == '.sql':
            return 'SQL'
        elif suffix in {'.sh', '.bash'}:
            return 'Shell Script'
        else:
            return 'Generic Text'
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file for complexity and SRP violations"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            complexity_score = 0
            srp_violations = []
            problem_areas = []
            recommendations = []
            
            # Analyze classes
            for cls in classes:
                methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
                if len(methods) > 15:
                    complexity_score += 20
                    srp_violations.append(f"Class '{cls.name}' has {len(methods)} methods (God Object)")
                    problem_areas.append(f"Large class: {cls.name}")
                    recommendations.append(f"Split class '{cls.name}' into smaller, focused classes")
            
            # Analyze functions
            for func in functions:
                func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
                if func_lines > 50:
                    complexity_score += 10
                    srp_violations.append(f"Function '{func.name}' is {func_lines} lines long")
                    problem_areas.append(f"Long function: {func.name}")
                    recommendations.append(f"Break down function '{func.name}' into smaller functions")
            
            # Check for excessive imports
            if len(imports) > 30:
                complexity_score += 15
                problem_areas.append(f"Excessive imports: {len(imports)}")
                recommendations.append("Consider splitting file to reduce import dependencies")
            
            # Check for mixed responsibilities
            has_api_code = any('request' in content.lower() or 'response' in content.lower())
            has_db_code = any('query' in content.lower() or 'database' in content.lower())
            has_ui_code = any('render' in content.lower() or 'template' in content.lower())
            
            responsibility_count = sum([has_api_code, has_db_code, has_ui_code])
            if responsibility_count > 1:
                complexity_score += 25
                srp_violations.append("File mixes multiple responsibilities (API, DB, UI)")
                recommendations.append("Separate concerns into dedicated modules")
            
        except Exception as e:
            complexity_score = 50  # Default high complexity for unparseable files
            srp_violations = [f"File parsing error: {str(e)}"]
            problem_areas = ["Unparseable Python file"]
            recommendations = ["Review file syntax and structure"]
        
        return {
            'complexity_score': complexity_score,
            'srp_violations': srp_violations,
            'problem_areas': problem_areas,
            'recommendations': recommendations
        }
    
    def _analyze_typescript_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze TypeScript/React file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            complexity_score = 0
            srp_violations = []
            problem_areas = []
            recommendations = []
            
            # Count React components
            component_matches = re.findall(r'(?:function|const)\s+(\w+).*?(?:React\.FC|JSX\.Element|\(\s*\)\s*=>)', content)
            if len(component_matches) > 5:
                complexity_score += 20
                problem_areas.append(f"Multiple components in one file: {len(component_matches)}")
                recommendations.append("Split into separate component files")
            
            # Check for large components (by useState/useEffect count)
            use_state_count = len(re.findall(r'useState', content))
            use_effect_count = len(re.findall(r'useEffect', content))
            
            if use_state_count > 10:
                complexity_score += 15
                srp_violations.append(f"Component has {use_state_count} useState hooks")
                recommendations.append("Consider using useReducer or splitting component state")
            
            if use_effect_count > 8:
                complexity_score += 15
                srp_violations.append(f"Component has {use_effect_count} useEffect hooks")
                recommendations.append("Split component or extract custom hooks")
            
            # Check for inline styles or large style objects
            style_objects = re.findall(r'style\s*=\s*\{[^}]+\}', content)
            if len(style_objects) > 10:
                complexity_score += 10
                problem_areas.append("Excessive inline styles")
                recommendations.append("Extract styles to CSS modules or styled-components")
            
        except Exception:
            complexity_score = 30
            srp_violations = ["File analysis error"]
            problem_areas = ["Unparseable TypeScript file"]
            recommendations = ["Review file syntax"]
        
        return {
            'complexity_score': complexity_score,
            'srp_violations': srp_violations,
            'problem_areas': problem_areas,
            'recommendations': recommendations
        }
    
    def _analyze_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JSON configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            complexity_score = 0
            srp_violations = []
            problem_areas = []
            recommendations = []
            
            # Check nesting depth
            max_depth = self._get_json_depth(data)
            if max_depth > 6:
                complexity_score += 20
                problem_areas.append(f"Deep nesting: {max_depth} levels")
                recommendations.append("Flatten JSON structure or split into multiple files")
            
            # Check number of top-level keys
            if isinstance(data, dict):
                top_level_keys = len(data.keys())
                if top_level_keys > 20:
                    complexity_score += 15
                    problem_areas.append(f"Too many top-level keys: {top_level_keys}")
                    recommendations.append("Split into logical configuration files by feature/environment")
            
        except Exception:
            complexity_score = 25
            srp_violations = ["Invalid JSON structure"]
            problem_areas = ["Unparseable JSON"]
            recommendations = ["Fix JSON syntax errors"]
        
        return {
            'complexity_score': complexity_score,
            'srp_violations': srp_violations,
            'problem_areas': problem_areas,
            'recommendations': recommendations
        }
    
    def _analyze_markdown_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Markdown documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            complexity_score = 0
            srp_violations = []
            problem_areas = []
            recommendations = []
            
            # Count headers
            headers = re.findall(r'^#+\s+', content, re.MULTILINE)
            if len(headers) > 30:
                complexity_score += 15
                problem_areas.append(f"Too many sections: {len(headers)}")
                recommendations.append("Split into multiple documentation files")
            
            # Check for very long sections
            sections = re.split(r'^#+\s+', content, flags=re.MULTILINE)
            long_sections = [i for i, section in enumerate(sections) if len(section.split('\n')) > 100]
            
            if long_sections:
                complexity_score += 10
                problem_areas.append(f"Long sections: {len(long_sections)}")
                recommendations.append("Break down long sections into subsections or separate files")
            
        except Exception:
            complexity_score = 10
            problem_areas = ["File reading error"]
            recommendations = ["Check file encoding"]
        
        return {
            'complexity_score': complexity_score,
            'srp_violations': srp_violations,
            'problem_areas': problem_areas,
            'recommendations': recommendations
        }
    
    def _analyze_sql_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze SQL file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            complexity_score = 0
            srp_violations = []
            problem_areas = []
            recommendations = []
            
            # Count statements
            statements = re.split(r';\s*\n', content)
            if len(statements) > 50:
                complexity_score += 20
                problem_areas.append(f"Too many SQL statements: {len(statements)}")
                recommendations.append("Split into multiple migration files")
            
            # Check for very long queries
            long_queries = [stmt for stmt in statements if len(stmt.split('\n')) > 20]
            if long_queries:
                complexity_score += 15
                problem_areas.append(f"Complex queries: {len(long_queries)}")
                recommendations.append("Break down complex queries or add views")
            
        except Exception:
            complexity_score = 15
            problem_areas = ["SQL parsing error"]
            recommendations = ["Review SQL syntax"]
        
        return {
            'complexity_score': complexity_score,
            'srp_violations': srp_violations,
            'problem_areas': problem_areas,
            'recommendations': recommendations
        }
    
    def _analyze_generic_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze generic text file"""
        complexity_score = 10  # Base complexity for large files
        srp_violations = []
        problem_areas = ["Large file requiring review"]
        recommendations = ["Review file structure and consider splitting"]
        
        return {
            'complexity_score': complexity_score,
            'srp_violations': srp_violations,
            'problem_areas': problem_areas,
            'recommendations': recommendations
        }
    
    def _get_json_depth(self, obj, depth=0) -> int:
        """Calculate maximum depth of JSON object"""
        if isinstance(obj, dict):
            return max([self._get_json_depth(v, depth + 1) for v in obj.values()], default=depth)
        elif isinstance(obj, list):
            return max([self._get_json_depth(item, depth + 1) for item in obj], default=depth)
        else:
            return depth
    
    def _calculate_risk_score(self, line_count: int, complexity_score: int, 
                            srp_violation_count: int, file_type: str) -> int:
        """Calculate risk/impact score for prioritization"""
        # Base score from line count
        line_score = min(line_count // 100, 50)  # Max 50 points
        
        # Complexity contribution
        complexity_contribution = min(complexity_score, 50)  # Max 50 points
        
        # SRP violation penalty
        srp_penalty = min(srp_violation_count * 10, 30)  # Max 30 points
        
        # File type multiplier
        type_multipliers = {
            'Python': 1.2,
            'TypeScript/React': 1.1,
            'JavaScript/React': 1.1,
            'JSON': 0.8,
            'SQL': 1.0,
            'Markdown': 0.6
        }
        
        multiplier = type_multipliers.get(file_type, 1.0)
        
        total_score = int((line_score + complexity_contribution + srp_penalty) * multiplier)
        return min(total_score, 100)  # Cap at 100
    
    def _determine_priority(self, risk_score: int) -> str:
        """Determine priority based on risk score"""
        if risk_score >= 80:
            return 'Critical'
        elif risk_score >= 60:
            return 'High'
        elif risk_score >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def generate_report(self) -> str:
        """Generate comprehensive markdown report"""
        report_lines = []
        
        # Header
        report_lines.extend([
            "# 🔍 LARGE FILE ANALYSIS REPORT",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Repository**: Sophia AI",
            f"**Analysis Threshold**: {self.line_threshold} lines",
            "",
            "---",
            ""
        ])
        
        # Executive Summary
        report_lines.extend([
            "## 📊 EXECUTIVE SUMMARY",
            "",
            f"**Total Large Files Identified**: {len(self.large_files)}",
            f"**Critical Priority Files**: {len([f for f in self.large_files if f.priority == 'Critical'])}",
            f"**High Priority Files**: {len([f for f in self.large_files if f.priority == 'High'])}",
            f"**Medium Priority Files**: {len([f for f in self.large_files if f.priority == 'Medium'])}",
            f"**Low Priority Files**: {len([f for f in self.large_files if f.priority == 'Low'])}",
            ""
        ])
        
        # Key themes
        file_types = {}
        total_violations = 0
        for file_analysis in self.large_files:
            file_types[file_analysis.file_type] = file_types.get(file_analysis.file_type, 0) + 1
            total_violations += len(file_analysis.srp_violations)
        
        report_lines.extend([
            "### 🎯 Key Findings",
            "",
            f"- **Most Common File Type**: {max(file_types.items(), key=lambda x: x[1])[0]} ({max(file_types.values())} files)",
            f"- **Total SRP Violations**: {total_violations}",
            f"- **Average Risk Score**: {sum(f.risk_impact_score for f in self.large_files) // len(self.large_files) if self.large_files else 0}",
            "",
            "### 🚨 Critical Issues Observed",
            ""
        ])
        
        # Add critical issues
        critical_files = [f for f in self.large_files if f.priority == 'Critical']
        if critical_files:
            for file_analysis in critical_files[:3]:  # Top 3 critical
                report_lines.append(f"- **{file_analysis.file_path}**: {', '.join(file_analysis.problem_areas[:2])}")
        else:
            report_lines.append("- No critical issues identified")
        
        report_lines.extend(["", "---", ""])
        
        # Prioritized Refactoring Plan
        report_lines.extend([
            "## 🎯 PRIORITIZED REFACTORING PLAN",
            "",
            "| Priority | File Path | Lines | Risk Score | Key Issues |",
            "|----------|-----------|-------|------------|------------|"
        ])
        
        # Top 10 files
        top_files = self.large_files[:10]
        for file_analysis in top_files:
            key_issues = ', '.join(file_analysis.problem_areas[:2])
            if len(key_issues) > 50:
                key_issues = key_issues[:47] + "..."
            
            report_lines.append(
                f"| {file_analysis.priority} | `{file_analysis.file_path}` | {file_analysis.line_count} | {file_analysis.risk_impact_score} | {key_issues} |"
            )
        
        report_lines.extend(["", "---", ""])
        
        # Detailed File-by-File Analysis
        report_lines.extend([
            "## 📋 DETAILED FILE-BY-FILE ANALYSIS",
            ""
        ])
        
        for i, file_analysis in enumerate(self.large_files, 1):
            report_lines.extend([
                f"### {i}. {file_analysis.file_path}",
                "",
                f"**File Type**: {file_analysis.file_type}",
                f"**Line Count**: {file_analysis.line_count:,} lines",
                f"**File Size**: {file_analysis.size_bytes:,} bytes",
                f"**Complexity Score**: {file_analysis.complexity_score}/100",
                f"**Risk/Impact Score**: {file_analysis.risk_impact_score}/100",
                f"**Priority**: {file_analysis.priority}",
                ""
            ])
            
            # Problem Analysis
            if file_analysis.srp_violations:
                report_lines.extend([
                    "#### 🚨 SRP Violations",
                    ""
                ])
                for violation in file_analysis.srp_violations:
                    report_lines.append(f"- {violation}")
                report_lines.append("")
            
            if file_analysis.problem_areas:
                report_lines.extend([
                    "#### ⚠️ Problem Areas",
                    ""
                ])
                for problem in file_analysis.problem_areas:
                    report_lines.append(f"- {problem}")
                report_lines.append("")
            
            # Actionable Recommendations
            if file_analysis.recommendations:
                report_lines.extend([
                    "#### 💡 Actionable Recommendations",
                    ""
                ])
                for i, recommendation in enumerate(file_analysis.recommendations, 1):
                    report_lines.append(f"{i}. {recommendation}")
                report_lines.append("")
            
            report_lines.extend(["---", ""])
        
        # Summary and Next Steps
        report_lines.extend([
            "## 🚀 IMPLEMENTATION STRATEGY",
            "",
            "### Phase 1: Critical Files (Immediate Action Required)",
            ""
        ])
        
        critical_files = [f for f in self.large_files if f.priority == 'Critical']
        if critical_files:
            for file_analysis in critical_files:
                report_lines.append(f"- **{file_analysis.file_path}** - {file_analysis.recommendations[0] if file_analysis.recommendations else 'Requires immediate review'}")
        else:
            report_lines.append("- No critical files identified")
        
        report_lines.extend([
            "",
            "### Phase 2: High Priority Files (Next Sprint)",
            ""
        ])
        
        high_files = [f for f in self.large_files if f.priority == 'High'][:5]
        for file_analysis in high_files:
            report_lines.append(f"- **{file_analysis.file_path}** - {file_analysis.recommendations[0] if file_analysis.recommendations else 'Requires review'}")
        
        report_lines.extend([
            "",
            "### Phase 3: Medium Priority Files (Future Sprints)",
            "",
            f"- {len([f for f in self.large_files if f.priority == 'Medium'])} files identified for future refactoring",
            "",
            "### Success Metrics",
            "",
            "- [ ] Reduce average file size by 30%",
            "- [ ] Eliminate all Critical priority files",
            "- [ ] Reduce SRP violations by 50%",
            "- [ ] Improve code maintainability scores",
            "",
            "---",
            "",
            "*This analysis was generated automatically. Review recommendations with the development team before implementation.*"
        ])
        
        return '\n'.join(report_lines)
    
    def save_report(self, output_path: str):
        """Save the analysis report to file"""
        report_content = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 Report saved to: {output_path}")
    
    def save_json_data(self, output_path: str):
        """Save raw analysis data as JSON"""
        data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_files_analyzed': len(self.large_files),
            'line_threshold': self.line_threshold,
            'files': [asdict(file_analysis) for file_analysis in self.large_files]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 JSON data saved to: {output_path}")

def main():
    """Main execution function"""
    project_root = "/home/ubuntu/sophia-main"
    analyzer = LargeFileAnalyzer(project_root)
    
    print("🚀 Starting Large File Analysis for Sophia AI...")
    print(f"📁 Project Root: {project_root}")
    print(f"📏 Line Threshold: {analyzer.line_threshold}")
    print()
    
    # Scan repository
    large_files = analyzer.scan_repository()
    
    if not large_files:
        print("✅ No large files found exceeding the threshold!")
        return
    
    # Generate and save report
    report_path = f"{project_root}/LARGE_FILE_ANALYSIS_REPORT.md"
    json_path = f"{project_root}/large_file_analysis_data.json"
    
    analyzer.save_report(report_path)
    analyzer.save_json_data(json_path)
    
    # Summary
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total Large Files: {len(large_files)}")
    print(f"Critical Priority: {len([f for f in large_files if f.priority == 'Critical'])}")
    print(f"High Priority: {len([f for f in large_files if f.priority == 'High'])}")
    print(f"Medium Priority: {len([f for f in large_files if f.priority == 'Medium'])}")
    print(f"Low Priority: {len([f for f in large_files if f.priority == 'Low'])}")
    print()
    print("📋 Reports Generated:")
    print(f"- Markdown Report: {report_path}")
    print(f"- JSON Data: {json_path}")
    print()
    print("🎯 Next Steps:")
    print("1. Review the detailed analysis report")
    print("2. Prioritize Critical and High priority files")
    print("3. Create refactoring tasks for development team")
    print("4. Implement recommendations in phases")

if __name__ == "__main__":
    main()

