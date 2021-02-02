from datetime import datetime
import hashlib
from bson import ObjectId
from flask import request

from bindings import app, database

users_namespace = '/users'


def hash_password(w):
    hash_object = hashlib.md5(w.encode())
    return hash_object.hexdigest()


def serialize(u):
    u['id'] = str(u['_id'])
    del u['_id']
    return u


def deserialize(u):
    u['_id'] = ObjectId(u['id'])
    del u['id']
    return u


@app.route(users_namespace, methods=['GET', 'POST', 'PUT'])
def user_cr_auth():
    if request.method == 'GET':
        user_list = [serialize(m) for m in database['users'].find({}, {'password': 0})]
        return {'users': user_list}

    elif request.method == 'PUT':
        request_json = request.get_json()

        if 'username' in request_json.keys():
            request_json['username'] = request_json['username'].lower()

        if 'password' in request_json.keys():
            request_json['password'] = hash_password(request_json['password'])

        user = database['users'].find_one(
            request_json, {'password': 0}
        )
        if user is None:
            return {'user': None}

        return {'user': serialize(user)}

    elif request.method == 'POST':
        request_json = request.get_json()

        if 'username' in request_json.keys():
            request_json['username'] = request_json['username'].lower()

        if 'password' in request_json.keys():
            request_json['password'] = hash_password(request_json['password'])

        database['users'].insert_one(request_json)
        print(request_json)
        return serialize(request_json)
