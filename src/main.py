import logging
import numpy as np
import uvicorn
from fastapi import FastAPI
from fuzzywuzzy import fuzz

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
    guess = guess_request.guess.lower()
    truth = game_manager.drawing_name
    if len(truth.split()) > 1:
        # we have two words, let's guess at least one:
        guessed_correctly = np.any([(fuzz.ratio(truth, word) > 85) for word in truth.split()])
    else:
        guessed_correctly = fuzz.ratio(truth, guess) > 80
    if guessed_correctly:
        # Stop drawing, do next image
        print('Correct! Next image...')
        game_manager.correct_guess_early()
    return {"message": f"TODO: This guess was {guessed_correctly}."}


@app.post("/startCameraFeed")
async def start_camera_feed():
    return {"message": "TODO: This will start the camera feed."}


if __name__ == "__main__":
    axidraw_client = AxiDraw()
    quickdraw_client = QuickDrawData()
    game_manager = GameManager(axidraw_client, quickdraw_client)

    uvicorn.run(app, host="0.0.0.0")
