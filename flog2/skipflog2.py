# skipflog functions
import csv,datetime,json,sys
import urllib.request
from time import gmtime, strftime
# External modules (gspread, bs4)
#import sys
#sys.path[0:0] = ['libs']
#import gspread
#from bs4 import BeautifulSoup
#from oauth2client.client import SignedJwtAssertionCredentials

# Misc properties
cache={}
events=None
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','mholtebeck':'Mark'}
numbers={'Steve':'5103005644@vtext.com','Mark':'5106739570@vmobl.com'}
pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]
event_url="https://docs.google.com/spreadsheet/pub?key=0Ahf3eANitEpndGhpVXdTM1AzclJCRW9KbnRWUzJ1M2c&single=true&gid=1&output=html&widget=true"
#events_api="https://storage.googleapis.com/skipflog/json/events.json"
events_api="../json/events.json"
events_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A1%3AE42&output=csv"
players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=B2%3AB155&output=csv"
results_tab="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=2&output=html"
ranking_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=3&output=html"
rankings_url="http://knarflog.appspot.com/ranking"
result_url="http://knarflog.appspot.com/results"
results_url="http://skipflog3.appspot.com/results"
players_api="http://knarflog.appspot.com/api/players"
#players_api="../json/players.json"
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
picks_api="http://skipflog.appspot.com/api/picks/"
picks_csv = "picks.csv"
picks_url = "http://skipflog2.appspot.com/picks?event_id="
rankings_api = "http://knarflog.appspot.com/api/rankings/"
results_api = "http://knarflog.appspot.com/api/results/"
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
    right_now=strftime("%c",gmtime())
    return str(right_now) 

def dict_to_list(d,k):
    if isinstance(d,dict):
        return sorted([i[1] for i in list(d.items())],key=lambda j:j[k],reverse=True)
    else:
        return d

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

# Get the rankings from the page
def get_rankings(size=150):
    if cache.get('rankings'):
        return cache["rankings"]
    ranking_url="http://www.owgr.com/ranking?pageSize="+str(size)
    soup=soup_results(ranking_url)
    rankings=[]
    rank=1
    for row in soup.findAll('tr'):
        name = row.find('a')
        if '(' in name:
            name=name[:name.index('(')]
        if name:
            points = float(row.findAll('td')[6].string)
            country = row.find("td",{"class","ctry"}).img.get("title")
            player={"rank":rank, "name":xstr(name.string), "country": xstr(country), "points":points }
            rankings.append(player)
            rank+=1
    cache["rankings"]=rankings
    return rankings

# Get the value for a string
def get_value(string):
    string=string.replace(',','').replace('-','0')
    try:
        value=round(float(string),2)
    except:
        value=0.0
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


def open_worksheet(spread,work):
    gc = gspread.service_account("skipflog.json")
    spreadsheet=gc.open(spread)
    worksheet=spreadsheet.worksheet(work)
    return worksheet

# json_results -- get results for a url
def json_results(url):
    if url[:4]!="http":
        return json.load(open(url))
    try:
        page=urllib.request.urlopen(url)
        results=json.load(page)
        return results
    except:
        return {}

def soup_results(url):
    try:
        page=urllib.request.urlopen(url)
        soup = BeautifulSoup(page.read(),"html.parser")
    except:
        return None
    return soup

def fetch_events():
    if cache.get('events'):
        return cache["events"]
    event_list=json_results(events_api)["events"]
    cache["events"]=event_list
    return event_list

def fetch_event(event_id):
    event_list=[e for e in fetch_events() if e['event_id']==event_id]
    if len(event_list)>0:
        return event_list[0]
    else:
        return {}

def fetch_players():
    players=cache.get("players",[])
    if len(players)==0:
        players=get_players()
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
    
