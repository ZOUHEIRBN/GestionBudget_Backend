from datetime import datetime

from bson import ObjectId
from flask import request

from bindings import app, database
from url_bindings.actions import LogAction

charge_namespace = '/charges'


def serialize_one(charge):
    charge['id'] = str(charge['_id'])
    del charge['_id']

    return charge

def deserialize_one(charge):
    charge['_id'] = ObjectId(charge['id'])
    del charge['id']
    return charge

@app.route(charge_namespace, methods=['GET', 'POST'])
def charge_cr():
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        charge_list = [serialize_one(m) for m in database['charges'].aggregate([
            {
                "$match": {"date": {
                    "$gte": datetime.strptime(f"1/1/2020", "%d/%m/%Y"),
                    "$lte": datetime.strptime(f"1/1/2022", "%d/%m/%Y")
                },
                }
            },
            {
                "$sort": {"_id": -1}
            }
        ])]


        return {'charges': charge_list}

    elif request.method == 'POST':
        new_charge = request.get_json()
        new_charge['date'] = datetime.fromisoformat(new_charge['date'][:-1].replace('T', ' '))
        operation = database['charges'].insert_one(new_charge)
        new_charge['id'] = str(operation.inserted_id)
        log = LogAction(actor_id, 'POST')
        log.make_statement('charge', 'POST', entity_id=new_charge['id'])
        log.insert()
        return serialize_one(new_charge)

@app.route(charge_namespace + '/<id>', methods=['PUT', 'DELETE', 'GET'])
def charge_ud(id):
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        log = LogAction(actor_id, 'GET')
        log.make_statement('charge', 'GET', entity_id=id)
        log.insert()
        return serialize_one(database['charges'].find_one({'_id': ObjectId(id)}))

    elif request.method == 'PUT':
        new_charge = deserialize_one(request.get_json())

        modif = dict((k, v) for k, v in new_charge.items() if k not in ['id', '_id', 'date'])
        database['charges'].update_many({'_id': new_charge['_id']},
                                      {'$set': modif}
                                      )
        database['charges'].update_many({'_id': new_charge['_id']},
                                      {'$set': {"date": datetime.strptime(new_charge['date'], "%a %b %d %Y")}}
                                      )

        log = LogAction(actor_id, 'PUT')
        log.make_statement('charge', 'PUT', entity_id=id)
        log.insert()
        return serialize_one(new_charge)

    elif request.method == 'DELETE':
        print(id)
        deleted = database['charges'].find_one({'_id': ObjectId(id)})
        database['charges'].delete_one({'_id': ObjectId(id)})
        print(deleted)

        log = LogAction(actor_id, 'DELETE')
        log.make_statement('charge', 'DELETE', entity_id=id)
        log.insert()

        return serialize_one(deleted)


@app.route(charge_namespace+'/byDate', methods=['GET'])
def charge_getByDate():
    actor_id = request.args['actor_id']
    cities = request.args.getlist('cities')

    req_json = request.args
    fmt = "%a %b %d %Y"
    charge_list = [serialize_one(m) for m in database['charges'].aggregate([
        {
            "$match": {"date": {
                "$gte": datetime.strptime(req_json['from'], fmt),
                "$lte": datetime.strptime(req_json['to'], fmt)
            }
            }


        },
        {
            "$sort": {"date": -1}
        }
    ])]

    log = LogAction(actor_id, 'GET')
    log.make_statement('charge', 'GET', single_element=False, additional_text=f"from {req_json['from']} to {req_json['to']}")
    log.insert()

    return {'charges': charge_list}

