#!/usr/bin/env python3
"""
Sophia AI SSL Certificate Fix

This script fixes SSL certificate verification issues by setting the SSL_CERT_FILE
environment variable to the path of the certifi cacert.pem file. It also creates
a wrapper script that can be used to run Python scripts with the SSL certificate
fix applied.

Usage:
    python fix_ssl_certificates.py
"""

import os
import sys
import subprocess
import logging
import certifi
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_certifi_path() -> str:
    """Get the path to the certifi cacert.pem file"""
    return certifi.where()

def create_wrapper_script() -> bool:
    """Create a wrapper script that sets the SSL_CERT_FILE environment variable"""
    try:
        certifi_path = get_certifi_path()
        wrapper_path = Path("run_with_ssl_fix.py")
        
        with open(wrapper_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
\"\"\"
Sophia AI SSL Certificate Fix Wrapper

This script runs a Python script with the SSL_CERT_FILE environment variable
set to the path of the certifi cacert.pem file.

Usage:
    python run_with_ssl_fix.py <script> [args...]
\"\"\"

import os
import sys
import subprocess

# Set the SSL_CERT_FILE environment variable
os.environ["SSL_CERT_FILE"] = "{certifi_path}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_with_ssl_fix.py <script> [args...]")
        sys.exit(1)
    
    # Get the script and arguments
    script = sys.argv[1]
    args = sys.argv[2:]
    
    # Run the script with the SSL certificate fix
    result = subprocess.run([sys.executable, script] + args)
    sys.exit(result.returncode)
""")
        
        # Make the wrapper script executable
        os.chmod(wrapper_path, 0o755)
        
        logger.info(f"Created wrapper script: {wrapper_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating wrapper script: {e}")
        return False

def update_env_file() -> bool:
    """Update the .env file with the SSL_CERT_FILE environment variable"""
    try:
        certifi_path = get_certifi_path()
        env_path = Path(".env")
        
        if not env_path.exists():
            logger.warning(".env file not found, skipping update")
            return False
        
        # Read the .env file
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Check if SSL_CERT_FILE is already set
        ssl_cert_file_set = False
        for i, line in enumerate(lines):
            if line.strip().startswith("SSL_CERT_FILE="):
                lines[i] = f"SSL_CERT_FILE={certifi_path}\n"
                ssl_cert_file_set = True
                break
        
        # If SSL_CERT_FILE is not set, add it to the end of the file
        if not ssl_cert_file_set:
            # Find the Configuration section
            config_section_index = -1
            for i, line in enumerate(lines):
                if line.strip() == "# Configuration":
                    config_section_index = i
                    break
            
            if config_section_index != -1:
                # Add SSL_CERT_FILE to the Configuration section
                lines.insert(config_section_index + 1, f"SSL_CERT_FILE={certifi_path}\n")
            else:
                # Add SSL_CERT_FILE to the end of the file
                lines.append(f"\n# SSL Certificate Fix\nSSL_CERT_FILE={certifi_path}\n")
        
        # Write the updated .env file
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        logger.info(f"Updated .env file with SSL_CERT_FILE={certifi_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating .env file: {e}")
        return False

def update_shell_profile() -> bool:
    """Update the shell profile with the SSL_CERT_FILE environment variable"""
    try:
        certifi_path = get_certifi_path()
        
        # Determine the shell profile file
        shell = os.environ.get("SHELL", "")
        home = os.path.expanduser("~")
        
        if "zsh" in shell:
            profile_path = os.path.join(home, ".zshrc")
        elif "bash" in shell:
            profile_path = os.path.join(home, ".bashrc")
        else:
            logger.warning(f"Unsupported shell: {shell}, skipping profile update")
            return False
        
        # Check if the profile file exists
        if not os.path.exists(profile_path):
            logger.warning(f"Profile file not found: {profile_path}, skipping profile update")
            return False
        
        # Read the profile file
        with open(profile_path, 'r') as f:
            content = f.read()
        
        # Check if SSL_CERT_FILE is already set
        if f"export SSL_CERT_FILE={certifi_path}" in content:
            logger.info(f"SSL_CERT_FILE already set in {profile_path}")
            return True
        
        # Add SSL_CERT_FILE to the profile file
        with open(profile_path, 'a') as f:
            f.write(f"\n# Sophia AI SSL Certificate Fix\nexport SSL_CERT_FILE={certifi_path}\n")
        
        logger.info(f"Updated {profile_path} with SSL_CERT_FILE={certifi_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating shell profile: {e}")
        return False

def test_ssl_verification() -> bool:
    """Test SSL certificate verification"""
    try:
        # Set the SSL_CERT_FILE environment variable
        os.environ["SSL_CERT_FILE"] = get_certifi_path()
        
        # Test SSL verification with a simple HTTPS request
        import urllib.request
        response = urllib.request.urlopen("https://www.google.com")
        
        if response.status == 200:
            logger.info("SSL certificate verification successful")
            return True
        else:
            logger.warning(f"SSL certificate verification returned status code: {response.status}")
            return False
    except Exception as e:
        logger.error(f"SSL certificate verification failed: {e}")
        return False

def main():
    print("\n===== Sophia AI SSL Certificate Fix =====\n")
    
    # Get the certifi path
    certifi_path = get_certifi_path()
    print(f"Certifi cacert.pem path: {certifi_path}")
    
    # Create the wrapper script
    if create_wrapper_script():
        print("\n✅ Created wrapper script: run_with_ssl_fix.py")
        print("   Usage: python run_with_ssl_fix.py <script> [args...]")
    else:
        print("\n❌ Failed to create wrapper script")
    
    # Update the .env file
    if update_env_file():
        print("\n✅ Updated .env file with SSL_CERT_FILE")
    else:
        print("\n❌ Failed to update .env file")
    
    # Update the shell profile
    if update_shell_profile():
        print("\n✅ Updated shell profile with SSL_CERT_FILE")
        print("   You need to restart your shell or run 'source ~/.bashrc' or 'source ~/.zshrc'")
    else:
        print("\n❌ Failed to update shell profile")
    
    # Test SSL verification
    if test_ssl_verification():
        print("\n✅ SSL certificate verification successful")
    else:
        print("\n❌ SSL certificate verification failed")
    
    print("\n===== SSL Certificate Fix Complete =====")
    print("\nTo use the SSL certificate fix in your scripts:")
    print("1. Add the following line to your Python scripts:")
    print(f"   os.environ['SSL_CERT_FILE'] = '{certifi_path}'")
    print("2. Or use the wrapper script:")
    print("   python run_with_ssl_fix.py <script> [args...]")
    print("3. Or set the environment variable in your shell:")
    print(f"   export SSL_CERT_FILE={certifi_path}")

if __name__ == "__main__":
    main()
