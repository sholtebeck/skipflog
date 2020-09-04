# this will test the skipflog back end
import random
from skipflog import *
players=fetch_players()
pnames=[p["name"] for p in players][:24]
for p in players:
    p["picked"]==0
assert(len(players)==30)
event=default_event()
event["players"]=players
assert(event["pick_no"]==1)
assert(len(event["players"])==len(players))
assert(len(event["pickers"])==2)
for n in range(len(pnames)):
    if event["next"]:
        assert(event["pick_no"]==n+1), event["pick_no"]
        event=pick_player(event,pnames[n]) 
        assert(event["pick_no"]==n+2), event["pick_no"]
        assert event["players"][n]["picked"]==1 , event["players"][n]["name"]
        if  event["lastpick"].split()[0] != event["next"]:
            print(event["pick_no"], event["lastpick"], event["nextpick"])