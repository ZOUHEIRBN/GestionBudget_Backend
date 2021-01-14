from datetime import datetime

from bson import ObjectId
from flask import request

from bindings import app, database

funds_namespace = '/funds'

def serialize(fund):
    if 'entries' in fund.keys():
        for f in fund['entries']:
            f['id'] = str(f['_id'])
            del f['_id']

    fund['date'] = fund['_id']
    del fund['_id']
    return fund

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

@app.route(funds_namespace + '/<id>', methods=['DELETE', 'PUT'])
def fund_ud(id):
    if request.method == 'GET':
        return serialize(database['funds'].find_one({'_id': ObjectId(id)}))

    elif request.method == 'PUT':
        new_fund = deserialize_one(request.get_json())
        database['funds'].update_one({'_id': ObjectId(id)}, {'$set': new_fund})
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
    print('\n\n')
    print(dict(req_json))
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