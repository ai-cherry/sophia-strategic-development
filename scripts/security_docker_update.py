#!/usr/bin/env python3
"""
Docker Security Update Script
Updates all Docker base images to latest secure versions
"""

import os
import re
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerSecurityUpdater:
    def __init__(self):
        self.dockerfile_patterns = [
            "Dockerfile*",
            "*/Dockerfile*"
        ]
        
        # Secure base image mappings
        self.secure_base_images = {
            'python:3.9': 'python:3.12-slim',
            'python:3.10': 'python:3.12-slim',
            'python:3.11': 'python:3.12-slim',
            'python:3.9-slim': 'python:3.12-slim',
            'python:3.10-slim': 'python:3.12-slim',
            'python:3.11-slim': 'python:3.12-slim',
            'node:16': 'node:20-alpine',
            'node:18': 'node:20-alpine',
            'node:16-alpine': 'node:20-alpine',
            'node:18-alpine': 'node:20-alpine',
            'ubuntu:20.04': 'ubuntu:22.04',
            'ubuntu:18.04': 'ubuntu:22.04',
            'debian:bullseye': 'debian:bookworm-slim',
            'debian:buster': 'debian:bookworm-slim',
            'nginx:latest': 'nginx:1.25-alpine',
            'nginx:1.20': 'nginx:1.25-alpine',
            'nginx:1.21': 'nginx:1.25-alpine',
            'redis:6': 'redis:7-alpine',
            'redis:latest': 'redis:7-alpine',
            'postgres:13': 'postgres:15-alpine',
            'postgres:14': 'postgres:15-alpine',
        }
        
        self.updated_files = []
        self.security_improvements = []
        
    def find_dockerfiles(self) -> List[Path]:
        """Find all Dockerfile configurations"""
        dockerfiles = []
        
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and backup directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 'backup' not in d.lower()]
            
            for file in files:
                if file.startswith('Dockerfile'):
                    dockerfile_path = Path(root) / file
                    dockerfiles.append(dockerfile_path)
                    
        return dockerfiles
    
    def analyze_dockerfile(self, dockerfile_path: Path) -> Dict:
        """Analyze a Dockerfile for security issues"""
        try:
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                
            analysis = {
                'path': dockerfile_path,
                'base_images': [],
                'security_issues': [],
                'recommendations': []
            }
            
            # Find FROM statements
            from_pattern = r'^FROM\s+([^\s]+)'
            matches = re.findall(from_pattern, content, re.MULTILINE)
            
            for match in matches:
                base_image = match.strip()
                analysis['base_images'].append(base_image)
                
                # Check for security issues
                if ':latest' in base_image:
                    analysis['security_issues'].append(f"Using :latest tag: {base_image}")
                    
                if base_image in self.secure_base_images:
                    analysis['recommendations'].append({
                        'current': base_image,
                        'recommended': self.secure_base_images[base_image],
                        'reason': 'Security update available'
                    })
                    
                # Check for outdated Python versions
                if 'python:3.9' in base_image or 'python:3.10' in base_image:
                    analysis['security_issues'].append(f"Outdated Python version: {base_image}")
                    
                # Check for outdated Node versions
                if 'node:16' in base_image or 'node:18' in base_image:
                    analysis['security_issues'].append(f"Outdated Node.js version: {base_image}")
                    
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {dockerfile_path}: {e}")
            return None
    
    def update_dockerfile(self, dockerfile_path: Path, analysis: Dict) -> bool:
        """Update a Dockerfile with secure base images"""
        try:
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                
            original_content = content
            updated = False
            
            # Apply recommendations
            for rec in analysis['recommendations']:
                old_image = rec['current']
                new_image = rec['recommended']
                
                # Update FROM statements
                pattern = rf'^FROM\s+{re.escape(old_image)}'
                replacement = f'FROM {new_image}'
                
                if re.search(pattern, content, re.MULTILINE):
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                    updated = True
                    
                    self.security_improvements.append({
                        'file': dockerfile_path,
                        'change': f'{old_image} → {new_image}',
                        'reason': rec['reason']
                    })
                    
            # Add security best practices
            if 'USER root' in content and 'USER ' not in content.split('USER root')[1]:
                # Add non-root user if missing
                content += '\n# Security: Create non-root user\nRUN adduser --disabled-password --gecos "" appuser\nUSER appuser\n'
                updated = True
                
            if updated:
                # Create backup
                backup_path = dockerfile_path.with_suffix('.backup')
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                    
                # Write updated content
                with open(dockerfile_path, 'w') as f:
                    f.write(content)
                    
                self.updated_files.append(dockerfile_path)
                logger.info(f"✅ Updated {dockerfile_path}")
                return True
            else:
                logger.info(f"ℹ️  No updates needed for {dockerfile_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating {dockerfile_path}: {e}")
            return False
    
    def validate_docker_images(self) -> bool:
        """Validate that updated Docker images are available"""
        logger.info("🔍 Validating Docker images...")
        
        unique_images = set()
        for improvement in self.security_improvements:
            new_image = improvement['change'].split(' → ')[1]
            unique_images.add(new_image)
            
        validation_results = []
        
        for image in unique_images:
            try:
                # Check if image exists
                result = subprocess.run([
                    'docker', 'manifest', 'inspect', image
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    validation_results.append(f"✅ {image} - Available")
                else:
                    validation_results.append(f"❌ {image} - Not available")
                    
            except Exception as e:
                validation_results.append(f"⚠️ {image} - Could not validate: {e}")
                
        for result in validation_results:
            logger.info(result)
            
        return all('✅' in result for result in validation_results)
    
    def generate_security_report(self) -> Dict:
        """Generate Docker security update report"""
        report = {
            'timestamp': subprocess.check_output(['date'], text=True).strip(),
            'dockerfiles_analyzed': len(self.find_dockerfiles()),
            'dockerfiles_updated': len(self.updated_files),
            'security_improvements': self.security_improvements,
            'updated_files': [str(f) for f in self.updated_files],
            'recommendations': [
                "Rebuild all Docker images with updated base images",
                "Test all services after Docker updates",
                "Update deployment scripts to use new images",
                "Schedule regular Docker security updates"
            ]
        }
        
        # Save report
        with open('docker_security_report.json', 'w') as f:
            import json
            json.dump(report, f, indent=2)
            
        return report
    
    def update_all_dockerfiles(self) -> bool:
        """Main function to update all Dockerfiles"""
        logger.info("🐳 Starting Docker security update...")
        
        # Find all Dockerfiles
        dockerfiles = self.find_dockerfiles()
        logger.info(f"📋 Found {len(dockerfiles)} Dockerfile(s)")
        
        # Analyze and update each Dockerfile
        for dockerfile in dockerfiles:
            logger.info(f"🔍 Analyzing {dockerfile}")
            analysis = self.analyze_dockerfile(dockerfile)
            
            if analysis and (analysis['security_issues'] or analysis['recommendations']):
                logger.info(f"⚠️  Security issues found in {dockerfile}")
                for issue in analysis['security_issues']:
                    logger.info(f"   - {issue}")
                    
                self.update_dockerfile(dockerfile, analysis)
            else:
                logger.info(f"✅ {dockerfile} is secure")
                
        # Validate images
        if self.security_improvements:
            self.validate_docker_images()
            
        # Generate report
        report = self.generate_security_report()
        
        # Summary
        logger.info(f"📊 Docker Security Update Summary:")
        logger.info(f"   📂 Dockerfiles analyzed: {report['dockerfiles_analyzed']}")
        logger.info(f"   ✅ Dockerfiles updated: {report['dockerfiles_updated']}")
        logger.info(f"   🔒 Security improvements: {len(self.security_improvements)}")
        
        if self.security_improvements:
            logger.info("🔒 Security improvements applied:")
            for improvement in self.security_improvements:
                logger.info(f"   - {improvement['file']}: {improvement['change']}")
                
        return len(self.security_improvements) > 0

def main():
    """Main entry point"""
    logger.info("🛡️ Docker Security Update for Sophia AI")
    
    updater = DockerSecurityUpdater()
    success = updater.update_all_dockerfiles()
    
    if success:
        logger.info("✅ Docker security updates completed successfully!")
        logger.info("🔄 Next steps:")
        logger.info("   1. Rebuild Docker images with updated base images")
        logger.info("   2. Test all services after updates")
        logger.info("   3. Update deployment scripts")
        logger.info("   4. Deploy to testing environment")
    else:
        logger.info("ℹ️  No Docker security updates were needed")
        
    return success

if __name__ == "__main__":
    main() 