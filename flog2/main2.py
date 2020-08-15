# Main program for golfpicks app (skipflog2.appspot.com)
import cgi,csv,json,datetime
import jinja2
import logging
import urllib2
import webapp2
import os,sys
import models
#from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import users
from skipflog2 import *

#Load templates from 'templates' folder
#jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment = jinja2.Environment(autoescape=True,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
     
   
def currentEvent():
    now=datetime.datetime.now()
    event_month=min(max(now.month,4),8)
    event_current=100*(now.year-2000)+event_month
    return event_current

def fetchEvents():
    events = memcache.get('events')
    if not events:
        events=fetch_events()
        memcache.add('events', events)
    return events

def getPlayers(event_id='0'):
    players = memcache.get('players')
    if not players:
        players=get_players()
        memcache.add('players', players)
    return players 

def getPicks(event_id):
    picks = memcache.get('picks'+event_id)
    if not picks:
        event = getEvent(event_id)
        memcache.add('picks'+event_id, event.get("picks"))
    return picks

def getResults(event_id):
    results_key='results'+str(event_id)
    resultstr = memcache.get(results_key)
    if resultstr:
        results=json.loads(resultstr)
    else:
        results=models.get_results(event_id)
        if not results or results["event"]["Status"]!="Final":
            try:
                results=get_results(int(event_id))
                models.update_results(results)
                resultstr=str(json.dumps(results))
                memcache.add(results_key,resultstr,240)
            except:
                memcache.delete(results_key)    
    return results

def getEvent(event_id):
#    event = Event.get(event_key(event_id))
    event = models.get_event(event_id)
    if event:
        event_data=event.event_json
    else:
        event_data=default_event(event_id)
        models.update_event(event_data)
    return event_data

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
    lastpick=memcache.get("lastpick")
    if (not lastpick or not lastpick.startswith(thispick.split()[0])):
        lastpick=thispick
    elif (not lastpick.endswith(thisplayer)):
        lastpick=lastpick+" and "+thisplayer
    memcache.delete("lastpick")  
    memcache.add("lastpick",lastpick)  
    return lastpick
    
def updateLastPick(event):
    lastpick=getLastPick(event['lastpick'])
    # send alert if needed
    pick_no = event['pick_no']
    event["next"]=event['pickers'][0] if mypicks.count(pick_no)>0 else event["pickers"][1]
    if (pick_no<23 and not lastpick.startswith(event["next"])):
        message = mail.EmailMessage(sender='admin@skipflog2.appspotmail.com',subject=event["event_name"])
        message.to = numbers.get(event["next"])
        message.body=lastpick
        message.send()    
    return

class MainPage(webapp2.RequestHandler):       
    def get(self):
        event_list = []
        event_name = "None"
        event_id = self.request.get('event_id');
        if not event_id:
            event_list=[{"event_id":event["ID"],"event_name":event["Name"]} for event in fetchEvents()]
    
        if users.get_current_user():
            user = names[users.get_current_user().nickname()]
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            user = ""
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'event_list': event_list,
            'event_name': event_name,
            'title': "Events",
            'url': url,
            'url_linktext': url_linktext,
            'user': user,
        }
        template = jinja_environment.get_template('index2.html')
        self.response.out.write(template.render(template_values))

class MailHandler(webapp2.RequestHandler):       
    def get(self):
        event_id = self.request.get('event_id')
        if event_id:
            results_html=fetch_tables(results_url)
            event_name = fetch_header(results_html)
            message = mail.EmailMessage(sender='admin@skipflog2.appspotmail.com',subject=event_name)
            message.to = "skipflog@googlegroups.com"
            message.html=results_html
            message.send()
 

    def post(self):
        event_id = self.request.get('event_id')
        event = getEvent(event_id)
        user = users.get_current_user()
        message = mail.EmailMessage(sender='admin@skipflog2.appspotmail.com',
                            subject=event.get('event_name')+" picks")
        message.to = "skipflog@googlegroups.com"
        message.html=event.get('event_name')+"<br>"
        for picker in skip_pickers:
            message.html += picker+"'s Picks:<ol>"
            for player in event.get('picks').get(picker):
                message.html+="<li>"+player
            message.html+="</ol>"
        message.send()
        self.redirect('/pick?event_id=' + event_id)

