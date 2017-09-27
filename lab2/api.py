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
from flask import Flask, url_for, request, json, jsonify
from plant import Plant, available_upgrades


app = Flask(__name__)

plant_list = {'basil':Plant('basil','Ocicum Basilicum','zYx54e3'),
              'adi':Plant('adi','Dionaea Muscipula', 'g3tRek7')} 
event_log = Plant.event_log

ADMIN_PASSWORD = 'nanjate'

# authentication
def check_auth(name, password):
    plant = plant_list[name]
    return plant.password == password

def authenticate():
    message = {'message': 'Authenticate.'}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()
        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#other wrapper
def requires_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers['Content-Type'] == 'application/json':
            return f(*args, **kwargs)
        else:
            return '415 - Unsupported Media Type la..'
    return decorated


# routes
@app.route('/')
def api_root():
    print(request)
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
        return json.dumps(plant_list[name].to_public_json())

@app.route('/myplant', methods = ['POST'])
@requires_auth
@requires_json
def api_myplant():
    '''
    view and upgrade

    request model:
    1) viewing:
        request.body.operation = view
    2) upgrading:
        request.body.operation = upgrade
        request.body.upgrade = <upgrade name>
    4) help: (show request format)
        request.body.operation = help 
    '''
    def handle_view(name, password):
        plant = plant_list[name]
        return json.dumps(plant.to_private_json(password))

    def handle_upgrade(name, upgr, password):
        plant = plant_list[name]
        upgraded = plant.upgrade(upgr)
        result_json = plant.to_private_json(password)
        result_json['message']=upgraded
        return json.dumps(result_json)

    def handle_vote(name, vote):
        if vote not in plant_list:
            return 'Invalid vote target'
        this_plant = plant_list[name]
        voted_plant = plant_list[vote]
        voted_plant.voted_by(this_plant)
        return '{this} votes for {that}'\
                .format(this=name, that=vote)

    name = request.authorization.username
    password = request.authorization.password
    body = request.json
    print body
    if 'operation' in body:
        ops = body['operation']
        if ops == 'UPGRADE':
            return handle_upgrade(name, body['upgrade'], password)
        elif ops == 'VIEW':
            return handle_view(name, password)
        elif ops == 'VOTE':
            return handle_vote(name, body['vote'])
    else:
        return 'Incorrect request body format'


@app.route('/admin')
def api_adminpage():
    return """
Office Forest admin page

  - /admin/register       : register a new plant (requires json)
  - /admin/delete/<name>  : delete a plant
    """

@app.route('/admin/register', methods = ['PUT'])
@requires_json
def api_register():
    plant_name = request.json['name']
    plant_type = request.json['plant_type']
    password = request.json['password']
    plant_list[plant_name] = Plant(name=plant_name,
                                   plant_type=plant_type,
                                   password=password)
    return "Registration ok!"

@app.route('/admin/delete/<plant_name>', methods=['DELETE'])
def api_delete(plant_name):
    if plant_name not in plant_list:
        return 'Plant does not exist'
    del plant_list[plant_name]
    msg = 'deleted {}'.format(plant_name)
    event_log.append(msg)
    return msg

if __name__ == '__main__':
    app.run()

