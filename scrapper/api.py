from fastapi import FastAPI
from starlette.responses import RedirectResponse
tenders_json: str

app = FastAPI()

@app.get("/status")
async def status():
    return {"Status":"OK"}

@app.get("/")
async def redirect_to_status():
    return RedirectResponse("/status")

@app.get("/tenders")
async def read_tenders():
    global tenders_json
    return tenders_json

def get_app():
    return app

def get_tenders(json):
    global tenders_json
    tenders_json = json