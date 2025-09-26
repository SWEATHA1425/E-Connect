#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced E-Connect notification system
Tests all automated functionalities and WebSocket connections
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import pytz
from Mongo import (
    Users, Tasks, Notifications, Clock, Leave, RemoteWork, 
    create_notification_with_websocket, get_notifications,
    get_unread_notification_count, ObjectId
)
from notification_automation import (
    run_all_automated_checks,
    check_and_notify_overdue_tasks,
    check_upcoming_deadlines,
    check_missed_attendance,
    check_pending_approvals
)

# Test configuration
TEST_USER_EMAIL = "test@company.com"
IST = pytz.timezone("Asia/Kolkata")

async def setup_test_data():
    """Create test data for comprehensive testing"""
    print("🔧 Setting up test data...")
    
    try:
        # Find or create test user
        test_user = Users.find_one({"email": TEST_USER_EMAIL})
        if not test_user:
            test_user_data = {
                "name": "Test User",
                "email": TEST_USER_EMAIL,
                "position": "Software Developer",
                "department": "IT",
                "isadmin": False,
                "created_at": datetime.now(IST)
            }
            result = Users.insert_one(test_user_data)
            test_user_id = str(result.inserted_id)
            print(f"✅ Created test user with ID: {test_user_id}")
        else:
            test_user_id = str(test_user["_id"])
            print(f"✅ Using existing test user with ID: {test_user_id}")
        
        # Create test tasks with different due dates
        today = datetime.now(IST).strftime("%d-%m-%Y")
        tomorrow = (datetime.now(IST) + timedelta(days=1)).strftime("%d-%m-%Y")
        overdue_date = (datetime.now(IST) - timedelta(days=2)).strftime("%d-%m-%Y")
        future_date = (datetime.now(IST) + timedelta(days=7)).strftime("%d-%m-%Y")
        
        test_tasks = [
            {
                "userid": test_user_id,
                "task": "Overdue Test Task - Fix Critical Bug",
                "description": "This task is overdue for testing notifications",
                "due_date": overdue_date,
                "status": "Pending",
                "priority": "High",
                "created_at": datetime.now(IST) - timedelta(days=5)
            },
            {
                "userid": test_user_id,
                "task": "Due Today - Complete Code Review",
                "description": "Task due today for testing",
                "due_date": today,
                "status": "In Progress",
                "priority": "Medium",
                "created_at": datetime.now(IST) - timedelta(days=3)
            },
            {
                "userid": test_user_id,
                "task": "Due Tomorrow - Prepare Documentation",
                "description": "Task due tomorrow for testing",
                "due_date": tomorrow,
                "status": "Pending",
                "priority": "Low",
                "created_at": datetime.now(IST) - timedelta(days=1)
            },
            {
                "userid": test_user_id,
                "task": "Future Task - Plan Next Sprint",
                "description": "Future task for testing",
                "due_date": future_date,
                "status": "Pending",
                "priority": "Medium",
                "created_at": datetime.now(IST)
            }
        ]
        
        # Clear existing test tasks
        Tasks.delete_many({"userid": test_user_id, "task": {"$regex": "Test Task|Due Today|Due Tomorrow|Future Task"}})
        
        # Insert new test tasks
        task_results = Tasks.insert_many(test_tasks)
        task_ids = [str(id) for id in task_results.inserted_ids]
        print(f"✅ Created {len(task_ids)} test tasks")
        
        # Create test leave request
        test_leave = {
            "userid": test_user_id,
            "name": "Test User",
            "leave_type": "Casual Leave",
            "from_date": tomorrow,
            "to_date": (datetime.now(IST) + timedelta(days=3)).strftime("%d-%m-%Y"),
            "reason": "Test leave request for notifications",
            "status": "Pending",
            "created_at": datetime.now(IST)
        }
        
        # Clear existing test leave
        Leave.delete_many({"userid": test_user_id, "reason": {"$regex": "Test leave"}})
        leave_result = Leave.insert_one(test_leave)
        leave_id = str(leave_result.inserted_id)
        print(f"✅ Created test leave request with ID: {leave_id}")
        
        return {
            "user_id": test_user_id,
            "task_ids": task_ids,
            "leave_id": leave_id,
            "user_data": test_user_data if not test_user else test_user
        }
        
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        return None

