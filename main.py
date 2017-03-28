# Main program for golfpicks app (skipflog.appspot.com)
import cgi,csv,json,datetime
import jinja2
import logging
import urllib2
import webapp2
import os,sys

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import users
from skipflog import *

#Load templates from 'templates' folder
#jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment = jinja2.Environment(autoescape=True,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
     
   
class Event(db.Model):
    event_id = db.IntegerProperty(required=True)
    event_name = db.StringProperty()
    event_url = db.StringProperty()
    first = db.StringProperty()
    next = db.StringProperty()
    field = db.StringListProperty()
    pickers = db.StringListProperty()
    picks = db.StringListProperty()
    start = db.IntegerProperty()  

class Pick(db.Model):
    who = db.StringProperty()
    player = db.StringProperty()
    when = db.DateTimeProperty(auto_now_add=True)
    pick_no = db.IntegerProperty()
    points = db.IntegerProperty()

def event_key(event_id):
  """Constructs a Datastore key for an Event entity with event_id."""
  return db.Key.from_path('Event', event_id)

def currentEvent():
    now=datetime.datetime.now()
    event_current=100*(now.year-2000)+now.month
    return event_current

def fetchEvents():
    result = urllib2.urlopen(events_url)
    reader = csv.reader(result)
    event_list=[]
    for row in reader:
        event_list.append(row)
    return event_list

def getEvents():
    events = memcache.get('events')
    if not events:
        events=[]
        rows=fetchEvents()
        for row in rows:
            event=Event(key_name=row[0], event_id=int(row[0]), event_name=row[1], event_url=row[2])
            events.append(event)
        memcache.add('events', events)
    return events

def getPlayers(event_id='0'):
    players = memcache.get('players')
    if not players:
        players=[]
        result = urllib2.urlopen(players_url)
        reader = csv.reader(result)
        for row in reader:
            players.append(str(row[0]))
        players.sort()
        memcache.add('players', players)
    return players 

def getPicks(event_id):
    picks = memcache.get('picks'+event_id)
    if not picks:
        picks_query = Pick.all().ancestor(event_key(event_id)).order('pick_no')
        picks = picks_query.fetch(25)
        memcache.add('picks'+event_id, picks)
    return picks

def deleteEvent(event_id):
    Event.delete(event_key(event_id))
    Pick.delete(all().ancestor(event_key(event_id)))

def getResults(event_id):
    event = getEvent(event_id)
    if (event.event_url and int(event_id)<currentEvent()):
        results = "<iframe width='1250' height='800' frameborder='0' src='"+result_url+"'&widget=true'></iframe>"
    else:
        results = "<iframe width='1250' height='800' frameborder='0' src='"+results_tab+"'&widget=true'></iframe>"
    return results

def getEvent(event_id):
    event = Event.get(event_key(event_id))
    if (not event):
        events=fetchEvents()
        for row in events:
            if (row[0]==event_id):
                event=Event(key_name=row[0], event_id=int(row[0]))
                event.event_name=row[1]
                event.event_url=row[2]
                event.first=row[3]
                event.next=skip_pickers[1 - skip_pickers.index(row[3])]
                event.pickers=[event.first,event.next]
                event.field=getPlayers(event.event_id)
                event.picks=[]
                event.start=int(row[4])
                event.put()
    return event

def nextEvent():
    event_current=currentEvent()
    query= Event.all().filter("event_id >=", event_current)
    event = query.get()
    if (not event):
        event_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A2%3AD2&output=csv"
        result = urllib2.urlopen(event_url)
        reader=csv.reader(result)
        row=reader.next()
        event=Event(key_name=row[0],event_id=int(row[0]))
        event.event_name=row[1]
        event.event_url=row[2]
        event.first=row[3]
        event.next=pickers[1 - pickers.index(row[3])]
        event.pickers=[event.first,event.next]
        event.field=getPlayers()
        event.picks=[]
        event.start=0
        event.put()
    return event

def updateEvents():
    return
    
