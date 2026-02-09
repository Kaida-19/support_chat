# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import datetime
# from .manager import ConnectionManager

# app = FastAPI()
# manager = ConnectionManager()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # tighten later
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.websocket("/ws/{room_id}")
# async def websocket_endpoint(websocket: WebSocket, room_id: str):
#     await manager.connect(room_id, websocket)
#     try:
#         while True:
#             data = await websocket.receive_json()
#             data["timestamp"] = datetime.utcnow().isoformat()
#             await manager.broadcast(room_id, data)
#     except WebSocketDisconnect:
#         manager.disconnect(room_id, websocket)


# @app.get("/rooms")
# def get_rooms():
#     return list(manager.active_rooms.keys())

# @app.get("/")
# def root():
#     return {"status": "alive"}

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

# 🔹 In-memory message storage
messages_store = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ SINGLE WebSocket endpoint
@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(room, websocket)

    if room not in messages_store:
        messages_store[room] = []

    try:
        while True:
            data = await websocket.receive_json()

            msg = {
                "sender": data["sender"],
                "content": data["content"],
                "timestamp": datetime.utcnow().isoformat()
            }

            # store message
            messages_store[room].append(msg)

            # broadcast to all in room
            await manager.broadcast(room, msg)

    except WebSocketDisconnect:
        manager.disconnect(room, websocket)


# ✅ Load previous messages
@app.get("/messages/{room}")
def get_messages(room: str):
    return messages_store.get(room, [])


# ✅ Room list
@app.get("/rooms")
def get_rooms():
    return list(manager.active_rooms.keys())


@app.get("/")
def root():
    return {"status": "alive"}
