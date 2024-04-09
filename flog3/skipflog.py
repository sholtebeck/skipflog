# skipflog functions
import csv,datetime,json,sys,urllib
from time import gmtime, strftime, sleep
import gspread
from bs4 import BeautifulSoup

# Misc properties
cache={}
firestore_json=json.load(open('config/firestore.json'))
events={ 4:'Masters',6:'US Open', 7:'Open Championship', 8:'PGA Championship'}
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','mholtebeck':'Mark'}
emails={'steve':'sholtebeck@gmail.com','mark':'mholtebeck@gmail.com'}
numbers={'Steve':'5103005644@tmomail.com','Mark':'5106739570@sms.boostmobile.com'}
pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]
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

# get current week and year
def current_event():
    this_event=strftime("%y%m",gmtime())
    return int(this_event) 

def current_month():
    this_month=strftime("%m",gmtime())
    return int(this_month) 

def current_week():
    this_week=strftime("%U",gmtime())
    return int(this_week)-1 

def current_year():
    this_year=strftime("%Y",gmtime())
    return int(this_year) 

def current_time():
    right_now=strftime("%c")
    return str(right_now) 

# determine the cut rank for the various majors
def cut_rank():
    this_month=current_month()
    if this_month == 4:
        return 50
    elif this_month == 6:
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

# Get the rankings from the getRankings cloud function
def get_rankings(size=200):
    columns=("avg pts","points","events","points lost","points gained")
    countries={'Argentina': 'ARG', 'Australia': 'AUS', 'Austria': 'AUT', 'Belgium': 'BEL', 'Canada': 'CAN', 'Chile': 'CHL', 'China': 'CHN', 'Chinese Taipei': 'TAI', 'Colombia': 'COL', 'Denmark': 'DEN', 'England': 'ENG', 'France': 'FRA', 'Germany': 'GER', 'India': 'IND', 'Ireland': 'IRE', 'Italy': 'ITA', 'Japan': 'JPN', 'Mexico': 'MEX', 'Netherlands':'NLD','New Zealand': 'NZL', 'Northern Ireland': 'NIR', 'Norway': 'NOR', 'Poland': 'POL', 'Scotland': 'SCO', 'South Africa': 'RSA', 'South Korea': 'KOR', 'Spain': 'ESP', 'Sweden': 'SWE', 'Thailand': 'THA', 'United States': 'USA', 'Venezuela': 'VEN', 'Wales': 'WAL', 'Zimbabwe': 'ZIM'}
    rankings=[]
    soup=soup_results(rankings_url)
    lastdate=str(soup.find("p"))[80:-4]
    headers=[th.string for th in soup.findAll("th")]
    rank=pos=0
    for row in soup.findAll('tr'):
        #This is a header row
        if row.find('a') and row.find("img") and len(row.findAll("td"))<4: 
            rank+=1
            name = row.find('a').string
            url = row.find('a').get("href")
            if (url):
                id = url.split('/')[7]
            country="USA"
            if (row.find("img")):
                country=row.find("img").get("title")
            player={"ID":id,"Rank":rank,"Name":name,"Country": countries.get(country,country[:3].upper),"Points":0 }
            rankings.append(player)
        elif len(row.findAll("td"))>4: 
            dlist=[float(t.string) for t in row.findAll("td")]
            for d in range(len(dlist)):
                if pos<len(rankings):
                    rankings[pos][columns[d].capitalize().replace(" ","_")]=dlist[d]
            pos+=1
    return {"ID": get_date(lastdate), "date":lastdate,"players":rankings}

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
def get_picks(event_id):
    picks={}
    pickdict=json_results(picks_api+str(event_id))
    if pickdict.get('picks'):
        for picker in skip_pickers:
            picklist=[str(pick) for pick in pickdict["picks"][picker][:10]]
            picks[picker]={'Name':picker,'Count':len(picklist),'Picks':picklist,'Points':0}
            for pick in picklist:
                picks[str(pick)]=picker
    else:
        for picker in skip_pickers:
            if pickdict.get(picker):
                picklist=[str(pick) for pick in pickdict[picker][:10]]
                picks[picker]={'Name':picker,'Count':len(picklist),'Picks':picklist,'Points':0}
                for pick in picklist:
                    picks[str(pick)]=picker
    return picks

def get_pickers(first):
    pickers=[sp for sp in skip_pickers if sp==first]+[sp for sp in skip_pickers if sp!=first]
    return [{"name":p,"number": numbers.get(p), "picks":[],"points":0} for p in pickers]

def open_worksheet(spread,work):
    gc = gspread.service_account('../../skipflog/skipflog.json')
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

