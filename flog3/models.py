"""
models.py

App Engine datastore models for Golf Picks app
Modified to use Firebase DB in August 2020
"""
#Authentication Object
#import pyrebase
from skipflog import firestore_json 
#config={key:firestore_json.get(key) for key in ("apiKey", "authDomain", "databaseURL", "storageBucket")}
#firebase = pyrebase.initialize_app(config)
#auth=firebase.auth()

#first try google_cloud then try firebase_admin
try:
    from google.cloud import firestore
    db = firestore.Client()
except:
    from firebase_admin import credentials,firestore,initialize_app
    firebase_cred = credentials.Certificate('config/skipflog3.json')
    initialize_app(firebase_cred)
    db = firestore.client()

def get_document(coll,id):
    doc=db.collection(coll).document(id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None 

def set_document(coll,id,data):
    db.collection(coll).document(id).set(data)
        
def get_event(event_id):
    return get_document('events',str(event_id))       
    
def get_results(event_id):
    return get_document('results',str(event_id))       
   
def update_event(event_data):
    set_document('events',str(event_data["ID"]),event_data)
    return event_data
    
def update_results(results_data):
    set_document('results',str(results_data['event']['ID']),results_data)

def is_sent(name):
    msg=get_document('messages',name)
    if msg:
        return True
    else:
        return False 
            
def send_message(name,sent):
    set_document('messages',name,{"name":name, "sent": sent })    
