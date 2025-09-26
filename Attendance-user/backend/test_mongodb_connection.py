#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Tests the MongoDB connection and provides detailed error information
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys

def test_mongodb_connection():
    """Test MongoDB connection and provide detailed error information"""
    print("🔍 Testing MongoDB Connection...")
    print("=" * 50)
    
    try:
        # Connection string from Mongo.py
        connection_string = "mongodb://localhost:27017"
        print(f"📡 Attempting to connect to: {connection_string}")
        
        # Create client with timeout
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        print("⏳ Testing server connection...")
        client.admin.command('ping')
        
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client["RBG_AI"]
        print(f"📂 Connected to database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        # Test basic operations
        test_collection = db["test_connection"]
        test_doc = {"test": "connection_test", "timestamp": "2025-01-01"}
        
        # Insert test document
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Remove test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("🗑️ Test document removed")
        
        print("\n🎉 All MongoDB tests passed successfully!")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        print("💡 MongoDB server is not running or not accessible")
        return False
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server Selection Timeout: {e}")
        print("💡 MongoDB server is not responding within the timeout period")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"🔍 Error Type: {type(e).__name__}")
        return False

def check_mongodb_service():
    """Check MongoDB service status on Windows"""
    import subprocess
    
    print("\n🔍 Checking MongoDB Service Status...")
    print("=" * 50)
    
    try:
        # Check MongoDB service
        result = subprocess.run(
            ["powershell", "-Command", "Get-Service -Name 'MongoDB' -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("📊 MongoDB Service Found:")
            print(result.stdout)
        else:
            print("⚠️ MongoDB service not found with name 'MongoDB'")
            
        # Check for alternative MongoDB service names
        alt_names = ["mongod", "MongoDBCompass", "MongoDB Community Server"]
        for name in alt_names:
            result = subprocess.run(
                ["powershell", "-Command", f"Get-Service -Name '*{name}*' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print(f"📊 Found MongoDB service with pattern '{name}':")
                print(result.stdout)
                
    except Exception as e:
        print(f"❌ Error checking service: {e}")

def provide_solutions():
    """Provide solutions for common MongoDB connection issues"""
    print("\n🔧 Common Solutions:")
    print("=" * 50)
    print("1. Start MongoDB Service:")
    print("   - Run: Start-Service -Name 'MongoDB'")
    print("   - Or: net start MongoDB")
    print("")
    print("2. Install MongoDB if not installed:")
    print("   - Download from: https://www.mongodb.com/try/download/community")
    print("   - Or use chocolatey: choco install mongodb")
    print("")
    print("3. Check MongoDB installation:")
    print("   - Look for mongod.exe in Program Files")
    print("   - Verify MongoDB is in system PATH")
    print("")
    print("4. Manual MongoDB start:")
    print("   - Navigate to MongoDB bin directory")
    print("   - Run: mongod --dbpath C:\\data\\db")
    print("")
    print("5. Alternative connection strings to try:")
    print("   - mongodb://127.0.0.1:27017")
    print("   - mongodb://localhost:27017/RBG_AI")

if __name__ == "__main__":
    print("🚀 MongoDB Connection Diagnostic Tool")
    print("=" * 50)
    
    # Check service status first
    check_mongodb_service()
    
    # Test connection
    success = test_mongodb_connection()
    
    if not success:
        provide_solutions()
        sys.exit(1)
    else:
        print("\n✅ MongoDB is working correctly!")
        sys.exit(0)
