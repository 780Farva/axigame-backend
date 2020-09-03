import logging

import uvicorn
from fastapi import FastAPI

from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from game_manager import GameManager

app = FastAPI()

log = logging.getLogger(__name__)


@app.post("/startGame")
async def start_game():
    game_manager.start()
    return {"message": f"Game is now in state: {game_manager.state}"}


@app.post("/guess")
async def guess():
    params = request.params
    guess_correct = True
    if guess_correct:

    return {"message": "TODO: This will register a guess."}


@app.post("/startCameraFeed")
async def start_camera_feed():
    return {"message": "TODO: This will start the camera feed."}


if __name__ == "__main__":
    axidraw_client = AxiDraw()
    quickdraw_client = QuickDrawData()
    game_manager = GameManager(axidraw_client, quickdraw_client)

    uvicorn.run(app, host="0.0.0.0")
