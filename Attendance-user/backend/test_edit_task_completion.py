#!/usr/bin/env python3
"""
Test script for the enhanced hierarchy-based task completion notifications via task editing

This script tests the edit_task flow to ensure hierarchy notifications work
"""

import sys
import os
from bson.objectid import ObjectId
import asyncio

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Mongo import (
    Users, Tasks, edit_the_task, add_task_list
)

async def test_edit_task_completion():
    """Test the hierarchy notifications through edit_task function"""
    print("🧪 Testing Edit Task Completion Hierarchy Notifications")
    print("=" * 60)
    
    try:
        # Test 1: Find an employee and create/edit a task
        print("\n📋 Test 1: Employee Task Edit → Manager Notification")
        employee = Users.find_one({"position": {"$not": {"$regex": "Manager|HR", "$options": "i"}}})
        
        if employee:
            employee_id = str(employee["_id"])
            employee_name = employee.get("name", "Test Employee")
            print(f"👤 Found Employee: {employee_name} (ID: {employee_id})")
            
            # Create a test task for the employee
            task_id = add_task_list(
                task="Test Task for Edit Completion",
                userid=employee_id,
                date="2025-09-25",
                due_date="2025-09-26",
                assigned_by="HR",
                priority="Medium"
            )
            
            if task_id:
                print(f"📝 Created test task: {task_id}")
                
                # Now edit the task to mark it as completed
                result = edit_the_task(
                    taskid=task_id,
                    userid=employee_id,
                    cdate="2025-09-25",
                    due_date="2025-09-26",
                    status="Completed"  # This should trigger hierarchy notifications
                )
                
                print(f"✅ Task edit result: {result}")
        else:
            print("⚠️  No regular employee found in database")
        
        # Test 2: Find a manager and test edit completion
        print("\n📋 Test 2: Manager Task Edit → HR Notification")
        manager = Users.find_one({"position": {"$regex": "Manager", "$options": "i"}})
        
        if manager:
            manager_id = str(manager["_id"])
            manager_name = manager.get("name", "Test Manager")
            print(f"👤 Found Manager: {manager_name} (ID: {manager_id})")
            
            # Create a test task for the manager
            task_id = add_task_list(
                task="Test Manager Task for Edit Completion",
                userid=manager_id,
                date="2025-09-25",
                due_date="2025-09-26",
                assigned_by="HR",
                priority="High"
            )
            
            if task_id:
                print(f"📝 Created test task: {task_id}")
                
                # Now edit the task to mark it as completed
                result = edit_the_task(
                    taskid=task_id,
                    userid=manager_id,
                    cdate="2025-09-25",
                    due_date="2025-09-26",
                    status="Completed"  # This should trigger HR notifications
                )
                
                print(f"✅ Task edit result: {result}")
        else:
            print("⚠️  No manager found in database")
        
        print("\n🎉 Edit task completion tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def run_sync_test():
    """Run the test synchronously"""
    print("🧪 Testing Edit Task Completion Hierarchy Notifications (Sync)")
    print("=" * 60)
    
    try:
        # Test with an employee
        print("\n📋 Test: Employee Task Status Change → Manager Notification")
        employee = Users.find_one({"position": {"$not": {"$regex": "Manager|HR", "$options": "i"}}})
        
        if employee:
            employee_id = str(employee["_id"])
            employee_name = employee.get("name", "Test Employee")
            print(f"👤 Found Employee: {employee_name} (ID: {employee_id})")
            
            # Create a test task
            task_id = add_task_list(
                task="Test Edit Status Change",
                userid=employee_id,
                date="2025-09-25",
                due_date="2025-09-26",
                assigned_by="HR",
                priority="Medium"
            )
            
            if task_id:
                print(f"📝 Created test task: {task_id}")
                
                # Edit task status to completed
                result = edit_the_task(
                    taskid=task_id,
                    userid=employee_id,
                    cdate="2025-09-25",
                    due_date="2025-09-26",
                    status="Completed"
                )
                
                print(f"✅ Edit result: {result}")
                print("🔔 Check notifications for hierarchy alerts!")
        
        # Test with a manager
        print("\n📋 Test: Manager Task Status Change → HR Notification")
        manager = Users.find_one({"position": {"$regex": "Manager", "$options": "i"}})
        
        if manager:
            manager_id = str(manager["_id"])
            manager_name = manager.get("name", "Test Manager")
            print(f"👤 Found Manager: {manager_name} (ID: {manager_id})")
            
            # Create a test task
            task_id = add_task_list(
                task="Test Manager Edit Status Change",
                userid=manager_id,
                date="2025-09-25",
                due_date="2025-09-26",
                assigned_by="HR",
                priority="High"
            )
            
            if task_id:
                print(f"📝 Created test task: {task_id}")
                
                # Edit task status to completed
                result = edit_the_task(
                    taskid=task_id,
                    userid=manager_id,
                    cdate="2025-09-25",
                    due_date="2025-09-26",
                    status="Completed"
                )
                
                print(f"✅ Edit result: {result}")
                print("🔔 Check notifications for HR alerts!")
        
        print("\n🎉 Sync tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Async test (recommended)")
    print("2. Sync test")
    
    # Run sync test by default
    run_sync_test()