def fetch_url(event_id):
    url={f["event_id"]: f["espn_url"] for f in fetch_events()}
    if url.get(event_id):
        return url[event_id]
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
    dates=soup.find("span",{"class":"Leaderboard__Event__Date"})
    if dates:
        headers['Dates']=xstr(dates.string) 
        headers['Year']=int(headers['Dates'][-4:])
    location=soup.find("div",{"class":"Leaderboard__Course__Location"})
    if location:
        headers['Location']=xstr(location.text)
    thead=soup.find('thead')
    if soup.find("div",{"class":"status"}):
        headers['Status']=str(soup.find("div",{"class":"status"}).find("span").string)
        if headers['Status'].startswith("Round "):
            headers['Round']=headers['Status'][6]
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
    for tr in soup.findAll('tr'):
        td =tr.findAll('td')
        if len(td)==2 and td[0].string and '/' in td[1].string:
            odds[xstr(td[0].string)]=xstr(td[1].string.split('/')[0])
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
            results['Total']='('+results.get('TO PAR')+') thru '+results['THRU']
        elif results['THRU'][-2:] in ('AM','PM'):
            results['Time']='@ '+results['THRU']
        elif results['THRU'] in ('MC','CUT'):
            results['Rank']=results['THRU']
            results['Today']=results['THRU']
        # Get Total
        if results.get('TOT') not in (None,"--"):
            results['Total']=results['TOT']+'('+results['TO PAR']+')'
    #remove unneeded values from the dictionary
    for key in [k for k in results.keys() if k in ('EARNINGS','FEDEX PTS','TO PAR','PLAYER','THRU','Today')]:
        results.pop(key)
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
    return str(BeautifulSoup(html).find('th').string)
    
# fetch all table rows
def fetch_rows(page):
#   return page.find('table').findAll('tr')    
    return page.findAll('tr')    


def get_pickers(first):
    pickers=[sp for sp in skip_pickers if sp==first]+[sp for sp in skip_pickers if sp!=first]
    return [{"name":p,"number": numbers.get(p), "picks":[],"points":0} for p in pickers]

# Get the list of players
def get_playerpicks(pickers,players):
    results={"pickers": pickers, "players":[]}
    pd={}
    for picker in pickers:
        for player in picker["picks"]:
            pd[player]=pickers.index(picker)
    for player in players:
        pts=player.pop("Ranking Points",0)
        p=pd.get(player["Name"],None)
        if p in (0,1):
            player["Picker"]=pickers[p]["Name"]
            results["players"].append(player)
            results["pickers"][p]["points"]+=player["Points"]
    return results

# Get the list of players from a spreadsheet (players tab)
def get_players():
    players=json_results(players_api).get("players")
    for player in players:
        name=player.get('name')
        player['rownum']=players.index(player)+1
        player['rank']=int(player['rank'])
        player['lastname']=name.split(" ")[-1]
        player['points']=player['points']
        player['picked']=0
    return players

# espn_results (all players)
def espn_results(event_id):
    url=fetch_url(event_id)
    page=soup_results(url)
    results={}
    results['event']=fetch_headers(page)
    results['players']=[]
    rows=fetch_rows(page)
    tie={"Points":100,"Players":[]}
    for row in rows:
        res=fetch_results(row, results.get('event').get('Columns'))
        if res.get("Points",None)!=tie.get("Points"):
            if len(tie["Players"])>1:
                tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
                for p in tie["Players"]:
                    results["players"][p]["Points"]=tie["Points"]
                tie={"Players": [len(results['players'])], "Points":res["Points"], "POS":res["POS"]}        
        if res.get('R1'):
            results['players'].append(res)
    return results
    
def get_results(event_id):
    picks=get_picks(event_id)
    for name in skip_pickers:
       picks[name]={"Name":name, "Count":0, "Points":0}
    res_url=fetch_url(event_id)
    page=soup_results(res_url)
    results={}
    tie={"Points":100,"Players":[]}
    results['event']=fetch_headers(page)
    results['event']['ID']=event_id
    results['players']=[]
    rows=fetch_rows(page)
    for row in rows:
        res=fetch_results(row, results.get('event').get('Columns'))
        if res.get('Name') in picks.keys():
            picker=xstr(picks[res['Name']])
            res['Picker']=picker
        if res.get('Points')>=9:
            if res["Points"]!=tie.get("Points"):
                if len(tie["Players"])>1:
                   tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
                   for p in tie["Players"]:
                        results["players"][p]["Points"]=tie["Points"]
                tie={"Players": [len(results['players'])], "Points":res["Points"], "POS":res["POS"]}
            else:
                tie["Players"].append(len(results['players']))
        if res.get('Picker') or res.get('Points')>=9:
            results['players'].append(res)
    # get last tie
    if len(tie["Players"])>1:
        tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
        for p in tie["Players"]:
            results["players"][p]["Points"]=tie["Points"]
    for picker in skip_pickers:
        picks[picker]["Count"]=len([player for player in results.get("players") if player.get("Picker")==picker])
        picks[picker]["Points"]=sum([player["Points"] for player in results.get("players") if player.get("Picker")==picker])
    results['pickers']=[picks[key] for key in picks.keys() if key in skip_pickers]
    if results['pickers'][1]['Points']>results['pickers'][0]['Points']:
        results['pickers'].reverse()
    results['pickers'][0]['Rank']=1
    results['pickers'][1]['Rank']=2
    return results
        
