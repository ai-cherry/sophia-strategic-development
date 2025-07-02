#!/usr/bin/env python3
"""Simple Codacy MCP Server for code quality automation."""

import asyncio
import json
import logging
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Basic FastAPI setup
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("FastAPI not available. Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCodeAnalyzer:
    """Simple code analysis without external dependencies."""
    
    def __init__(self):
        self.security_patterns = [
            (r'eval\s*\(', 'Use of eval() is dangerous'),
            (r'exec\s*\(', 'Use of exec() is dangerous'),
            (r'os\.system\s*\(', 'Use of os.system() is dangerous'),
            (r'subprocess\.call\s*\(.*shell=True', 'Shell injection risk'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password detected'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key detected'),
        ]
        
        self.complexity_patterns = [
            (r'def\s+\w+\([^)]*\):', 'function_definition'),
            (r'class\s+\w+', 'class_definition'),
            (r'if\s+', 'conditional'),
            (r'for\s+', 'loop'),
            (r'while\s+', 'loop'),
            (r'try:', 'exception_handling'),
        ]
    
    async def analyze_code(self, code: str, filename: str = "unknown") -> Dict[str, Any]:
        """Analyze code for security issues and complexity."""
        lines = code.split('\n')
        
        # Security analysis
        security_issues = []
        for i, line in enumerate(lines, 1):
            for pattern, message in self.security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    security_issues.append({
                        "line": i,
                        "issue": message,
                        "code": line.strip(),
                        "severity": "high" if "dangerous" in message else "medium"
                    })
        
        # Complexity analysis
        complexity_score = 0
        complexity_details = {}
        
        for pattern, element_type in self.complexity_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            count = len(matches)
            complexity_details[element_type] = count
            
            # Weight different elements
            if element_type == 'function_definition':
                complexity_score += count * 2
            elif element_type == 'class_definition':
                complexity_score += count * 3
            elif element_type in ['conditional', 'loop']:
                complexity_score += count * 1
            else:
                complexity_score += count * 0.5
        
        # Code quality metrics
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        quality_score = 100
        if security_issues:
            quality_score -= len(security_issues) * 10
        if complexity_score > 50:
            quality_score -= (complexity_score - 50) * 0.5
        if comment_lines / non_empty_lines < 0.1:  # Less than 10% comments
            quality_score -= 10
        
        quality_score = max(0, quality_score)
        
        return {
            "filename": filename,
            "total_lines": total_lines,
            "non_empty_lines": non_empty_lines,
            "comment_lines": comment_lines,
            "security_issues": security_issues,
            "complexity_score": complexity_score,
            "complexity_details": complexity_details,
            "quality_score": quality_score,
            "recommendations": self._get_recommendations(security_issues, complexity_score, comment_lines, non_empty_lines)
        }
    
    def _get_recommendations(self, security_issues: List, complexity_score: int, comment_lines: int, non_empty_lines: int) -> List[str]:
        """Generate code improvement recommendations."""
        recommendations = []
        
        if security_issues:
            recommendations.append(f"Fix {len(security_issues)} security issues")
        
        if complexity_score > 50:
            recommendations.append("Consider breaking down complex functions")
        
        if comment_lines / non_empty_lines < 0.1:
            recommendations.append("Add more code comments for better maintainability")
        
        if complexity_score > 100:
            recommendations.append("Refactor code to reduce complexity")
        
        if not recommendations:
            recommendations.append("Code quality looks good!")
        
        return recommendations

# Create FastAPI app
app = FastAPI(title="Simple Codacy MCP Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create analyzer
analyzer = SimpleCodeAnalyzer()

@app.get("/")
async def root():
    return {
        "name": "Simple Codacy MCP Server",
        "version": "1.0.0",
        "status": "running",
        "capabilities": ["code_analysis", "security_scan", "complexity_analysis"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "codacy_mcp",
        "timestamp": datetime.now().isoformat(),
        "capabilities": {
            "security_analysis": True,
            "complexity_analysis": True,
            "quality_scoring": True
        }
    }

@app.post("/api/v1/analyze/code")
async def analyze_code(data: Dict[str, Any]):
    """Analyze code snippet."""
    try:
        code = data.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Code is required")
        
        filename = data.get("filename", "snippet.py")
        
        result = await analyzer.analyze_code(code, filename)
        
        logger.info(f"Analyzed {filename}: {result['quality_score']}/100 quality score")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze/file")
async def analyze_file(data: Dict[str, Any]):
    """Analyze a file by path."""
    try:
        file_path = data.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        code = path.read_text()
        result = await analyzer.analyze_code(code, str(path))
        
        logger.info(f"Analyzed file {file_path}: {result['quality_score']}/100 quality score")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/security/scan")
async def security_scan(data: Dict[str, Any]):
    """Focused security scan."""
    try:
        code = data.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Code is required")
        
        result = await analyzer.analyze_code(code)
        
        return {
            "security_issues": result["security_issues"],
            "severity_summary": {
                "high": len([i for i in result["security_issues"] if i["severity"] == "high"]),
                "medium": len([i for i in result["security_issues"] if i["severity"] == "medium"]),
                "low": len([i for i in result["security_issues"] if i["severity"] == "low"])
            },
            "recommendations": [r for r in result["recommendations"] if "security" in r.lower() or "fix" in r.lower()]
        }
    except Exception as e:
        logger.error(f"Error in security scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analyze/stats")
async def get_analysis_stats():
    """Get analysis statistics."""
    return {
        "total_analyses": 0,  # Would track in real implementation
        "security_patterns": len(analyzer.security_patterns),
        "complexity_patterns": len(analyzer.complexity_patterns),
        "supported_languages": ["python", "javascript", "typescript"]
    }

async def main():
    """Run the server."""
    logger.info("Starting Simple Codacy MCP Server on port 3008...")
    
    try:
        # Try to load ESC config if available
        try:
            from backend.core.auto_esc_config import get_config_value
            logger.info("✅ Pulumi ESC integration available")
        except Exception as e:
            logger.warning(f"Pulumi ESC not available: {e}")
        
        # Start server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=3008,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
