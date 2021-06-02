from datetime import datetime
from random import choice

from bson import ObjectId

from bindings import database
from helper import *
from url_bindings.users import hash_password


# {
#   "$project": {
#       '_id': {"$toString": '$_id'},
#       'mo': 1, 'market_no': 1,
#       'object': 1, 'begin_date': 1,
#       'deadline': 1, 'end_date': 1,
#       'def_caution': 1, 'total_sum': 1,
#       'trimester_sum': 1,
#       'agents_number': 1,
#       'owner': 1, 'privileges': 1,
#       'execution_site': 1, 'cumulative_sum': 1,
#       'payments.realization_sum': 1,
#       'payments.billing_sum': 1,
#       'payments.collected_sum': 1,
#       'payments.realization_date': 1,
#       'payments.billing_date': 1,
#       'payments.collected_date': 1,
#       'payments.sum': {"$map": {
#           "input": "$payments",
#           "as": "p",
#           "in": {"$add": ["$$p.realization_sum", "$$p.billing_sum", "$$p.collected_sum"]}
#       }}
#     }

mkts = [x for x in database['markets'].aggregate([
    {"$match": {"owner": {"$eq": "NAJD"}}},
    {"$addFields": {
        'payments.sum': {"$arrayElemAt": [{"$map": {
            "input": "$payments",
            "as": "p",
            "in": {"$add": ["$$p.realization_sum", "$$p.billing_sum", "$$p.collected_sum"]}
        }}, -1]},
        'payments.left': {"$arrayElemAt": [{"$map": {
            "input": "$payments",
            "as": "p",
            "in": {"$subtract": ["$cumulative_sum",
                                 {"$add": ["$$p.realization_sum", "$$p.billing_sum", "$$p.collected_sum"]}]}
        }}, -1]},
        'payments.left_this_year': {"$arrayElemAt": [{"$map": {
            "input": "$payments",
            "as": "p",
            "in": {"$subtract": ["$cumulative_sum", "$$p.collected_sum"]}
        }}, -1]}

    }},
    {"$addFields": {
       "root": "$$ROOT",
        'payments.billing_year': {"$map": {
            "input": '$payments',
            "as": "d",
            "in": {"$year": {"date": {"$toDate": "$$d.billing_date"}}}
        }},
        'payments.realization_year': {"$map": {
            "input": '$payments',
            "as": "d",
            "in": {"$year": {"date": {"$toDate": "$$d.realization_date"}}}
        }},
    }},


])]
print(len(mkts))
for m in mkts:
    # print(sorted({y for ys in [list(m[x].keys())+[x] if type(m[x]).__name__ == "dict" else [x] for x in m.keys()]
    #               for y in ys}))

    for k,v in m.items():
        print(k, ': ', v)
    break