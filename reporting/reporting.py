import os

from flask import render_template, make_response, request
import pdfkit
import json
from bindings import app, database
from url_bindings.markets import serialize as serialize_market
from url_bindings.actions import serialize as serialize_action

@app.route('/markets/report', methods=['GET'])
def generate_market_report(request_dict=None):
    if request_dict is None:
        request_dict = {}

    markets = database['markets'].find(request_dict, {})
    markets = [serialize_market(m) for m in markets]
    template = render_template('market_report.html', markets=markets)
    pdf = pdfkit.from_string(template, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = "inline; filename=market_report.pdf"

    return template

REPLACEMENTS = {
    'Consultation': "Consultation",
    'Liste': "Liste",
    'Modification': "Modification",
    'Ajout': "Ajout",
    'Suppression': "Suppression",
    'Marchés': 'market',
    'Caisses': 'fund',
    'Rapports': 'report',
    'Utilisateurs': 'user',
    'Charges': 'charge'
}

@app.route('/actions/report', methods=['GET'])
def generate_actions_report():
    os.system("cls")
    request_dict = {}

    request_json = json.loads(request.args['query_data'])
    for k,v in request_json.items():
        request_dict[k] = [REPLACEMENTS.get(x, x) for x in v.keys() if v[x]]

    print(request_dict, '\n')

    #Generating the query
    match_dict = {}
    match_dict_and = []
    if len(request_dict.get('entities', [])) > 0:
        match_dict["entity_type"] = {"$in": request_dict['entities']}

    if len(request_dict.get('actions', [])) > 0:
        match_dict["operation_type"] = {"$in": request_dict['actions']}

    if len(request_dict.get('roles', [])) > 0:
        match_dict_and.append({"$and": [{
                    "roles.name": {"$in": request_dict['roles']}
                }, {
                    "roles.type": 'rank'
                }]})

    if len(request_dict.get('directions', [])) > 0:
        match_dict_and.append({"$and": [{
                    "roles.name": {"$in": request_dict['directions']}
                }, {
                    "roles.type": 'city'
                }]})
    if len(match_dict_and) > 0:
        match_dict["$and"] = match_dict_and



    actions = database['actions'].aggregate([
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
        {"$match": match_dict}
    ])



    """
        for a in actions:
        for k, v in a.items():
            break
            print(f"{k}:\t{v}")
        print('\n')
        break
    """
    actions = [x for x in actions]
    print(len(actions))

    template = render_template('action_report.html', actions=actions, request_dict=request_dict)
    response = convertToPDF(template)

    return response



def convertToPDF(template):
    # pdf = pdfkit.from_string(template, "test.pdf", css="static/styles.css")
    pdf = pdfkit.from_string(template, False, css="static/styles.css")

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = "inline; filename=action_report.pdf"
    
    return response