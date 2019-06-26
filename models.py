"""
models.py

App Engine datastore models for Golf Picks app

"""
from google.appengine.ext import ndb
from time import gmtime,strftime
import datetime

class Event(ndb.Model):
    event_id = ndb.IntegerProperty(required=True)
    event_name = ndb.StringProperty()
    pick_no = ndb.IntegerProperty(indexed=False)
    field = ndb.StringProperty(repeated=True)
    picks = ndb.StringProperty(repeated=True)
    event_json = ndb.JsonProperty()
    results_json = ndb.JsonProperty()

class Pick(ndb.Model):
    who = ndb.StringProperty()
    player = ndb.StringProperty()
    when = ndb.DateTimeProperty(auto_now_add=True)
    pick_no = ndb.IntegerProperty()
    points = ndb.IntegerProperty()

def event_key(event_id):
    return ndb.Key('Event',event_id) 

def get_event(event_id):
    event=Event.get_by_id(int(event_id))
#    if not event:
#        event=Event.query().filter(Event.event_id == int(event_id)).fetch(1)[0]
    return event

def get_picks(event):
    event_key=ndb.Key( 'Event', str(event.event_id) )
    picks={}
    for pick in Pick.query(ancestor=event_key).fetch(25):
        picker=str(pick.who)
        player=str(pick.player)
        picks[player]=picker
        picks[picker]=picks.get(picker,[])+[player]
    return picks

def add_pick(pickdict): 
    pick = Pick(parent=event_key(pickdict['event_id']))     
    pick.who= pickdict.get('picker')
    pick.pick_no = pickdict.get('pick_no')
    pick.player = pickdict.get('player')
    pick.put()  
    
def get_results(event_id):
    event=Event.get_by_id(int(event_id))
    if event:
        return event.results_json
    else:
        return None
    
def update_event(event_data):
    event_id = int(event_data["event_id"])
    event=Event(id=event_id,event_id=event_id,event_name=event_data["event_name"],event_json=event_data)
    event.put()
    
def update_results(results_data):
    event=get_event(results_data['event']['ID'])
    event.results_json=results_data
    event.put()