def fetch_events(nrows=50):
    if cache.get("events"):
        return cache["events"]
    if nrows>0:
        event_list=json_results(events_api).get("events")
    if len(event_list)==0:
        cache["events"]=event_list
    return event_list

# Get the list of events from the spreadsheet 
def get_events():
    worksheet=open_worksheet('Majors','Events')
    events=[]
    all_rows=worksheet.get_all_values()
    cols=[c for c in all_rows[0] if len(c)>0]
    for r in range(1,len(all_rows)):
        event={cols[c]:all_rows[r][c] for c in range(len(cols))}
        events.append(event)
    return events

def fetch_players():
    players=cache.get("players",[])
    if len(players)==0:
        players=json_results(events_api).get("players")
        cache["players"]=players
    return players

# Get a default event dictionary
def default_event(event_id=current_event()):
    event=[e for e in fetch_events()][0]
    event["event_id"]=int(event['ID'])
    event["event_year"]=int(event['Name'][:4])
    event["event_name"]=event['Name']
    event["next"]=event["first"]
    event["nextpick"]=event["next"]+"'s First Pick"
    event["pickers"]=get_pickers(event["first"])
    event["players"]=fetch_players()
    event["pick_no"]=1 
    return event

# Get the event data for a given event
def fetch_event(event_id):
    fevents=[f for f in fetch_events() if f["ID"]==str(event_id)]
    if len(fevents)>0:
        return fevents[0]
    else:
        return {"ID": event_id, "espn_url": espn_url }

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
    headers['Year']=current_year()
    event_name = soup.find('title')
    if event_name and event_name.string:
        event_string=str(event_name.string.replace(u'\xa0',u''))
        headers['Name']=event_string[:event_string.index(' Golf')]
    last_update = soup.find('span',{'class': "ten"})
    if last_update:
        headers['Last Update']= str(last_update.string[-13:])
    else:
        headers['Last Update']= current_time()
    dates=soup.find("div", { "class" : "date"})
    if dates:
        headers['Dates']=xstr(dates.string) 
        headers['Year']=int(headers['Dates'][-4:])
    thead=soup.find('thead')
    if soup.find("div",{"class":"status"}):
        headers['Status']=str(soup.find("div",{"class":"status"}).find("span").string)
        if headers['Status'].startswith("Round "):
            headers['Round']=headers['Status'][6]
        if "Complete" in headers["Status"] or "Final" in headers["Status"]:
            headers["Complete"]=True
        else:
            headers["Complete"]=False
    else:
        headers['Round']=0
    tables=soup.findAll("table")
    if tables:
        headers['Columns']=[]
        for th in tables[-1].findAll('th'):
            if th.a:
                headers['Columns'].append(str(th.a.string))
            elif th.string:
                headers['Columns'].append(str(th.string))
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

def fetch_rankings(row):
    name = row.find('a')
    cols = row.findAll('td')
    player={}
    if name and len(cols)>=10:
        player_name=str(name.string)
        player={'Rank': int(cols[0].text), 'Name': player_name }
        player['Country']= str(cols[3].img.get('title'))
        player['Average']=float(cols[5].text)
        player['Total']=float(cols[6].text)
        player['Events']=int(cols[7].text)
        player['Points']=float(cols[9].text) 
    return player
       
def fetch_results(row, columns):
    results={}
    player=row.find('a')
    if player:
        results['Name']=str(player.string)
        debug_values('Name',results['Name'])
#       results['Link']=yahoo_base_url+str(player.get('href'))
#       debug_values('Link',results['Link'])
        values=[val.string for val in row.findAll('td')]
        for col,val in zip(columns,values):
            if col not in ("None",None):
                results[col]=str(val)
        # Get Rank and Points
        results['Rank']=get_rank(results.get('POS','99'))
        results['Points']=get_points(results['Rank'])
        # Get Scores
        scores=[]
        for round in ("R1","R2","R3","R4"):
            if results.get(round) and results.get(round) not in ("--"):
                scores.append(results.get(round))
                results["Today"]=results[round]
        results['Scores']="-".join(scores)
        # Get Today
        if not results.get('THRU'):
            results['THRU']='-'
        elif results.get('THRU')=='F':
            results['Today']+='('+results['TODAY']+')'
        elif results.get('THRU').isdigit():
            results['Today']='('+results['TODAY']+') thru '+results['THRU']
            results['Total']='('+results.get('SCORE')+') thru '+results['THRU']
        elif results['THRU'][-2:] in ('AM','PM'):
            results['Time']='@ '+results['THRU']
        elif results['THRU'] in ('MC','CUT'):
            results['Rank']=results['THRU']
            results['Today']=results['THRU']
        # Get Total
        if results.get('TOT') not in (None,"--"):
            results['Total']=results['TOT']+'('+results['SCORE']+')'
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
            players.append([current_rank,player['Name'],player['Avg'],player['Week'],player['Rank'],player['Points'],player['Picker']])
            current_rank+=1
    return players

