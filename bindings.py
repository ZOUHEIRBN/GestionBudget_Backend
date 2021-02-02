from flask_socketio import SocketIO, send
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient

#Loading Database
client = MongoClient(port=27017)
database = client["GestionBudget"]


SERVER_URL = 'http://localhost:3000'
app = Flask(__name__, template_folder='./templates', static_folder='./static')

CORS(app)
socket = SocketIO(app, cors_allowed_origins="*")

from url_bindings import markets, funds, users