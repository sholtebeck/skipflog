# Main program for golfpicks app (skipflog.appspot.com)
from flask import Flask, abort, jsonify, render_template, redirect, request, session
#from google.appengine.api import users, wrap_wsgi_app
import json,datetime,os
import mail
import models
from skipflog import *

# set Flask app
app=Flask(__name__)
app.secret_key = str.encode(firestore_json.get("apiKey"))
#app.wsgi_app = wrap_wsgi_app(app.wsgi_app)
   
   
def currentEvent():
#    now=datetime.datetime.now()
#    event_month=min(max(now.month,4),8)
#    event_current=100*(now.year-2000)+event_month
    return "2212"

def lastSunday():
    today=datetime.date.today()
    sunday=today-datetime.timedelta(today.isoweekday())
    return sunday.strftime('%y%m%d')

def fetchEvents():
    events = [{"event_id":int(f["ID"]),"event_dates":f["event_dates"], "event_loc":f["event_loc"],"event_name":f["Name"]} for f in fetch_events() if len(f["ID"])==4]
    return events

def getPlayers(event_id='current'):
    players = models.get_event(event_id).get("players")
    return players

def getPicks(event_id):
    event = getEvent(event_id)
    return event.get("pickers")

def getResults(event_id):
    results = models.get_results(event_id)
    if not results:
        try:
            results=new_results(int(event_id))
            models.update_results(results)
        except:
            results=None
    return results

def getEvent(event_id=currentEvent()):
    event=models.get_event(event_id)
    for picker in event['pickers']:
        picker['picks']=picker.get("picks",[])
    return event

def getUser(id_token=None):
    if session.get("user"):
        return session["user"]
    else:
        return ""

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

  
def updateLastPick(event):
    lastpick=getLastPick(event.get('lastpick',""))
    # send alert if needed
    pick_no = event['pick_no']
    event["next"]=event['pickers'][0] if mypicks.count(pick_no)>0 else event["pickers"][1]
    if (pick_no<23 and not lastpick.startswith(event["next"])):
        message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',subject=event["event_name"])
        message.to = numbers.get(event["next"])
        message.body=lastpick
        message.send()    
    return

# API routes
@app.route('/api/event', methods=['GET'])
@app.route('/api/event/<string:event_id>', methods=['GET','POST'])
def api_event(event_id=currentEvent()):
    if request.method == "POST":
        event_json = request.json
        updateEvent(event_json)
    event = getEvent(event_id)
    return jsonify(event)

@app.route('/api/events', methods=['GET','POST'])
def api_events():
    events=models.get_events()
    return jsonify({'events': events })

@app.route('/api/pick/<string:event_id>', methods=['PUT'])
def api_pick(event_id=currentEvent()):
    if not request.json or not 'player' in request.json:
        abort(400)
    picker=request.json.get("picker")
    player=request.json.get('player')
    event=getEvent(event_id)
#   picker=event["next"]
    if picker != event["next"]:
        return jsonify({'success':False,'message':event["nextpick"]})
    if player not in [p["name"] for p in event["players"] if p["picked"]==0]:
        return jsonify({'success':False,'message': player+ " is not available"})
    new_event=pick_player(event,player)
    if new_event != event: 
        success=updateEvent(new_event)
#       updateLastPick(new_event)
        message=new_event.get("lastpick")
    return jsonify({'request': request.json, 'success':success,'message':message,'event':new_event })

@app.route('/api/picks', methods=['GET'])
@app.route('/api/picks/<int:event_id>', methods=['GET'])
def picks_handler(event_id=currentEvent()):      
    event = getEvent(event_id)
    pick_dict={}
    for picker in event["pickers"]:
        pickname=picker["Name"]
        pick_dict[pickname]=picker["Picks"]
        for player in pick_dict[pickname]:
            pick_dict[player]=pickname
    return jsonify({'picks': pick_dict })

@app.route('/api/player/<int:player_id>', methods=['GET'])
def api_player(player_id=0): 
    player=models.get_document("players",player_id)
    return jsonify({"player":player})

@app.route('/api/players', methods=['GET'])
def api_players(picked=None):   
    players=[{"ID": p["rownum"],"Name":p["Name"],"POS":p["POS"],"Picked-Mark":p["picked"]["Mark"],"Picked-Steve":p["picked"]["Steve"],"Picked-Total":p["picked"]["Total"],"Points": p["picked"]["Points"]} for p in models.get_players() if p]
    return jsonify({"players":players})