# Update the picks to the Players tab in Majors spreadshee
# Get a matching name from a list of names
def match_name(name, namelist):
    if name in namelist:
        new_name=name
    else:
        names=name.split()
        listnames=[n for n in namelist if names[0] in n and names[-1] in n]
        listnames.append(name)
        new_name=listnames[0]
    return new_name
   
# Post the players to the Players tab in Majors spreadsheet
def post_players():
#    current_csv='https://docs.google.com/spreadsheets/d/1v3Jg4w-ZvbMDMEoOQrwJ_2kRwSiPO1PzgtwqO08pMeU/pub?single=true&gid=0&output=csv'
#    result = urllib2.urlopen(current_csv)
#    rows=[row for row in csv.reader(result)]
#    names=[name[1] for name in rows[3:] if name[1]!='']
    odds_names=[n.strip() for n in open("app\players.txt").readlines()]
#    odds=fetch_odds()
#    odds_names=odds.keys()
    odds_names.sort()
    rankings=get_rankings(1500)
    rank_names=[rank['name'] for rank in rankings]
    worksheet=open_worksheet('Majors','Players')
    current_cell=0
    cell_list = worksheet.range('A2:F'+str(len(odds_names)+1))
    for name in odds_names:
        debug_values(odds.get(name), name)
        matching_name=match_name(name,rank_names)
        if matching_name in rank_names:
            player=rankings[rank_names.index(matching_name)]
            cell_list[current_cell].value=player['rank']
            cell_list[current_cell+1].value=player['name']
            cell_list[current_cell+2].value=player['points']
            cell_list[current_cell+3].value=player['country']
        else:
            cell_list[current_cell].value=9999
            cell_list[current_cell+1].value=name
            cell_list[current_cell+2].value=0.0
            cell_list[current_cell+3].value='USA'
        if name in odds.keys():
            cell_list[current_cell+4].value=odds[name]
        else:
            cell_list[current_cell+4]=9999
        cell_list[current_cell+5].value=0
        print(matching_name)
        current_cell += 6
    worksheet.update_cells(cell_list)
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
    players=get_playerpicks(results['players'])["players"]
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

def load_majors(y):
    yfile="C:\\Users\\sholtebeck\\Documents\\GitHub\\knarflog\\json\\majors\\"+str(y)+".json"
    return json_results(yfile)['majors']

def load_events(k=42):
    events=json_results('../json/events.json')["events"][:k]
    majors=[]
    #change ecount to run this process
    ecount=0  
    for n in range(ecount):
        e=events[n]
        if e["Year"]==2017:
            event_id=int(e.get("event_id",e.get("ID")))
            event_name=e.get("Name")
            event_year=2017
            print(event_id,event_name)
            if len(majors)==0:
                majors=load_majors(event_year)
            m=majors[0]
            e0 = {"event_id":event_id, "ID": str(event_id),"Name": event_name,"Year": int(event_year) } 
            e0["Week"]=m["Week"]
            e0["Winner"]=m["Winner"]
            e0["pickers"]=e["pickers"]
            for q in range(2):
                e0["pickers"][q]["points"]=0.0
            e0["espn_url"]=fetch_url(event_id)
            s=soup_results(e0["espn_url"])
            h=fetch_headers(s)
            e0["event_dates"]=h["Dates"]    
            e0["event_loc"]=h["Location"]
            e0["owgr_id"]=m["ID"]
            e0["event_name"]=m["Event Name"]
            pp=get_playerpicks(e0["pickers"],m["results"])
            e0["pickers"]=pp["pickers"]
            e0["players"]=pp["players"]
            events[n]=e0
            majors.remove(m)
    return events   

def load_players(events=load_events()):
    pd={}
    players=[]
    for e in events:
        for p in e["players"]:
            pname=p["Name"]
            if pname not in pd.keys():
                pd[pname]=len(players)
                players.append({"Name":pname, "pickers":[]})
            pick=str(e["event_id"])+p["Picker"][0]
            players[pd[pname]]["pickers"].append(pick)
    for p in players:
        p["picked"]={q:len([r for r in p["pickers"] if r[-1]==q[0]]) for q in skip_pickers}
        p["picked"]["Total"]=sum(p["picked"].values())
        p["pickers"]=','.join(p["pickers"])
    players.sort(key=lambda p:p["Name"])
    return {"players":players}   