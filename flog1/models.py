"""
models.py

App Engine datastore models for Golf Picks app
Modified to use pyrebase lib in March 2022
"""
import pyrebase
from skipflog import firestore_json 

config={key:firestore_json.get(key) for key in ("apiKey", "authDomain", "databaseURL", "storageBucket")}
firebase = pyrebase.initialize_app(config)
auth=firebase.auth()
db = firebase.database()
      
def get_event(event_id):
    event_data=dict(db.child("events").child(str(event_id)).get().val())
    return event_data     

def get_events():
    events=dict(db.child("events").get().val())
    event_list=[{k:events[e][k] for k in events[e].keys() if k not in ("pickers","players")} for e in events.keys()]
    return event_list   

def update_event(event_data):
    event_dict={ekey:event_data[ekey] for ekey in event_data.keys() if ekey !="results"}
    db.child("events").child(str(event_dict["ID"])).set(event_dict)
    return True

def get_players():
    players_data=db.child("players").get().val()
    return players_data

def get_results(event_id):
    results_data=dict(db.child("results").child(str(event_id)).get().val())
    return results_data

def update_player(player):
    db.child("players").child(str(player["POS"])).set(player)
    return True
    
def update_results(results_data):
    event_id=str(results_data.get("event").get("ID"))
    db.child("results").child(event_id).set(results_data)

def get_document(coll,id):
    doc=db.child(coll).child(id).get()
    if doc:
        return dict(doc.val())
    else:
        return None 

def set_document(coll,id,data):
    return db.child(coll).child(id).set(data)

def get_userid(email,password):
    user=auth.sign_in_with_email_and_password(email, password)
    uid=user["localId"]
    set_document("users",uid,auth.get_account_info(user["idToken"]))
    return uid
    

def is_sent(name):
    msg=get_document('messages',name)
    if msg:
        return True
    else:
        return False 
            
def send_message(name,sent):
    set_document('messages',name,{"name":name, "sent": sent })    


