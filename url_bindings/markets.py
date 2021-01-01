from bson import ObjectId
from flask import request

from bindings import app, database

market_namespace = '/markets'

def serialize(market):
    market['id'] = str(market['_id'])
    del market['_id']
    return market

def deserialize(market):
    market['_id'] = ObjectId(market['id'])
    del market['id']
    return market

@app.route(market_namespace, methods=['GET', 'POST', 'PUT'])
def market_cr():
    if request.method == 'GET':
        market_list = [serialize(m) for m in database['markets'].find({})]
        return {'markets': market_list}

    elif request.method == 'POST':
        new_market = request.get_json()
        operation = database['markets'].insert_one(new_market)
        new_market['id'] = str(operation.inserted_id)

        return serialize(new_market)

@app.route(market_namespace+'/<id>', methods=['GET', 'DELETE', 'PUT'])
def market_ud(id):
    if request.method == 'GET':
        return serialize(database['markets'].find_one({'_id': ObjectId(id)}))

    elif request.method == 'PUT':
        new_market = deserialize(request.get_json())
        database['markets'].update_one({'_id': ObjectId(id)}, {"$set": new_market})
        return serialize(new_market)

    elif request.method == 'DELETE':
        deleted = database['markets'].find_one({'_id': ObjectId(id)})
        database['markets'].delete_one({'_id': ObjectId(id)})
        return serialize(deleted)
