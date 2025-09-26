# E-Connect Real-time Notification System

## Overview

The E-Connect notification system provides real-time updates for all user activities including tasks, leaves, work-from-home requests, and system alerts. It features a centralized notification dashboard with WebSocket support for instant delivery and polling fallback.

## Features

### ✅ Centralized Panel
- All updates in one place: Tasks, Leaves, WFH, System Alerts
- Unified notification dashboard accessible from sidebar
- Priority-based notification display

### ✅ Real-time Updates  
- WebSocket connection for instant delivery
- Automatic fallback to polling when WebSocket unavailable
- Browser notification support with permission request

### ✅ Read/Unread Status
- Visual unread badge with count
- Mark individual notifications as read/unread
- Mark all notifications as read functionality

### ✅ Click-to-Action
- Each notification links to its related module
- Direct navigation to relevant sections (tasks, leave history, etc.)
- Contextual action URLs based on notification type

### ✅ Priority Levels
- **Low**: System messages, successful clock-in/out
- **Medium**: Leave submissions, task assignments, routine updates
- **High**: Manager task assignments, leave rejections
- **Urgent**: Critical system alerts, urgent deadlines

## System Architecture

### Backend Components

#### 1. Database Schema (MongoDB)
```javascript
notifications: {
  _id: ObjectId,
  userid: String,
  title: String,
  message: String,
  type: String, // 'task', 'leave', 'wfh', 'system', 'attendance'
  priority: String, // 'low', 'medium', 'high', 'urgent'
  action_url: String,
  related_id: String,
  metadata: Object,
  is_read: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 2. API Endpoints
- `POST /notifications/create` - Create new notification
- `GET /notifications/{userid}` - Get user notifications with filters
- `PUT /notifications/{notification_id}/read` - Mark as read/unread
- `PUT /notifications/{userid}/mark-all-read` - Mark all as read
- `GET /notifications/{userid}/unread-count` - Get unread count
- `DELETE /notifications/{notification_id}` - Delete notification
- `WS /ws/notifications/{userid}` - WebSocket connection

#### 3. WebSocket Manager
- Handles real-time connections per user
- Broadcasts notifications instantly
- Manages connection lifecycle and reconnection

### Frontend Components

#### 1. NotificationDashboard.jsx
- Main notification center interface
- Filtering by type, priority, and read status
- Real-time updates via WebSocket

#### 2. NotificationBell.jsx
- Sidebar notification indicator
- Real-time unread count
- Connection status indicator

#### 3. useNotificationWebSocket.js
- Custom React hook for WebSocket management
- Automatic reconnection logic
- Browser notification integration

## Notification Types and Triggers

### Task Notifications
- **Created**: When new task assigned
- **Updated**: When task status/details change
- **Assigned by Manager**: High priority manager assignments
- **Due Soon**: Automated reminders (planned)

### Leave Notifications
- **Submitted**: When leave request submitted
- **Approved/Rejected**: Final status updates
- **Recommended**: Manager recommendations

### Work from Home Notifications
- **Submitted**: WFH request submitted
- **Approved/Rejected**: Status updates

### System Notifications
- **Maintenance**: System maintenance alerts
- **Updates**: Feature updates and announcements

### Attendance Notifications
- **Clock-in/out**: Successful attendance records
- **Auto Clock-out**: Automated end-of-day clock-out
- **Missed Clock-out**: Alert for missed clock-out

## Installation and Setup

### Backend Setup
1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Added packages to requirements.txt:
- `websockets==11.0.3`
- `APScheduler==3.10.4`
- `requests==2.31.0`

3. Start the server:
```bash
python Server.py
```

### Frontend Setup
The notification system is integrated into the existing React application. No additional packages needed.

### Database Setup
MongoDB collections are automatically created. The `notifications` collection will be created on first notification.

## Usage

### For Users
1. **Access Notifications**: Click the bell icon in sidebar or navigate to `/User/notifications`
2. **Real-time Updates**: Notifications appear instantly when WebSocket connected
3. **Filter Notifications**: Use dropdown filters for type, priority, and read status
4. **Mark as Read**: Click checkmark icon or click notification to mark as read
5. **Navigate to Source**: Click notification to go to related module

### For Developers
1. **Create Notifications**: Use helper functions in `Mongo.py`
```python
# Create task notification
create_task_notification(userid, task_title, action, task_id, priority)

# Create leave notification  
create_leave_notification(userid, leave_type, action, leave_id, priority)

# Create custom notification
create_notification(userid, title, message, type, priority, action_url, related_id, metadata)
```

2. **WebSocket Integration**: Notifications automatically sent via WebSocket when created

3. **Testing**: Use test endpoint to verify system
```bash
POST /notifications/test/{userid}
```

## Configuration

### WebSocket Configuration
- Default port: 8000
- Auto-reconnection: 5 seconds
- Connection timeout: 30 seconds

### Polling Fallback
- Interval: 30 seconds when WebSocket unavailable
- Automatic switch between WebSocket and polling

### Browser Notifications
- Permission requested automatically
- Notifications show for new items when tab not active

## Security Considerations

- User-specific WebSocket connections
- JWT authentication for API endpoints (when enabled)
- MongoDB ObjectId validation
- Input sanitization for notification content

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check server is running on correct port
   - Verify WebSocket URL in `useNotificationWebSocket.js`
   - Check firewall/proxy settings

2. **Notifications Not Appearing**
   - Verify userid in localStorage
   - Check browser console for errors
   - Test with `/notifications/test/{userid}` endpoint

3. **High CPU Usage**
   - Reduce polling interval if needed
   - Check for memory leaks in WebSocket connections

### Debug Mode
Add console logging in:
- `websocket_manager.py` for connection debugging
- `useNotificationWebSocket.js` for frontend debugging

## Future Enhancements

### Planned Features
- Push notifications for mobile PWA
- Notification templates and customization
- Bulk notification operations
- Advanced filtering and search
- Notification analytics and reporting
- Email notification fallback
- Notification scheduling

### Performance Optimizations
- Notification caching strategy
- Database indexing optimization
- WebSocket connection pooling
- Batch notification processing

## API Documentation

### Notification Object Structure
```javascript
{
  "_id": "notification_id",
  "userid": "user_id", 
  "title": "Notification Title",
  "message": "Notification message content",
  "type": "task|leave|wfh|system|attendance",
  "priority": "low|medium|high|urgent",
  "action_url": "/User/specific-module",
  "related_id": "related_object_id",
  "metadata": {
    "additional": "context_data"
  },
  "is_read": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### WebSocket Message Format
```javascript
{
  "type": "notification|broadcast|unread_count_update",
  "data": { /* notification object or update data */ },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Support and Maintenance

For issues or feature requests related to the notification system:
1. Check this documentation
2. Review console logs for errors
3. Test with the debug endpoint
4. Check WebSocket connection status in the UI

The notification system is designed to be self-healing with automatic reconnection and graceful fallback to polling when needed.