class PickHandler(webapp2.RequestHandler):
    def get(self):     
        event_id = int(self.request.get('event_id',currentEvent()))
        event = getEvent(event_id)
        pick_no = event["pick_no"]
        picknum = pick_ord[pick_no]
        # get next player
        if picknum != "Done":
            event["next"]=event["pickers"][0] if mypicks.count(pick_no)>0 else event["pickers"][1]
        else:
            event["next"]="Done"
        # check results
        if memcache.get("lastpick"):
            event["lastpick"]=memcache.get("lastpick")
        event["results"]=results_url+"?event_id="+str(event_id)
        if users.get_current_user():
            user = names[users.get_current_user().nickname()]
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            user = ""
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
     
        template_values = {
            'event': event,
            'pick_no': pick_no,
            'picknum': picknum,
            'url': url,
            'url_linktext': url_linktext,
            'user': user
        }
        template = jinja_environment.get_template('picks2.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        event_id = self.request.get('event_id')
        picker = self.request.get('who')
        player = self.request.get('player')
        memcache.delete('picks'+event_id)
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
        self.redirect('/pick?event_id=' + event_id) 

class EventHandler(webapp2.RequestHandler):
    def get(self):     
        event_id = int(self.request.get('event_id',currentEvent()))
        output=self.request.get('output')
        if "results" in self.request.url:
            template_values = { 'results': getResults(event_id) }
            template = jinja_environment.get_template('results2.html')
            self.response.out.write(template.render(template_values))
        else:
            event = getEvent(event_id)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(event))
            
    def post(self):     
        event_data = self.request.get('event_data')
        event_json = json.loads(event_data)
        updateEvent(event_json)
        event_id = str(event_json["event_id"])
        self.redirect('/event?event_id=' +event_id) 

class PicksHandler(webapp2.RequestHandler):   
    def get(self):
        output_format = self.request.get('output','json')
        event_id = self.request.get('event_id',currentEvent())
        if not event_id:
            event_id=currentEvent()    
        event = getEvent(event_id)
        if event:
            pick_dict={}
            for picker in skip_pickers:
                pick_dict[picker]=event["picks"][picker]
                for player in pick_dict[picker]:
                     pick_dict[player]=picker
            if output_format=='json':
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps({"picks":pick_dict}))
                    
    def post(self):
        picklist = self.request.get('picklist')
        pick_players(picklist)     

class PlayersHandler(webapp2.RequestHandler):   
    def get(self):
        event_id = self.request.get('event_id')
        if event_id:
            event = getEvent(event_id)
        else:
            event = nextEvent()
        output_format = self.request.get('output')
        if not output_format:
            output_format='html'
        players=getPlayers()
        self.response.headers['Content-Type'] = 'application/json'
        template_values = { 'event': event.event_json, "players": players }
        self.response.write(json.dumps(template_values))

class RankingHandler(webapp2.RequestHandler): 
    def get(self):
        taskqueue.add(url='/ranking', params={'event_week': current_week(),'event_year': current_year()})
#       taskqueue.add(url='/results', params={'event_week': current_week(),'event_year': current_year()})
        
    def post(self):
#       event_update=post_rankings()
        rankings_html=fetch_tables(rankings_url)
        event_name = fetch_header(rankings_html)
        message = mail.EmailMessage(sender='admin@skipflog2.appspotmail.com',subject=event_name)
        message.to = "skipflog@googlegroups.com"
        message.html=rankings_html+"<p>"
        message.html+=fetch_tables(result_url)
        message.send()        
            
class ResultsHandler(webapp2.RequestHandler):   
    def get(self):
        output_format = self.request.get('output')
        if not output_format:
            output_format='html'
        event_id = self.request.get('event_id')
        if not event_id:
            event_id = currentEvent()
        results = getResults(event_id)
        if output_format=='json':
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps({"results":results}))
        elif output_format=='html':
            template_values = {'results': results }
            template = jinja_environment.get_template('results2.html')
            self.response.out.write(template.render(template_values))
                    
    def post(self):
        event_week = self.request.get('event_week')
        event_year = self.request.get('event_year')
        this_week = str((int(event_year)-2000)*100+int(event_week))
        event_update=post_results(this_week)
        event_name = event_year + " World Golf Results (Week "+str(event_week)+")"
        message = mail.EmailMessage(sender='admin@skipflog2.appspotmail.com',subject=event_name)
        message.to = "skipflog@googlegroups.com"
        message.html=fetch_tables(result_url)
        message.send()        

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        current=datetime.datetime.now()
        taskqueue.add(url='/update', params={'event_id': currentEvent()})

    def post(self):
        event_id = self.request.get('event_id')
        event_update=update_results(event_id)

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/event', EventHandler),
  ('/mail', MailHandler),
  ('/pick', PickHandler),
  ('/picks', PicksHandler),
  ('/players', PlayersHandler),
  ('/ranking', RankingHandler),
  ('/results', ResultsHandler), 
  ('/update', UpdateHandler)  
], debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()
