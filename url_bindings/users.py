from datetime import datetime
import hashlib
from bson import ObjectId
from flask import request

from bindings import app, database
from helper import set_privileges
from url_bindings import socket, actions

users_namespace = '/users'


def hash_password(w):
    hash_object = hashlib.md5(w.encode())
    return hash_object.hexdigest()


def serialize(u, actor_id=None, num_actions=5):
    u['id'] = str(u['_id'])
    del u['_id']
    u['actions'] = [a for a in database['actions'].find({'actor_id': u['id']}, {'_id': 0, 'actor_id': 0})]
    if num_actions != 0:
        u['actions'] = u['actions'][-num_actions:][::-1]

    if actor_id is None:
        return u
    return set_privileges(u, actor_id)


def deserialize(u):
    del u['actions']
    u['_id'] = ObjectId(u['id'])
    del u['id']

    return u


@app.route(users_namespace, methods=['GET', 'POST', 'PUT'])
def user_cr():
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        user_list = [serialize(m, actor_id) for m in database['users'].find({}, {'password': 0})]
        return {'users': user_list}

    elif request.method == 'POST':
        request_json = request.get_json()

        if 'username' in request_json.keys():
            request_json['username'] = request_json['username'].lower()

        if 'password' in request_json.keys():
            request_json['password'] = hash_password(request_json['password'])

        for f in ['firstname', 'lastname', 'email']:
            if f in request_json.keys():
                request_json[f] = request_json[f].lower()

        database['users'].insert_one(request_json)

        return serialize(request_json)

@app.route(users_namespace+'/connect', methods=['PUT'])
def authenticate():
    # actor_id = request.args.get('actor_id', '1234567890AB'*2)
    if request.method == 'PUT':
        request_json = request.get_json()
        search = {}

        if 'username' in request_json.keys():
            search['username'] = request_json['username'].lower()

        if 'password' in request_json.keys():
            search['password'] = hash_password(request_json['password'])

        for f in ['firstname', 'lastname', 'email']:
            if f in request_json.keys():
                search[f] = request_json[f].lower()

        # print(search)
        user = database['users'].find_one(
            search, {'password': 0}
        )

        if user is None:
            return {'user': None}
        user = serialize(user)
        user['ip'] = request_json['ip']

        return {'user': user}

def get_roles(user_id):
    if user_id == 'undefined':
        return []
    roles = [r for r in database['users'].find_one({'_id': ObjectId(user_id)}, {'roles': 1})['roles']]
    userlist = database['users'].aggregate([
        {
            "$match": {
                "roles": {"$in": roles}
            }
        }
    ])
    userlist = [str(u['_id']) for u in userlist]
    userlist.remove(user_id)
    return userlist

def get_full_name(user_id):
    user = database['users'].find_one({'_id': ObjectId(user_id)})
    return user.get('firstname', '').title() + ' ' + user.get('lastname', '').upper()

