# from datetime import datetime
#
# from bson import ObjectId
from flask import request
#
from bindings import app, database
# from url_bindings.actions import LogAction

REPLACEMENT_DICT = {'id': "ID",
    'for_company':"Assurance", 'total_market_amount': "Montant du marché", 'execution_deadline': "Délai d'exécution", 'market_ref': "Réf. marché",
    'master': "Maitre d'ouvrage", 'total_sum': "Charges directes", 'coef_affect_ch_ind': "Coefficient d'affectation des charges indirectes", 'indirect_charges': "Charges indirectes",
    'charges_sum': "Montant total des charges: (directes + indirectes)", 'periodic_amount': "Montant facturé TTC",
    'tva_amount': "Dont TVA", 'before_fines': "Résultat avant impots", 'ratio':'RATIO Résultat/TVA',
    'fund_id': 'ID Caisse', 'charge_id': "ID Charge"
}

@app.route('/summary', methods=['GET', 'POST'])
def getSummary():
    actor_id = request.args['actor_id']
    match_dict = None  #request.args['query_dict']
    if match_dict is None:
        match_dict = {
            # 'for_company': 'XY CONSEIL'
        }
    cur = [x for x in database['summary'].aggregate([
        {"$match": {
            "fund_id": {"$ne": 0},
            "charge_id": {"$ne": 0}
        }},
        {"$project": {
            "fund_id": {
                "$toObjectId": "$fund_id"
            },
            "charge_id": {
                "$toObjectId": "$charge_id"
            },
            "execution_deadline": 1,
            "total_market_amount": 1
        }},
        {"$lookup": {
            "from": "charges",
            "localField": "charge_id",
            "foreignField": "_id",
            "as": "charge"
        }},
        {"$replaceRoot": {
            "newRoot": {
                "$mergeObjects": [{"$arrayElemAt": ["$charge", -1]}, "$$ROOT"]
            }
        }},
        {"$lookup": {
            "from": "funds",
            "localField": "fund_id",
            "foreignField": "_id",
            "as": "fund"
        }},
        {"$replaceRoot": {
            "newRoot": {
                "$mergeObjects": [{"$arrayElemAt": ["$fund", -1]}, "$$ROOT"]
            }
        }},
        {"$lookup": {
            "from": "charges",
            "localField": "for_company",
            "foreignField": "for_company",
            "as": "company"
        }},
        {"$match": match_dict},
        {"$addFields": {
            'market_sum': {'$sum': '$company.total_sum'},
            'indirect_charges_drc': 7301.84
        }},

        {"$project": {
            'id': {
                "$toString": "$_id"
            },
            '_id': 0,
            'total_market_amount': 1,
            'execution_deadline': 1,
            'fund_id': {
                "$toString": "$fund_id"
            },
            'charge_id': {
                "$toString": "$charge_id"
            },
            'market_ref': 1,
            'for_company': 1,
            'master': 1,
            'total_sum': 1,
            'coef_affect_ch_ind': {"$divide": ['$total_market_amount', '$market_sum']},

            'indirect_charges': {
                "$multiply": [{"$divide": ['$total_market_amount', '$market_sum']}, '$indirect_charges_drc']},
            'charges_sum': {"$add": ['$total_sum',
                                     {"$divide": [{"$divide": ['$total_market_amount', '$market_sum']}, 10]}
                                     ]},
            'periodic_amount': {"$divide": ['$total_market_amount', '$execution_deadline']},
            'tva_amount': {"$divide": [{"$divide": ['$total_market_amount', '$execution_deadline']}, 6]},
            'before_fines': {"$subtract": [
                {"$divide": ['$total_market_amount', '$execution_deadline']},
                {"$add": ['$total_sum',
                          {"$divide": [{"$divide": ['$total_market_amount', '$market_sum']}, 10]}
                          ]}
            ]},
            'ratio': {'$divide': [{"$subtract": [
                {"$divide": ['$total_market_amount', '$execution_deadline']},
                {"$add": ['$total_sum',
                          {"$divide": [{"$divide": ['$total_market_amount', '$market_sum']}, 10]}
                          ]}
            ]}, {"$divide": [{"$divide": ['$total_market_amount', '$execution_deadline']}, 6]}]}
        }},

    ])]

    return {'summary': [dict((REPLACEMENT_DICT[k], x[k]) for k in x.keys()) for x in cur], 'features': list(REPLACEMENT_DICT.values())}
