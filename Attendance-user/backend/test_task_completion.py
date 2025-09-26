#!/usr/bin/env python3
"""
Test script to verify task completion notifications are working correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Mongo import *
from bson import ObjectId
import asyncio

async def test_task_completion_notification():
    """Test the task completion notification system"""
    
    print("🧪 Testing Task Completion Notification System")
    print("=" * 50)
    
    try:
        # Step 1: Find a sample employee and manager
        print("1️⃣ Finding sample users...")
        
        # Find an employee (non-manager)
        employee = Users.find_one({"position": {"$nin": ["Manager", "HR", "Admin"]}})
        if not employee:
            print("❌ No employee found in database")
            return
        
        employee_id = str(employee["_id"])
        employee_name = employee.get("name", "Test Employee")
        print(f"   📋 Employee: {employee_name} ({employee_id})")
        
        # Find a manager
        manager = Users.find_one({"position": "Manager"})
        if not manager:
            print("❌ No manager found in database")
            return
        
        manager_id = str(manager["_id"])
        manager_name = manager.get("name", "Test Manager")
        print(f"   👔 Manager: {manager_name} ({manager_id})")
        
        # Step 2: Create a test task assigned by manager to employee
        print("\n2️⃣ Creating test task...")
        
        task_title = "Test Task - Completion Notification"
        
        # Insert task directly to database
        task_data = {
            "task": task_title,
            "status": "Not completed",
            "date": "25-09-2025",
            "due_date": "26-09-25",
            "userid": employee_id,
            "assigned_by": manager_id,
            "TL": manager_name,
            "priority": "High",
            "subtasks": [],
            "comments": [],
            "files": [],
            "created_at": get_current_timestamp_iso()
        }
        
        result = Tasks.insert_one(task_data)
        task_id = str(result.inserted_id)
        print(f"   ✅ Task created: {task_title} (ID: {task_id})")
        print(f"   📝 Assigned by: {manager_name} ({manager_id})")
        print(f"   👤 Assigned to: {employee_name} ({employee_id})")
        
        # Step 3: Simulate task completion
        print("\n3️⃣ Simulating task completion...")
        
        # Update task status to completed
        update_result = Tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": "Completed", "completed_date": "25-09-2025"}}
        )
        
        if update_result.modified_count > 0:
            print("   ✅ Task status updated to Completed")
            
            # Step 4: Trigger the completion notification
            print("\n4️⃣ Triggering completion notification...")
            
            # Get the updated task
            updated_task = Tasks.find_one({"_id": ObjectId(task_id)})
            
            # Call the create_task_completion_notification function directly
            notifications = await create_task_completion_notification(
                assignee_id=employee_id,
                manager_id=manager_id,
                task_title=task_title,
                assignee_name=employee_name,
                task_id=task_id
            )
            
            print(f"   📨 Notifications sent: {len(notifications)}")
            
            if notifications:
                # Step 5: Verify notification was created
                print("\n5️⃣ Verifying notifications...")
                
                for notification_id in notifications:
                    notification = Notifications.find_one({"_id": ObjectId(notification_id)})
                    if notification:
                        print(f"   ✅ Notification created successfully:")
                        print(f"      📧 To: {notification.get('userid')}")
                        print(f"      📋 Title: {notification.get('title')}")
                        print(f"      💬 Message: {notification.get('message')}")
                        print(f"      🏷️ Type: {notification.get('type')}")
                        print(f"      🔥 Priority: {notification.get('priority')}")
                    else:
                        print(f"   ❌ Notification {notification_id} not found in database")
            else:
                print("   ❌ No notifications were created")
        else:
            print("   ❌ Failed to update task status")
        
        # Step 6: Clean up test data
        print("\n6️⃣ Cleaning up test data...")
        Tasks.delete_one({"_id": ObjectId(task_id)})
        
        # Clean up any notifications created during test
        if 'notifications' in locals():
            for notification_id in notifications:
                Notifications.delete_one({"_id": ObjectId(notification_id)})
        
        print("   🧹 Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    await test_task_completion_notification()

if __name__ == "__main__":
    asyncio.run(main())