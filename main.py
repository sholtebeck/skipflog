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
from google.appengine.api import users
from skipflog import *

br="</br>"
events={ 4:'Masters',6:'US Open', 7:'Open Championship', 8:'PGA Championship'}
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','mholtebeck':'Mark'}
pickers=('Steve','Mark')
pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]
event_url="https://docs.google.com/spreadsheet/pub?key=0Ahf3eANitEpndGhpVXdTM1AzclJCRW9KbnRWUzJ1M2c&single=true&gid=1&output=html&widget=true"
events_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A2%3AE20&output=csv"
players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=B1%3AB156&output=csv"
results_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=2&output=html"
ranking_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=3&output=html"
leaderboard_url="http://sports.yahoo.com/golf/pga/leaderboard"

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
      
   
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

def getEvents():
    events = memcache.get('events')
    if not events:
        events=[]
        result = urllib2.urlopen(events_url)
        reader = csv.reader(result)
        for row in reader:
            events.append(row)
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
        results = "<iframe width='1250' height='800' frameborder='0' src='"+event.event_url+"'&widget=true'></iframe>"
    else:
        results = "<iframe width='1250' height='800' frameborder='0' src='"+results_url+"'&widget=true'></iframe>"
    return results
    Event.delete(event_key(event_id))

def getEvent(event_id):
    event = Event.get(event_key(event_id))
    if (not event):
        events=getEvents()
        for row in events:
            if (row[0]==event_id):
                event=Event(key_name=row[0], event_id=int(row[0]))
                event.event_name=row[1]
                event.event_url=row[2]
                event.first=row[3]
                event.next=pickers[1 - pickers.index(row[3])]
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
        event.put()
    return event

def updateEvents():
    return

class MainPage(webapp2.RequestHandler):       
    def get(self):
        event_list = ""
        event_name = "None"
        event_id = self.request.get('event_id');
        events=getEvents()
        for event in events:
             event_list+='<option value=' + event[0] + '>' + event[1] + "</option>"
    
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
        event_day = int(current.day-event.start)
        event_name = event.event_name
        # Special Handler for weekly job
        if (event_id == "1401"):
            event_week=current.isocalendar()[1]-1
            message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',
                            subject=event_name+" results (week "+str(event_week)+")")
            message.to = "skipflog@googlegroups.com"
            result = urllib2.urlopen(ranking_url)
            message.html=result.read()
            message.send()
        elif (event_day >0 and event_day < 5):
            message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',
                            subject=event_name+" results (round "+str(event_day)+")")
            message.to = "skipflog@googlegroups.com"
            result = urllib2.urlopen(results_url)
            message.html=result.read()
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
        for picker in pickers:
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
            'url': url,
            'url_linktext': url_linktext,
            'user': user
        }
        template = jinja_environment.get_template('index.html')
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
        lastpick=pick.who+" picked "+pick.player
        memcache.delete('lastpick')
        memcache.add("lastpick",lastpick)
        self.redirect('/pick?event_id=' + event_id)	

class EventsHandler(webapp2.RequestHandler):   
    def get(self):
        event_id = self.request.get('event_id')
        output_format = self.request.get('output')
        if not output_format:
            output_format='csv'
        events=getEvents()
        for row in events:
            if (row[0]==event_id or not event_id):
                event=getEvent(row[0])
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
        output_format = self.request.get('output')
        if not output_format:
            output_format='csv'
        event_id = self.request.get('event_id')
        if not event_id:
            self.redirect('/events')	
        else:
            event = getEvent(event_id)
            if event:
                for pick in getPicks(event_id):
                    if output_format=='csv':                   
                        pick_list=[event_id, pick.pick_no, pick.who, pick.player]
                        self.response.write(",".join(str(entry) for entry in pick_list)+'\n')
                    elif output_format=='json':
                        pick_dict={'event_id':event_id,'pick_no':pick.pick_no, 'who':pick.who, 'player':pick.player}
                        self.response.write(json.dumps(pick_dict)+'\n')
                    elif output_format=='xml':
                        self.response.write(pick.to_xml())

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

class ResultsHandler(webapp2.RequestHandler):   
    def get(self):
        output_format = self.request.get('output')
        if not output_format:
            output_format='csv'
        event_id = self.request.get('event_id')
        if event_id:
            event = getEvent(event_id)
            page = soup_results(leaderboard_url)
            headers = fetch_headers(page)
            if output_format=='csv':
                self.response.write('Pos,Player,Scores,Today,Total,Points'+br)
            elif output_format=='html':
                self.response.write('<table>')
                self.response.write(page.find('thead'))
            elif output_format=='json':
                self.response.write(json.dumps(headers))
            # Get header
            head_columns=headers.get('Columns')
            rows = fetch_rows(page)
            for row in rows:
                res=fetch_results(row, headers.get('Columns'))
                if res.get('Rank') in range(1,10) or res.get('Name') in event.picks:
                    if output_format=='csv':
                        self.response.write(str(res.get('Rank'))+','+res.get('Name')+','+res.get('Scores')+',')
                        self.response.write(res.get('Time')+','+res.get('Total')+','+str(res.get('Points')))
                        self.response.write(br)
                    elif output_format=='html':
                        self.response.write(row)
                    elif output_format=='json':                 
                        self.response.write(json.dumps(res))

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/events', EventsHandler),
  ('/mail', MailHandler),
  ('/pick', PickHandler),
  ('/picks', PicksHandler),
  ('/players', PlayersHandler),
  ('/results', ResultsHandler)  
], debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()
