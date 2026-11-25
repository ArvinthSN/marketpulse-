import asyncio
from datetime import datetime, timezone
from fastapi import WebSocket


class LiveConnectionManager:
    def __init__(self, max_connections: int = 1000, max_subscriptions: int = 100):
        self.max_connections = max_connections
        self.max_subscriptions = max_subscriptions
        self.connections: dict[int, WebSocket] = {}
        self.subscriptions: dict[int, set[str]] = {}

    async def connect(self, websocket: WebSocket) -> bool:
        if len(self.connections) >= self.max_connections:
            await websocket.close(code=1013, reason='Maximum live connections reached')
            return False
        await websocket.accept()
        client_id = id(websocket)
        self.connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        client_id = id(websocket)
        self.connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)

    def subscribe(self, websocket: WebSocket, symbols: list[str]) -> set[str]:
        client_id = id(websocket)
        current = self.subscriptions.setdefault(client_id, set())
        if len(current.union(set(symbols))) > self.max_subscriptions:
            raise ValueError('Maximum subscriptions per client exceeded')
        current.update(symbol.upper() for symbol in symbols)
        return current

    def unsubscribe(self, websocket: WebSocket, symbols: list[str]) -> set[str]:
        client_id = id(websocket)
        current = self.subscriptions.setdefault(client_id, set())
        current.difference_update(symbol.upper() for symbol in symbols)
        return current

    async def broadcast_symbol(self, symbol: str, event: dict) -> None:
        for client_id, websocket in list(self.connections.items()):
            if symbol.upper() not in self.subscriptions.get(client_id, set()):
                continue
            try:
                await asyncio.wait_for(websocket.send_json(event), timeout=2.0)
            except Exception:
                self.disconnect(websocket)
