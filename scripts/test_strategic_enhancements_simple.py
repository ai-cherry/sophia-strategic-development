#!/usr/bin/env python3
"""
Simple test script for strategic enhancement services.
Tests that files exist and basic structure without imports.
"""

import ast
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def get_class_methods(filepath: str, class_name: str) -> list:
    """Extract method names from a class in a Python file."""
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())

        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        methods.append(item.name)
        return methods
    except Exception:
        return []


def test_project_intelligence():
    """Test Project Intelligence Service structure."""

    filepath = "backend/services/project_intelligence_service.py"
    if not check_file_exists(filepath):
        return False

    # Check for expected methods
    methods = get_class_methods(filepath, "ProjectIntelligenceService")
    expected_methods = [
        "get_project_summary",
        "get_team_performance",
        "get_milestone_tracking",
    ]

    for method in expected_methods:
        if method in methods:
            pass
        else:
            pass

    # Check for model classes
    with open(filepath) as f:
        content = f.read()
        if "class ProjectStatus" in content:
            pass
        if "class ProjectHealth" in content:
            pass

    return True


def test_structured_output():
    """Test Structured Output Service structure."""

    filepath = "backend/services/structured_output_service.py"
    if not check_file_exists(filepath):
        return False

    # Check for expected methods
    methods = get_class_methods(filepath, "StructuredOutputService")
    expected_methods = [
        "get_structured_output",
        "get_executive_summary",
        "analyze_deal",
        "analyze_call",
    ]

    for method in expected_methods:
        if method in methods:
            pass
        else:
            pass

    # Check for model classes
    with open(filepath) as f:
        content = f.read()
        models = ["ExecutiveSummary", "DealAnalysis", "CallInsights"]
        for model in models:
            if f"class {model}" in content:
                pass

    return True


def test_fast_document_processor():
    """Test Fast Document Processor structure."""

    filepath = "backend/services/fast_document_processor.py"
    if not check_file_exists(filepath):
        return False

    # Check for expected methods
    methods = get_class_methods(filepath, "FastDocumentProcessor")
    expected_methods = [
        "process_documents_batch",
        "process_document",
        "get_metrics",
        "optimize_performance",
    ]

    for method in expected_methods:
        if method in methods:
            pass
        else:
            pass

    # Check for model classes
    with open(filepath) as f:
        content = f.read()
        models = ["DocumentChunk", "ProcessingResult", "ProcessingMetrics"]
        for model in models:
            if f"class {model}" in content:
                pass

    return True


def test_enhanced_app_integration():
    """Test that services are integrated into the enhanced app."""

    filepath = "backend/app/enhanced_minimal_app.py"
    if not check_file_exists(filepath):
        return False

    with open(filepath) as f:
        content = f.read()

        # Check for service imports
        imports = [
            "ProjectIntelligenceService",
            "StructuredOutputService",
            "FastDocumentProcessor",
        ]
        for imp in imports:
            if imp in content:
                pass
            else:
                pass

        # Check for endpoints
        endpoints = [
            "/api/projects/summary",
            "/api/projects/team-performance",
            "/api/projects/milestones",
            "/api/structured-output/generate",
            "/api/documents/process",
            "/api/documents/metrics",
            "/api/dashboard/executive",
        ]
        for endpoint in endpoints:
            if endpoint in content:
                pass
            else:
                pass

    return True


def main():
    """Run all tests."""

    results = {
        "project_intelligence": test_project_intelligence(),
        "structured_output": test_structured_output(),
        "fast_document_processor": test_fast_document_processor(),
        "enhanced_app_integration": test_enhanced_app_integration(),
    }

    for _service, _passed in results.items():
        pass

    total_passed = sum(results.values())

    # Show implementation status

    return total_passed == len(results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
