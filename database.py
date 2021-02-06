from datetime import datetime
from random import choice
from bindings import database
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


# database['users'].update_many({'username': 'zouheirbn'}, {'$set': {'roles': [{'name': 'Siège', 'type': 'city'}, {'name': 'Directeur régional', 'type': 'rank'}]}})

# print(list(database['users'].find({})))


# funds = [x['_id'] for x in database['funds'].find({})]
# cities = ['Oriental', 'Daraa-Tafilalet', 'Souss-Massa', 'Centre', 'Sud', 'Atlas-Océan', 'Siège']
#
# for fid in funds:
#     random_city = choice(cities)
#     database['funds'].update_one({'_id': fid}, {'$set':
#                                                     {'city': random_city}
#                                                 })
#     print(f"Fund (ID:{fid}) -> {random_city}")

funds_siege = [x['_id'] for x in database['funds'].find({'city': 'Oriental'})]

print(len(funds_siege), funds_siege)


# database['users'].update_one({'username': 'zouheirbn'}, {'$push':
#                                                              {
#                                                                 "roles": {'name': 'Oriental', 'type': 'city'}
#                                                              }})