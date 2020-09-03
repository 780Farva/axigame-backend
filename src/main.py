from fastapi import FastAPI

app = FastAPI()


@app.post("/startGame")
async def start_game():
    return {"message": "TODO: This will start the game."}


@app.post("/guess")
async def start_game():
    return {"message": "TODO: This will register a guess."}


@app.post("/startCameraFeed")
async def start_game():
    return {"message": "TODO: This will start the camera feed."}
