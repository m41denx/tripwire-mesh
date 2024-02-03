import os
import pathlib
from flask import Flask, request, make_response
from wg_meshconf import wg_meshconf, wireguard

TOKEN = os.environ.get('TOKEN')

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def health():
    return 'OK'


@app.route('/getconf/<node>', methods=['GET'])
def getconfig(node):
    token = request.headers.get('Authorization')
    if token != TOKEN:
        return make_response('Unauthorized', 401)
    if not os.path.exists(f'output/{node}.conf'):
        return make_response('Not Found', 404)
    with open(f'output/{node}.conf', 'r') as f:
        return f.read()


@app.route('/new', methods=['POST'])
def newconf():
    token = request.headers.get('Authorization')
    if token != TOKEN:
        return make_response('Unauthorized', 401)
    data = request.get_json()
    dbm = wg_meshconf.DatabaseManager(pathlib.Path("database.csv"))
    dbm.addpeer(Name=data['name'], Address=data['address'], Endpoint=data['endpoint'], ListenPort=data['port'],
                PrivateKey=data['private_key'])
    dbm.genconfig(None, pathlib.Path("output"))
    return 'OK'


@app.route('/update', methods=['POST'])
def updateconf():
    token = request.headers.get('Authorization')
    if token != TOKEN:
        return make_response('Unauthorized', 401)
    data = request.get_json()
    dbm = wg_meshconf.DatabaseManager(pathlib.Path("database.csv"))
    dbm.updatepeer(Name=data['name'], Address=data['address'], Endpoint=data['endpoint'], ListenPort=data['port'],
                   PrivateKey=data['private_key'])
    dbm.genconfig(None, pathlib.Path("output"))
    return 'OK'


@app.route('/delete/<node>', methods=['POST'])
def deleteconf(node):
    token = request.headers.get('Authorization')
    if token != TOKEN:
        return make_response('Unauthorized', 401)
    dbm = wg_meshconf.DatabaseManager(pathlib.Path("database.csv"))
    dbm.delpeer(Name=node)
    dbm.genconfig(None, pathlib.Path("output"))
    return 'OK'


@app.route('/client', methods=['GET'])
def client():
    with open("client.py", "r") as f:
        return f.read()


if __name__ == '__main__':
    dbm = wg_meshconf.DatabaseManager(pathlib.Path("database.csv"))
    dbm.genconfig(None, pathlib.Path("output"))
    app.run(host='0.0.0.0', port=8080)
    conf = {
        "private_key": "...",
        "address": "VPC IP",
        "endpoint": "Real IP",
        "port": "1080",
        "name": "default"
    }
