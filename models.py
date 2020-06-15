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
    event_json = ndb.JsonProperty()
    results_json = ndb.JsonProperty()

class Picker(ndb.Model):
    picks = ndb.StringProperty(repeated=True)
    count = ndb.IntegerProperty()
    points = ndb.FloatProperty()

def get_event(event_id):
    event=Event.get_by_id(int(event_id))
    return event
	
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
