from flask_socketio import SocketIO, send
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient

#Loading Database
mode = ""

if mode == "DEV":
    import subprocess
    subprocess.Popen("mongod")
    client = MongoClient(port=27017)

else:
    db_credentials = {
        "password": "OMXklA8zUKGvDoEX",
        "username": "bdg_admin",
        "db_name": ""
    }
    database_address = f"mongodb+srv://{db_credentials['username']}:{db_credentials['password']}@gestionbudgetcluster.irghg.mongodb.net/{db_credentials['db_name']}?retryWrites=true&w=majority"

    client = MongoClient(database_address)


database = client["GestionBudget"]


SERVER_URL = 'http://localhost:3000'
app = Flask(__name__, template_folder='./templates', static_folder='./static')

CORS(app)
socket_io = SocketIO(app, cors_allowed_origins="*")
socket_io.init_app(app, cors_allowed_origins="*")


@app.route('/', methods=["GET"])
def default_text():
    return "Gestion Budget API"


from url_bindings import markets, funds, users, charges, expenses, socket, summary
from reporting import reporting