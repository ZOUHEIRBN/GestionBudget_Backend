from datetime import datetime

from bson import ObjectId
from flask import request

from bindings import app, database
from url_bindings.actions import LogAction

funds_namespace = '/funds'


def serialize_one(fund):
    fund['id'] = str(fund['_id'])
    del fund['_id']

    return fund

def deserialize_one(fund):
    fund['_id'] = ObjectId(fund['id'])
    del fund['id']
    return fund

@app.route(funds_namespace, methods=['GET', 'POST'])
def fund_cr():
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        fund_list = [serialize_one(m) for m in database['funds'].aggregate([
            # {
            #     "$match": {"date": {
            #         "$gte": datetime.strptime(f"1/1/1970", "%d/%m/%Y"),
            #         "$lte": datetime.strptime(f"1/1/2022", "%d/%m/%Y")
            #     },
            #     }
            # },
            {
                "$sort": {"_id": -1}
            }
        ])]


        return {'funds': fund_list}

    elif request.method == 'POST':
        new_fund = request.get_json()
        new_fund['date'] = datetime.strptime(new_fund['date'], "%a %b %d %Y")

        operation = database['funds'].insert_one(new_fund)
        new_fund['id'] = str(operation.inserted_id)
        log = LogAction(actor_id, 'POST')
        log.make_statement('fund', 'POST', entity_id=new_fund['id'])
        log.insert()
        return serialize_one(new_fund)

@app.route(funds_namespace + '/<id>', methods=['PUT', 'DELETE', 'GET'])
def fund_ud(id):
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        log = LogAction(actor_id, 'GET')
        log.make_statement('fund', 'GET', entity_id=id)
        log.insert()
        return serialize_one(database['funds'].find_one({'_id': ObjectId(id)}))

    elif request.method == 'PUT':
        new_fund = deserialize_one(request.get_json())

        modif = dict((k, v) for k, v in new_fund.items() if k not in ['id', '_id', 'date'])
        database['funds'].update_many({'_id': new_fund['_id']},
                                      {'$set': modif}
                                      )
        database['funds'].update_many({'_id': new_fund['_id']},
                                      {'$set': {"date": datetime.fromisoformat(new_fund['date'][:-1].replace('T', ' '))}}
                                      )

        log = LogAction(actor_id, 'PUT')
        log.make_statement('fund', 'PUT', entity_id=id)
        log.insert()
        return serialize_one(new_fund)

    elif request.method == 'DELETE':
        print(id)
        deleted = database['funds'].find_one({'_id': ObjectId(id)})
        database['funds'].delete_one({'_id': ObjectId(id)})
        print(deleted)

        log = LogAction(actor_id, 'DELETE')
        log.make_statement('fund', 'DELETE', entity_id=id)
        log.insert()

        return serialize_one(deleted)


@app.route(funds_namespace+'/byDate', methods=['GET'])
def fund_getByDate():
    actor_id = request.args['actor_id']
    cities = request.args.getlist('cities')
    print(cities)
    req_json = request.args
    fmt = "%a %b %d %Y"
    match_dict = {"date": {
                "$gte": datetime.strptime(req_json['from'], fmt),
                "$lte": datetime.strptime(req_json['to'], fmt)
            },
                "city": {"$in": cities}
    }
    if req_json['budget_type'] != '':
        match_dict['budget_type'] = req_json['budget_type']


    fund_list = [serialize_one(m) for m in database['funds'].aggregate([
        {
            "$match": match_dict
        },
        {
            "$sort": {"date": -1}
        }
    ])]

    log = LogAction(actor_id, 'GET')
    log.make_statement('fund', 'GET', single_element=False, additional_text=f"from {req_json['from']} to {req_json['to']}")
    log.insert()

    return {'funds': fund_list}

