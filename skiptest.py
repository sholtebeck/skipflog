# this will test the skipflog back end
from skipflog import *
import models
print("testing picks..")
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
#       if  event["lastpick"].split()[0] != event["next"]:
#           print(event["pick_no"], event["lastpick"], event["nextpick"])

current=current_event()
print("testing results for",current)
picks=get_picks(current)
assert len(picks.keys())==22, "wrong number of picks"
url=fetch_url(current)
res=get_results(current)
res["players"].sort(key=lambda p:p["Total"])
players=res["players"]
total = ""
pos = 1
points=skip_points[pos]
pickers=[q["Name"] for q in res["pickers"]]
for x in range(2):
    res["pickers"][x]["Count"]=0
    res["pickers"][x]["Points"]=0
for p in players:
    if p["R1"]!=total:
        total=p["R1"]
        rank=get_rank(str(pos))
        tcount=len([q for q in players if q["R1"]==total])
        if tcount==1:
            p["POS"]=str(pos)
            p["Rank"]=rank
            p["Points"]=points=skip_points[pos]
        else:
            p["POS"]='T'+str(pos)
            lastpos=p["POS"]
            p["Rank"]=rank
            points=round(sum(skip_points[pos:pos+tcount])/tcount,2)
            p["Points"]=points
    else:
        p["POS"]=lastpos
        p["Rank"]=rank
        p["Points"]=points
    if p.get("Picker") in pickers:
        x=pickers.index(p.get("Picker"))
        res["pickers"][x]["Count"]+=1
        res["pickers"][x]["Points"]+=points
    print(p["Name"],p["R1"],p["POS"],p["Points"])
    pos+=1        

res["players"]=[p for p in res["players"] if p.get("Picked")]            
for key in res["event"].keys():
    print(key,':', res["event"][key])
for p in res["players"]:
    if p.get("Picker"):
        print(p["Name"], p["POS"], p["Scores"], p["Points"] )
models.update_results(res)