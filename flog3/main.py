# Main program for golfpicks app (skipflog.appspot.com)
from flask import Flask, abort,json,jsonify,render_template, redirect, request
import datetime,mail,models
from skipflog import *

#Load templates from 'templates' folder
#jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
#jinja_environment = jinja2.Environment(autoescape=True,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
app = Flask(__name__)
app.config['DEBUG'] = True    
default_url='/app/index.html'
   
def currentEvent():
    now=datetime.datetime.now()
    event_month=min(max(now.month,4),10)
    event_current=100*(now.year-2000)+event_month
    return event_current

def fetchEvents():
    events = [{"event_id":f["ID"], "event_name":f["Name"]} for f in fetch_events() if len(f["ID"])==4]
    return events

def getPlayers(event_id='0'):
    players = get_players()
    return players 

def getPicks(event_id):
    event = getEvent(event_id)
    return event.get("picks")

def getResults(event_id):
    results = models.get_results(event_id)
    if not results or results["event"]["Status"]!="Final":
        try:
            results=get_results(int(event_id))
            models.update_results(results)
        except:
            results=None
    return results

def getEvent(event_id):
    event = models.get_event(event_id)
    if not event:
        event=default_event(event_id)
        models.update_event(event)
    return event

def nextEvent():
    event_current=currentEvent()
    event = models.get_event(event_current)
    if not event:
        event=default_event(event_current)
    return event

def updateEvent(event_data):
    models.update_event(event_data)
    
def getLastPick(thispick):
    thisplayer=' '.join(thispick.split()[2:])
    current_event=models.get_event("current")
    lastpick=current_event.get("lastpick")
    if (not lastpick or not lastpick.startswith(thispick.split()[0])):
        lastpick=thispick
    elif (not lastpick.endswith(thisplayer)):
        lastpick=lastpick+" and "+thisplayer
    current_event["lastpick"]=lastpick
    models.update_event(current_event)  
    return lastpick

def nextPick(event):
    if event['picknum'] == "Done":
        return "Done"
    elif event['pick_no'] in mypicks:
        return event["pickers"][0]
    else:
        return event["pickers"][1]
    
def updateLastPick(event):
    lastpick=getLastPick(event['lastpick'])
    # send alert if needed
    pick_no = event['pick_no']
    event["next"]=event['pickers'][0] if mypicks.count(pick_no)>0 else event["pickers"][1]
    if (pick_no<23 and not lastpick.startswith(event["next"])):
        mail.send_message(numbers.get(event["next"]),lastpick)
    return


@app.route('/')
def main_page(): 
    event_id=int( request.args.get('event_id',currentEvent()) )
    event = getEvent(event_id)
    event_list=getEvent("current").get("events")
    user='Steve'
    url='/'
    if event_id:
        event=getEvent(event_id) 
    else:    
        event=getEvent('current')
    pick_no = event.get("pick_no",1)
    event["picknum"] = pick_ord[pick_no]
    event["next"]=nextPick(event)
    event["results"]=results_url+"/"+str(event_id)
    user=event["next"]
    return render_template('index.html',event=event,event_list=event_list,results=2008,url=url,user=user)

@app.route('/api/events', methods=['GET','POST'])
def api_events():
    events=fetchEvents()    
    return jsonify({'events': events })

@app.route('/event', methods=['GET','POST'])
@app.route('/event/<int:event_id>', methods=['GET','POST'])
def api_event(event_id=currentEvent()):
    if request.method == "POST":
        event_data = request.form.get('event_data')
        event_json = json.loads(event_data)
        updateEvent(event_json)
    event = getEvent(event_id)
    return jsonify(event)

@app.route('/mail', methods=['GET'])
@app.route('/mail/<int:event_id>', methods=['GET'])
def mail_handler(event_id=currentEvent()):
    results_html=fetch_tables(results_url)
    event_name = fetch_header(results_html)
    sent=models.is_sent(event_name)
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
            event["lastpick"]=picker+" picked "+player
            event["pick_no"]+=1
            updateEvent(event)
        # update last pick message
        updateLastPick(event)
    # redirect to main page
    return redirect('/',code=302)

@app.route('/picks', methods=['GET','POST'])
def picks_handler(event_id=currentEvent()):   
    if request.method=="POST":
        picklist = request.form.get('picklist')
        pick_players(picklist)     
    event = getEvent(event_id)
    pick_dict={}
    for picker in skip_pickers:
        pick_dict[picker]=event["picks"][picker]
        for player in pick_dict[picker]:
            pick_dict[player]=picker
    return jsonify({'picks': pick_dict })   

@app.route('/api/players', methods=['GET'])
@app.route('/api/players/<int:event_id>', methods=['GET'])
def ApiPlayers(event_id=currentEvent()):   
    event=getEvent(event_id)
    players=getPlayers()
    return jsonify({'event': event, "players":players })   

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
        mail.send_mail(event_name,rankings_html)
        models.send_message(event_name)
    return jsonify({"event":event_name, "sent":sent})       

@app.route('/results', methods=['GET'])
@app.route('/results/<int:event_id>', methods=['GET'])
def ResultsHandler(event_id=currentEvent()):   
    results = getResults(event_id)
    return render_template('results.html',results=results)

if __name__ == '__main__':
    app.run(debug=True)
