# Main program for golfpicks app (skipflog3.appspot.com)
from flask import Flask,redirect

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main_page(): 
    return redirect("/static/index.html")

@app.route("/manifest.json")
def manifest():
    return redirect('/static/manifest.json')
@app.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.ico')

@app.route('/api/events.json', methods=['GET'])
def api_events():
    return redirect('/static/api/events.json')

@app.route('/api/players.json', methods=['GET'])
def api_players():
    return redirect('/static/api/players.json')



if __name__ == '__main__':
    app.run(debug=True,port=5000)