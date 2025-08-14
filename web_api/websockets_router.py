import logging
from fastapi import WebSocket, WebSocketDisconnect
from llm.llm import LLM

logger = logging.getLogger(__name__)

async def dialog_with_llm(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            answer = await LLM().llm_request(data)
            await websocket.send_text(answer)

    except WebSocketDisconnect:
        logger.info("ws disconnect")
