from datetime import datetime
from random import choice

from bson import ObjectId

from bindings import database
from helper import *
from url_bindings.users import hash_password
# for i in range(21, 28):
#     database['funds'].update_many({'date': f'{i}/12/2020'},
#                               {'$set': {'date': datetime.strptime(f"{i}/12/2020", "%d/%m/%Y")}})
#
# {"$group": {"_id": {"$dateToString": {"format": "%d-%m-%Y", "date": "$date" } },
#                         "entries": {"$push": "$$ROOT"}}},
# database['users'].insert_one({'username': 'Coordinateur', 'password': hash_password('coord'), 'firstname': 'Coo', "lastname": "rdinateur"})

# f = database['funds'].find({})
#
#
# for i in range(1, 32):
#     database['funds'].update_many({'date': '2021-01-{:02}T00:00:00.000Z'.format(i)},
#                               {'$set': {'date': datetime.strptime(f"{i}/01/2021", "%d/%m/%Y")}})
#
# print(sorted({x['date'] for x in f if 'datetime' in str(type(x['date']))}))


# database['actions'].insert_one({
#     'actor_id': '5ffa335adf09d518d9636cfd',
#     'action': 'Ut enim ad minim veniam',
#     'timestamp': datetime.now()
# })

# database['users'].update_many({}, {'$set': {'firstname': 'Zouheir', 'lastname': 'BN'}})

# actions = list(database['actions'].find({}))
# for a in actions:
#     print(a)


# database['users'].update_many({'username': 'AstDR'}, {'$set': {'username': 'astdr'}})
# print(list(database['users'].find({'lastname': 'rdinateur'})))


# funds = [x['_id'] for x in database['funds'].find({})]
# cities = ['Oriental', 'Daraa-Tafilalet', 'Souss-Massa', 'Centre', 'Sud', 'Atlas-Océan', 'Siège']
#
# for fid in funds:
#     random_city = choice(cities)
#     database['funds'].update_one({'_id': fid}, {'$set':
#                                                     {'city': random_city}
#                                                 })
#     print(f"Fund (ID:{fid}) -> {random_city}")
#
# funds_siege = [x['date'] for x in database['charges'].find({})]
#
# print(funds_siege)
#
#
# database['users'].update_one({'username': 'zouheirbn'}, {'$push':
#                                                              {
#                                                                 "roles": {'name': 'Sud', 'type': 'city'}
#                                                              }})

"""
aa = database['actions'].aggregate([
    {"$match": {
        "actor_id": {"$ne": 'undefined'},
    }},

    {"$project": {
      "actor_id": {
        "$toObjectId": "$actor_id"
      },
        'action': 1,
        'timestamp': 1,
        'entity_type': 1,
        'operation_type': 1
    }},

    {"$lookup": {
        "from": "users",
        "localField": "actor_id",
        "foreignField": "_id",
        "as": "actor"
    }},
    {"$replaceRoot": {
        "newRoot": {
            "$mergeObjects": [{"$arrayElemAt": ["$actor", -1]}, "$$ROOT"]
        }
    }},
    {"$project": {'password': 0, 'actor': 0, 'actor_id': 0}},
    {"$match": {
        "operation_type": {"$in": ['PUT']},
        "$and": [
            {"$and": [{
                "roles.name": {"$in": ['Siège', 'Sud']}
            }, {
                "roles.type": 'city'
            }]},
            {"$and": [{
                "roles.name": {"$in": ['Directeur régional']}
            }, {
                "roles.type": 'rank'
            }]}
        ]

        # "actions": {"$in": ['charge']},
    }}
])
for a in aa:
    for k, v in a.items():
        print(f"{k}:\t{v}")

    break
"""

# database['actions'].update_many({'operation_type': "Consultation"}, {"$set":
# {'operation_type': "Liste"}
#                                                          })
#
# o = [x['operation_type'] for x in database['actions'].find()]
# print(o)



# expense = {
#     "expense_type": "personal_charges",
#     "date": datetime.strptime("22/01/2021", "%d/%m/%Y"),
#     "beneficient": ObjectId('5ffa335adf09d518d9636cfd'),
#     "engaged_amount": 700,
#     "paid_amount": 700,
#     "objective": "Location d'une maison",
#     "phase": 1
# }

# p = database['expenses'].aggregate([
#     {"$lookup": {
#         "from": "users",
#         "localField": "beneficient",
#         "foreignField": "_id",
#         "as": "user"
#     }},
#     {"$replaceRoot": {
#         "newRoot": {
#             "$mergeObjects": [{"$arrayElemAt": ["$user", -1]}, "$$ROOT"]
#         }
#     }},
#     {"$project": {
#         "password": 0,
#         "user": 0,
#     }}
# ])

"""
p = database['expenses'].aggregate([
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
        ])


for pp in database['funds'].find():
    print(pp)
"""

# database['users'].insert_one({"firstname":"Super","lastname":"User",
#                               "roles":[{"name":"Sud","type":"city"},{"name":"Centrale","type":"rank"},{"name":"Oriental","type":"city"}],"username":"superuser", "password": hash_password('superuser')})


# print((list(database['actions'].find({"entity_id": {"$exists": 1}}))))


# uuuu = database['users'].aggregate([
#     {"$project": {
#         "rolename": {
#             "$map": {
#                 "input": "$roles.name",
#                 "as": "r",
#                 "in": {
#                     "primaryGroup": {
#                         "$filter": {
#                             "input": "$roles",
#                             "as": "rr",
#                             "cond": {"$eq": ["$$rr.type", "city"]}
#                         }
#                     },
#                 }
#             }
#         }
#     }},
#     {"$project": {
#         "cities": "$rolename.primaryGroup.name"
#     }},
#     {"$unwind": "$cities"}
# ])
# for u in uuuu:
#     print(u)


# entity_type = "market"
# entity_city = "Sud"
#
# rr = generate_role_grid(entity_type, entity_city)
# df = pd.DataFrame(rr)
# print(df)
# # df.to_csv('roles.csv')

# ENTITY_TYPES = ['market']
# data = {}
# for entity_type in ENTITY_TYPES:
#     for city in sorted(ALL_CITIES):
#         roles = {}
#         for role in sorted(ALL_ROLES):
#             for entity_city in sorted(ALL_CITIES):
#                 r = is_role_eligible(entity_type, {role}, entity_city, {city})
#                 roles[role+"_"+entity_city] = r
#         data[entity_type+"_"+city] = roles
#
# print(pd.DataFrame(data))
# # pd.DataFrame(data).to_csv('access_rights.csv')

print({c['operation_type'] for c in database['actions'].find()})