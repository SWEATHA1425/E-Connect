#!/usr/bin/env python3
import asyncio
from datetime import datetime
import pytz
from Mongo import Tasks, Users, Notifications, ObjectId

async def check_overdue_tasks_debug():
    """Debug function to check for overdue tasks"""
    try:
        current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        current_date = current_time.strftime("%d-%m-%Y")
        print(f"🔍 Current date: {current_date}")
        print(f"🔍 Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Find all tasks for user Sadhana Shree
        user = Users.find_one({"name": {"$regex": "Sadhana", "$options": "i"}})
        if user:
            userid = str(user["_id"])
            print(f"👤 Found user: {user['name']} (ID: {userid})")
            
            # Find all tasks for this user
            user_tasks = list(Tasks.find({"userid": userid}))
            print(f"📋 Total tasks for user: {len(user_tasks)}")
            
            for task in user_tasks:
                due_date_str = task.get("due_date")
                status = task.get("status", "Pending")
                task_title = task.get("task")
                task_id = str(task.get("_id"))
                
                print(f"\n📝 Task: {task_title}")
                print(f"   Due Date: {due_date_str}")
                print(f"   Status: {status}")
                print(f"   Task ID: {task_id}")
                
                if due_date_str:
                    try:
                        # Parse due date (format: DD-MM-YYYY)
                        due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
                        current_date_obj = datetime.strptime(current_date, "%d-%m-%Y")
                        
                        days_diff = (current_date_obj - due_date).days
                        
                        if days_diff > 0:
                            print(f"   🚨 OVERDUE by {days_diff} days!")
                        elif days_diff == 0:
                            print(f"   ⏰ Due TODAY!")
                        else:
                            print(f"   ✅ Due in {abs(days_diff)} days")
                            
                        # Check if there are existing notifications for this task
                        overdue_notifications = list(Notifications.find({
                            "userid": userid,
                            "type": "task_overdue",
                            "related_id": task_id
                        }))
                        
                        due_soon_notifications = list(Notifications.find({
                            "userid": userid,
                            "type": "task_due_soon",
                            "related_id": task_id
                        }))
                        
                        print(f"   📬 Overdue notifications: {len(overdue_notifications)}")
                        print(f"   📬 Due soon notifications: {len(due_soon_notifications)}")
                        
                    except ValueError:
                        print(f"   ⚠️ Invalid date format: {due_date_str}")
        else:
            print("❌ User 'Sadhana Shree' not found")
            
        # Check all overdue tasks across all users
        print(f"\n" + "="*50)
        print("🔍 CHECKING ALL OVERDUE TASKS")
        print("="*50)
        
        all_tasks = list(Tasks.find({"status": {"$ne": "Completed"}}))
        overdue_count = 0
        
        for task in all_tasks:
            due_date_str = task.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
                    current_date_obj = datetime.strptime(current_date, "%d-%m-%Y")
                    
                    if due_date < current_date_obj:
                        overdue_count += 1
                        user_info = Users.find_one({"_id": ObjectId(task.get("userid"))})
                        user_name = user_info.get("name", "Unknown") if user_info else "Unknown"
                        
                        print(f"🚨 Overdue Task #{overdue_count}:")
                        print(f"   User: {user_name}")
                        print(f"   Task: {task.get('task')}")
                        print(f"   Due: {due_date_str}")
                        print(f"   Status: {task.get('status', 'Pending')}")
                        print(f"   Days overdue: {(current_date_obj - due_date).days}")
                        
                except ValueError:
                    continue
        
        print(f"\n📊 Total overdue tasks found: {overdue_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_overdue_tasks_debug())
