import json
from typing import Dict, Set
from fastapi import WebSocket
from datetime import datetime
import pytz

# Helper function for timezone-aware timestamps
def get_current_timestamp_iso():
    """Get current timestamp in IST timezone with proper ISO format"""
    return datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()

class NotificationManager:
    def __init__(self):
        # Store active connections: {userid: set_of_websockets}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, userid: str, name: str = None):
        """Accept new WebSocket connection for a user"""
        await websocket.accept()

        if userid not in self.active_connections:
            self.active_connections[userid] = set()

        self.active_connections[userid].add(websocket)
        display_name = name if name else userid
        print(f"✅ User {display_name} connected. Connections: {len(self.active_connections[userid])}")
    def disconnect(self, websocket: WebSocket, userid: str):
        """Remove WebSocket connection for a user"""
        if userid in self.active_connections:
            self.active_connections[userid].discard(websocket)

            if not self.active_connections[userid]:
                del self.active_connections[userid]

        print(f"❌ User {userid} disconnected")

    async def send_personal_notification(self, userid: str, notification_data: dict):
        """Send a REAL notification to a specific user"""
        if userid not in self.active_connections:
            print(f"⚠️ User {userid} not connected, notification not sent")
            return

        # Ensure the notification has the correct userid
        if "userid" not in notification_data:
            notification_data["userid"] = userid
        
        # Double-check that this notification is for the correct user
        if notification_data.get("userid") != userid:
            print(f"🚨 ERROR: Notification userid mismatch! Expected: {userid}, Got: {notification_data.get('userid')}")
            return

        message = json.dumps({
            "type": "notification",
            "data": notification_data,
            "timestamp": get_current_timestamp_iso()
        })

        print(f"📢 Sending notification to user {userid}: {notification_data.get('title', 'No title')}")

        disconnected = set()
        sent_count = 0
        for connection in self.active_connections[userid]:
            try:
                # Check if connection is still open before sending
                if connection.client_state.value == 1:  # WebSocketState.CONNECTED
                    await connection.send_text(message)
                    sent_count += 1
                else:
                    # Connection is closed, mark for removal
                    disconnected.add(connection)
            except Exception as e:
                print(f"⚠️ Error sending to {userid}: {e}")
                disconnected.add(connection)

        print(f"✅ Notification sent to {sent_count} connections for user {userid}")

        # Cleanup broken connections
        for connection in disconnected:
            self.active_connections[userid].discard(connection)

    async def send_broadcast_notification(self, notification_data: dict):
        """Send a broadcast notification to ALL connected users"""
        message = json.dumps({
            "type": "broadcast",
            "data": notification_data,
            "timestamp": get_current_timestamp_iso()
        })

        disconnected_users = []
        for userid, connections in self.active_connections.items():
            disconnected = set()
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"⚠️ Error sending broadcast to {userid}: {e}")
                    disconnected.add(connection)

            # Remove disconnected connections
            for conn in disconnected:
                connections.discard(conn)

            if not connections:
                disconnected_users.append(userid)

        # Remove users with no active connections
        for userid in disconnected_users:
            del self.active_connections[userid]

    async def send_unread_count_update(self, userid: str, unread_count: int):
        """Send ONLY an unread count update"""
        if userid not in self.active_connections:
            return

        message = json.dumps({
            "type": "unread_count_update",
            "data": {"unread_count": unread_count}
        })

        disconnected = set()
        for connection in self.active_connections[userid]:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"⚠️ Error sending unread count to {userid}: {e}")
                disconnected.add(connection)

        # Cleanup broken connections
        for conn in disconnected:
            self.active_connections[userid].discard(conn)

    def get_active_users(self) -> list:
        """Return list of user IDs with active connections"""
        return list(self.active_connections.keys())

    def get_user_connection_count(self, userid: str) -> int:
        """Return number of active connections for a user"""
        return len(self.active_connections.get(userid, []))


# Global notification manager instance
notification_manager = NotificationManager()