# skipflog functions
import csv,json,sys,urllib2
# External modules (gspread, bs4)
import sys
sys.path[0:0] = ['libs']
import gspread
from bs4 import BeautifulSoup

# Misc properties
br="</br>"
events={ 4:'Masters',6:'US Open', 7:'Open Championship', 8:'PGA Championship'}
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','mholtebeck':'Mark'}
pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]
event_url="https://docs.google.com/spreadsheet/pub?key=0Ahf3eANitEpndGhpVXdTM1AzclJCRW9KbnRWUzJ1M2c&single=true&gid=1&output=html&widget=true"
events_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A2%3AE21&output=csv"
players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=B1%3AB156&output=csv"
results_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=2&output=html"
ranking_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=3&output=html"
rankings_url="http://knarflog.appspot.com/ranking"
leaderboard_url="http://sports.yahoo.com/golf/pga/leaderboard/2015/397"
skip_user="skipfloguser"
skip_pass="sK2pfL1g"
skip_picks={}
skip_pickers=["Mark","Steve"]
skip_points=[0, 100, 60, 40, 35, 30, 25, 20, 15, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2]

# Misc urls
espn_url="http://espn.go.com/golf/leaderboard"
golfchannel_url="http://www.golfchannel.com/tours/usga/2014/us-open/"
owg_url="http://www.owgr.com/en/Events/EventResult.aspx?eventid=5520"
pga_url="http://www.pga.com/news/golf-leaderboard/pga-tour-leaderboard"
pgatour_url="http://www.pgatour.com/leaderboard.html"
picks_csv = "picks.csv"
picks_url = "http://skipflog.appspot.com/picks?event_id="
rankings_api = "http://knarflog.appspot.com/api/rankings"
ranking_url="http://www.owgr.com/ranking"
yahoo_base_url="http://sports.yahoo.com"
yahoo_url=yahoo_base_url+"/golf/pga/leaderboard"
debug=False


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
        return str(string.encode('ascii','ignore').strip())

# Function to get_points for a Position
def get_rank(position):
    if not position.replace('T','').isdigit():
        return 0
    else:
        rank = int(position.replace('T',''))
        return rank

def get_points(rank):
    if rank < len(skip_points):
        return skip_points[rank]
    elif rank <= 67:
        return 1
    else:
        return 0


# Get the picks for an event
def get_picks(event_id):
    picks={}
    for picker in skip_pickers:
        picks[picker]=[]
    try:
        debug_values("fetching .. ", picks_csv)
        result = open(picks_csv, "rb")
    except IOError:
        picks_url = "http://skipflog.appspot.com/picks?event_id="+str(event_id)
        debug_values("fetching .. ", picks_url)
        result = urllib2.urlopen(picks_url)
    reader = csv.reader(result)
    for row in reader:
        debug_values(row[0],row)
        if int(row[1])<=20 and row[0]==str(event_id):
            picker=row[2]
            player=row[3]
            picks[player]=picker
            picks[picker].append(player)
    return picks

def open_worksheet(spread,work):
    gc = gspread.login(skip_user,skip_pass)
    spreadsheet=gc.open(spread)
    worksheet=spreadsheet.worksheet(work)
    return worksheet

# json_results -- get results for a url
def json_results(url):
    page=urllib2.urlopen(url)
    results=json.load(page)
    return results

def soup_results(url):
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    return soup

def fetch_headers(soup):
    headers={}
    event_name = soup.find('h4',{'class': "yspTitleBar"})
    if event_name and event_name.string:
        headers['Event Name']= str(event_name.string.replace(u'\xa0',u''))
    last_update = soup.find('span',{'class': "ten"})
    if last_update:
        headers['Last Update']= str(last_update.string[-13:])
#   headers['thead']=soup.find('thead')
    columns=soup.findAll('th')
    colnum=0
    for col in columns:
        if col.string:
            header=str(col.string.replace('\n','').replace(u'\xd1','').replace(u'\xbb',''))
            debug_values(colnum, header)
            if header=='Pos': 
                headers['Columns']=[header]
                colnum=1
            elif headers.get('Columns') and header!='Name':
                headers['Columns'].append(header)
                colnum+=1
    return headers

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
        results['Link']=yahoo_base_url+str(player.get('href'))
        debug_values('Link',results['Link'])
        results['Scores']=""
        results['Total']=0
        cols=row.findAll('td')
        colnum=0
        for col in cols:
            if col.string and colnum<=len(columns):
                column=columns[colnum].replace('R','')
                value=str(col.string.replace('\n',''))
                debug_values(columns[colnum],value)
                if column=='Pos':
                    results['Pos']=value
                    results['Rank']=get_rank(value)
                    results['Points']=get_points(results['Rank'])
                elif column == '1':
                    results['Scores']=value
                    if value.isdigit():
                        results['Total']=int(value)
                        results['Today']=value
                elif column in ('2','3','4'):
                    if value.isdigit():
                        results['Scores']+="-"+value
                        results['Total']+=int(value)
                        results['Today']=value
                    elif value [-2:] in ('am','pm'):
                        results['Time']=value
                    elif value in ('MC','WD','CUT'):
                        results['Pos']=value
                        results['Points']=0
                        results['Total']=0
                elif column == 'Today':
                     if results['Total'] and value[0] in ('+','-','E'):
                        results['Today']=results.get('Today')+"("+value+")"
                elif column == 'Thru':
                    results[column]=value
                    if value not in ('-','F'):
                        results['Today']=results.get('Today')+" thru "+value
                elif column == 'Total':
                    if value[0] in ('+','-','E'):
                        results['Total']="("+value+")"
                elif column in ('Agg','Strokes'):
                    if value.isdigit():
                        if results.get('Scores')!=value:
                            results['Scores']+="-"+value
                        results['Total']=value+"("+last_value+")"
                else:
                        results[column]=value
                colnum+=1
                last_value=value
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


# fetch all table rows
def fetch_rows(page):
    return page.findAll('tr')    

# Get the list of players
def get_players(playlist):
    current_rank=1
    players=[]
    for player in playlist:
        if player.get('Picker'):
            players.append([current_rank,player['Name'],player['Avg'],player['Total'],player['Rank'],player['Points'],player['Picker']])
            current_rank+=1
    return players

def get_results(event_id):
    page=soup_results(leaderboard_url)
    headers=fetch_headers(page)
    results=[headers]
    rows=fetch_rows(page)
    for row in rows:
        res=fetch_results(row, headers.get('Columns'))
        if res.get('Points')>0:
            results.append(res)
    return results

# Post the rankings to the "Rankings" tab
def post_rankings():
    results=json_results(rankings_api)
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
    players=get_players(results['players'])
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

