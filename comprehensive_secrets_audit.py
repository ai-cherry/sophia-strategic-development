#!/usr/bin/env python3
"""
Comprehensive GitHub Organization Secrets Audit & Alignment
Ensures ALL secrets from GitHub are properly mapped and synced to Pulumi ESC
"""

import re
import os

def extract_github_workflow_secrets():
    """Extract all secrets from GitHub Actions workflow"""
    print("🔍 EXTRACTING SECRETS FROM GITHUB ACTIONS WORKFLOW")
    print("=" * 60)
    
    workflow_file = ".github/workflows/sync_secrets.yml"
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    # Find all ${{ secrets.SECRET_NAME }} patterns
    secret_pattern = r'\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}'
    secrets = re.findall(secret_pattern, content)
    
    # Remove duplicates and sort
    unique_secrets = sorted(list(set(secrets)))
    
    print(f"📊 Found {len(unique_secrets)} unique secrets in GitHub Actions workflow:")
    
    # Categorize secrets
    categories = {
        'AI Services': [],
        'Business Intelligence': [],
        'Communication': [],
        'Data Infrastructure': [],
        'Cloud Infrastructure': [],
        'Observability': [],
        'Research Tools': [],
        'Development Tools': [],
        'Data Integration': [],
        'Security': []
    }
    
    for secret in unique_secrets:
        if any(ai_key in secret for ai_key in ['OPENAI', 'ANTHROPIC', 'HUGGINGFACE', 'LANGCHAIN', 'PORTKEY', 'OPENROUTER', 'PERPLEXITY', 'MISTRAL', 'DEEPSEEK', 'CODESTRAL', 'TOGETHERAI', 'XAI', 'VENICE', 'LLAMA']):
            categories['AI Services'].append(secret)
        elif any(bi_key in secret for bi_key in ['GONG', 'HUBSPOT', 'SALESFORCE', 'LINEAR', 'NOTION']):
            categories['Business Intelligence'].append(secret)
        elif any(comm_key in secret for comm_key in ['SLACK']):
            categories['Communication'].append(secret)
        elif any(data_key in secret for data_key in ['SNOWFLAKE', 'PINECONE', 'WEAVIATE', 'DATABASE', 'REDIS']):
            categories['Data Infrastructure'].append(secret)
        elif any(cloud_key in secret for cloud_key in ['LAMBDA', 'VERCEL', 'VULTR', 'PULUMI']):
            categories['Cloud Infrastructure'].append(secret)
        elif any(obs_key in secret for obs_key in ['ARIZE', 'GRAFANA', 'PROMETHEUS']):
            categories['Observability'].append(secret)
        elif any(research_key in secret for research_key in ['APIFY', 'SERP', 'TAVILY', 'EXA', 'BRAVE', 'ZENROWS']):
            categories['Research Tools'].append(secret)
        elif any(dev_key in secret for dev_key in ['GH_API', 'RETOOL', 'DOCKER', 'NPM']):
            categories['Development Tools'].append(secret)
        elif any(integration_key in secret for integration_key in ['ESTUARY', 'PIPEDREAM']):
            categories['Data Integration'].append(secret)
        elif any(security_key in secret for security_key in ['JWT', 'ENCRYPTION', 'API_SECRET']):
            categories['Security'].append(secret)
        else:
            categories['Security'].append(secret)  # Default to security
    
    for category, secrets_list in categories.items():
        if secrets_list:
            print(f"\n  📂 {category} ({len(secrets_list)} secrets):")
            for secret in secrets_list:
                print(f"    - {secret}")
    
    return unique_secrets, categories

def extract_sync_script_mappings():
    """Extract current mappings from sync script"""
    print(f"\n🔍 EXTRACTING CURRENT SYNC SCRIPT MAPPINGS")
    print("=" * 50)
    
    sync_file = "scripts/ci/sync_from_gh_to_pulumi.py"
    
    with open(sync_file, 'r') as f:
        content = f.read()
    
    # Extract mappings from the secret_mappings dictionary
    mappings_pattern = r'"([A-Z_]+)":\s*"([a-z_]+)"'
    mappings = re.findall(mappings_pattern, content)
    
    print(f"📊 Found {len(mappings)} mappings in sync script:")
    for github_secret, pulumi_key in mappings:
        print(f"  {github_secret} → {pulumi_key}")
    
    return dict(mappings)

def generate_complete_mappings(github_secrets, categories):
    """Generate complete mappings for all GitHub secrets"""
    print(f"\n🔧 GENERATING COMPLETE MAPPINGS FOR ALL SECRETS")
    print("=" * 55)
    
    complete_mappings = {}
    
    # Generate systematic mappings based on secret names
    for secret in github_secrets:
        # Convert to lowercase and replace underscores for Pulumi key
        pulumi_key = secret.lower()
        complete_mappings[secret] = pulumi_key
    
    print(f"📊 Generated {len(complete_mappings)} complete mappings:")
    
    # Group by category for display
    for category, secrets_list in categories.items():
        if secrets_list:
            print(f"\n  📂 {category}:")
            for secret in secrets_list:
                print(f"    \"{secret}\": \"{complete_mappings[secret]}\",")
    
    return complete_mappings

