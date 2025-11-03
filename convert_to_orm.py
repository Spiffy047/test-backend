#!/usr/bin/env python3
"""
Script to convert remaining raw SQL queries to ORM equivalents
This ensures the entire project uses proper ORM patterns
"""

import os
import re

def convert_file_to_orm(file_path):
    """Convert raw SQL in a file to ORM equivalents"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Common ORM conversions
    conversions = [
        # Simple SELECT queries
        (r'db\.session\.execute\(text\(\s*"SELECT \* FROM users"\s*\)\)', 
         'User.query.all()'),
        
        # COUNT queries
        (r'db\.session\.execute\(text\(\s*"SELECT COUNT\(\*\) FROM (\w+)"\s*\)\)\.scalar\(\)',
         r'db.session.query(\1).count()'),
        
        # Basic WHERE clauses
        (r'db\.session\.execute\(text\(\s*"SELECT \* FROM users WHERE role = :role"\s*\), \{[\'"]role[\'"]:\s*(\w+)\}\)',
         r'User.query.filter_by(role=\1).all()'),
    ]
    
    # Apply conversions
    for pattern, replacement in conversions:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Convert all Python files in the project"""
    
    converted_files = []
    
    # Walk through all Python files
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if convert_file_to_orm(file_path):
                    converted_files.append(file_path)
    
    print(f"Converted {len(converted_files)} files:")
    for file_path in converted_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    main()