import ast
import os
from pathlib import Path
from collections import defaultdict
import csv

class DependencyAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.imports = []
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
            
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)

def analyze_dependencies(root_dir='backend'):
    """Analyze all Python files and their dependencies"""
    dependencies = defaultdict(set)
    
    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ and .git
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                module_path = str(file_path).replace('/', '.').replace('.py', '')
                
                try:
                    with open(file_path, 'r') as f:
                        tree = ast.parse(f.read())
                        analyzer = DependencyAnalyzer(str(file_path))
                        analyzer.visit(tree)
                        
                        for imp in analyzer.imports:
                            if imp.startswith('backend.'):
                                dependencies[module_path].add(imp)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
    
    return dependencies

def generate_dependency_report(dependencies):
    """Generate CSV report of dependencies"""
    with open('reports/backend_dependencies.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['From Module', 'To Module', 'Current Layer', 'Target Layer'])
        
        for from_module, to_modules in dependencies.items():
            current_layer = classify_current_layer(from_module)
            for to_module in to_modules:
                target_layer = classify_target_layer(to_module)
                writer.writerow([from_module, to_module, current_layer, target_layer])

def classify_current_layer(module_path):
    """Classify module into current architecture layer"""
    if 'backend.api' in module_path:
        return 'api'
    elif 'backend.agents' in module_path:
        return 'agents'
    elif 'backend.services' in module_path:
        return 'services'
    elif 'backend.models' in module_path:
        return 'models'
    elif 'backend.integrations' in module_path:
        return 'integrations'
    elif 'backend.core' in module_path:
        return 'core'
    elif 'backend.domain' in module_path:
        return 'domain'
    elif 'backend.mcp_servers' in module_path:
        return 'mcp_servers'
    elif 'backend.etl' in module_path:
        return 'etl'
    elif 'backend.monitoring' in module_path:
        return 'monitoring'
    elif 'backend.utils' in module_path:
        return 'utils'
    else:
        return 'other'

def classify_target_layer(module_path):
    """Classify where module should go in new architecture"""
    parts = module_path.split('.')
    
    # API layer
    if 'api' in parts or 'routes' in parts:
        return 'api'
    
    # Domain layer
    if 'models' in parts or 'entities' in parts:
        return 'domain'
    
    # Infrastructure layer
    if any(x in parts for x in ['integrations', 'mcp_servers', 'etl', 'monitoring', 'security']):
        return 'infrastructure'
    
    # Core layer
    if any(x in parts for x in ['agents', 'services', 'workflows', 'orchestration', 'use_cases']):
        return 'core'
    
    # Shared layer
    if any(x in parts for x in ['utils', 'prompts', 'constants']):
        return 'shared'
    
    return 'core'  # default

if __name__ == '__main__':
    print("Analyzing backend dependencies...")
    dependencies = analyze_dependencies()
    generate_dependency_report(dependencies)
    print(f"Found {len(dependencies)} modules with dependencies")
    print("Report saved to reports/backend_dependencies.csv") 