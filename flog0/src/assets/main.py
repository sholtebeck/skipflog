import urllib.request,json
api_folder="F:\\users\\sholtebeck\\GitHub\\flog0\\src\\data\\"
events_json=api_folder+"events.json"
players_json=api_folder+"players.json"
event_api="http://skipflog3.appspot.com/api/event/"

event_keys=["ID", "name", "event_dates", "event_id", "event_loc", "pickers", "players", "winner", "winner_points", "loser", "loser_points", "margin"]
picker_keys=["wins", "losses", "points", "name", "picks", "altpick", "rank"]
player_keys=["name","pos","rank", "points", "total", "scores", "picker"]

def json_results(url):
    print("fetching",url)
    try:
        if url[:4]=="http":
            page=urllib.request.urlopen(url)
        else:
            page=open(url)
        results=json.load(page)
        return results
    except:
        return {}

def format_picker(picker,p):
    cpicker={k.lower():picker.get(k) for k in picker.keys() }
    cpicker["name"]=picker.get("name",picker.get("Name"))
    cpicker["points"]=round(picker.get("points",picker.get("Points")),2)
    cpicks=picker.get("picks",picker.get("Picks"))
    if cpicks:
        cpicker["picks"]=cpicks[:10]
        if len(cpicks)>10:
            cpicker["altpick"]=cpicks[10]
        cpicker["wins"]=1-p
        cpicker["losses"]=p
    cpicker["rank"]=p+1
    return cpicker

def format_player(player,p):
    cplayer={k.lower():player.get(k) for k in player.keys() if k.lower() in player_keys}
    if not cplayer.get('scores'):
        cplayer['scores']='-'.join([str(player[r]) for r in ('R1','R2','R3','R4') if player[r] not in ('-','--')])
    cplayer["points"]=round(cplayer["points"],2)
    cplayer["pos"]=cplayer["pos"] if cplayer["pos"]!='-' else "MC"
    cplayer["rownum"]=p
    return cplayer

def event_results(event_id):
    cevent=json_results(event_api+str(event_id))
    event={k:cevent.get(k) for k in event_keys}
    event["ID"]=int(cevent["ID"])
    event["name"]=cevent["Name"]
    # update wins and losses per player
    for p in range(2):
        event["pickers"][p]["wins"]=1-p
        event["pickers"][p]["losses"]=p
    event["winner"]=event["pickers"][0].get("name")
    event["winner_points"]=round(event["pickers"][0].get("points"),2)
    event["loser"]=event["pickers"][1].get("name")
    event["loser_points"]=round(event["pickers"][1].get("points"),2)
    event["margin"]=round(event["winner_points"]-event["loser_points"],2)
    return event

def player_pos(player):
    return player.get("pos",999)

def player_rownum(player):
    return player.get("rownum",999)

def flat_players(players):
    fplayers=[]
    fp_keys=['name', 'rownum', 'pos','pickers']
    for p in players:
        nplayer={k:p.get(k) for k in fp_keys}
        for k in p['picked'].keys():
            nplayer[k.lower()]=p['picked'][k]
        nplayer["first"]=min(q["name"][:4] for q in p['events'])
        nplayer["last"]=max(q["name"][:4] for q in p['events'])
        nplayer["points"]='{0:.2f}'.format(float(nplayer["points"]))
        nplayer["pickers"][0]["points"]='{0:.2f}'.format(float(nplayer["pickers"][0]["points"]))
        nplayer["pickers"][1]["points"]='{0:.2f}'.format(float(nplayer["pickers"][1]["points"]))
        fplayers.append(nplayer)  
    return fplayers  

def update_players(json_events):
    pickers=("Mark","Steve")
    players=[]
    pnames=[]
    for event in json_events:
        for player in [p for p in event["players"] if p.get("picker")]:
            pname=player["name"]
            if pname not in pnames:
                pnames.append(pname)
                nplayer={"name":pname,"events":[],"pickers":[{"name": picker, "count": 0, "points": 0.0, "rank": pickers.index(picker)+1} for picker in pickers]}
                nplayer["rownum"]=len(pnames)-1
                nplayer["picked"]={"Mark": 0, "Steve": 0, "total": 0, "points": 0.0}
                nplayer["pos"]=len(pnames)
                players.append(nplayer)
                pnum=len(pnames)-1
            else:
                pnum=pnames.index(pname)
            picker=player.get("picker")
            points=round(player.get("points"),2)
            pknum=pickers.index(picker)
            players[pnum]["picked"][picker]+=1
            players[pnum]["picked"]["total"]+=1
            players[pnum]["picked"]["points"]+=points
            players[pnum]["pickers"][pknum]["count"]+=1
            players[pnum]["pickers"][pknum]["points"]+=points
            pevent={k:player[k] for k in player.keys()}
            pevent["name"]=event.get("name",event.get("event_name"))
            pevent["ID"]=event["ID"]
            pevent["points"]=points
            players[pnum]["events"].append(pevent)
    for p in range(len(players)):
        players[p]["rownum"]=len([player for player in players if player["name"]<=players[p]["name"]])        
        players[p]["pos"]=len([player for player in players if player["picked"]["points"]>=players[p]["picked"]["points"]]) 
        players[p]["picked"]["points"]=round(players[p]["picked"]["points"],2)
        if players[p]["pickers"][1]["points"]>players[p]["pickers"][0]["points"]:
            players[p]["pickers"][1]["rank"]=1
            players[p]["pickers"][0]["rank"]=2
            players[p]["pickers"]=players[p]["pickers"][::-1]           
    players.sort(key=player_pos)  
    return flat_players(players)  

def update_event(event_id):
    events_json=api_folder+"events.json"
    json_events=json_results(events_json)
    event_ids=[e["ID"] for e in json_events]
    event=event_results(event_id)
    if event["ID"] not in event_ids:
        json_events.insert(0,event)
    else:
        i=event_ids.index(event["ID"])
        json_events[i]=event
    with open(events_json, "w") as f:
        json.dump(json_events, f)   
    json_players=update_players(json_events)
    with open(players_json, "w") as f:
        json.dump(json_players, f)

def format_event(event):
    new_event={k:event.get(k) for k in event_keys}
    new_event["ID"]=int(event["ID"])
    new_event["name"]=event.get("name",event.get("Name"))
    for p in range(len(new_event["players"])):
        new_event["players"][p]=format_player(new_event["players"][p],p)   
    for p in range(len(new_event["pickers"])):
        new_event["pickers"][p]=format_picker(new_event["pickers"][p],p)
    cpickers=new_event["pickers"] 
    new_event["winner"]=cpickers[0].get("name")
    new_event["winner_points"]=round(cpickers[0].get("points"),2)
    new_event["loser"]=cpickers[1].get("name")
    new_event["loser_points"]=round(cpickers[1].get("points"),2)
    new_event["margin"]=round(event["winner_points"]-event["loser_points"],2)
    return new_event    

def update_events():
    json_events=json_results(events_json)
    for e in range(len(json_events)):
        json_events[e]=format_event(json_events[e]) 
        print(json_events[e]["name"])  
    for p in range(len(json_events["pickers"])):
        json_events["pickers"][p]=format_picker(json_events["pickers"][p],p)   
    with open(events_json, "w") as f:
        json.dump(json_events, f)   
    json_players=update_players(json_events)
    with open(players_json, "w") as f:
        json.dump(json_players, f)

if __name__ == "__main__":
    from datetime import datetime
    current_event=datetime.now().strftime("%y%m")
    update_event(current_event) 