@app.route('/api/rankings', methods=['GET','POST'])
@app.route('/api/rankings/<int:date_id>', methods=['GET'])
def api_rankings(date_id=lastSunday()):   
    if request.method=="POST":
        rankings=get_rankings() 
        models.set_document("rankings", rankings["ID"], rankings)
    else:
        rankings = models.get_document('rankings',date_id)
    return jsonify(rankings)

@app.route('/api/results', methods=['GET'])
@app.route('/api/results/<int:event_id>', methods=['GET','POST'])
def ApiResults(event_id=currentEvent()): 
    if request.method=="POST":
        results=get_results(event_id) 
        if results:
            models.update_results(results)     
    results = getResults(event_id)
    return jsonify({"results":results})

@app.route('/api/user', methods=['GET'])
def ApiUser(event_id=currentEvent()):   
    user= getUser()
    return jsonify({"user":user})

@app.route('/', methods=['GET','POST'])
def main_page(): 
    user=getUser()
    if user in skip_pickers or user=="skipflog":
#       event_id=currentEvent()
        event=getEvent()
#        results=getResults()
        results={}
        return render_template('index.html',event=event,results=results,user=user)
    else:
        return redirect('/login')


@app.route('/event', methods=['GET','POST'])
def post_event(event_id=currentEvent()):
    if request.method == "POST":
        event_data = request.form.get('event_data')
        event_json = json.loads(event_data)
        updateEvent(event_json)
    return jsonify(event)

@app.route('/login', methods=['GET','POST'])
def login(): 
    if request.method == "POST":
        user=request.form.get('user')
        password=request.form.get('password')
        email=emails.get(user.lower())
        try:
            email=emails.get(user)
            usr=models.auth.sign_in_with_email_and_password(email, password)
            token=models.auth.refresh(usr['refreshToken'])
            session["user"]=user
            return redirect("/")
        except Exception as e:
            return jsonify({"form":request.form, "user":user, "email":email,"error": str(e) })
    else:
        user=getUser()
        title='skipflog - major golf picks'
        return render_template('login.html',config=firestore_json,title=title,user=user)

@app.route('/logout', methods=['POST'])
def logout(): 
    title='skipflog - major golf picks'
    session.pop('user', None)
    return redirect('/login')


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
        sent=mail.send_mail(event_name,results_html)
        models.send_message(event_name,current_time())
    return jsonify({'event': event_name, "sent":sent })

@app.route('/pick', methods=['GET','POST'])
def pick_handler(event_id = currentEvent()): 
    if request.method=="POST":
        event_id = request.form.get('event_id',event_id)
        picker = request.form.get('who')
        player = request.form.get('player')
        event = getEvent(event_id)
        # update event (add to picks, remove from field)
        if player in [p["name"] for p in event["players"]]:
            new_event=pick_player(event,player)
            if new_event != event:
                updateEvent(new_event)
#               updateLastPick(new_event)
    # redirect to main page
    return redirect('/',code=302)

@app.route('/picks', methods=['GET'])
@app.route('/picks/<int:event_id>', methods=['GET'])
def Picks(event_id=currentEvent()):   
    event=getEvent(event_id)
    return render_template('picks.html',event=event)    

@app.route('/players', methods=['GET'])
@app.route('/players/<int:event_id>', methods=['GET'])
def Players(event_id=currentEvent()):   
    event=getEvent(event_id)
    event_name=event["Name"]
    players=event.get("players")
    return render_template('players.html',event=event)

@app.route('/ranking', methods=['GET'])
def RankingHandler(): 
    rankings_html=fetch_tables(rankings_url)
    event_name = fetch_header(rankings_html)
    sent=models.is_sent(event_name)
    if not sent:
        mail.send_mail(event_name,rankings_html)
        models.send_message(event_name,current_time())
    return jsonify({"event":event_name, "sent":sent}) 

@app.route('/results', methods=['GET'])
@app.route('/results/<int:event_id>', methods=['GET'])
def ResultsHandler(event_id=currentEvent()):   
    results = getResults(event_id)
    return render_template('results.html',results=results)

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))

