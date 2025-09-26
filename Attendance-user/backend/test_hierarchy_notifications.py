#!/usr/bin/env python3
"""
Test script for the enhanced hierarchy-based task completion notifications

This script tests:
1. Employee task completion → Manager notification
2. Manager task completion → HR notification
"""

import sys
import os
from bson.objectid import ObjectId
import asyncio

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Mongo import (
    Users, Tasks, create_task_completion_notification, 
    get_hr_users, get_user_role, add_task_list
)

async def test_hierarchy_notifications():
    """Test the hierarchy-based notification system"""
    print("🧪 Testing Enhanced Hierarchy-based Task Completion Notifications")
    print("=" * 70)
    
    try:
        # Test 1: Find an employee and test employee → manager notification
        print("\n📋 Test 1: Employee Task Completion → Manager Notification")
        employee = Users.find_one({"position": {"$not": {"$regex": "Manager|HR", "$options": "i"}}})
        
        if employee:
            employee_id = str(employee["_id"])
            employee_name = employee.get("name", "Test Employee")
            print(f"👤 Found Employee: {employee_name} (ID: {employee_id})")
            
            # Create a test task for the employee
            task_id = add_task_list(
                task="Test Task for Hierarchy Notification",
                userid=employee_id,
                date="2025-09-25",
                due_date="2025-09-26",
                assigned_by="HR",
                priority="Medium"
            )
            
            if task_id:
                print(f"📝 Created test task: {task_id}")
                
                # Test completion notification
                notifications = await create_task_completion_notification(
                    assignee_id=employee_id,
                    manager_id="HR",  # Simulate HR as manager
                    task_title="Test Task for Hierarchy Notification",
                    assignee_name=employee_name,
                    task_id=task_id
                )
                
                if notifications:
                    print(f"✅ Employee completion notifications sent: {len(notifications)}")
                else:
                    print("❌ No notifications sent for employee completion")
        else:
            print("⚠️  No regular employee found in database")
        
        # Test 2: Find a manager and test manager → HR notification
        print("\n📋 Test 2: Manager Task Completion → HR Notification")
        manager = Users.find_one({"position": {"$regex": "Manager", "$options": "i"}})
        
        if manager:
            manager_id = str(manager["_id"])
            manager_name = manager.get("name", "Test Manager")
            print(f"👤 Found Manager: {manager_name} (ID: {manager_id})")
            
            # Create a test task for the manager
            task_id = add_task_list(
                task="Test Manager Task for HR Notification",
                userid=manager_id,
                date="2025-09-25",
                due_date="2025-09-26",
                assigned_by="HR",
                priority="High"
            )
            
            if task_id:
                print(f"📝 Created test task: {task_id}")
                
                # Test completion notification
                notifications = await create_task_completion_notification(
                    assignee_id=manager_id,
                    manager_id="HR",  # This should be ignored since assignee is manager
                    task_title="Test Manager Task for HR Notification",
                    assignee_name=manager_name,
                    task_id=task_id
                )
                
                if notifications:
                    print(f"✅ Manager completion notifications sent to HR: {len(notifications)}")
                else:
                    print("❌ No notifications sent for manager completion")
        else:
            print("⚠️  No manager found in database")
        
        # Test 3: Check HR users
        print("\n📋 Test 3: HR User Detection")
        hr_users = get_hr_users()
        print(f"👥 Found {len(hr_users)} HR users:")
        for hr_user in hr_users:
            print(f"   - {hr_user.get('name', 'Unknown')} ({hr_user.get('position', 'N/A')})")
        
        # Test 4: Test role detection
        print("\n📋 Test 4: Role Detection")
        test_users = list(Users.find().limit(3))
        for user in test_users:
            user_id = str(user["_id"])
            role = get_user_role(user_id)
            print(f"👤 {user.get('name', 'Unknown')}: Role = {role}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_hierarchy_notifications())