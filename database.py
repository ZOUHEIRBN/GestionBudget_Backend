from datetime import datetime

from bindings import database
from url_bindings.users import hash_password
# for i in range(21, 28):
#     database['funds'].update_many({'date': f'{i}/12/2020'},
#                               {'$set': {'date': datetime.strptime(f"{i}/12/2020", "%d/%m/%Y")}})
#
# {"$group": {"_id": {"$dateToString": {"format": "%d-%m-%Y", "date": "$date" } },
#                         "entries": {"$push": "$$ROOT"}}},
# database['users'].insert_one({'username': 'ZouheirBN', 'password': hash_password('zouheir6')})
f = database['funds'].find({})
print([e for e in f])