# Get the list of players from the spreadsheet 
def get_players():
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

def get_results(event_id):
    picks=get_picks(event_id)
    for name in skip_pickers:
       picks[name]={"Name":name, "Count":0, "Points":0}
    res_event=fetch_event(event_id)
    res_url=res_event["espn_url"]
    page=soup_results(res_url)
    results={}
    tie={"Points":100,"Players":[]}
    results['event']=fetch_headers(page)
    results['event']['ID']=event_id
    results['event']['Name']=res_event["Name"]
    results['players']=[]
    rows=fetch_rows(page)
    for row in rows:
        res=fetch_results(row, results.get('event').get('Columns'))
        if res.get('Name') in picks.keys():
            picker=xstr(picks[res['Name']])
            res['Picker']=picker
        if res.get('Points',0)>=9:
            if res["Points"]!=tie.get("Points"):
                if len(tie["Players"])>1:
                   tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
                   for p in tie["Players"]:
                        results["players"][p]["Points"]=tie["Points"]
                tie={"Players": [len(results['players'])], "Points":res["Points"], "POS":res["POS"]}
            else:
                tie["Players"].append(len(results['players']))
        if res.get('Picker') or res.get('Points',0)>=9:
            res["Points"]=round(res["Points"],2)
            del res["PLAYER"]
            results['players'].append(res)
    # get last tie
    if len(tie["Players"])>1:
        tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
        for p in tie["Players"]:
            results["players"][p]["Points"]=tie["Points"]
    # filter players
    results["players"]=[p for p in results["players"] if p["Points"]>20 or p.get("Picker")]
    for picker in skip_pickers:
        picks[picker]["Count"]=len([player for player in results.get("players") if player.get("Picker")==picker])
        picks[picker]["Points"]=sum([player["Points"] for player in results.get("players") if player.get("Picker")==picker])
    results['pickers']=[picks[key] for key in picks.keys() if key in skip_pickers]
    if results['pickers'][1]['Points']>results['pickers'][0]['Points']:
        results['pickers'].reverse()
    for r in range(len(results["pickers"])):
        results['pickers'][r]['Points']=round(results['pickers'][r]['Points'],2)
        results['pickers'][r]['Rank']=r+1
    return results

def new_results(event_id):
    picks=get_picks(event_id)
    for name in skip_pickers:
       picks[name]={"Name":name, "Count":0, "Points":0}
    res_url=fetch_url(event_id)
    page=soup_results(res_url)
    tie={"Points":100,"Players":[]}
    results=json_results(results_api)
    pts=[get_points(r) for r in range(len(results["players"])) if get_points(r)>0]
    positions={p["POS"]: sum(1 for q in results["players"] if q["POS"]==p["POS"]) for p in results["players"]}
    points={p:round(sum(pts[get_rank(p):get_rank(p)+positions[p]])/positions[p],2) for p in positions.keys() if get_rank(p)<len(pts)}
    results['event']['ID']=event_id
    for res in results["players"]:
        res["Points"]=points.get(res["POS"],get_points(res["Rank"]))
        if res.get('Name') in picks.keys():
            picker=xstr(picks[res['Name']])
            res['Picker']=picker
    # filter players
    results["players"]=[p for p in results["players"] if p["Points"]>20 or p.get("Picker")]
    for picker in skip_pickers:
        picks[picker]["Count"]=len([player for player in results.get("players") if player.get("Picker")==picker])
        picks[picker]["Points"]=sum([player["Points"] for player in results.get("players") if player.get("Picker")==picker])
    results['pickers']=[picks[key] for key in picks.keys() if key in skip_pickers]
    if results['pickers'][1]['Points']>results['pickers'][0]['Points']:
        results['pickers'].reverse()
    for r in range(len(results["pickers"])):
        results['pickers'][r]['Points']=round(results['pickers'][r]['Points'],2)
        results['pickers'][r]['Rank']=r+1
    return results

def next_pick(picknames,pick_no):
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

