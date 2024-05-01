# soupflog functions
import gspread,json,urllib.request
from bs4 import BeautifulSoup
from datetime import datetime

# Misc properties
cache={}
events={ 4:'Masters',6:'US Open', 7:'Open Championship', 8:'PGA Championship'}
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','mholtebeck':'Mark'}
emails={'steve':'sholtebeck@gmail.com','mark':'mholtebeck@gmail.com'}
numbers={'Steve':'5103005644@tmomail.com','Mark':'5106739570@sms.boostmobile.com'}
#pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]
event_list=[]
events_api="https://skipflog3.appspot.com/api/event/2000"
mail_url="https://skipflog3.appspot.com/api/mail"
events_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A1%3AF21&output=csv"
players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=B2%3AB155&output=csv"
results_tab="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=2&output=html"
rankings_url="https://espn.com/golf/rankings"
ranking_url="https://us-west2-skipflog.cloudfunctions.net/getRankings"
result_url="https://us-west2-skipflog.cloudfunctions.net/getResults"
result_api="https://skipflog3.appspot.com/api/results/"
results_url="https://skipflog3.appspot.com/results"
players_api="http://knarflog.appspot.com/api/players"
players_json="https://spreadsheets.google.com/feeds/cells/0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E/2/public/full?alt=json"
leaderboard_url="http://sports.yahoo.com/golf/pga/leaderboard"
skip_user="skipfloguser"
skip_picks={}
skip_pickers=["Steve","Mark"]
#skip_points=[0, 100, 60, 40, 35, 30, 25, 20, 15, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2]
skip_points=[0, 100, 60, 40, 30, 24, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9.5, 9, 8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,4,3.5,3.5,3,3,2.5,2.5,2,2,2,1.5,1.5]
# Misc urls
espn_url="http://www.espn.com/golf/leaderboard"
feed_url='https://spreadsheets.google.com/feeds'
golfchannel_url="http://www.golfchannel.com/tours/usga/2014/us-open/"
owg_url="http://www.owgr.com/en/Events/EventResult.aspx?eventid=5520"
pga_url="http://www.pga.com/news/golf-leaderboard/pga-tour-leaderboard"
pgatour_url="http://www.pgatour.com/leaderboard.html"
picks_csv = "picks.csv"
picks_api = "https://skipflog3.appspot.com/api/picks/"
picks_url = "https://skipflog3.appspot.com/picks"
rankings_api="https://us-west2-skipflog.cloudfunctions.net/getRankings"
results_api="https://us-west2-skipflog.cloudfunctions.net/getResults"
owg_ranking_url="http://www.owgr.com/ranking"
yahoo_base_url="http://sports.yahoo.com"
yahoo_url=yahoo_base_url+"/golf/pga/leaderboard"
debug=False

# get current week and year  (using datetime module)
def current_event():
    this_event=str(datetime.now())[2:7].replace('-','')
    return int(this_event) 

def current_month():
    this_month=str(datetime.now())[5:7]
    return int(this_month) 

def current_week():
    this_week=datetime.now().isocalendar()[1]
    return int(this_week)-1 

def current_year():
    return datetime.now().year

def current_time():
    return str(datetime.now())[:19] 

# determine the cut rank for the various majors
def cut_rank():
    this_month=current_month()
    if this_month in (4,6):
        return 60
    else:
        return 70
        
# debug values
def debug_values(number, string):
    if debug:
        print (number, string)

# Handler for string values to ASCII or integer
def xstr(string):
    if string is None:
        return None 
    elif string.isdigit():
        return int(string)
    else:
        return str(''.join([i if ord(i) < 128 else ' ' for i in string]))

# get Date in yymmdd format
def get_date(datestr):
    months=("","January","February","March","April","May","June","July","August","September","October","November","December")
    (mm,dd,yyyy)=datestr.replace(',','').split()
    return yyyy[2:]+str(months.index(mm)).zfill(2)+dd.zfill(2)

# Function to get_points for a Position
def get_rank(position):
    if not position.replace('T','').isdigit():
        return 99
    else:
        rank = int(position.replace('T',''))
        return rank

def get_points(rank):
    if rank < len(skip_points):
        return skip_points[rank]
    elif rank <= cut_rank():
        return 1
    else:
        return 0

