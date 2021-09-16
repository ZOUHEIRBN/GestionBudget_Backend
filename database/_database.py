from datetime import datetime
from random import choice

from bson import ObjectId

from bindings import database
from helper import *
from url_bindings.users import hash_password

BILAN_PIPELINE = {"$map": {
        "input": "$root.payments",
        "as": "b",
        "in": {
            "real_y": "$$b"
        }
    }}
DESIRED_KEYS = ['_id', 'mo', 'market_no', 'object', 'begin_date', 'deadline', 'end_date', 'def_caution', 'total_sum', 'trimester_sum', 'agents_number', 'owner', 'execution_site', 'cumulative_sum', 'payments', 'is_reconductible']



def make_zip(col):
    return {"$map": {
        "input": {"$zip": {
                   "inputs": [
                       {"$map": {
                           "input": "$root.payments",
                           "as": "p",
                           "in": {"$year": {"$toDate": f"$$p.{col}_date"}}
                       }},
                       {"$map": {
                           "input": "$root.payments",
                           "as": "p",
                           "in": f"$$p.{col}_sum"
                       }}
                   ]
           }
        },
        "as": "m",
        "in": {"year": {"$arrayElemAt": ["$$m", 0]}, "sum": {"$arrayElemAt": ["$$m", 1]}}
    }}
def matrix_filter(col):
    return {"$sum": {"$map": {
                   "input": {"$filter": {
                       "input": "$root.payments",
                       "as": "f",
                       "cond": {"$and": [
                           {"$eq": [{"$year": {"$toDate": "$$p.realization_date"}},
                                    {"$year": {"$toDate": "$$f.realization_date"}}]},
                           {"$eq": [{"$year": {"$toDate": "$$p.billing_date"}},
                                    {"$year": {"$toDate": "$$f.billing_date"}}]},
                           {"$eq": [{"$year": {"$toDate": "$$p.collected_date"}},
                                    {"$year": {"$toDate": "$$f.collected_date"}}]},
                       ]}
                   }},
                   "as": "m",
                   "in": f"$$m.{col}_sum"
               }}}

# {"$addFields": {
#             "bilan": {"$map": {
#                 "input": "$payments",
#                 "as": "p",
#                 "in": {
#                     "realization_year": {"$year": {"$toDate": "$$p.realization_date"}},
#                     "billing_year": {"$year": {"$toDate": "$$p.billing_date"}}
#                 }
#             }}
#         }},
#     {"$addFields": {
#         f"{f}_sum": {"$map": {
#             "input": "$bilan",
#             "as": "b",
#             "in": {"$sum": {"$map": {
#                 "input": {"$filter": {
#                     "input": "$payments",
#                     "as": "f",
#                     "cond": {"$and": [
#                         {"$eq": ["$$b.realization_year", {"$year": {"$toDate": "$$f.realization_date"}}]},
#                         {"$eq": ["$$b.billing_year", {"$year": {"$toDate": "$$f.billing_date"}}]},
#                     ]}
#                 }},
#                 "as": "p",
#                 "in": f"$$p.{f}_sum"
#             }}}
#         }}
#         for f in ['realization', 'billing']
#     }},
#     {"$addFields": {
#        "X": {"$map": {
#            "input": {"$zip": {"inputs": ["$bilan.realization_year", "$realization_sum", "$bilan.billing_year", "$billing_sum"]}},
#            "as": "z",
#            "in": {
#                 "realization_year": {"$arrayElemAt": ["$$z", 0]},
#                 "realization_sum": {"$arrayElemAt": ["$$z", 1]},
#                 "billing_year": {"$arrayElemAt": ["$$z", 2]},
#                 "billing_sum": {"$arrayElemAt": ["$$z", 3]},
#            }
#        }}
#     }},
mkts = [x for x in database['markets'].aggregate([
        {"$project": {k: 1 for k in DESIRED_KEYS}},

        {"$addFields": {
                    "bilan": {"$map": {
                        "input": "$payments",
                        "as": "p",
                        "in": {
                            "realization_year": {"$year": {"$toDate": "$$p.realization_date"}},
                            "billing_year": {"$year": {"$toDate": "$$p.billing_date"}},
                            "collected_year": {"$year": {"$toDate": "$$p.collected_date"}},
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
                                {"$eq": ["$$b.collected_year", {"$year": {"$toDate": "$$f.collected_date"}}]},
                            ]}
                        }},
                        "as": "p",
                        "in": f"$$p.{f}_sum"
                    }}}
                }}
                for f in ['realization', 'billing', 'collected']
            }},
        {"$addFields": {
               "bilan": {"$map": {
                   "input": {"$zip": {"inputs": ["$bilan.realization_year", "$realization_sum", "$bilan.billing_year", "$billing_sum", "$bilan.collected_year", "$collected_sum"]}},
                   "as": "z",
                   "in": {
                        "realization_year": {"$arrayElemAt": ["$$z", 0]},
                        "realization_sum": {"$arrayElemAt": ["$$z", 1]},
                        "billing_year": {"$arrayElemAt": ["$$z", 2]},
                        "billing_sum": {"$arrayElemAt": ["$$z", 3]},
                        "collected_year": {"$arrayElemAt": ["$$z", 4]},
                        "collected_sum": {"$arrayElemAt": ["$$z", 5]},
                   }
               }}
            }},

        {"$project": {
            "id": {"$toString": "$_id"},
            "_id": 0,
            "root": "$$ROOT",
        }},



        {"$replaceRoot": {
        "newRoot": {
            "$mergeObjects": "$root"
        }
    }}
])]
print(len(mkts))
for m in mkts:
    # print([k for k in m.keys()])
    for k,v in m.items():
        if k != 'payment':
            print(k, ': ', v)
        else:
            print([kk for kk in v[0].keys()])
    break