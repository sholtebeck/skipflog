import urllib.request,json
api_folder="D:\\Users\\sholtebeck\\GitHub\\skipflog3\\flog0\\static\\api\\"
events_json=api_folder+"events.json"
events_api="http://skipflog3.appspot.com/api/events"
event_api="http://skipflog3.appspot.com/api/event/"
results_api="http://skipflog3.appspot.com/api/results/"

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

def event_results(event_id):
    cevent=json_results(event_api+str(event_id))
    event={k:cevent[k] for k in cevent.keys() if k not in ('first', 'lastpick', 'next', 'nextpick', 'pick_no')}
    cresults=json_results(results_api+str(event_id)).get("results")
    # get a list of pickers
    cpickers=cresults.get("pickers")
    for p in range(2):
        cpickers[p]["Picks"]=[e["picks"][:10] for e in cevent["pickers"] if e["name"]==cpickers[p]["Name"]][0]
    event["pickers"]=cpickers
    event['event_url']=cevent['espn_url']
    event['winner']=cpickers[0]["Name"]
    event['winner_points']=cpickers[0]["Points"]
    event['loser']=cpickers[1]["Name"]
    event['loser_points']=cpickers[1]["Points"]
    event['winning_margin']=event['winner_points']-event['loser_points']
    # get a list of players
    cplayers=[]
    for player in cresults["players"]:
        if player.get("Picker") or player["Rank"]==1:
            eplayer=[e for e in cevent["players"] if e.get("Name",e.get("name"))==player["Name"]][0]
            cplayer={"Name":player["Name"],"Agg": int(player["TOT"]),"Cntry":player.get("country","USA"),"Pos":player["POS"],"Ranking Points":player['Points']}
            for ckey in ['R4', 'R1', 'R2', 'R3', 'Rank', 'Points', 'Name', 'Total', 'POS', 'Picker']:
                cplayer[ckey]=player.get(ckey,'')
            cplayers.append(cplayer)
    event["players"]=cplayers
    return event

def update_players(json_events):
    pickers=("Mark","Steve")
    players=[]
    pnames=[]
    for event in json_events:
        for player in [p for p in event['players'] if p.get("Picker")]:
            pname=player["Name"]
            if pname not in pnames:
                pnames.append(pname)
                nplayer={"Name":pname,"events":[],"pickers":[{'Name': picker, 'Count': 0, 'Points': 0.0, 'Rank': pickers.index(picker)+1} for picker in pickers]}
                nplayer["rownum"]=len(pnames)-1
                nplayer["picked"]={'Mark': 0, 'Steve': 0, 'Total': 0, 'Points': 0.0}
                nplayer['POS']=len(pnames)
                players.append(nplayer)
                pnum=len(pnames)-1
            else:
                pnum=pnames.index(pname)
            picker=player.get("Picker")
            points=round(player.get("Points"),2)
            pknum=pickers.index(picker)
            players[pnum]["picked"][picker]+=1
            players[pnum]["picked"]["Total"]+=1
            players[pnum]["picked"]["Points"]+=points
            players[pnum]["pickers"][pknum]["Count"]+=1
            players[pnum]["pickers"][pknum]["Points"]+=points
            pevent={k:player[k] for k in player.keys()}
            pevent["Name"]=event["Name"]
            pevent["ID"]=event["ID"]
            pevent["Points"]=points
            players[pnum]["events"].append(pevent)
    for p in range(len(players)):
        players[p]["rownum"]=len([player for player in players if player["Name"]<=players[p]["Name"]])        
        players[p]["POS"]=len([player for player in players if player["picked"]["Points"]>=players[p]["picked"]["Points"]]) 
        if players[p]["pickers"][1]["Points"]>players[p]["pickers"][0]["Points"]:
            players[p]["pickers"][1]["Rank"]=1
            players[p]["pickers"][0]["Rank"]=2
            players[p]["pickers"]=players[p]["pickers"][::-1]           
    players.sort(key=lambda p:p["rownum"])  
    return players  

def update_event(event_id):
    events_json=api_folder+"events.json"
    json_events=json_results(events_json)
    players_json=api_folder+"players.json"
    json_players=json_results(players_json)
    event_ids=[e["ID"] for e in json_events["events"]]
    event=event_results(event_id)
    if event["ID"] not in event_ids:
        json_events["events"].insert(0,event)
    else:
        i=event_ids.index(event["ID"])
        json_events["events"][i]=event
    epickers=json_events.get("pickers")
    for p in range(2):
        epickers[p]["Wins"]=len([e for e in json_events["events"] if e["winner"]== epickers[p]["Name"] ])
        winner_points=sum([e["winner_points"] for e in json_events["events"] if e["winner"]== epickers[p]["Name"] ])
        epickers[p]["Losses"]=len([e for e in json_events["events"] if e["loser"]== epickers[p]["Name"] ])
        loser_points=sum([e["loser_points"] for e in json_events["events"] if e["loser"]== epickers[p]["Name"] ])
        epickers[p]["Points"]=winner_points+loser_points
        epickers[p]["Rank"]=p+1
    json_events["pickers"]=epickers
    with open(events_json, 'w') as f:
        json.dump(json_events, f)   
    json_players["players"]=update_players(json_events["events"])
    with open(players_json, 'w') as f:
        json.dump(json_players, f)   

if __name__ == "__main__":
    from time import gmtime, strftime
    current_event=strftime("%y%m",gmtime())
    update_event(current_event) 