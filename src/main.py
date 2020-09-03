import logging
import numpy as np
import uvicorn
from fastapi import FastAPI
from fuzzywuzzy import fuzz

from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from game_manager import GameManager
from pydantic import BaseModel

from threading import Thread

app = FastAPI()

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)

axidraw_client = AxiDraw()
quickdraw_client = QuickDrawData()
game_manager = GameManager(axidraw_client, quickdraw_client)
game_thread = None


class GuessRequest(BaseModel):
    guess: str


@app.post("/startGame")
async def start_game():
    log.debug(f"{game_manager.states}")
    global game_thread
    if game_manager.state == "idle":
        if game_thread is not None:
            game_thread = None
        game_thread = Thread(target=game_manager.start)
        game_thread.start()
        return {"message": f"Game is now started."}
    else:
        return {
            "message": f"There is already an active game in state {game_manager.state}."
        }


@app.get("/guess/{guess_request}")
async def guess(guess_request: str):
    log.warning(f'==================Processing request: {guess_request}')
    if game_manager.state in ["drawing", "final_guessing"]:
        guess = guess_request.lower()
        truth = game_manager.drawing_name
        log.debug(f"Comparing guess {guess} to truth {truth}.")
        if len(truth.split()) > 1:
            # we have two words, let's guess at least one:
            guessed_correctly = np.any(
                [(fuzz.ratio(truth, word) > 85) for word in truth.split()]
            )
        else:
            guessed_correctly = fuzz.ratio(truth, guess) > 80

        if guessed_correctly:
            # Stop drawing, do next image
            print("Correct! Next image...")
            game_manager.correct_guess_early()
        # return {"message": f"TODO: This guess was {guessed_correctly}."}
        print(f"TODO: This guess was {guessed_correctly}.")
        return True
    else:
        # TODO: Return with a meaningful status code
        # return {"message": f"Not ready. Game is in state {game_manager.state}"}
        print(f"Not ready. Game is in state {game_manager.state}")
        return False


@app.post("/startCameraFeed")
async def start_camera_feed():
    return {"message": "TODO: This will start the camera feed."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", loop="asyncio", debug=True)