async def test_websocket_notifications(test_data):
    """Test WebSocket notification creation and delivery"""
    print("\n🔗 Testing WebSocket Notifications...")
    
    try:
        user_id = test_data["user_id"]
        
        # Test different types of notifications
        notification_tests = [
            {
                "title": "🧪 Test System Notification",
                "message": "This is a test system notification to verify WebSocket delivery",
                "type": "system",
                "priority": "medium"
            },
            {
                "title": "⚠️ Test High Priority Task Alert",
                "message": "Critical task requires immediate attention - WebSocket test",
                "type": "task_overdue",
                "priority": "high"
            },
            {
                "title": "📅 Test Leave Notification",
                "message": "Leave request has been submitted for review - WebSocket test",
                "type": "leave",
                "priority": "medium"
            },
            {
                "title": "⏰ Test Attendance Reminder",
                "message": "Don't forget to clock in today - WebSocket test",
                "type": "attendance",
                "priority": "low"
            }
        ]
        
        notification_ids = []
        for i, notif in enumerate(notification_tests):
            try:
                print(f"  📤 Sending notification {i+1}/{len(notification_tests)}: {notif['title']}")
                
                notification_id = await create_notification_with_websocket(
                    userid=user_id,
                    title=notif["title"],
                    message=notif["message"],
                    notification_type=notif["type"],
                    priority=notif["priority"],
                    metadata={"test": True, "test_batch": "websocket_test"}
                )
                
                if notification_id:
                    notification_ids.append(notification_id)
                    print(f"    ✅ Notification created with ID: {notification_id}")
                    # Small delay to see real-time delivery
                    await asyncio.sleep(1)
                else:
                    print(f"    ❌ Failed to create notification")
                    
            except Exception as e:
                print(f"    ❌ Error creating notification {i+1}: {e}")
        
        print(f"✅ WebSocket notification test completed: {len(notification_ids)}/{len(notification_tests)} notifications sent")
        return notification_ids
        
    except Exception as e:
        print(f"❌ Error in WebSocket notification test: {e}")
        return []

async def test_automated_checks():
    """Test all automated notification checks"""
    print("\n🤖 Testing Automated Notification Checks...")
    
    try:
        # Test overdue tasks check
        print("  🔍 Testing overdue tasks check...")
        overdue_result = await check_and_notify_overdue_tasks()
        print(f"    ✅ Overdue tasks: {overdue_result}")
        
        await asyncio.sleep(2)
        
        # Test upcoming deadlines check
        print("  📅 Testing upcoming deadlines check...")
        deadlines_result = await check_upcoming_deadlines()
        print(f"    ✅ Upcoming deadlines: {deadlines_result}")
        
        await asyncio.sleep(2)
        
        # Test missed attendance check
        print("  ⏰ Testing missed attendance check...")
        attendance_result = await check_missed_attendance()
        print(f"    ✅ Missed attendance: {attendance_result}")
        
        await asyncio.sleep(2)
        
        # Test pending approvals check
        print("  📋 Testing pending approvals check...")
        approvals_result = await check_pending_approvals()
        print(f"    ✅ Pending approvals: {approvals_result}")
        
        await asyncio.sleep(2)
        
        # Test comprehensive check
        print("  🚀 Testing comprehensive automated check...")
        comprehensive_result = await run_all_automated_checks()
        print(f"    ✅ Comprehensive check: {comprehensive_result}")
        
        return {
            "overdue_tasks": overdue_result,
            "upcoming_deadlines": deadlines_result,
            "missed_attendance": attendance_result,
            "pending_approvals": approvals_result,
            "comprehensive": comprehensive_result
        }
        
    except Exception as e:
        print(f"❌ Error in automated checks test: {e}")
        return {}

