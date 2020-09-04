import logging
from threading import Thread

import uvicorn
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from pyaxidraw.axidraw import AxiDraw
from pydantic import BaseModel
from quickdraw import QuickDrawData

from game_manager import GameManager

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

axidraw_client = AxiDraw()
quickdraw_client = QuickDrawData()
game_manager = GameManager(axidraw_client, quickdraw_client)
game_thread = None


class GuessRequest(BaseModel):
    guess: str


@app.on_event("shutdown")
def shutdown_event():
    log.info("shutting down")
    if game_thread is not None:
        log.debug("Joining game thread")
        game_thread.join()
        log.debug("game thread joined")


@app.get("/")
def root():
    return RedirectResponse(url="/docs")



@app.post("/startGame")
async def start_game():
    log.debug(f"{game_manager.states}")
    global game_thread
    if game_manager.state == "idle":
        if game_thread is not None:
            game_thread.join()
            game_thread = None
        game_thread = Thread(target=game_manager.start)
        game_thread.start()
        return {"message": f"Game is now started."}
    else:
        return {
            "message": f"There is already an active game in state {game_manager.state}."
        }


@app.get("/guess/{guess_request}")
async def guess(guess_request: str, response: Response):
    log.warning(f'==================Processing request: {guess_request}')
    if game_manager.state in ["drawing", "final_guessing"]:
        decoded = urllib.
        guessed_correctly, guess_time = game_manager.try_guess(guess_request.lower())
        log.info(f'The {guess_request} guess was {guessed_correctly}. Time elapsed : {(guess_time):.2f}s')
        return JSONResponse(content={"correct": guessed_correctly, "time": guess_time})
    else:
        log.info(f"Not ready. Game is in state {game_manager.state}")
        response.status_code = status.HTTP_204_NO_CONTENT


@app.post("/startCameraFeed")
async def start_camera_feed():
    return {"message": "TODO: This will start the camera feed."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", loop="asyncio", debug=True)
