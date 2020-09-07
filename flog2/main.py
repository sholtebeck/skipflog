# Main program for golfpicks app (skipflog.appspot.com)
from flask import Flask, abort,json,jsonify,render_template,redirect,request
import datetime,mail
from skipflog2 import *

#Load templates from 'templates' folder
#jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
#jinja_environment = jinja2.Environment(autoescape=True,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
app = Flask(__name__)
app.config['DEBUG'] = True    
default_url='/static/index.html'
   
def currentEvent():
    return int(fetch_events()[0]["ID"])

def fetchEvents():
     events = [{"event_id":f["ID"], "event_name":f["Name"], "event_dates": f["event_dates"], "event_loc": f["event_loc"]} for f in fetch_events() if len(f["ID"])==4]
     return events

def getPlayers(event_id='current'):
    players=json_results(players_api)
    return players 

def getPicks(event_id):
    picks=get_picks(event_id)
    return picks

def getResults(event_id):
    results= get_api_results(event_id)
    return results

def getEvent(event_id):
    event = fetch_event(event_id)
    return event

def nextEvent():
    event_current=currentEvent()
    event=get_event(event_current)
    if not event:
        event=default_event(event_current)
    return event

def updateEvent(event_data):
    update_event(event_data)
    
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
        mail.send_message(numbers.get(event["next"]),event["event_name"],event["lastpick"])
    return

def getUser(id_token):
    user_data={"user":'Steve'}
    return user_data

@app.route('/login')
def login_page(): 
    title='skipflog - golf picks'
    event_list=fetch_events()
    id_token = request.cookies.get("token")
    error_message = None
    user_data = getUser(id_token)
    return render_template('login.html',config=firestore_json,event_list=event_list,title=title,user_data=user_data, error_message=error_message)

@app.route('/')
def main_page(): 
    id_token=request.cookies.get("token")
    user_data=getUser(id_token)
    event_id=int( request.args.get('event_id',currentEvent()) )
    event = getEvent(event_id)
    event_list=fetch_events()
    user=user_data.get("user")
    event=getEvent(event_id) 
    pick_no = event.get("pick_no",1)
    event["picknum"] = pick_ord[pick_no]
    event["next"]=nextPick(event)
    event["results"]=getResults(event_id).get("results")
    return render_template('index.html',event=event,event_list=event_list,user=user)

@app.route('/api/events', methods=['GET','POST'])
def api_events():
    events=fetchEvents()    
    return jsonify({'events': events })

@app.route('/api/event', methods=['GET','POST'])
@app.route('/api/event/<int:event_id>', methods=['GET','POST'])
def api_event(event_id=currentEvent()):
    if request.method == "POST":
        event_data = request.form.get('event_data')
        event_json = json.loads(event_data)
        updateEvent(event_json)
    event = getEvent(event_id)
    event["pickers"]=dict_to_list(event["pickers"],"points")
    return jsonify(event)

@app.route('/mail', methods=['GET','POST'])
@app.route('/mail/<int:event_id>', methods=['GET'])
def mail_handler(event_id=currentEvent()):
    if request.method=="POST":
        results_html=fetch_tables(picks_url)
    else:
        results_html=fetch_tables(results_url)
    event_name=fetch_header(results_html)
    if not sent:
        mail.send_mail(event_name,results_html)
    return jsonify({'event': event_name, "sent":sent })

@app.route('/pick', methods=['GET','POST'])
def pick_handler(event_id = currentEvent()): 
    if request.method=="POST":
        event_id = request.form.get('event_id')
        picker = request.form.get('who')
        player = request.form.get('player')
        # update event (add to picks, remove from field)
        event = getEvent(event_id)
        if player in event["picks"]["Available"]:
            event["picks"]["Available"].remove(player)
            event["picks"]["Picked"].append(player)
            event["picks"][picker].append(player)
            event["lastpick"]=getLastPick(event,picker,player)
            event["pick_no"]+=1
            updateEvent(event)
        # update last pick message
        updateLastPick(event)
    # redirect to main page
    return redirect('/',code=302)

@app.route('/api/picks', methods=['GET'])
@app.route('/api/picks/<int:event_id>', methods=['GET'])
def picks_handler(event_id=currentEvent()):   
    if request.method=="POST":
        picklist = request.form.get('picklist')
        pick_players(picklist)     
    event = getEvent(event_id)
    pick_dict=event.get("pickers")
    return jsonify({'event_name':event.get("Name"), 'picks': pick_dict })   

@app.route('/picks', methods=['GET'])
@app.route('/picks/<int:event_id>', methods=['GET'])
def Picks(event_id=currentEvent()):   
    event=getEvent(event_id)
    return render_template('picks.html',event=event)

@app.route('/api/players', methods=['GET'])
@app.route('/api/players/<int:event_id>', methods=['GET'])
def ApiPlayers(event_id=currentEvent()):  
    players=json_results(players_api)
    return jsonify(players)

@app.route('/players', methods=['GET'])
@app.route('/players/<int:event_id>', methods=['GET'])
def Players(event_id=currentEvent()):   
    event=getEvent(event_id)
    players=getPlayers()
    return render_template('players.html',event=event,players=players)

@app.route('/ranking', methods=['GET'])
def RankingHandler(): 
    rankings_html=fetch_tables(rankings_url)
    event_name = fetch_header(rankings_html)
    sent=models.is_sent(event_name)
    if not sent:
        sent=mail.send_mail(event_name,rankings_html)
        models.set_document('message',event_name,sent)
    return jsonify({"event":event_name, "sent":sent})       

@app.route('/api/results', methods=['GET'])
@app.route('/api/results/<int:event_id>', methods=['GET'])
def ApiResults(event_id=currentEvent()):   
    results = getResults(event_id)
    return jsonify(results)   

@app.route('/results', methods=['GET'])
@app.route('/results/<int:event_id>', methods=['GET'])
def ResultsHandler(event_id=currentEvent()):   
    results = getResults(event_id)
    return render_template('results.html',results=results["results"])

if __name__ == '__main__':
    app.run(debug=True)
