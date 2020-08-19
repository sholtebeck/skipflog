"""
models.py

App Engine datastore models for Golf Picks app
Modified to use google.cloud ndb in August 2020
"""
#from google.appengine.ext import ndb
from google.cloud import ndb
client = ndb.Client()

class Event(ndb.Model):
    event_id = ndb.IntegerProperty(required=True)
    event_name = ndb.StringProperty()
    event_json = ndb.JsonProperty()
    results_json = ndb.JsonProperty()

class Token(ndb.Model):
    dtype = ndb.StringProperty()
    name = ndb.StringProperty()
    value = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)   

def get_event(event_id):
    with client.context():
        event=Event.get_by_id(int(event_id))
        return event

def get_event_json(event_id):
    event=get_event(event_id)
    if event:
        return event.event_json
    else:
        return None

    
def get_results_json(event_id):
    event=get_event(event_id)
    if event:
        return event.results_json
    else:
        return None
    
def update_event(event_data):
    with client.context():
        event_id = int(event_data["event_id"])
        event=Event(id=event_id,event_id=event_id,event_name=event_data["event_name"],event_json=event_data)
        event.put()
    
def update_results(results_data):
    with client.context():
        event=get_event(results_data['event']['ID'])
        event.results_json=results_data
        event.put()

def is_sent(name):
    with client.context():
        token=Token.get_or_insert(name)
        if not token.name == name:
            token.dtype='message'
            token.name=name
            token.put()
            return False    
        else:
            return True 
			
def set_document(dtype,dname,dvalue):
    with client.context():
        token=Token(id=dname,dtype=dtype,name=dname,value=dvalue)
        token.put()

def get_document(dtype,dname):
    with client.context():
        token=Token.get_or_insert(dname)
        return token.value