def getLastPick(pick):
    lastpick=memcache.get("lastpick")
    if (not lastpick or not lastpick.startswith(pick.who)):
        lastpick=pick.who+" picked "+pick.player
    elif (not lastpick.endswith(pick.player)):
        lastpick=lastpick+" and "+pick.player
    memcache.delete("lastpick")  
    memcache.add("lastpick",lastpick)  
    return lastpick
    
def updateLastPick(event,pick):
    lastpick=getLastPick(pick)
    # send alert if needed
    pick_no = len(event.picks)+1
    event.next=event.pickers[0] if mypicks.count(pick_no)>0 else event.pickers[1]
    if (pick_no<21 and not lastpick.startswith(event.next)):
        message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',subject=event.event_name)
        message.to = numbers.get(event.next)
        message.body=lastpick
        message.send()   
    return

class MainPage(webapp2.RequestHandler):       
    def get(self):
        event_list = []
        event_name = "None"
        event_id = self.request.get('event_id');
        events=getEvents()
        for event in events:
             event_list.append(event)
#            event_list+='<option value=' + event[0] + '>' + event[1] + "</option>"
    
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
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class MailHandler(webapp2.RequestHandler):       
    def get(self):
        event_id = self.request.get('event_id')
        if event_id:
            event = getEvent(event_id)
        else:
            event = nextEvent()
        current=datetime.datetime.now()
        if event:
            event_day = datetime.datetime.today().weekday()-2
            if event_day in range(5):
                event_name = event.event_name
                message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',subject=event_name+" results (round "+str(event_day)+")")
                message.to = "skipflog@googlegroups.com"
                result = urllib2.urlopen(results_url)
                message.html=result.read()
                message.send()
            else:
                pick_no = len(event.picks)+1
                event.next=event.pickers[0] if mypicks.count(pick_no)>0 else event.pickers[1]
                if (pick_no>1 and pick_no<20):
                    message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',subject=event.event_name)
                    message.to = "skipflog@googlegroups.com"
                    message.body=event.next+" is on the clock. http://skipflog.appspot.com"
                    message.send()   

    def post(self):
        event_id = self.request.get('event_id')
        event = getEvent(event_id)
        user = users.get_current_user()
        message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',
                            subject=event.event_name+" picks")
        message.to = "skipflog@googlegroups.com"
        message.html=event.event_name+"<br>"
        players = {"Steve":[],"Mark":[]}
        picks = getPicks(event_id)
        for pick in picks:
            players[pick.who].append(pick.player)
        for picker in skip_pickers:
            message.html += picker+"'s Picks:<ol>"
            for player in players[picker]:
                message.html+="<li>"+player
            message.html+="</ol>"
        message.send()
        self.redirect('/pick?event_id=' + event_id)

