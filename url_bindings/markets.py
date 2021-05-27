from bson import ObjectId
from flask import request

from bindings import app, database
from helper import set_privileges
from url_bindings.actions import LogAction

market_namespace = '/markets'

def serialize(market, actor_id):
    market['id'] = str(market['_id'])
    del market['_id']
    return set_privileges(market, actor_id, entity_type='market')

def deserialize(market):
    market['_id'] = ObjectId(market['id'])
    del market['id']
    return market

@app.route(market_namespace, methods=['GET', 'POST', 'PUT'])
def market_cr():
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        market_list = [serialize(m, actor_id) for m in database['markets'].find({})]
        log = LogAction(actor_id, 'GET')
        log.make_statement('market', 'GET', single_element=False)
        log.insert()
        return {'markets': market_list}

    elif request.method == 'POST':
        new_market = request.get_json()
        operation = database['markets'].insert_one(new_market)
        new_market['id'] = str(operation.inserted_id)
        log = LogAction(actor_id, 'POST')
        log.make_statement('market', 'POST', entity_id=new_market['id'])
        log.insert()
        return serialize(new_market, actor_id)

@app.route(market_namespace+'/<id>', methods=['GET', 'DELETE', 'PUT'])
def market_ud(id):
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        log = LogAction(actor_id, 'GET')
        log.make_statement('market', 'GET', entity_id=id)
        log.insert()
        return serialize(database['markets'].find_one({'_id': ObjectId(id)}))

    elif request.method == 'PUT':
        new_market = deserialize(request.get_json())
        database['markets'].update_one({'_id': ObjectId(id)}, {"$set": new_market})
        log = LogAction(actor_id, 'PUT')
        log.make_statement('market', 'PUT', entity_id=id)
        log.insert()
        return serialize(new_market, actor_id)

    elif request.method == 'DELETE':
        deleted = database['markets'].find_one({'_id': ObjectId(id)})
        database['markets'].delete_one({'_id': ObjectId(id)})
        log = LogAction(actor_id, 'DELETE')
        log.make_statement('market', 'DELETE', entity_id=id)
        log.insert()
        return serialize(deleted, actor_id)