def rank_name(name):
    ranknames={'Ludvig Åberg':'Ludvig Aberg','Nicolai Højgaard':'Nicolai Hojgaard','Thorbjørn Olesen':'Thorbjorn Olesen'}
    if name in ranknames.keys():
        return ranknames.get(name)
    else:
        return name
 

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
def post_players():
#    current_csv='https://docs.google.com/spreadsheets/d/1v3Jg4w-ZvbMDMEoOQrwJ_2kRwSiPO1PzgtwqO08pMeU/pub?single=true&gid=0&output=csv'
#    result = urllib.request.urlopen(current_csv)
#    rows=[row for row in csv.reader(result)]
#    names=[name[1] for name in rows[3:] if name[1]!='']
    odds=fetch_odds()
    odds_names=[o for o in odds.keys() if not o.startswith("event")]
    odds_names.sort(key=lambda o:odds[o])
    rankings=get_rankings().get('players',[])
    rank_names=[rank_name(rank['Name']) for rank in rankings]
    worksheet=open_worksheet('Majors','Players')
    row=2
    players=[]
#   event=json_results(event_json)
    for pname in odds_names:
        cell_list = worksheet.range('A'+str(row)+':F'+str(row))
        if pname in rank_names:
            player=rankings[rank_names.index(match_name(pname,rank_names))]
            player["Odds"]=odds.get(pname)
            player["Picked"]=0
            cell_list[0].value=player['Rank']
            cell_list[1].value=pname
            cell_list[2].value=player['Points']
            cell_list[3].value=player['Country']
            cell_list[4].value=player['Odds']
            cell_list[5].value=0
            row+=1
            update=worksheet.update_cells(cell_list)
            players.append(player)
        else:
            print(pname + " NOT RANKED")
            player={"Rank": 999, "Name": pname, "Points": 0, "Country": "USA", "Odds": odds.get(pname)}
            cell_list[0].value=player['Rank']
            cell_list[1].value=player['Name']
            cell_list[2].value=player['Points']
            cell_list[3].value=player['Country']
            cell_list[4].value=player['Odds']
            cell_list[5].value=0
            row+=1
            update=worksheet.update_cells(cell_list)
            players.append(player)
        sleep(1)
    return players


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
            worksheet.update_cell(current_row, 9, player['Points'])
            if player.get('Picker'):
                worksheet.update_cell(current_row, 10, player['Picker'])
                points[player['Picker']]+=player['Points']
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

def update_results(event_id):
    results=get_results(event_id)
    worksheet=open_worksheet('Majors','Results')
    #get date and week number from header
    results_update=str(results['event']['Last Update'])
    worksheet_update=str(worksheet.acell('I2').value)
    # check if update required
    if (results_update==worksheet_update):
        return False
    # Update header information
    worksheet.update_cell(2, 2, results['event'].get('Name'))
    worksheet.update_cell(2, 8, 'Update:')
    worksheet.update_cell(2, 9, results_update)
    worksheet.update_cell(1, 1, 'Pos')
    worksheet.update_cell(1, 2, 'Player')
    worksheet.update_cell(1, 3, 'R1')
    worksheet.update_cell(1, 4, 'R2')
    worksheet.update_cell(1, 5, 'R3')
    worksheet.update_cell(1, 6, 'R4')
    worksheet.update_cell(1, 7, 'Today')
    worksheet.update_cell(1, 8, 'Total')
    worksheet.update_cell(1, 9, 'Points')
    worksheet.update_cell(1, 10, 'Picked By')
    # Update points per player
    points={picker:0 for picker in skip_pickers}
    # Clear worksheet
    cell_list = worksheet.range('A3:J40')
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
        worksheet.update_cell(current_row, 9, player['Points'])
        if player.get('Picker'):
            worksheet.update_cell(current_row, 10, player.get('Picker'))
            points[player['Picker']]+=player['Points']
        current_row += 1
    # update points per picker
    pickers=results['pickers']
    current_row+=1
    for picker in pickers:
        idx = pickers.index(picker)
        worksheet.update_cell(current_row, 1, idx+1)
        worksheet.update_cell(current_row, 2, picker['Name'])
        worksheet.update_cell(current_row, 9, picker['Points'])
        current_row+=1
    return True

def mail_results():
    res=get_results(current_event())
    status=res["event"]["Status"]
    if 'Complete' in status:
        models.update_results(res)
        res=json_results(mail_url)
    else:
        res={"last update":res["event"]["Last Update"], "status":status}
    return res
    
def post_event(event):
    event_api=events_api.replace('2000',str(event["ID"]))
    req = urllib.request.Request(event_api)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(event)
    jsonbytes = jsondata.encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', len(jsonbytes))
    response = urllib.request.urlopen(req, jsonbytes)
    return response