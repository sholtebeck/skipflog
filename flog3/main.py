# Main program for golfpicks app (skipflog3.appspot.com)
from flask import Flask, abort, jsonify, render_template, redirect, request, session
#from flask_cors import CORS
from google.auth.transport import requests
import google.oauth2.id_token
import datetime, mail, models
from skipflog import *

app = Flask(__name__)
#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = str.encode(firestore_json.get("apiKey"))
default_url='/static/index.html'
   
def currentEvent():
    now=datetime.datetime.now()
    event_month=min(max(now.month,4),11)
    event_current=100*(now.year-2000)+event_month
    return event_current

def fetchEvents():
    events = [{"event_id":int(f["ID"]),"event_dates":f["event_dates"], "event_loc":f["event_loc"],"event_name":f["Name"]} for f in fetch_events()[:10] if len(f["ID"])==4]
    return events

def getPlayers(event_id='current'):
    players = models.get_event(event_id).get("players")
    return players 

def getPicks(event_id):
    event = getEvent(event_id)
    return event.get("picks")

def getResults(event_id):
    results = models.get_results(event_id)
    if not results:
        try:
            results=get_results(int(event_id))
            models.update_results(results)
        except:
            results=None
    return results

def getEvent(event_id):
    event = models.get_event(event_id)
    return event


def nextEvent():
    event_current=currentEvent()
    event = models.get_event(event_current)
    if not event:
        event=default_event(event_current)
    return event

def updateEvent(event_data):
    models.update_event(event_data)
    return True 
    
def getLastPick(event,picker,player):
    lastpick=event.get("lastpick")
    if lastpick.startswith(picker):
        return lastpick+" and "+player
    else:
        return picker+" picked "+player

def nextPick(event):
    if event['picknum'] == "Done":
        return "Done"
    elif event['pick_no'] in mypicks:
        return event["pickers"][0]
    else:
        return event["pickers"][1]

def updateLastPick(event):
    # send alert if needed
    pick_no = event['pick_no']
    if (pick_no%2==0 or pick_no==21):
        nextnum=[p["number"] for p in event["pickers"] if p["name"]==event["next"]]
        mail.send_message(nextnum[0], event["event_name"], event["lastpick"])
        models.send_message(event["lastpick"],current_time())
    return True

def getUser(id_token=None):
    user=None
    if id_token:
        try:
            user_data = google.oauth2.id_token.verify_firebase_token(id_token, requests.Request())
            user = user_data["name"].split()[0] 
            session['user'] = user_data["user"]=user
            models.set_document("users", user, user_data)
        except:
            return None 
    else:
        user=session.get("user")
    return user

@app.route('/login', methods=['GET','POST'])
def login_page(): 
    title='skipflog - major golf picks'
    user=None
    id_token = request.cookies.get("token")
    if id_token:
        user = getUser(id_token)
    return render_template('login.html',config=firestore_json,id_token=id_token,title=title,user=user)

@app.route('/logout', methods=['POST'])
def logout(): 
    title='skipflog - major golf picks'
    session.pop('username', None)
    return redirect('/login')

@app.route('/')
def main_page(): 
    #find the username in either the session or cookie
    user=getUser()
    if not user:
        id_token=request.cookies.get("token")
        user=getUser(id_token)
    if user:
        event_id=currentEvent()
        event=getEvent(event_id)
        results=getResults(event_id)
        return render_template('index.html',event=event,results=results,user=user)
    else:
        return redirect('/login')

@app.route('/api/events', methods=['GET','POST'])
def api_events():
    events=fetchEvents()    
    return jsonify({'events': events })

@app.route('/api/event', methods=['GET'])
@app.route('/api/event/<string:event_id>', methods=['GET','POST'])
def api_event(event_id=currentEvent()):
    if request.method == "POST":
        event_json = request.json
        updateEvent(event_json)
    event = getEvent(event_id)
    return jsonify(event)

@app.route('/mail', methods=['GET','POST'])
@app.route('/mail/<int:event_id>', methods=['GET'])
def mail_handler(event_id=currentEvent()):
    if request.method=="POST":
        results_html=fetch_tables(picks_url)
    else:
        results_html=fetch_tables(results_url)
    event_name = fetch_header(results_html)
    sent=models.is_sent(event_name)
    if not sent:
        mail.send_mail(event_name,results_html)
        models.send_message(event_name,current_time())
    return jsonify({'event': event_name, "sent":sent })

