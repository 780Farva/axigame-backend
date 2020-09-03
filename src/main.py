import logging

import uvicorn
from fastapi import FastAPI

from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from game_manager import GameManager
from pydantic import BaseModel

app = FastAPI()

log = logging.getLogger(__name__)


class GuessRequest(BaseModel):
    guess: str


@app.post("/startGame")
async def start_game():
    game_manager.start()
    return {"message": f"Game is now in state: {game_manager.state}"}


@app.post("/guess")
async def guess(guess_request: GuessRequest):
    guessed_correctly = game_manager.drawing_name == guess_request.guess
    return {"message": f"TODO: This guess was {guessed_correctly}."}


@app.post("/startCameraFeed")
async def start_camera_feed():
    return {"message": "TODO: This will start the camera feed."}


if __name__ == "__main__":
    axidraw_client = AxiDraw()
    quickdraw_client = QuickDrawData()
    game_manager = GameManager(axidraw_client, quickdraw_client)

    uvicorn.run(app, host="0.0.0.0")