# Allow for names with extended chars
def rank_name(name):
    ranknames={'Ludvig Åberg':'Ludvig Aberg','Nicolai Højgaard':'Nicolai Hojgaard','Thorbjørn Olesen':'Thorbjorn Olesen'}
    if name in ranknames.keys():
        return ranknames.get(name)
    else:
        return name

# Get the rankings from the getRankings cloud function
def fetch_rankings(size=200):
    xcols=("avg_pts","points","events","pts_lost","pts_gained")
    countries={'Argentina': 'ARG', 'Australia': 'AUS', 'Austria': 'AUT', 'Belgium': 'BEL', 'Canada': 'CAN', 'Chile': 'CHL', 'China': 'CHN', 'Chinese Taipei': 'TAI', 'Colombia': 'COL', 'Denmark': 'DEN', 'England': 'ENG', 'France': 'FRA', 'Germany': 'GER', 'India': 'IND', 'Ireland': 'IRE', 'Italy': 'ITA', 'Japan': 'JPN', 'Mexico': 'MEX', 'Netherlands':'NLD','New Zealand': 'NZL', 'Northern Ireland': 'NIR', 'Norway': 'NOR', 'Poland': 'POL', 'Scotland': 'SCO', 'South Africa': 'RSA', 'South Korea': 'KOR', 'Spain': 'ESP', 'Sweden': 'SWE', 'Thailand': 'THA', 'United States': 'USA', 'Venezuela': 'VEN', 'Wales': 'WAL', 'Zimbabwe': 'ZIM'}
    players=[]
    soup=soup_results(rankings_url)
    lastupdate=str(soup.find("p"))[80:-4]
    headers=[th.string for th in soup.findAll("th")]
    rows=[row for row in soup.findAll('tr') if row.find('a') and len(row.findAll("td"))==2]
    xrows=[row for row in soup.findAll('tr') if len(row.findAll("td"))>2]
    for s in range(size):
        player={"rank":s+1,"name":rank_name(rows[s].find('a').string)}
        player["id"]=rows[s].find('a').get('href').split("/")[-2]
        country=rows[s].find("img").get("title")
        if country in countries.keys():
            country=countries.get(country)
        player["country"]=country
        xvals=[get_value(x.string) for x in xrows[s].findAll("td")]
        for (col,val) in zip(xcols,xvals):
            player[col]=val
        player["events"]=int(player["events"])
        players.append(player)
    return {"ID": get_date(lastupdate),"lastupdate":lastupdate, "size":size, "players":players}

# Get the value for a string
def get_value(string):
    string=str(string).replace(',','').replace('-','0')
    try:
        value=round(float(string),2)
    except:
        value=0.0
    if abs(value-int(value))<0.0001:
        value=int(value)
    return value
    
# Get the picks for an event
def get_picks(pickers):
    for picker in pickers:
        picker_name=picker["name"]
        picks[picker_name]={k:picker.get(k) for k in ("picks","points")}
        for pick in picker['picks'][:10]:
            picks[str(pick)]=picker_name
    return picks

def get_pickers(first):
    pickers=[sp for sp in skip_pickers if sp==first]+[sp for sp in skip_pickers if sp!=first]
    return [{"name":p,"number": numbers.get(p), "picks":[],"points":0} for p in pickers]

def open_worksheet(spread,work):
    gc = gspread.service_account('./config/skipflog.json')
    spreadsheet=gc.open(spread)
    worksheet=spreadsheet.worksheet(work)
    return worksheet

# json_results -- get results for a url (or file)
def json_results(url):
    try:
        if url[:4]=="http":
            page=urllib.request.urlopen(url)
        else:
            page=open(url)
        results=json.load(page)
        return results
    except:
        return {}

def soup_results(url):
    page=urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read(),"html.parser")
    return soup

def get_events(nrows=50):
    if cache.get("events"):
        return cache["events"]
    if nrows>0:
        event_list=json_results(events_api).get("events")
    if len(event_list)==0:
        cache["events"]=event_list
    return event_list

# Get the list of events from the spreadsheet 
def fetch_events():
    worksheet=open_worksheet('Majors','Events')
    events=[]
    all_rows=worksheet.get_all_values()
    cols=[c for c in all_rows[0] if len(c)>0]
    for r in range(1,len(all_rows)):
        event={cols[c]:all_rows[r][c] for c in range(len(cols))}
        if event.get("ID"):
            events.append(event)
    return events

