import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)

async def consumer_handler(websocket: WebSocketClientProtocol) -> None:
    async for message in websocket:
        log_message(message)

async def consume(hostname: str, port: int) -> None:
    websocket_resource_url = f"ws://{hostname}:{port}"
    async with websocets.connect(websocket_resource_url) as websocket:
        await consumer_handler(websocket)

def log_message(message:str) -> None:
    logging.info(f"Message : {message}")