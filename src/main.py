from fastapi import FastAPI
import uvicorn
from game_manager import GameManager

app = FastAPI()


@app.post("/startGame")
async def start_game():
    game_manager.start()
    return {"message": f"Game is now in state: {game_manager.state}"}


@app.post("/guess")
async def guess():
    return {"message": "TODO: This will register a guess."}


@app.post("/startCameraFeed")
async def start_camera_feed():
    return {"message": "TODO: This will start the camera feed."}

if __name__ is "__main__":
    game_manager = GameManager()
    uvicorn.run(app)