class PickHandler(webapp2.RequestHandler):
    def get(self):     
        event_id = self.request.get('event_id')
        if (event_id):
            event = getEvent(event_id)
            results = getResults(event_id)
        else:
            event = nextEvent()
            results = ""
        lastpick=memcache.get("lastpick")
        players = {"Steve":[],"Mark":[]}
        picks = getPicks(event_id)
        for pick in picks:
            players[pick.who].append(pick.player)

        pick_no = len(picks)+1

        picknum = pick_ord[pick_no]
        # get next player
        if picknum != "Done":
            event.next=event.pickers[0] if mypicks.count(pick_no)>0 else event.pickers[1]
        else:
            event.next="Done"
    
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
            'mplayers': players['Mark'],
            'splayers': players['Steve'],
            'lastpick': memcache.get("lastpick"),
            'pick_no': pick_no,
            'picknum': picknum,
            'results': results,
            'title': 'Picks',
            'url': url,
            'url_linktext': url_linktext,
            'user': user
        }
        template = jinja_environment.get_template('picks.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        event_id = self.request.get('event_id')
        pick = Pick(parent=event_key(event_id))     
        pick.who= self.request.get('who')
        pick.pick_no = int(self.request.get('pick_no'))
        pick.player = self.request.get('player')
        pick.put()
        memcache.delete('picks'+event_id)
        # update event (add to picks, remove from field)
        event = Event.get(event_key(event_id))
        event.field.remove(pick.player)
        event.picks.append(pick.player)
        event.put()
        # update last pick message
        updateLastPick(event,pick)
        self.redirect('/pick?event_id=' + event_id) 

class EventsHandler(webapp2.RequestHandler):   
    def get(self):
        event_id = self.request.get('event_id')
        output_format = self.request.get('output')
        if not output_format:
            output_format='csv'
        events=getEvents()
        if output_format=='html':
            template_values = {'events': events }
            template = jinja_environment.get_template('events.html')
            self.response.out.write(template.render(template_values))
        for event in events:
            if (event.event_id==event_id or not event_id):
                if output_format=='csv':
                    event_list=[event.event_id, event.event_name, event.start, event.picks]
                    self.response.write(",".join(str(entry) for entry in event_list)+'\n')
                elif output_format=='json':
                    event_dict={'id':event.event_id,'name':event.event_name, 'start':event.start, 'picks':event.picks}
                    self.response.write(json.dumps(event_dict)+'\n')
                elif output_format=='xml':
                    self.response.write(event.to_xml())

class PicksHandler(webapp2.RequestHandler):   
    def get(self):
        output_format = self.request.get('output','json')
        event_id = self.request.get('event_id')
        if not event_id:
            self.redirect('/events')    
        else:
            event = getEvent(event_id)
            if event:
                pick_dict={'event_id':event_id,'event_name': event.event_name,'picks':{} }
                for picker in skip_pickers:
                    pick_dict['picks'][picker]=[]
                for pick in getPicks(event_id):
                    if output_format=='csv':                   
                        pick_list=[event_id, pick.pick_no, pick.who, pick.player]
                        self.response.write(",".join(str(entry) for entry in pick_list)+'\n')
                    elif output_format=='json' and pick.pick_no<=20:
                        pick_dict['picks'][pick.who].append(pick.player)
                    elif output_format=='xml':
                        self.response.write(pick.to_xml())
                if output_format=='json':
                    self.response.write(json.dumps(pick_dict))

class PlayersHandler(webapp2.RequestHandler):   
    def get(self):
        output_format = self.request.get('output')
        if not output_format:
            output_format='none'
        players=getPlayers()
        if output_format=='csv':                   
            self.response.write(",".join(player for player in players)+'\n')
        elif output_format=='json':
            self.response.write(json.dumps(players)+'\n')  
        else:            
            self.response.write(players)

class RankingHandler(webapp2.RequestHandler): 
    def get(self):
        taskqueue.add(url='/ranking', params={'event_week': current_week(),'event_year': current_year()})
#       taskqueue.add(url='/results', params={'event_week': current_week(),'event_year': current_year()})
        
    def post(self):
#       event_update=post_rankings()
        event_week = self.request.get('event_week')
        event_year = self.request.get('event_year')
        event_name = event_year + " World Golf Rankings and Results (Week "+str(event_week)+")"
        message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',subject=event_name)
        message.to = "skipflog@googlegroups.com"
        message.html=fetch_tables(rankings_url)
        message.html+="<p>"
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
        results = get_results(event_id)
        if output_format=='csv':
            self.response.write('Pos,Player,Scores,Today,Total,Points'+br)
        elif output_format=='json':
            self.response.write(json.dumps(results))
        elif output_format=='html':
            template_values = {'results': results }
            template = jinja_environment.get_template('results.html')
            self.response.out.write(template.render(template_values))
                    
    def post(self):
        event_week = self.request.get('event_week')
        event_year = self.request.get('event_year')
        this_week = str((int(event_year)-2000)*100+int(event_week))
        event_update=post_results(this_week)
        event_name = event_year + " World Golf Results (Week "+str(event_week)+")"
        message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',subject=event_name)
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
  ('/events', EventsHandler),
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
