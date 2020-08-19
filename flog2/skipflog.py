# skipflog functions
import csv,datetime,json,sys,urllib2
from time import gmtime, strftime
# External modules (gspread, bs4)
#import gspread
from bs4 import BeautifulSoup
#from oauth2client.client import SignedJwtAssertionCredentials
from skipconfig import *

firestore_json=json.load(open('config/skipfire.json'))

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
    right_now=strftime("%H%M",gmtime())
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
        print number, string

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
def get_rankings(size):
    ranking_url="http://www.owgr.com/ranking?pageSize="+str(size)
    soup=soup_results(ranking_url)
    rankings=[]
    rank=1
    for row in soup.findAll('tr'):
        name = row.find('a')
        if name:
            points = float(row.findAll('td')[6].string)
            country = row.find("td",{"class","ctry"}).img.get("title")
            player={"rank":rank, "name":xstr(name.string), "country": xstr(country), "points":points }
            rankings.append(player)
            rank+=1
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
    pickdict=json_results(picks_url+str(event_id))
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
    json_key = json.load(open('skipflog.json'))
    scope = [feed_url]
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
#    gc = gspread.authorize(credentials)
#    spreadsheet=gc.open(spread)
#    worksheet=spreadsheet.worksheet(work)
    worksheet=None
    return worksheet

# json_results -- get results for a url
def json_results(url):
    try:
        page=urllib2.urlopen(url)
        results=json.load(page)
        return results
    except:
        return {}

def soup_results(url):
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    return soup

def fetch_events():
    result = urllib2.urlopen(events_url)
    reader = csv.DictReader(result)
    event_list=[]
    for row in reader:
        event_list.append(row)
    return event_list

# Get a default event dictionary
def default_event(event_id=current_event()):
    event=[e for e in fetch_events()][0]
    event["event_id"]=int(event['ID'])
    event["event_year"]=int(event['Name'][:4])
    event["event_name"]=event['Name']
    event["pickers"]=skip_pickers
    event["next"]=event.get('First',skip_pickers[0])
    event["picks"]={"Picked":[],"Available":[] }
    for picker in skip_pickers:
        event["picks"][picker]=[]
    event["picks"]["Available"]=players=[player['name'] for player in get_players()]
    event["pick_no"]=1 
    return event
    
def fetch_url(event_id):
    url={
    1604: 'http://www.espn.com/golf/leaderboard?tournamentId=2493', 
    1606: 'http://www.espn.com/golf/leaderboard?tournamentId=2501', 
    1607: 'http://www.espn.com/golf/leaderboard?tournamentId=2505', 
    1608: 'http://www.espn.com/golf/leaderboard?tournamentId=2507',
    1704: 'http://www.espn.com/golf/leaderboard?tournamentId=2700', 
    1706: 'http://www.espn.com/golf/leaderboard?tournamentId=3066', 
    1707: 'http://www.espn.com/golf/leaderboard?tournamentId=2710', 
    1708: 'http://www.espn.com/golf/leaderboard?tournamentId=2712',
    1804: 'http://www.espn.com/golf/leaderboard?tournamentId=401025221',
    1806: 'http://www.espn.com/golf/leaderboard?tournamentId=401025255',
    1807: 'http://www.espn.com/golf/leaderboard?tournamentId=401025259',
    1808: 'http://www.espn.com/golf/leaderboard?tournamentId=401025263'
    }
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
    dates=soup.find("div", { "class" : "date"})
    if dates:
        headers['Dates']=xstr(dates.string) 
        headers['Year']=int(headers['Dates'][-4:])
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

# Get the list of players
def get_playerpicks(playlist):
    current_rank=1
    players=[]
    for player in playlist:
        if player.get('Picker'):
            players.append([current_rank,player['Name'],player['Avg'],player['Week'],player['Rank'],player['Points'],player['Picker']])
            current_rank+=1
    return players

# Get the list of players from a spreadsheet (players tab)
def get_players():
    picks=get_picks(current_event()).keys()
    players=[]
    players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=A2%3AF155&output=csv"
    result = urllib2.urlopen(players_url)
    reader = csv.reader(result)
    rownum = 1
    for row in reader:
        if row:
            rownum += 1
            player={'rownum':rownum }
            player['rank']=get_value(row[0])
            player['name']=row[1]
            player['lastname']=row[1].split(" ")[-1]
            player['points']=get_value(row[2].replace(',','').replace('-','0'))
            if len(row)>5:           
                player['country']=row[3]
                player['odds']=get_value(row[4])
                player['picked']=picks.count(row[1])
            else:
                player['hotpoints']=0.0
                player['odds']=999
                player['picked']=0
            players.append(player)
    return players

def old_results(event_id):
    picks=get_picks(event_id)
    for name in names.values():
        picks[name]["Count"]=0
    page=soup_results(espn_url)
    results={}
    results['event']=fetch_headers(page)
    results['players']=[]
    rows=fetch_rows(page)
    for row in rows:
        res=fetch_results(row, results.get('event').get('Columns'))
        if res.get('Name') in picks.keys():
            picker=xstr(picks[res['Name']])
            res['Picker']=picker
            picks[picker]['Count']+=1
            picks[picker]['Points']+=res['Points']
        if res.get('Points')>10 or res.get('Picker'):
            if res.get('R1'):
                results['players'].append(res)
    results['pickers']=[picks[key] for key in picks.keys() if key in picks.values()]
    if results['pickers'][1]['Points']>results['pickers'][0]['Points']:
        results['pickers'].reverse()
    results['pickers'][0]['Rank']=1
    results['pickers'][1]['Rank']=2
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
        
# Update the picks to the Players tab in Majors spreadsheet
def pick_players(picklist):
    try:
        players=json_results(players_api)
        worksheet=open_worksheet('Majors','Players')
        for player in players['players']:
            if str(player['name']) in picklist:
                worksheet.update_cell(player["rownum"], 6, 1)
    except:
        pass
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
