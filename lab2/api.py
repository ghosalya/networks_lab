'''
Networks Lab 2 - Flask RESTful API
Gede Ria Ghosalya - 1001841

- must have widgets & entries

======== Office Forest ========
API calls:
- GET plant (anyone's)
- GET list of plants
- POST your own plant (with password)
- POST plant upgrade
- PUT votes
- POST new plants (new user)
- DELETE plants (your own only)
- GET events (in home page)
'''
from functools import wraps
from flask import Flask, url_for, request, jsonify
from plant import Plant, available_upgrades


app = Flask(__name__)

plant_list = {'basil':Plant('basil','Ocicum Basilicum','zYx54e3'),
              'adi':Plant('adi','Dionaea Muscipula', 'g3tRek7')} 
event_log = Plant.event_log

# authentication
def check_auth(plant, password):
    return plant.password == password

def authenticate():
    message = {'message': 'Authenticate.'}
    resp = jsonify(message)

# routes
@app.route('/')
def api_root():
    welcome = '''Welcome to Office Forest!
    /plants - view all available plants
    /plants/<name> - view specific plants
    
    Events:'''

    for event in reversed(event_log):
        welcome += '\n    - {}'.format(event)
    welcome += '\n'

    return welcome

@app.route('/plants')
def api_plants():
    plants = '\nAvailable plants:\n'
    for plant in plant_list.values():
        plants += '  {name} - {type} ({vote} votes)\n'\
                  .format(name=plant.name, type=plant.type, vote=plant.votes)
    return plants

@app.route('/plants/<name>', methods = ['GET'])
def api_plant(name):
    if name not in plant_list:
        return 'Plant not found'
    else:
        return plant_list[name].to_public_json()

@app.route('/myplant', methods = ['POST'])
def api_myplant():
    '''
    view and upgrade
    '''

if __name__ == '__main__':
    app.run()