def get_players():
    players=cache.get("players",[])
    if len(players)==0:
        players=json_results(events_api).get("players")
        cache["players"]=players
    return players

# Get a default event dictionary
def default_event(event_id=current_event()):
    event=fetch_event(event_id)
    event["event_id"]=int(event['ID'])
    event["event_year"]=int(event['Name'][:4])
    event["Name"]=event['name']
    event["next"]=event["first"]
    event["nextpick"]=event["next"]+"'s First Pick"
    event["pickers"]=get_pickers(event["first"])
    event["pick_no"]=1 
    odds=fetch_odds()
    odds_names=[o for o in odds.keys() if not o.startswith("event")]
    players=[]
    player_keys=['country', 'lastname', 'name', 'odds', 'picked', 'points', 'rank', 'rownum']
    ranks={p["name"]:{k:p.get(k) for k in player_keys} for p in fetch_rankings().get("players") if p["name"] in odds_names}
    for pname in ranks.keys():
        if pname in odds_names:
            player=ranks[pname]
            player["lastname"]=pname.split()[-1]
            player["odds"]=odds[pname]
            player["picked"]=0
            player["rownum"]=len(players)
            players.append(player)
            odds_names.remove(pname)
    # Add unranked players from previous year           
    r=json_results(events_api.replace('2000',str(event_id-100)))
    for player in r["players"]:
        pname=player["name"]
        if pname in odds_names:
            player["odds"]=odds[player["name"]]
            player["points"]=0
            player["rank"]=999
            player["picked"]=0
            player["rownum"]=len(players)
            players.append(player)
            odds_names.remove(player["name"])
    for pname in odds_names:
        player={"name":pname,"lastname":pname.split()[-1],"odds":odds[pname]}
        player["country"]="USA"
        player["points"]=0
        player["rank"]=999
        player["picked"]=0
        player["rownum"]=len(players)  
        players.append(player) 
    event["players"]=players    
    return event

# Get the event data for a given event
def fetch_event(event_id):
    event_data=json_results(events_api.replace("2000",str(event_id)))
    if not event_data:
        event_data=[e for e in fetch_events() if e["ID"]==str(event_id)][0]
    return event_data

# Pull the ESPN url for a given event
def fetch_url(event_id):
    fevents=[f for f in fetch_events() if f["ID"]==str(event_id)]
    if len(fevents)>0:
        return fevents[0].get("espn_url",espn_url)
    else:
         return espn_url

def fetch_headers(soup):
    if not soup:
        return None
    headers={}
    headers['year']=current_year()
    event_name = soup.find('title')
    if event_name and event_name.string:
        event_string=str(event_name.string.replace(u'\xa0',u''))
        headers['name']=event_string[:event_string.index(' Golf')]
    last_update = soup.find('span',{'class': "ten"})
    if last_update:
        headers['lastupdate']= str(last_update.string[-13:])
    else:
        headers['lastupdate']= current_time()
    dates=soup.find("div", { "class" : "date"})
    if dates:
        headers['dates']=xstr(dates.string) 
        headers['year']=int(headers['Dates'][-4:])
    thead=soup.find('thead')
    if soup.find("div",{"class":"status"}):
        headers['status']=str(soup.find("div",{"class":"status"}).find("span").string)
        if headers['status'].startswith("round "):
            headers['round']=headers['status'][6]
        if "Complete" in headers["status"] or "Final" in headers["status"]:
            headers["complete"]=True
        else:
            headers["complete"]=False
    else:
        headers['round']=0
    tables=soup.findAll("table")
    if tables:
        headers['columns']=[]
        for th in tables[-1].findAll('th'):
            if th.a:
                headers['columns'].append(str(th.a.string))
            elif th.string:
                headers['columns'].append(str(th.string))
    return headers
    
def fetch_odds():
    odds_url='http://golfodds.com/upcoming-major-odds.html'
    soup=soup_results(odds_url)
    odds={}
    spans=soup.findAll("span")
    odds["event_name"]=str(current_year())+" "+" ".join(spans[1].text.split())
    locdate=[s.strip() for s in spans[2].text.split('\r\n')]
    odds["event_loc"]=" ".join(locdate[:2])
    odds["event_dates"]=locdate[2]
    for tr in soup.findAll('tr')[:120]:
        td =tr.findAll('td')
        if len(td)==2 and td[0].string and '/' in td[1].string:
            name=xstr(td[0].string)
            if name not in odds.keys():
                odds[name]=xstr(td[1].string.split('/')[0])
    return odds        