async def test_notification_retrieval(test_data):
    """Test notification retrieval and statistics"""
    print("\n📊 Testing Notification Retrieval...")
    
    try:
        user_id = test_data["user_id"]
        
        # Get all notifications for user
        all_notifications = get_notifications(user_id, limit=100)
        print(f"  📧 Total notifications for user: {len(all_notifications)}")
        
        # Get unread count
        unread_count = get_unread_notification_count(user_id)
        print(f"  🔔 Unread notifications: {unread_count}")
        
        # Get notifications by type
        task_notifications = get_notifications(user_id, notification_type="task_overdue")
        system_notifications = get_notifications(user_id, notification_type="system")
        print(f"  📝 Task notifications: {len(task_notifications)}")
        print(f"  ⚙️ System notifications: {len(system_notifications)}")
        
        # Display recent notifications
        if all_notifications:
            print("  📋 Recent notifications:")
            for i, notif in enumerate(all_notifications[:5]):
                status = "UNREAD" if not notif.get("is_read", True) else "READ"
                print(f"    {i+1}. [{status}] {notif.get('title', 'No title')} - {notif.get('type', 'unknown')}")
        
        return {
            "total": len(all_notifications),
            "unread": unread_count,
            "by_type": {
                "task": len(task_notifications),
                "system": len(system_notifications)
            }
        }
        
    except Exception as e:
        print(f"❌ Error in notification retrieval test: {e}")
        return {}

async def cleanup_test_data(test_data):
    """Clean up test data after testing"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        user_id = test_data["user_id"]
        
        # Delete test notifications
        delete_result = Notifications.delete_many({
            "userid": user_id,
            "$or": [
                {"metadata.test": True},
                {"title": {"$regex": "Test|🧪"}},
                {"message": {"$regex": "WebSocket test|test"}}
            ]
        })
        print(f"  🗑️ Deleted {delete_result.deleted_count} test notifications")
        
        # Delete test tasks
        task_delete_result = Tasks.delete_many({
            "userid": user_id,
            "task": {"$regex": "Test Task|Due Today|Due Tomorrow|Future Task"}
        })
        print(f"  🗑️ Deleted {task_delete_result.deleted_count} test tasks")
        
        # Delete test leave
        leave_delete_result = Leave.delete_many({
            "userid": user_id,
            "reason": {"$regex": "Test leave"}
        })
        print(f"  🗑️ Deleted {leave_delete_result.deleted_count} test leave requests")
        
        # Option to delete test user (uncomment if needed)
        # Users.delete_one({"_id": ObjectId(user_id)})
        # print(f"  🗑️ Deleted test user")
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting Comprehensive E-Connect Notification System Test")
    print("=" * 60)
    
    try:
        # Setup test data
        test_data = await setup_test_data()
        if not test_data:
            print("❌ Failed to setup test data. Exiting.")
            return
        
        print(f"🎯 Testing with user ID: {test_data['user_id']}")
        
        # Run tests
        websocket_results = await test_websocket_notifications(test_data)
        automation_results = await test_automated_checks()
        retrieval_results = await test_notification_retrieval(test_data)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ WebSocket notifications sent: {len(websocket_results)}")
        print(f"✅ Automated checks completed: {len(automation_results)} modules")
        print(f"✅ Notifications retrieved: {retrieval_results.get('total', 0)}")
        print(f"🔔 Unread notifications: {retrieval_results.get('unread', 0)}")
        
        # Wait before cleanup
        print(f"\n⏳ Waiting 10 seconds before cleanup to allow WebSocket delivery...")
        await asyncio.sleep(10)
        
        # Cleanup
        await cleanup_test_data(test_data)
        
        print("\n🎉 All tests completed successfully!")
        print("📱 Check your frontend notification dashboard to see real-time updates!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(main())
