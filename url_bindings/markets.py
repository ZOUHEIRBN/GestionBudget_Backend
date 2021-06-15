from bson import ObjectId
from flask import request

from bindings import app, database
from helper import set_privileges
from url_bindings.actions import LogAction

market_namespace = '/markets'

def serialize(market, actor_id):
    try:
        market['id'] = str(market['_id'])
        del market['_id']
    except:
        pass
    return set_privileges(market, actor_id, entity_type='market')

def deserialize(market):
    market['_id'] = ObjectId(market['id'])
    del market['id']
    return market

DESIRED_KEYS = ['_id', 'mo', 'market_no', 'object', 'begin_date', 'deadline', 'end_date', 'def_caution', 'total_sum', 'trimester_sum', 'agents_number', 'owner', 'execution_site', 'cumulative_sum', 'payments', 'is_reconductible']

@app.route(market_namespace, methods=['GET', 'POST', 'PUT'])
def market_cr():
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        market_list = [serialize(m, actor_id) for m in database['markets'].aggregate([
            {"$project": {k: 1 for k in DESIRED_KEYS}},

            {"$addFields": {
                    "bilan": {"$map": {
                        "input": "$payments",
                        "as": "p",
                        "in": {
                            "realization_year": {"$year": {"$toDate": "$$p.realization_date"}},
                            "billing_year": {"$year": {"$toDate": "$$p.billing_date"}}
                        }
                    }}
                }},
            {"$addFields": {
                f"{f}_sum": {"$map": {
                    "input": "$bilan",
                    "as": "b",
                    "in": {"$sum": {"$map": {
                        "input": {"$filter": {
                            "input": "$payments",
                            "as": "f",
                            "cond": {"$and": [
                                {"$eq": ["$$b.realization_year", {"$year": {"$toDate": "$$f.realization_date"}}]},
                                {"$eq": ["$$b.billing_year", {"$year": {"$toDate": "$$f.billing_date"}}]},
                            ]}
                        }},
                        "as": "p",
                        "in": f"$$p.{f}_sum"
                    }}}
                }}
                for f in ['realization', 'billing']
            }},
            {"$addFields": {
               "bilan": {"$map": {
                   "input": {"$zip": {"inputs": ["$bilan.realization_year", "$realization_sum", "$bilan.billing_year", "$billing_sum"]}},
                   "as": "z",
                   "in": {
                        "realization_year": {"$arrayElemAt": ["$$z", 0]},
                        "realization_sum": {"$arrayElemAt": ["$$z", 1]},
                        "billing_year": {"$arrayElemAt": ["$$z", 2]},
                        "billing_sum": {"$arrayElemAt": ["$$z", 3]},
                   }
               }}
            }},

            {"$project": {
                "id": {"$toString": "$_id"},
                "_id": 0,
                "root": "$$ROOT"
            }},
            {"$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": "$root"
                }
            }}
        ])]
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
        print(new_market)
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
