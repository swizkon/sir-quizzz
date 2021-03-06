from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import CreateQuiz

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

quiz_repository = [{"id": 1, "name": "QL Quiz I test"},{"id": 2,"name": "QL Quiz II draft"}]

def find_quiz_by_id(id):
    for q in quiz_repository:
        if(q['id'] == id):
            return q

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Sir Quizzz</title>
    </head>
    <body>
        <h1>Sir Quizzz</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script src="/static/stuff.js">
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/quiz")
async def quiz_list():
    return {"data": quiz_repository}
    
@app.get("/quiz/{id}")
async def quiz_details(id: int, response: Response):
    p = find_quiz_by_id(id)
    if not p:
        response.status_code = 404
    return {"data": p}
    
@app.post("/quiz")
async def create_quiz(new_quiz: CreateQuiz):
    new_entry = new_quiz.dict()
    quiz_repository.append(new_entry)
    return {"data": quiz_repository}


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
