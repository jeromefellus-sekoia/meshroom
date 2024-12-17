from datetime import datetime, timezone
import logging
from fastapi import (
    FastAPI,
    WebSocket,
)
from fastapi.encoders import ENCODERS_BY_TYPE
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from os.path import isdir

from meshroom.utils import UI_DIR, VERSION, read_file

logging.basicConfig(level="INFO", format="\033[0;33m%(asctime)s %(levelname)s \033[0m%(message)s")


# Override JSON encoders for all API responses
ENCODERS_BY_TYPE[datetime] = lambda d: d.replace(tzinfo=timezone.utc).isoformat()


app = FastAPI(
    title="Meshroom, the composable SOC assistant",
    version=VERSION,
)


@app.websocket("/websocket")
async def websocket(ws: WebSocket):
    try:
        await ws.accept()
        logging.info("websocket connected")
        while True:
            data = await ws.receive_json()
    except Exception as e:
        logging.error(e)
    finally:
        logging.info("websocket left")


# Serve Single-Page Application
if isdir(UI_DIR):
    app.mount("/static", StaticFiles(directory=UI_DIR / "static"), name="static")
    app.mount("/assets", StaticFiles(directory=UI_DIR / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def webui():
        return HTMLResponse(read_file(UI_DIR, "index.html"))
