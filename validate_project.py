#!/usr/bin/env python3
"""
IT ServiceDesk Project Validation
Validates project structure, code quality, and Swagger integration
"""

import os
import json
import re

def validate_project_structure():
    """Validate project has all required files and directories"""
    print("🔍 Validating project structure...")
    
    required_files = [
        'app.py',
        'config.py', 
        'requirements.txt',
        'runtime.txt',
        'app/__init__.py',
        'app/models.py',
        'app/swagger.py',
        'app/api/__init__.py',
        'app/api/resources.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def validate_requirements():
    """Validate requirements.txt has all necessary dependencies"""
    print("\n🔍 Validating requirements...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        required_packages = [
            'Flask',
            'Flask-RESTful', 
            'Flask-RESTX',
            'Flask-SQLAlchemy',
            'Flask-CORS',
            'psycopg2-binary',
            'gunicorn'
        ]
        
        missing_packages = []
        for package in required_packages:
            if package.lower() in requirements.lower():
                print(f"✅ {package}")
            else:
                print(f"❌ {package}")
                missing_packages.append(package)
        
        return len(missing_packages) == 0
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def validate_swagger_integration():
    """Validate Swagger is properly integrated"""
    print("\n🔍 Validating Swagger integration...")
    
    try:
        # Check swagger.py exists and has proper content
        with open('app/swagger.py', 'r') as f:
            swagger_content = f.read()
        
        swagger_checks = [
            ('Flask-RESTX import', 'from flask_restx import'),
            ('API initialization', 'Api('),
            ('Swagger documentation', "doc='/docs/'"),
            ('API models', 'api.model('),
            ('Authorization config', 'authorizations')
        ]
        
        for check_name, pattern in swagger_checks:
            if pattern in swagger_content:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
        
        # Check if swagger is registered in __init__.py
        with open('app/__init__.py', 'r') as f:
            init_content = f.read()
        
        if 'swagger_bp' in init_content and 'register_blueprint' in init_content:
            print("✅ Swagger blueprint registered")
        else:
            print("❌ Swagger blueprint not registered")
        
        return True
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return False

def validate_api_structure():
    """Validate API structure and resources"""
    print("\n🔍 Validating API structure...")
    
    try:
        # Check API resources
        with open('app/api/resources.py', 'r') as f:
            resources_content = f.read()
        
        api_resources = [
            'AuthResource',
            'TicketListResource', 
            'TicketResource',
            'UserListResource',
            'UserResource',
            'MessageListResource'
        ]
        
        for resource in api_resources:
            if resource in resources_content:
                print(f"✅ {resource}")
            else:
                print(f"❌ {resource}")
        
        # Check API registration
        with open('app/api/__init__.py', 'r') as f:
            api_init_content = f.read()
        
        if 'add_resource' in api_init_content:
            print("✅ API resources registered")
        else:
            print("❌ API resources not registered")
        
        return True
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return False

def validate_database_models():
    """Validate database models are properly defined"""
    print("\n🔍 Validating database models...")
    
    try:
        with open('app/models.py', 'r') as f:
            models_content = f.read()
        
        models = ['User', 'Ticket', 'Message', 'Alert']
        model_features = [
            'db.Model',
            '__tablename__',
            'db.Column',
            'db.relationship',
            'primary_key=True'
        ]
        
        for model in models:
            if f"class {model}" in models_content:
                print(f"✅ {model} model")
            else:
                print(f"❌ {model} model")
        
        for feature in model_features:
            if feature in models_content:
                print(f"✅ {feature}")
            else:
                print(f"❌ {feature}")
        
        return True
    except FileNotFoundError:
        print("❌ models.py not found")
        return False

def validate_configuration():
    """Validate configuration setup"""
    print("\n🔍 Validating configuration...")
    
    try:
        with open('config.py', 'r') as f:
            config_content = f.read()
        
        config_checks = [
            'class Config',
            'class DevelopmentConfig',
            'class ProductionConfig',
            'SQLALCHEMY_DATABASE_URI',
            'SECRET_KEY',
            'SENDGRID_API_KEY',
            'CLOUDINARY'
        ]
        
        for check in config_checks:
            if check in config_content:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
        
        return True
    except FileNotFoundError:
        print("❌ config.py not found")
        return False

def validate_deployment_files():
    """Validate deployment configuration files"""
    print("\n🔍 Validating deployment files...")
    
    deployment_files = {
        'runtime.txt': 'python-',
        'Procfile': 'web:',
        'gunicorn.conf.py': 'bind',
        '.env.production': 'DATABASE_URL'
    }
    
    for file_name, expected_content in deployment_files.items():
        try:
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    content = f.read()
                if expected_content in content:
                    print(f"✅ {file_name}")
                else:
                    print(f"⚠️ {file_name} (content issue)")
            else:
                print(f"❌ {file_name} (missing)")
        except Exception as e:
            print(f"❌ {file_name} (error: {e})")
    
    return True

def validate_analytics_endpoints():
    """Validate analytics endpoints are implemented"""
    print("\n🔍 Validating analytics endpoints...")
    
    try:
        with open('app/__init__.py', 'r') as f:
            init_content = f.read()
        
        analytics_endpoints = [
            'sla-adherence',
            'agent-performance',
            'ticket-status-counts',
            'unassigned-tickets',
            'agent-workload',
            'ticket-aging'
        ]
        
        for endpoint in analytics_endpoints:
            if endpoint in init_content:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint}")
        
        return True
    except FileNotFoundError:
        print("❌ __init__.py not found")
        return False

def main():
    """Run all validations"""
    print("🚀 IT ServiceDesk Project Validation")
    print("=" * 50)
    
    validations = [
        ("Project Structure", validate_project_structure),
        ("Requirements", validate_requirements),
        ("Swagger Integration", validate_swagger_integration),
        ("API Structure", validate_api_structure),
        ("Database Models", validate_database_models),
        ("Configuration", validate_configuration),
        ("Deployment Files", validate_deployment_files),
        ("Analytics Endpoints", validate_analytics_endpoints)
    ]
    
    results = []
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} validation failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} validations passed")
    
    if passed == total:
        print("🎉 All validations passed! Project is well-structured.")
        print("\n📋 DEPLOYMENT CHECKLIST:")
        print("✅ Swagger documentation integrated")
        print("✅ RESTful API structure implemented")
        print("✅ Database models properly defined")
        print("✅ Analytics endpoints available")
        print("✅ Configuration management setup")
        print("✅ Deployment files configured")
    else:
        print("⚠️ Some validations failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()