@app.route('/pick', methods=['GET','POST'])
def pick_handler(event_id = currentEvent()): 
    if request.method=="POST":
        event_id = request.form.get('event_id')
        picker = request.form.get('who')
        player = request.form.get('player')
        # update event (add to picks, remove from field)
        event = getEvent(event_id)
        if player in [p["name"] for p in event["players"]]:
            new_event=pick_player(event,player)
            if new_event != event:
                updateEvent(new_event)
                updateLastPick(new_event)
    # redirect to main page
    return redirect('/',code=302)

@app.route('/api/pick', methods=['POST'])
def api_pick():
    if not request.json or not 'player' in request.json:
        abort(400)
    picker=request.json.get("picker")
    player=request.json.get('player')
    event=models.get_event('current')
    picker=event["next"]
    if picker != event["next"]:
        return jsonify({'success':False,'message':event["nextpick"]})
    if player not in [p["name"] for p in event["players"] if p["picked"]==0]:
        return jsonify({'success':False,'message': player+ " is not available"})
    new_event=pick_player(event,player)
    if new_event != event: 
        success=updateEvent(new_event)
        updateLastPick(new_event)
        message=new_event.get("lastpick")
    return jsonify({'success':success,'message':message})

@app.route('/api/picks', methods=['GET'])
@app.route('/api/picks/<int:event_id>', methods=['GET'])
def picks_handler(event_id=currentEvent()):      
    event = getEvent(event_id)
    pick_dict={}
    for picker in event["pickers"]:
        pickname=picker["name"]
        pick_dict[pickname]=picker["picks"]
        for player in pick_dict[pickname]:
            pick_dict[player]=pickname
    return jsonify({'picks': pick_dict })   

@app.route('/picks', methods=['GET'])
@app.route('/picks/<int:event_id>', methods=['GET'])
def Picks(event_id=currentEvent()):   
    event=getEvent(event_id)
    return render_template('picks.html',event=event)

@app.route('/api/players', methods=['GET'])
@app.route('/api/players/<int:picked>', methods=['GET'])
def ApiPlayers(picked=None):   
    event=getEvent(currentEvent())
    eventdict={k:event[k] for k in [e for e in event.keys() if e.startswith("event") or e.endswith("pick")]}
    eventdict["picker"]=getUser()
    eventdict["nopick"]=(event["next"]!=eventdict["picker"])
    players=event["players"]
    if picked in (0,1):
        players=[p for p in players if p.get("picked")==picked]
    return jsonify({"event":eventdict, "players":players})

@app.route('/players', methods=['GET'])
@app.route('/players/<int:event_id>', methods=['GET'])
def Players(event_id=currentEvent()):   
    event=getEvent(event_id)
    event_name=event["Name"]
    players=event.get("players")
    return render_template('players.html',event_name=event_name)

@app.route('/ranking', methods=['GET'])
def RankingHandler(): 
    rankings_html=fetch_tables(rankings_url)
    event_name = fetch_header(rankings_html)
    sent=models.is_sent(event_name)
    if not sent:
        mail.send_mail(event_name,rankings_html)
        models.send_message(event_name,current_time())
    return jsonify({"event":event_name, "sent":sent})       

@app.route('/api/results', methods=['GET'])
@app.route('/api/results/<int:event_id>', methods=['GET','POST'])
def ApiResults(event_id=currentEvent()): 
    if request.method=="POST":
        results=get_results(event_id) 
        if results:
            models.update_results(results)     
    results = getResults(event_id)
    return jsonify({"results":results})   

@app.route('/results', methods=['GET'])
@app.route('/results/<int:event_id>', methods=['GET'])
def ResultsHandler(event_id=currentEvent()):   
    results = getResults(event_id)
    return render_template('results.html',results=results)

@app.route('/api/user', methods=['GET'])
def ApiUser(event_id=currentEvent()):   
    user= getUser()
    return jsonify(models.get_document("users",user))


if __name__ == '__main__':
    app.run(debug=True,port=5000)