def get_rankings(row):
    name = row.find('a')
    cols = row.findAll('td')
    player={}
    if name and len(cols)>=10:
        player_name=rankname(name.string)
        player={'Rank': int(cols[0].text), 'Name': player_name }
        player['Country']= str(cols[3].img.get('title'))
        player['Average']=float(cols[5].text)
        player['Total']=float(cols[6].text)
        player['Events']=int(cols[7].text)
        player["points"]=float(cols[9].text) 
    return player
       
def fetch_details(row, columns):
    dcols=["name","pos","rank","points","score","total"]
    details={}
    name=row.find('a')
    if name:
        details['name']=rank_name(name.string)
        values=[val.string for val in row.findAll('td')]
        results={col:xstr(val) for col,val in zip(columns,values)}
        # Get Rank and Points
        details['rank']=get_rank(str(results.get('POS','99')))
        details['points']=get_points(details['rank'])
        # Get Scores
        scores=[str(results.get(round)) for round in ("R1","R2","R3","R4") if results.get(round) and results.get(round) not in ("-","--")]
        details['scores']="-".join(scores)
        # Get Total
        total=sum([int(score) for score in scores])
        if total>0 and results.get("SCORE"):
            details['total']=str(total)+'('+results['SCORE']+')'
    return results

def fetch_scores(url):
    scores=[[],[], 0,0]
    page=soup_results(url)
    rows=fetch_rows(page)
    cols=[]
    if len(rows)>4:
        cols=rows[3].findAll('td')
    holenum=0
    for col in cols:
        if col.string.isdigit():
            score=int(col.string)
            if score < 20:
                debug_values(holenum, score)
                if holenum<10:
                    scores[0].append(str(score))
                    scores[2]+=score
                else:
                    scores[1].append(str(score))
                    scores[3]+=score
            else:
                holenum-=1 
        holenum+=1
    scores.append(scores[2]+scores[3])
    return scores       

def fetch_tables(url):
    page=soup_results(url)
    tables=page.findAll('table')
    results=''
    for table in tables:
        results=results+str(table)
        results=results+"<p>"
    return results[:-3]

def fetch_header(html):
    str_header=str(BeautifulSoup(html,"html.parser").find('th').string)
    str_header=str_header.replace("The "," ")
    str_year=str(current_year())+" "
    if str_header[:5]!=str_year:
        str_header=str_year+str_header
    return str_header
    
# fetch all table rows
def fetch_rows(page):
#   return page.find('table').findAll('tr')    
    return page.findAll('tr')    

# Get the list of players
def get_playerpicks(playlist):
    current_rank=1
    players=[]
    for player in playlist:
        if player.get('Picker'):
            players.append([current_rank,player['Name'],player['Avg'],player['Week'],player['Rank'],player["points"],player['Picker']])
            current_rank+=1
    return players

# Fetch the list of players from the spreadsheet 
def fetch_players():
    cnum=ncols=6
    worksheet=open_worksheet('Majors','Players')
    players=[]
    all_rows=worksheet.get_all_values()
    r=len(players)+2
    cols=all_rows[0]
    for r in range(1,len(all_rows)):
        player={cols[c]:all_rows[r][c] for c in range(len(cols))}
        player['rownum']=r
        player['rank']=get_value(player.get('rank',999))
        player['lastname']=player['name'].split(" ")[-1]
        player['points']=float(player['points'])
        player['odds']=int(player.get('odds',9999))
        player['picked']=0
        players.append(player)
#       print(player["name"])
    return players

