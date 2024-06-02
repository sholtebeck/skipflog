from fastapi import FastAPI
from soupflog import fetch_event,fetch_events,fetch_majors,fetch_odds,fetch_players,fetch_rankings,post_rankings,fetch_results
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello skipflog"}

@app.get("/event/{event_id}")
async def event(event_id:int):
    return fetch_event(event_id)

@app.get("/events")
async def events():
    return fetch_events()

@app.get("/majors/{season}")
async def majors(season:int):
    return fetch_majors(season)

@app.get("/odds")
async def odds():
    return fetch_odds()

@app.get("/players")
async def players():
    return fetch_players()

@app.get("/rankings")
async def rankings():
    return fetch_rankings()

@app.post("/rankings/{id}")
async def postrank(id:int):
    rankings=fetch_rankings()
    if rankings.get("ID")==id:
        post_rankings()
    return rankings

@app.get("/results/{event_id}")
async def results(event_id:int):
    return fetch_results(event_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
