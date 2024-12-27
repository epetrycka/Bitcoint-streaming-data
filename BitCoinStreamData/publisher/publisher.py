import websockets
import json
import asyncio
import os
from dotenv import load_dotenv
from google.cloud import pubsub_v1

load_dotenv("./.env")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH")
publisher = pubsub_v1.PublisherClient()
project_id = os.getenv("PROJECT_ID")
topic_id = os.getenv("TOPIC_ID")
topic_path = publisher.topic_path(project=project_id, topic=topic_id)

async def streamTrade(symbol: str) -> None:
    url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
    async with websockets.connect(url, ping_timeout=3600, close_timeout=3600) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            data_with_attributes = {
                "type": "trade",
                "data": data
            }
            future = publisher.publish(topic_path, json.dumps(data_with_attributes).encode("utf-8"))
            print(data_with_attributes['type'])
            future.result()

async def streamDepth(symbol: str) -> None:#
    url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth"
    async with websockets.connect(url, ping_timeout=3600, close_timeout=3600) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            data_with_attributes = {
                "type": "depth",
                "data": data
            }
            future = publisher.publish(topic_path, json.dumps(data_with_attributes).encode("utf-8"))
            print(data_with_attributes['type'])
            future.result()

async def main():
    symbol = "btcusdt"

    await asyncio.gather(
        streamTrade(symbol=symbol),
        streamDepth(symbol=symbol)
    )

asyncio.run(main())