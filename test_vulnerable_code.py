#!/usr/bin/env python3
"""
Test file with deliberately vulnerable code patterns
for testing Codacy security analysis capabilities
"""

import os
import subprocess
import sqlite3

# SQL Injection vulnerability
def get_user_data(user_id):
    """Vulnerable SQL query - direct string interpolation"""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)  # SQL injection risk
    return cursor.fetchall()

# Command injection vulnerability  
def process_file(filename):
    """Vulnerable command execution"""
    cmd = f"cat {filename}"
    result = subprocess.run(cmd, shell=True, capture_output=True)  # Command injection risk
    return result.stdout

# Hardcoded secrets
API_KEY = "sk-1234567890abcdef"  # Hardcoded API key
DATABASE_PASSWORD = "super_secret_password"  # Hardcoded password

# Insecure random number generation
import random
def generate_token():
    """Weak random token generation"""
    return str(random.randint(100000, 999999))  # Cryptographically weak

# Path traversal vulnerability
def read_config_file(config_name):
    """Vulnerable file reading"""
    file_path = f"/app/config/{config_name}"
    with open(file_path, 'r') as f:  # Path traversal risk
        return f.read()

# Insecure deserialization
import pickle
def load_user_session(session_data):
    """Vulnerable pickle deserialization"""
    return pickle.loads(session_data)  # Arbitrary code execution risk

# Missing error handling
def divide_numbers(a, b):
    """Function without proper error handling"""
    return a / b  # Division by zero risk

# Overly complex function
def complex_business_logic(data, config, options, filters, transformations, validations, enrichments, aggregations):
    """Overly complex function with too many parameters and nested logic"""
    if data and config:
        if options.get('enable_processing'):
            if filters:
                filtered_data = []
                for item in data:
                    if item.get('status') == 'active':
                        if transformations:
                            for transform in transformations:
                                if transform.get('type') == 'normalize':
                                    if validations:
                                        for validation in validations:
                                            if validation.get('required'):
                                                if enrichments:
                                                    for enrichment in enrichments:
                                                        if enrichment.get('enabled'):
                                                            if aggregations:
                                                                for agg in aggregations:
                                                                    if agg.get('method') == 'sum':
                                                                        filtered_data.append({
                                                                            'original': item,
                                                                            'transformed': transform,
                                                                            'validated': validation,
                                                                            'enriched': enrichment,
                                                                            'aggregated': agg
                                                                        })
                return filtered_data
    return None

if __name__ == "__main__":
    # Test the vulnerable functions
    print("Testing vulnerable code patterns...")
    user_data = get_user_data("1 OR 1=1")
    file_content = process_file("../../../etc/passwd")
    token = generate_token()
    config = read_config_file("../../../etc/hosts")
    print(f"Generated token: {token}") 