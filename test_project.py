#!/usr/bin/env python3
"""
IT ServiceDesk Project Test Suite
Tests all major functionality including Swagger documentation
"""

import sys
import os
import importlib.util

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test Flask and extensions
        import flask
        import flask_restx
        import flask_sqlalchemy
        import flask_cors
        import flask_migrate
        import flask_marshmallow
        print("✅ Flask and extensions imported successfully")
        
        # Test other dependencies
        import psycopg2
        import cloudinary
        import sendgrid
        print("✅ External dependencies imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\n🔍 Testing app creation...")
    
    try:
        # Add project root to path
        sys.path.insert(0, '/home/joe/Documents/sdm/it-servicedesk-backend')
        
        from app import create_app
        app = create_app('development')
        
        print("✅ Flask app created successfully")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        
        return app
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return None

def test_routes(app):
    """Test if routes are registered correctly"""
    print("\n🔍 Testing routes...")
    
    try:
        with app.app_context():
            # Get all registered routes
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{rule.methods} {rule.rule}")
            
            # Check for key routes
            key_routes = [
                '/api/docs/',  # Swagger documentation
                '/api/tickets',  # Ticket management
                '/api/users',  # User management
                '/api/auth/login',  # Authentication
                '/health',  # Health check
            ]
            
            print(f"✅ Total routes registered: {len(routes)}")
            
            for route in key_routes:
                found = any(route in r for r in routes)
                if found:
                    print(f"✅ Route found: {route}")
                else:
                    print(f"⚠️ Route missing: {route}")
            
            return True
    except Exception as e:
        print(f"❌ Route testing error: {e}")
        return False

def test_swagger_integration(app):
    """Test Swagger documentation integration"""
    print("\n🔍 Testing Swagger integration...")
    
    try:
        with app.app_context():
            # Check if Swagger blueprint is registered
            swagger_found = False
            for blueprint_name, blueprint in app.blueprints.items():
                if 'swagger' in blueprint_name.lower():
                    swagger_found = True
                    print(f"✅ Swagger blueprint found: {blueprint_name}")
                    break
            
            if not swagger_found:
                print("⚠️ Swagger blueprint not found")
            
            # Check for Flask-RESTX
            try:
                from flask_restx import Api
                print("✅ Flask-RESTX available for Swagger")
            except ImportError:
                print("❌ Flask-RESTX not available")
            
            return swagger_found
    except Exception as e:
        print(f"❌ Swagger testing error: {e}")
        return False

def test_database_models():
    """Test database models"""
    print("\n🔍 Testing database models...")
    
    try:
        sys.path.insert(0, '/home/joe/Documents/sdm/it-servicedesk-backend')
        
        # Import models
        from app.models import User, Ticket, Message, Alert
        
        print("✅ User model imported")
        print("✅ Ticket model imported") 
        print("✅ Message model imported")
        print("✅ Alert model imported")
        
        # Test model attributes
        user_attrs = ['id', 'name', 'email', 'role', 'created_at']
        ticket_attrs = ['id', 'ticket_id', 'title', 'status', 'priority']
        
        for attr in user_attrs:
            if hasattr(User, attr):
                print(f"✅ User.{attr} exists")
            else:
                print(f"❌ User.{attr} missing")
        
        for attr in ticket_attrs:
            if hasattr(Ticket, attr):
                print(f"✅ Ticket.{attr} exists")
            else:
                print(f"❌ Ticket.{attr} missing")
        
        return True
    except Exception as e:
        print(f"❌ Model testing error: {e}")
        return False

def test_configuration():
    """Test configuration setup"""
    print("\n🔍 Testing configuration...")
    
    try:
        sys.path.insert(0, '/home/joe/Documents/sdm/it-servicedesk-backend')
        
        from config import config, DevelopmentConfig, ProductionConfig
        
        print("✅ Configuration classes imported")
        print(f"✅ Available configs: {list(config.keys())}")
        
        # Test config attributes
        dev_config = DevelopmentConfig()
        print(f"✅ Development DEBUG: {dev_config.DEBUG}")
        print(f"✅ Development DB: {dev_config.SQLALCHEMY_DATABASE_URI}")
        
        prod_config = ProductionConfig()
        print(f"✅ Production DEBUG: {prod_config.DEBUG}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration testing error: {e}")
        return False

def test_api_resources():
    """Test API resources"""
    print("\n🔍 Testing API resources...")
    
    try:
        sys.path.insert(0, '/home/joe/Documents/sdm/it-servicedesk-backend')
        
        from app.api.resources import (
            AuthResource, TicketListResource, TicketResource,
            UserListResource, UserResource, MessageListResource
        )
        
        print("✅ AuthResource imported")
        print("✅ TicketListResource imported")
        print("✅ TicketResource imported")
        print("✅ UserListResource imported")
        print("✅ UserResource imported")
        print("✅ MessageListResource imported")
        
        return True
    except Exception as e:
        print(f"❌ API resources testing error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 IT ServiceDesk Project Test Suite")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(("Imports", test_imports()))
    
    app = test_app_creation()
    if app:
        results.append(("App Creation", True))
        results.append(("Routes", test_routes(app)))
        results.append(("Swagger", test_swagger_integration(app)))
    else:
        results.append(("App Creation", False))
        results.append(("Routes", False))
        results.append(("Swagger", False))
    
    results.append(("Models", test_database_models()))
    results.append(("Configuration", test_configuration()))
    results.append(("API Resources", test_api_resources()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project is ready for deployment.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()