def fetch_results(event_id):
    res_event=fetch_event(event_id)
    picks=get_picks(res_event["pickers"])
    res_url=res_event["espn_url"]
    page=soup_results(res_url)
    headers=fetch_headers(page)
    rows=fetch_rows(page)
    tie={"points":100,"players":[]}
    results={k:res_event[k] for k in res_event.keys() if k.startswith("event")}
    results['event_name']=res_event["Name"]
    results['players']=[]
    for row in rows:
        res=fetch_details(row,headers.get('columns'))
        name=res["name"]=rank_name(res.get("name"))
        if name in picks.keys():
            picker=xstr(picks[name])
            res['picker']=picker
        if res.get('points',0)>=9:
            if res["points"]!=tie.get("points"):
                if len(tie["players"])>1:
                   tie["points"]=float(sum([skip_points[p+1] for p in tie["players"]]))/len(tie["Players"])
                   for p in tie["players"]:
                        results["players"][p]["points"]=tie["points"]
                tie={"players": [len(results['players'])], "points":res["points"], "pos":res["POS"]}
            else:
                tie["players"].append(len(results['players']))
        if res.get('picker') or res.get('points',0)>=10:
            res["points"]=round(res["points"],2)
            results['players'].append(res)
    # get last tie
    if len(tie["players"])>1:
        tie["points"]=float(sum([skip_points[p+1] for p in tie["players"]]))/len(tie["players"])
        for p in tie["players"]:
            results["players"][p]["points"]=tie["points"]
    # filter players
    results["players"]=[p for p in results["players"] if p["points"]>50 or p.get("picker")]
    for picker in skip_pickers:
        picks[picker]["count"]=len([player for player in results.get("players") if player.get("picker")==picker])
        picks[picker]["points"]=sum([player["points"] for player in results.get("players") if player.get("picker")==picker])
    results['pickers']=[picks[key] for key in picks.keys() if key in skip_pickers]
    if results['pickers'][1]["points"]>results['pickers'][0]['points']:
        results['pickers'].reverse()
    for r in range(len(results["pickers"])):
        results['pickers'][r]['points']=round(results['pickers'][r]['points'],2)
        results['pickers'][r]['rank']=r+1
    return results

def new_results(event_id):
    picks=get_picks(event_id)
    for name in skip_pickers:
       picks[name]={"Name":name, "Count":0, "points":0}
    res_url=fetch_url(event_id)
    page=soup_results(res_url)
    tie={"points":100,"Players":[]}
    results=json_results(results_api)
    pts=[get_points(r) for r in range(len(results["players"])) if get_points(r)>0]
    positions={p["POS"]: sum(1 for q in results["players"] if q["POS"]==p["POS"]) for p in results["players"]}
    points={p:round(sum(pts[get_rank(p):get_rank(p)+positions[p]])/positions[p],2) for p in positions.keys() if get_rank(p)<len(pts)}
    results['event']['ID']=event_id
    for res in results["players"]:
        res["points"]=points.get(res["POS"],get_points(res["Rank"]))
        if res.get('Name') in picks.keys():
            picker=xstr(picks[res['Name']])
            res['Picker']=picker
    # filter players
    results["players"]=[p for p in results["players"] if p["points"]>20 or p.get("Picker")]
    for picker in skip_pickers:
        picks[picker]["Count"]=len([player for player in results.get("players") if player.get("Picker")==picker])
        picks[picker]["points"]=sum([player["points"] for player in results.get("players") if player.get("Picker")==picker])
    results['pickers']=[picks[key] for key in picks.keys() if key in skip_pickers]
    if results['pickers'][1]["points"]>results['pickers'][0]["points"]:
        results['pickers'].reverse()
    for r in range(len(results["pickers"])):
        results['pickers'][r]["points"]=round(results['pickers'][r]["points"],2)
        results['pickers'][r]['Rank']=r+1
    return results

def next_pick(picknames,pick_no):
    mypicks = [1,4,5,8,9,12,13,16,17,20,22]
    yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
    pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]
    picknum=pick_ord[pick_no%len(pick_ord)]
    if picknum == "Done":
        return ("Done", "We're Done")
    elif pick_no in mypicks:
        return (picknames[0],picknum)
    else:
        return (picknames[1],picknum)

# Update an event with a picked player. Passing an event dict and an "X picked Y message"
#  Verify that picker X is next and player Y is available (not picked yet)
def pick_player(event, player):
    new_event=event.copy()
    picker=event["next"]
    picknames=[n["name"] for n in event["pickers"]]
    playnames=[p["name"]+("z"*p["picked"]) for p in event["players"]]
    if picker in picknames and player in playnames:
        p=picknames.index(picker)
        q=playnames.index(player)
        new_event["pickers"][p]["picks"].append(player)
        new_event["players"][q]["picked"]=1
        new_event["pick_no"]=event["pick_no"]+1
        if event.get("lastpick") and event["lastpick"].startswith(picker):
            new_event["lastpick"]=event["lastpick"]+" and "+player
        else:
            new_event["lastpick"]=picker+" picked "+player
        picknext,picknum=next_pick(picknames,new_event["pick_no"])
        new_event["next"]=picknext
        if picknext:
            new_event["nextpick"]=picknext+"'s "+picknum+" Pick"
        else:
            new_event["nextpick"]=picknum
    return new_event


 

