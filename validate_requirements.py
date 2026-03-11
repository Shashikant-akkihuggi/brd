#!/usr/bin/env python3
"""
Validate requirements files for Docker build.
Checks for invalid packages like python-cors.
"""

import os
import sys
from pathlib import Path

def check_file_for_invalid_deps(filepath):
    """Check a requirements file for invalid dependencies."""
    invalid_packages = ['python-cors', 'flask-cors', 'django-cors']
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    print(f"\n📄 Checking: {filepath}")
    print("=" * 60)
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    found_invalid = False
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Check for invalid packages
        for invalid_pkg in invalid_packages:
            if invalid_pkg in line.lower():
                print(f"❌ Line {i}: Found invalid package: {line}")
                found_invalid = True
                break
    
    if not found_invalid:
        print(f"✅ No invalid dependencies found")
        print(f"📊 Total dependencies: {sum(1 for l in lines if l.strip() and not l.strip().startswith('#'))}")
    
    return not found_invalid

def main():
    """Main validation function."""
    print("=" * 60)
    print("🔍 Docker Requirements Validation")
    print("=" * 60)
    
    # Find all requirements files
    requirements_files = [
        'backend/requirements.txt',
        'backend/requirements_enhanced.txt',
    ]
    
    all_valid = True
    
    for req_file in requirements_files:
        if not check_file_for_invalid_deps(req_file):
            all_valid = False
    
    print("\n" + "=" * 60)
    print("📋 Dockerfile Analysis")
    print("=" * 60)
    
    # Check which file Dockerfile uses
    dockerfile_path = 'Dockerfile'
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
        if 'requirements_enhanced.txt' in content:
            print("✅ Dockerfile uses: backend/requirements_enhanced.txt")
            print("   Command: COPY backend/requirements_enhanced.txt requirements.txt")
        elif 'backend/requirements.txt' in content:
            print("✅ Dockerfile uses: backend/requirements.txt")
            print("   Command: COPY backend/requirements.txt requirements.txt")
        else:
            print("⚠️  Could not determine which requirements file is used")
    
    print("\n" + "=" * 60)
    if all_valid:
        print("✅ VALIDATION PASSED")
        print("=" * 60)
        print("\n🎉 All requirements files are valid!")
        print("📦 No invalid dependencies found")
        print("🚀 Docker build should succeed")
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print("=" * 60)
        print("\n⚠️  Invalid dependencies found!")
        print("🔧 Please remove invalid packages before deploying")
        return 1

if __name__ == '__main__':
    sys.exit(main())
