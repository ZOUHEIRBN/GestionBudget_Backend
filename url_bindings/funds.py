from datetime import datetime

from bson import ObjectId
from flask import request

from bindings import app, database

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
    if request.method == 'GET':
        fund_list = [serialize_one(m) for m in database['funds'].aggregate([
            {
                "$match": {"date": {
                    "$gte": datetime.strptime(f"1/1/2020", "%d/%m/%Y"),
                    "$lte": datetime.strptime(f"1/1/2022", "%d/%m/%Y")
                }}
            },
            {
                "$sort": {"_id": -1}
            }
        ])]
        return {'funds': fund_list}

    elif request.method == 'POST':
        new_fund = request.get_json()
        operation = database['funds'].insert_one(new_fund)
        new_fund['id'] = str(operation.inserted_id)

        return serialize_one(new_fund)

@app.route(funds_namespace + '/<id>', methods=['PUT', 'DELETE', 'GET'])
def fund_ud(id):
    if request.method == 'GET':
        return serialize_one(database['funds'].find_one({'_id': ObjectId(id)}))

    elif request.method == 'PUT':
        new_fund = deserialize_one(request.get_json())
        print(new_fund['date'], datetime.fromisoformat(new_fund['date'][:-1].replace('T', ' ')))
        print()
        print(database['funds'].find_one({'_id': new_fund['_id']}))
        modif = dict((k, v) for k, v in new_fund.items() if k not in ['id', '_id', 'date'])
        database['funds'].update_many({'_id': new_fund['_id']},
                                      {'$set': modif}
                                      )
        database['funds'].update_many({'_id': new_fund['_id']},
                                      {'$set': {"date": datetime.fromisoformat(new_fund['date'][:-1].replace('T', ' '))}}
                                      )
        return serialize_one(new_fund)

    elif request.method == 'DELETE':
        print(id)
        deleted = database['funds'].find_one({'_id': ObjectId(id)})
        database['funds'].delete_one({'_id': ObjectId(id)})
        print(deleted)
        return serialize_one(deleted)


@app.route(funds_namespace+'/byDate', methods=['GET'])
def getByDate():
    req_json = request.args
    fmt = "%a %b %d %Y %H:%M:%S GMT 0100 (GMT 01:00)"
    fund_list = [serialize_one(m) for m in database['funds'].aggregate([
        {
            "$match": {"date": {
                "$gte": datetime.strptime(req_json['from'], fmt),
                "$lte": datetime.strptime(req_json['to'], fmt)
            }}
        },
        {
            "$sort": {"_id": -1}
        }
    ])]
    return {'funds': fund_list}