# Get a matching name from a list of names
def match_name(mname, namelist):
    name=mname
    if name in namelist:
        new_name=name
    else:
        firstinitial=name[:2]
        lastname=name.split()[-1]
        listnames=[n for n in namelist if n.startswith(firstinitial) and n.endswith(lastname)]
        listnames.append(name)
        new_name=listnames[0]
    return new_name
   
# Post the players to the Players tab in Majors spreadsheet
def post_players(players):
    worksheet=open_worksheet('Majors','Players')
    cell_list=worksheet.range('A2:F'+str(len(players)+2))
    for p in range(len(players)):
        cell=p*6
        cell_list[cell].value=players[p]["rank"]
        cell_list[cell+1].value=players[p]["name"]
        cell_list[cell+2].value=players[p]['points']
        cell_list[cell+3].value=players[p]['country']
        cell_list[cell+4].value=players[p]['odds']
        cell_list[cell+5].value=players[p]['picked']
    update=worksheet.update_cells(cell_list)
    return True


# Post the rankings to the "Rankings" tab
def post_rankings():
    this_week=str((current_year()-2000)*100+current_week())
    results=json_results(rankings_api+this_week)
    worksheet=open_worksheet('Majors','Rankings')
    #get date and week number from header
    results_date=results['headers']['date']
    results_week=int(results['headers']['Week'])
    worksheet_week=int(worksheet.acell('D1').value)
    # check if update required
    if (results_week==worksheet_week):
        return False
    else:
        worksheet.update_cell(1, 4, results_week)
        worksheet.update_cell(1, 2, results_date)
    #get all table rows from the page
    players=get_playerpicks(results['players'])
    players.sort(key=lambda player:player[5], reverse=True)
    current_row=3
    pickvals={}
    for picker in skip_pickers:
        pickvals[picker]={'count':0,'total':0.0,'points':0.0 }
    for player in players:
        picker = player[6]
        if (pickvals[picker]['count']<15):
            player[0]=current_row-2
            cell_values = worksheet.range('A'+str(current_row)+':G'+str(current_row))
            for col,cell in zip(player,cell_values):
                cell.value=col
            worksheet.update_cells(cell_values)
            pickvals[picker]['total']+=float(player[3])
            pickvals[picker]['points']+=player[5]
            pickvals[picker]['count']+=1
            current_row += 1
    # update totals
    if pickvals[skip_pickers[1]]['points']>pickvals[skip_pickers[0]]['points']:
        skip_pickers.reverse()
    current_row+=1
    for picker in skip_pickers:
        idx = skip_pickers.index(picker)
        worksheet.update_cell(current_row, 1, idx+1)
        worksheet.update_cell(current_row, 2, picker)
        worksheet.update_cell(current_row, 3, pickvals[picker]['points']/pickvals[picker]['count'])
        worksheet.update_cell(current_row, 4, pickvals[picker]['total'])
        worksheet.update_cell(current_row, 5, pickvals[picker]['count'])
        worksheet.update_cell(current_row, 6, pickvals[picker]['points'])
        current_row+=1    
    return True

