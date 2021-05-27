from datetime import datetime

from bson import ObjectId
from flask import request

from bindings import app, database
from helper import set_privileges
from url_bindings.actions import LogAction

expense_namespace = '/expenses'
DATE_FMT = "%a %b %d %Y"
REPLACEMENT_DICT = {
'firstname' :  'Prénom du bénéficiaire',
'lastname' :  'Nom du bénéficiaire',
'expense_type' :  'Type de dépense',
'date' :  'Date',
'beneficient' :  'ID du bénéficiaire',
'engaged_amount' :  'Montant engagé',
'paid_amount' :  'Montant payé',
'remainder': 'Reste à payer',
'objective' :  'Motif',
'phase' :  'Phase',
}

EXPENSE_TYPES = {
      "Charges du personel": "personal_charges",
      "Matière première": "raw_material",
      "Location matériel/Transport": "loc_transport",
      "Carburant": "fuel",
      "Réparation du matériel": "maintenance",
  }
def serialize_one(expense, actor_id):
    REVERSE_EXPENSE_TYPES = {v: k for k, v in EXPENSE_TYPES.items()}
    expense['expense_type'] = REVERSE_EXPENSE_TYPES.get(expense['expense_type'], expense['expense_type'])
    expense['beneficient'] = str(expense['beneficient'])
    if type(expense['date']).__name__ == 'datetime':
        expense['date'] = expense['date'].strftime(DATE_FMT)

    expense['id'] = str(expense['_id'])
    del expense['_id']
    return set_privileges(expense, actor_id)

def deserialize_one(expense):
    expense['expense_type'] = EXPENSE_TYPES.get(expense['expense_type'], expense['expense_type'])
    expense['beneficient'] = ObjectId(expense['beneficient'])
    expense['date'] = datetime.strptime(expense['date'], DATE_FMT)
    expense['_id'] = ObjectId(expense['id'])
    del expense['id']
    del expense['remainder']
    return expense

def fetch_privileges(actor_id):
    return ['view', 'list', 'edit', 'add', 'delete']

@app.route(expense_namespace, methods=['GET', 'POST'])
def expense_cr():
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        expense_list = [serialize_one(m, actor_id) for m in database['expenses'].aggregate([
            {"$lookup": {
                "from": "users",
                "localField": "beneficient",
                "foreignField": "_id",
                "as": "user"
            }},
            {"$project": {
                "username": 0,
                "firstname": 0,
                "lastname": 0
            }},
            {"$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": [{"$arrayElemAt": ["$user", -1]}, "$$ROOT"]
                }
            }},
            {"$project": {
                "password": 0,
                "user": 0,
                "roles": 0
            }},
            {"$sort": {
                "_id": -1
            }}
        ])]
        log = LogAction(actor_id, 'POST')
        log.make_statement('expense', 'POST', single_element=False)
        log.insert()
        return {'expenses': [x for x in expense_list], 'features': REPLACEMENT_DICT, 'privileges': fetch_privileges(actor_id)}

    elif request.method == 'POST':
        new_expense = request.get_json()
        new_expense['date'] = datetime.strptime(new_expense['date'], DATE_FMT)
        operation = database['expenses'].insert_one(new_expense)
        new_expense['id'] = str(operation.inserted_id)
        log = LogAction(actor_id, 'POST')
        log.make_statement('expense', 'POST', entity_id=new_expense['id'])
        log.insert()
        return serialize_one(new_expense, actor_id)

@app.route(expense_namespace + '/<id>', methods=['PUT', 'DELETE', 'GET'])
def expense_ud(id):
    actor_id = request.args['actor_id']
    if request.method == 'GET':
        log = LogAction(actor_id, 'GET')
        log.make_statement('expense', 'GET', entity_id=id)
        log.insert()
        return serialize_one(database['expenses'].find_one({'_id': ObjectId(id)}), actor_id)

    elif request.method == 'PUT':
        print(request.get_json())
        new_expense = deserialize_one(request.get_json())

        modif = dict((k, v) for k, v in new_expense.items() if k not in ['id', '_id', 'date'])
        database['expenses'].update_many({'_id': new_expense['_id']},
                                      {'$set': modif}
                                      )
        database['expenses'].update_many({'_id': new_expense['_id']},
                                      {'$set': {"date": new_expense['date']}}
                                      )

        log = LogAction(actor_id, 'PUT')
        log.make_statement('expense', 'PUT', entity_id=id)
        log.insert()
        return serialize_one(new_expense, actor_id)

    elif request.method == 'DELETE':
        print(id)
        deleted = database['expenses'].find_one({'_id': ObjectId(id)})
        database['expenses'].delete_one({'_id': ObjectId(id)})
        print(deleted)

        log = LogAction(actor_id, 'DELETE')
        log.make_statement('expense', 'DELETE', entity_id=id)
        log.insert()

        return serialize_one(deleted, actor_id)
