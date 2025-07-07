import os
import re
import json
import yaml

def update_dockerfile(file_path):
    """Update Dockerfile paths"""
    if not os.path.exists(file_path):
        return False
        
    with open(file_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # Update COPY commands
    content = re.sub(r'COPY backend/', 'COPY api/ core/ domain/ infrastructure/ shared/', content)
    content = re.sub(r'WORKDIR /app/backend', 'WORKDIR /app', content)
    content = re.sub(r'backend/main.py', 'api/main.py', content)
    content = re.sub(r'backend.main:app', 'api.main:app', content)
    
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def update_docker_compose(file_path):
    """Update docker-compose.yml files"""
    if not os.path.exists(file_path):
        return False
        
    with open(file_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # Update volume mounts
    content = re.sub(r'./backend:/app/backend', './api:/app/api:ro\n      - ./core:/app/core:ro\n      - ./domain:/app/domain:ro\n      - ./infrastructure:/app/infrastructure:ro\n      - ./shared:/app/shared:ro', content)
    content = re.sub(r'backend.main:app', 'api.main:app', content)
    
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def update_github_workflows():
    """Update GitHub workflow files"""
    workflow_dir = '.github/workflows'
    if not os.path.exists(workflow_dir):
        return
        
    updated = 0
    for file in os.listdir(workflow_dir):
        if file.endswith('.yml') or file.endswith('.yaml'):
            file_path = os.path.join(workflow_dir, file)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            original = content
            
            # Update paths
            content = re.sub(r'backend/', 'api/', content)
            content = re.sub(r'cd backend', 'cd api', content)
            content = re.sub(r'backend/requirements.txt', 'requirements.txt', content)
            
            if content != original:
                with open(file_path, 'w') as f:
                    f.write(content)
                updated += 1
                print(f"Updated workflow: {file}")
    
    return updated

def update_pyproject_toml():
    """Update pyproject.toml if it exists"""
    if not os.path.exists('pyproject.toml'):
        return False
        
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    original = content
    
    # Update module paths
    content = re.sub(r'"backend"', '"api", "core", "domain", "infrastructure", "shared"', content)
    content = re.sub(r'backend/', '', content)
    
    if content != original:
        with open('pyproject.toml', 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Update all configuration files"""
    print("Updating configuration files...")
    
    # Update Dockerfiles
    dockerfiles = ['Dockerfile', 'Dockerfile.production', 'Dockerfile.dev']
    for df in dockerfiles:
        if update_dockerfile(df):
            print(f"Updated {df}")
    
    # Update docker-compose files
    compose_files = ['docker-compose.yml', 'docker-compose.production.yml', 'docker-compose.dev.yml']
    for cf in compose_files:
        if update_docker_compose(cf):
            print(f"Updated {cf}")
    
    # Update GitHub workflows
    workflow_count = update_github_workflows()
    if workflow_count:
        print(f"Updated {workflow_count} workflow files")
    
    # Update pyproject.toml
    if update_pyproject_toml():
        print("Updated pyproject.toml")
    
    # Update VS Code settings
    vscode_settings = '.vscode/settings.json'
    if os.path.exists(vscode_settings):
        with open(vscode_settings, 'r') as f:
            settings = json.load(f)
        
        # Update Python paths
        if 'python.analysis.extraPaths' in settings:
            settings['python.analysis.extraPaths'] = ["api", "core", "domain", "infrastructure", "shared"]
        
        with open(vscode_settings, 'w') as f:
            json.dump(settings, f, indent=2)
        print("Updated VS Code settings")
    
    print("\nConfiguration update complete!")

if __name__ == '__main__':
    main() 