def identify_conflicts_and_gaps(github_secrets, current_mappings):
    """Identify conflicts and gaps between GitHub and sync script"""
    print(f"\n🔍 IDENTIFYING CONFLICTS AND GAPS")
    print("=" * 40)
    
    github_set = set(github_secrets)
    sync_set = set(current_mappings.keys())
    
    missing_from_sync = github_set - sync_set
    extra_in_sync = sync_set - github_set
    
    print(f"📊 ANALYSIS RESULTS:")
    print(f"  GitHub secrets: {len(github_secrets)}")
    print(f"  Sync mappings: {len(current_mappings)}")
    print(f"  Missing from sync: {len(missing_from_sync)}")
    print(f"  Extra in sync: {len(extra_in_sync)}")
    
    if missing_from_sync:
        print(f"\n❌ MISSING FROM SYNC SCRIPT ({len(missing_from_sync)} secrets):")
        for secret in sorted(missing_from_sync):
            print(f"    - {secret}")
    
    if extra_in_sync:
        print(f"\n⚠️ EXTRA IN SYNC SCRIPT ({len(extra_in_sync)} secrets):")
        for secret in sorted(extra_in_sync):
            print(f"    - {secret}")
    
    return missing_from_sync, extra_in_sync

def update_sync_script_with_complete_mappings(complete_mappings):
    """Update sync script with complete mappings"""
    print(f"\n🔧 UPDATING SYNC SCRIPT WITH COMPLETE MAPPINGS")
    print("=" * 55)
    
    sync_file = "scripts/ci/sync_from_gh_to_pulumi.py"
    
    with open(sync_file, 'r') as f:
        content = f.read()
    
    # Generate the new mappings section
    mappings_lines = []
    mappings_lines.append("        # COMPLETE MAPPINGS - ALL GITHUB ORGANIZATION SECRETS")
    mappings_lines.append("        # Automatically generated to match ALL secrets in GitHub Actions workflow")
    mappings_lines.append("        self.secret_mappings = {")
    
    # Group mappings by category for better organization
    categories = {
        'Core AI Services': ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GONG_ACCESS_KEY', 'PINECONE_API_KEY'],
        'Extended AI Services': [k for k in complete_mappings.keys() if any(x in k for x in ['HUGGINGFACE', 'LANGCHAIN', 'PORTKEY', 'OPENROUTER', 'PERPLEXITY', 'MISTRAL', 'DEEPSEEK', 'CODESTRAL', 'TOGETHERAI', 'XAI', 'VENICE', 'LLAMA'])],
        'Business Intelligence': [k for k in complete_mappings.keys() if any(x in k for x in ['GONG', 'HUBSPOT', 'SALESFORCE', 'LINEAR', 'NOTION']) and k not in ['GONG_ACCESS_KEY']],
        'Communication': [k for k in complete_mappings.keys() if 'SLACK' in k],
        'Data Infrastructure': [k for k in complete_mappings.keys() if any(x in k for x in ['SNOWFLAKE', 'PINECONE', 'WEAVIATE', 'DATABASE', 'REDIS']) and k not in ['PINECONE_API_KEY']],
        'Cloud Infrastructure': [k for k in complete_mappings.keys() if any(x in k for x in ['LAMBDA', 'VERCEL', 'VULTR', 'PULUMI'])],
        'Observability': [k for k in complete_mappings.keys() if any(x in k for x in ['ARIZE', 'GRAFANA', 'PROMETHEUS'])],
        'Research Tools': [k for k in complete_mappings.keys() if any(x in k for x in ['APIFY', 'SERP', 'TAVILY', 'EXA', 'BRAVE', 'ZENROWS'])],
        'Development Tools': [k for k in complete_mappings.keys() if any(x in k for x in ['GH_API', 'RETOOL', 'DOCKER', 'NPM'])],
        'Data Integration': [k for k in complete_mappings.keys() if any(x in k for x in ['ESTUARY', 'PIPEDREAM'])],
        'Security': [k for k in complete_mappings.keys() if any(x in k for x in ['JWT', 'ENCRYPTION', 'API_SECRET'])]
    }
    
    for category, secrets in categories.items():
        if secrets:
            mappings_lines.append(f"            # {category}")
            for secret in sorted(secrets):
                if secret in complete_mappings:
                    mappings_lines.append(f'            "{secret}": "{complete_mappings[secret]}",')
            mappings_lines.append("")
    
    mappings_lines.append("        }")
    
    new_mappings_section = "\n".join(mappings_lines)
    
    # Replace the existing mappings
    pattern = r'self\.secret_mappings = \{[^}]+\}'
    content = re.sub(pattern, new_mappings_section, content, flags=re.DOTALL)
    
    with open(sync_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated sync script with {len(complete_mappings)} complete mappings")

def main():
    """Run comprehensive secrets audit and alignment"""
    print("🚀 COMPREHENSIVE GITHUB ORGANIZATION SECRETS AUDIT")
    print("=" * 70)
    
    # Extract secrets from GitHub workflow
    github_secrets, categories = extract_github_workflow_secrets()
    
    # Extract current sync script mappings
    current_mappings = extract_sync_script_mappings()
    
    # Identify conflicts and gaps
    missing, extra = identify_conflicts_and_gaps(github_secrets, current_mappings)
    
    # Generate complete mappings
    complete_mappings = generate_complete_mappings(github_secrets, categories)
    
    # Update sync script
    update_sync_script_with_complete_mappings(complete_mappings)
    
    print(f"\n🎉 COMPREHENSIVE AUDIT COMPLETE!")
    print("=" * 40)
    print(f"✅ Analyzed {len(github_secrets)} GitHub secrets")
    print(f"✅ Generated {len(complete_mappings)} complete mappings")
    print(f"✅ Updated sync script with ALL secrets")
    print(f"✅ Eliminated {len(missing)} missing mappings")
    print(f"✅ Ready for complete GitHub→Pulumi ESC sync")
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Commit updated sync script")
    print("2. Push to trigger GitHub Actions")
    print("3. Verify all secrets sync to Pulumi ESC")
    print("4. Test Lambda Labs and other service access")

if __name__ == "__main__":
    main()
