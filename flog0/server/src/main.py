import urllib
from time import gmtime, strftime
from bs4 import BeautifulSoup
from flask import request,jsonify

# Function to get_points for a Position
def getRank(position):
    if not position.replace('T','').isdigit():
        return 99
    else:
        rank = int(position.replace('T',''))
        return rank

def getPoints(rank):
    points=[0, 100, 60, 40, 30, 24, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9.5, 9, 8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,4,3.5,3.5,3,3,2.5,2.5,2,2,2,1.5,1.5]
    if rank < len(points):
        return points[rank]
    elif rank <= 60:
        return 1
    else:
        return 0
		
# Handler for string values to ASCII or integer
def xStr(string):
    if string is None:
        return None 
    elif string.isdigit():
        return int(string)
    else:
        return str(''.join([i if ord(i) < 128 else ' ' for i in string]))

def fetchHeaders(soup):
    if not soup:
        return None
    headers={}
    headers['Year']=strftime("%Y",gmtime())
    event_name = soup.find('title')
    if event_name and event_name.string:
        event_string=str(event_name.string.replace(u'\xa0',u''))
        headers['Name']=event_string[:event_string.index(' Golf')]
    last_update = soup.find('span',{'class': "ten"})
    if last_update:
        headers['Last Update']= str(last_update.string[-13:])
    else:
        headers['Last Update']= str(strftime("%c",gmtime()))
    dates=soup.find("span",{"class":"Leaderboard__Event__Date"})
    if dates:
        headers['Dates']=xStr(dates.string) 
        headers['Year']=int(headers['Dates'][-4:])
    location=soup.find("div",{"class":"Leaderboard__Course__Location"})
    if location:
        headers['Location']=xStr(location.text)
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

def fetchResults(row, columns):
    results={}
    player=row.find('a')
    if player:
        results['Name']=str(player.string)
        values=[val.string for val in row.findAll('td')]
        for col,val in zip(columns,values):
            if col not in ("None",None):
                results[col]=str(val)
        # Get Rank and Points
        results['Rank']=getRank(results.get('POS','99'))
        results['Points']=getPoints(results['Rank'])
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
            results['Total']=results['TOT']+'('+results.get('SCORE')+')'
    #remove unneeded values from the dictionary
    for key in [k for k in results.keys() if k in ('EARNINGS','FEDEX PTS','TO PAR','PLAYER','THRU','Today')]:
        results.pop(key)
    return results

def getResults():
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    url="http://www.espn.com/golf/leaderboard"
    page = BeautifulSoup(urllib.request.urlopen(url).read(),"html.parser")
    results={}
    results['event']=fetchHeaders(page)
    results['players']=[]
    rows=page.findAll('tr') 
    tie={"Points":100,"Players":[]}
    for row in rows:
        res=fetchResults(row, results.get('event').get('Columns'))
        if res.get("Points",None)!=tie.get("Points"):
            if len(tie["Players"])>1:
                tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
                for p in tie["Players"]:
                    results["players"][p]["Points"]=tie["Points"]
                tie={"Players": [len(results['players'])], "Points":res["Points"], "POS":res["POS"]}        
        if res.get('R1'):
            results['players'].append(res)
    return results
