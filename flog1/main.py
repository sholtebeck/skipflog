from fastapi import FastAPI
from soupflog import fetch_events,fetch_odds,fetch_players,fetch_rankings
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/events")
async def events():
    return fetch_events()

@app.get("/odds")
async def odds():
    return fetch_odds()

@app.get("/players")
async def players():
    return fetch_players()

@app.get("/rankings")
async def rankings():
    return fetch_rankings()