def post_results(week_id):
#   results=get_results(event_id)
    if not week_id:
        week_id=str((current_year()-2000)*100+current_week())
    results=json_results(results_api+str(week_id))
    worksheet=open_worksheet('Majors','Results')
    #get date and week number from header
    results_week=str(results['results'][0]['Week'])
    worksheet_week=str(worksheet.acell('I2').value)
    # check if update required
    if (results_week==worksheet_week):
        return False
    # Update points per player
    points={picker:0 for picker in skip_pickers}
    # Clear worksheet
    cell_list = worksheet.range('A2:J40')
    for cell in cell_list:
        cell.value=''
    worksheet.update_cells(cell_list)
    current_row=2
    for event in results['results']:
        worksheet.update_cell(current_row, 1, 'Event:')
        worksheet.update_cell(current_row, 2, event.get('Event Name'))
        worksheet.update_cell(current_row, 7, event.get('Year'))
        worksheet.update_cell(current_row, 8, 'Week:')
        worksheet.update_cell(current_row, 9, event.get('Week'))
        current_row+=1
        for player in event['Results']:
            worksheet.update_cell(current_row, 1, player['Rank'])
            worksheet.update_cell(current_row, 2, player['Name'])
            worksheet.update_cell(current_row, 3, player['R1'])
            worksheet.update_cell(current_row, 4, player['R2'])
            worksheet.update_cell(current_row, 5, player['R3'])
            worksheet.update_cell(current_row, 6, player['R4'])
            worksheet.update_cell(current_row, 8, player['Agg'])
            worksheet.update_cell(current_row, 9, player["points"])
            if player.get('Picker'):
                worksheet.update_cell(current_row, 10, player['Picker'])
                points[player['Picker']]+=player["points"]
            current_row += 1
    # update points per picker
    pickers=skip_pickers
    if points[pickers[1]]>points[pickers[0]]:
        pickers.reverse()
    current_row+=1
    for picker in pickers:
        idx = pickers.index(picker)
        worksheet.update_cell(current_row, 1, idx+1)
        worksheet.update_cell(current_row, 2, picker)
        worksheet.update_cell(current_row, 9, points[picker])
        current_row+=1    
    return True

def update_results(event):
    worksheet=open_worksheet('Majors','Results')
    #get date and week number from header
    # check if update required
    if (results_update==worksheet_update):
        return False
    # Update header information
    worksheet.update_cell(1, 2, event["Name"])
    worksheet.update_cell(1, 4, event["lastupdate"])
    # Update points per player
    points={picker:0 for picker in skip_pickers}
    # Clear worksheet
    cell_list = worksheet.range('A3:F30')
    for cell in cell_list:
        cell.value=''
    worksheet.update_cells(cell_list)
    current_row=3
    for player in results['players']:
        worksheet.update_cell(current_row, 1, player['Rank'])
        worksheet.update_cell(current_row, 2, player['Name'])
        worksheet.update_cell(current_row, 3, player['R1'])
        worksheet.update_cell(current_row, 4, player['R2'])
        worksheet.update_cell(current_row, 5, player['R3'])
        worksheet.update_cell(current_row, 6, player['R4'])
        if player.get('Time'):
            worksheet.update_cell(current_row, 7, player['Time'])
        else:
            worksheet.update_cell(current_row, 7, player['Today'])
        worksheet.update_cell(current_row, 8, player['Total'])
        worksheet.update_cell(current_row, 9, player["points"])
        if player.get('Picker'):
            worksheet.update_cell(current_row, 10, player.get('Picker'))
            points[player['Picker']]+=player["points"]
        current_row += 1
    # update points per picker
    pickers=results['pickers']
    current_row+=1
    for picker in pickers:
        idx = pickers.index(picker)
        worksheet.update_cell(current_row, 1, idx+1)
        worksheet.update_cell(current_row, 2, picker['Name'])
        worksheet.update_cell(current_row, 9, picker["points"])
        current_row+=1
    return True
   
def post_event(event):
    event_api=events_api.replace('2000',str(event["ID"]))
    req = urllib.request.Request(event_api)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(event)
    jsonbytes = jsondata.encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', len(jsonbytes))
    response = urllib.request.urlopen(req, jsonbytes)
    return response
       
def event_results(event_id=current_event()):
    event_api=events_api.replace('2000',str(current_event()))
    new_event=json_results(event_api)
    new_results=get_results(current_event())
    top20_picks=[]    
    for p in range(2):
        r=[q["Name"] for q in new_results["pickers"]].index(new_event["pickers"][p]["name"])
        new_event["pickers"][p]["points"]=new_results["pickers"][r]["points"]
        new_event["pickers"][p]["rank"]=new_results["pickers"][r]["Rank"]
        if len(new_event["pickers"][p]["picks"])>10:
            new_event["pickers"][p]["altpick"]=new_event["pickers"][p]["picks"][-1]
            new_event["pickers"][p]["picks"]=new_event["pickers"][p]["picks"][:10]
            top20_picks=top20_picks+new_event["pickers"][p]["picks"]            
    new_event["lastupdate"]=new_results.get("event").get("Last Update")
    new_event["status"]=new_results.get("event").get("Status")
    new_event["players"]=[{k:p[k] for k in p.keys() if p[k] and p[k]!='--'} for p in new_results["players"]]
    return new_event