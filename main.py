import cgi,csv,datetime
import jinja2
import urllib2
import webapp2
import os

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import users

events={ 4:'Masters',6:'US Open', 7:'Open Championship', 8:'PGA Championship'}
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','mholtebeck':'Mark'}
pickers=('Steve','Mark')
pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]

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

class Pick(db.Model):
    who = db.StringProperty()
    player = db.StringProperty()
    when = db.DateTimeProperty(auto_now_add=True)
    pick_no = db.IntegerProperty()
    points = db.IntegerProperty()

def event_key(event_id):
  """Constructs a Datastore key for an Event entity with event_id."""
  return db.Key.from_path('Event', event_id)


def getEvents():
    events = memcache.get('events')
    if not events:
        events=[]
        events_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A3%3AD16&output=csv"
        result = urllib2.urlopen(events_url)
        reader = csv.reader(result)
        for row in reader:
            events.append(row)
        memcache.add('events', events)
    return events

def getPlayers(event_id=0):
    players = memcache.get('players')
    if not players:
        players=[]
        if (event_id!=0): 
            players_url="https://docs.google.com/spreadsheet/pub?key=0Ahf3eANitEpndE5tMHlhZGJRZ01TTk5vMi1WaFRmRHc&single=true&gid=1&range=B3%3AB90&output=csv"
        else:
            players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdFJQeUVuLTJqeFRTMGstZ3BZdEI2aWc&single=true&gid=6&range=B3%3AB62&output=csv"
        result = urllib2.urlopen(players_url)
        reader = csv.reader(result)
        for row in reader:
            players.append(row[0])
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

def getResults(event_id):
    event = getEvent(event_id)
    results = ""
    if (event.event_url):
        results += '<br><iframe src="' + event.event_url + '" width=450 height=350></iframe>'
    return results

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
                event.put()
    return event
 
def nextEvent():
    now=datetime.datetime.now()
    event_current=100*(now.year-2000)+now.month
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
        self.redirect('/pick?event_id=' + event_id)	

class ResultsHandler(webapp2.RequestHandler):   
    def get(self):
        event_id = self.request.get('event_id')
        players = {"Steve":[],"Mark":[]}
        picks = getPicks(event_id)
        for pick in picks:
            self.response.write(event_id+","+str(pick.pick_no)+","+pick.who+","+pick.player+'\n')

    def post(self):
        event_id = self.request.get('event_id')
        event = getEvent(event_id)
        user = users.get_current_user()
        message = mail.EmailMessage(sender='admin@skipflog.appspotmail.com',
                            subject=event.event_name+" picks")
        message.to = "mholtebeck@gmail.com,sholtebeck@gmail.com"
        message.html=event.event_name+"<p>"
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

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/pick', PickHandler),
  ('/results', ResultsHandler)
], debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()
