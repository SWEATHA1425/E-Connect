# ws_manager.py
from fastapi import WebSocket
from collections import defaultdict



class DirectChatManager:
    def __init__(self):
        # user_id -> list of sockets
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def handle_message(self, message: dict):
        """
        Handle incoming messages:
        - type: "text" or "file"
        """
        if message.get("type") == "file":
            try:
                file_bytes = base64.b64decode(message["content"])
                file_doc = {
                    "filename": message["filename"],
                    "content": Binary(file_bytes),
                    "from_user": message["from_user"],
                    "to_user": message["to_user"],
                    "timestamp": datetime.utcnow(),
                    "size": len(file_bytes),
                    "mime_type": message.get("mime_type", "application/octet-stream"),
                }
                result = files_collection.insert_one(file_doc)
                message["id"] = str(result.inserted_id)
                message["type"] = "file"
                # Remove base64 content before broadcasting
                message.pop("content", None)
            except Exception as e:
                print("File upload error:", e)
                return  # optionally send error back to sender

        await self.send_message(message["to_user"], message)

    async def send_message(self, to_user_id: str, message: dict):
        # send to recipient
        if to_user_id in self.active_connections:
            for ws in list(self.active_connections[to_user_id]):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.active_connections[to_user_id].remove(ws)
     
        # echo back to sender
        sender_id = message.get("from")
        if sender_id in self.active_connections:
            for ws in list(self.active_connections[sender_id]):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.active_connections[sender_id].remove(ws)


class GeneralChatManager:
    def __init__(self):
        # room -> list of sockets
        self.rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        self.rooms[room].append(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
        if not self.rooms.get(room):
            self.rooms.pop(room, None)

    async def broadcast(self, room: str, message: dict):
        if room in self.rooms:
            for ws in list(self.rooms[room]):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.rooms[room].remove(ws)


class NotifyManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        for ws in list(self.connections):
            try:
                await ws.send_json(message)
            except Exception:
                self.connections.remove(ws)
class GroupChatManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # group_id -> list of websockets

    async def connect(self, group_id: str, websocket: WebSocket):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)

    def disconnect(self, group_id: str, websocket: WebSocket):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
            if not self.active_connections[group_id]:
                del self.active_connections[group_id]

    async def broadcast(self, group_id: str, message: dict):
        if group_id in self.active_connections:
            for ws in self.active_connections[group_id]:
                await ws.send_json(message)



