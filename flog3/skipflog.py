# skipflog functions
import csv,datetime,json,sys,urllib
from time import gmtime, strftime, sleep
from urllib import request
#import gspread
from bs4 import BeautifulSoup

# Misc properties
names={'sholtebeck':'Steve','mholtebeck':'Mark'}
emails={'steve':'sholtebeck@gmail.com','mark':'mholtebeck@gmail.com'}
numbers={'Steve':'5103005644@tmomail.com','Mark':'5106739570@sms.boostmobile.com'}
skip_pickers=["Steve","Mark"]
#skip_points=[0, 100, 60, 40, 35, 30, 25, 20, 15, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2]
skip_points=[0, 100, 60, 40, 30, 24, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9.5, 9, 8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,4,3.5,3.5,3,3,2.5,2.5,2,2,2,1.5,1.5]
# Misc urls
espn_url="http://www.espn.com/golf/leaderboard"
results_url="https://skipflog3.appspot.com/results"
# feed_url='https://spreadsheets.google.com/feeds'
# golfchannel_url="http://www.golfchannel.com/tours/usga/2014/us-open/"
# owg_url="http://www.owgr.com/en/Events/EventResult.aspx?eventid=5520"
# pga_url="http://www.pga.com/news/golf-leaderboard/pga-tour-leaderboard"
# pgatour_url="http://www.pgatour.com/leaderboard.html"
# picks_csv = "picks.csv"
# picks_api = "https://skipflog3.appspot.com/api/picks/"
# picks_url = "https://skipflog3.appspot.com/picks"
# rankings_api="https://skipflog.appspot.com/rankings"
# results_api="https://skipflog.appspot.com/results/"
# owg_ranking_url="http://www.owgr.com/ranking"
# yahoo_base_url="http://sports.yahoo.com"
# yahoo_url=yahoo_base_url+"/golf/pga/leaderboard"
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
        return 60
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
def get_picks(pickers):
    picks={}
    for picker in pickers:
        picker_name=picker["name"]
        picks[picker_name]={k:picker.get(k) for k in ("picks","points")}
        for pick in picker['picks'][:10]:
            picks[str(pick)]=picker_name
    return picks

def get_pickers(first):
    pickers=[sp for sp in skip_pickers if sp==first]+[sp for sp in skip_pickers if sp!=first]
    return [{"name":p,"number": numbers.get(p), "picks":[],"points":0} for p in pickers]

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
    return json_results(events_api)

# Get the list of events from the spreadsheet 
def get_events():
    events=cache.get("events",[])
    if len(events)==0:
        events=json_results(events_api)
        cache["events"]=events
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

# Get the event name for an event ID
def event_name(event_id):
    ename={"04":" Masters","05":" PGA Championship","06":" US Open","07":" Open Championship","08":" PGA Championship"}
    return "20"+str(event_id)[:2]+ename.get(str(event_id)[2:])

# Get the event data for a given event
def fetch_event(event_id):
    event=json_results(event_api+str(event_id))
    if not event:
        event={"ID": event_id, "Name":event_name(event_id), "espn_url": espn_url }
    return event

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
    odds_api='https://skipflog.appspot.com/odds'
    return json_results(odds_api) 

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
       
def fetch_details(row, columns):
    dcols=["name","pos","rank","points","scores","total"]
    details={dc:"" for dc in dcols}
    name=row.find('a')
    if name:
        details['name']=rank_name(name.string)
        vals={col:fetch_value(val) for col,val in zip(columns,row.findAll('td')) if col and val}
        # Get POS, Rank and Points
        details['pos']=vals.get("POS")
        details['rank']=get_rank(str(vals.get('POS','99')))
        details['points']=get_points(details['rank'])
        # Get Scores
        details['scores']='-'.join([str(vals.get(round)) for round in ("R1","R2","R3","R4") if vals.get(round) and vals.get(round) not in ("-","--")])
        # Get Total
        #total=sum([int(score) for score in scores])
        details['total']=vals.get("TOT")+'('+vals.get('SCORE')+')'
    return details

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
    return fetch_players()

def fetch_results(event_id):
    event=fetch_event(event_id)
    if event.get("status")!="Final":
        picks=get_picks(event["pickers"])
        pickedplayers=[p["name"] for p in event["players"]]
        page=soup_results(event["espn_url"])
        headers=fetch_headers(page)
        event["lastupdate"]=headers.get("lastupdate")
        event["status"]=headers.get("status")
        rows=fetch_rows(page)
        hdr=[fetch_value(th) for th in rows[0].findAll('th')]
        players=[fetch_details(row,hdr) for row in rows[1:] if row.find('a')]
        ties={t:tie_points(t,len([p for p in players if p["pos"]==t])) for t in set(p['pos'] for p in players if p['pos'][0]=='T')}
        for player in players:
            player["points"]=ties.get(player["pos"],player["points"])
            if player["name"] in pickedplayers:
                player["picker"]=picks[player["name"]]
                pp=picked_players.index(player["name"])
                for key in player.keys():
                    event["players"][pp][key]=player[key]
        event["players"].sort(key=lambda p:p["points"],reverse=True)
        # filter players
        if event['pickers'][1]["points"]>event['pickers'][0]['points']:
            event['pickers']=[event['pickers'][1],event['pickers'][0]]
            event["pickers"][0]["rank"]=1
            event["pickers"][1]["rank"]=2
    return event

def fetch_value(td):
    if td.string:
        return td.string
    elif td.find("a"):
        return td.find("a").string


def event_results(event_id=current_event()):
    results=json_results(results_api+str(event_id))
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
   
# This will check results and send mail if complete
def send_results():
    res=get_results(current_event())
    status=res["event"]["Status"]
    if res["event"].get('Complete'):
        from mail import send_mail
        from models import update_results
        update_results(res)
        results_html=fetch_tables(results_url)
        subject=fetch_header(results_html)
        sent=send_mail(status,results_html)
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
