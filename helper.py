from bson import ObjectId
from bindings import database
# import pandas as pd

PRIVILEGES = ['view', 'list', 'edit', 'add', 'delete']
ALL_CITIES = {city for cities in database['users'].aggregate([
    {"$project": {
        "rolename": {
            "$map": {
                "input": "$roles.name",
                "as": "r",
                "in": {
                    "primaryGroup": {
                        "$filter": {
                            "input": "$roles",
                            "as": "rr",
                            "cond": {"$eq": ["$$rr.type", "city"]}
                        }
                    },
                }
            }
        }
    }},
    {"$project": {
        "cities": "$rolename.primaryGroup.name"
    }},
    {"$unwind": "$cities"}
]) for city in cities['cities']}

ALL_ROLES = {role for roles in database['users'].aggregate([
    {"$project": {
        "rolename": {
            "$map": {
                "input": "$roles.name",
                "as": "r",
                "in": {
                    "primaryGroup": {
                        "$filter": {
                            "input": "$roles",
                            "as": "rr",
                            "cond": {"$eq": ["$$rr.type", "rank"]}
                        }
                    },
                }
            }
        }
    }},
    {"$project": {
        "roles": "$rolename.primaryGroup.name"
    }},
    {"$unwind": "$roles"}
]) for role in roles['roles']}

CITY_ATTRIBUTE_NAME = {
'market', 'fund', 'charge', 'expense'
}

DEFAULT_PERMISSIONS = ['default', 'market', 'fund', 'charge', 'expense']
def fetch_user_rank_roles(user_id):
    user = database['users'].aggregate([
        {'$match': {'_id': ObjectId(user_id)}},
        {'$addFields': {
            'roles': {
                '$filter': {
                    'input': '$roles',
                    'cond': {
                      '$eq': ["$$this.type", "rank"]
                    }
                }
            }
        }},
        {'$project': {
            'roles': {
                "$map": {
                    "input": "$roles",
                    "as": "role",
                    "in": "$$role.name"
                }
            }
        }}
    ])
    return set([x for x in user][0]['roles'])

def fetch_user_city_roles(user_id):
    user = database['users'].aggregate([
        {'$match': {'_id': ObjectId(user_id)}},
        {'$addFields': {
            'roles': {
                '$filter': {
                    'input': '$roles',
                    'cond': {
                      '$eq': ["$$this.type", "city"]
                    }
                }
            }
        }},
        {'$project': {
            'roles': {
                "$map": {
                    "input": "$roles",
                    "as": "role",
                    "in": "$$role.name"
                }
            }
        }}
    ])
    return set([x for x in user][0]['roles'])

def find_editors_history(element_id):
    element_actions = list(database['actions'].aggregate([
        {"$match": {'entity_id': element_id}},
        {"$sort": {"timestamp": 1}},
        {"$project":{
            "timestamp": 1,
            "actor_id": 1,
            "_id": 0
        }}
    ]))
    return element_actions

def is_city_eligible(element_cities, user_cities):
    EC = {e.upper() for e in element_cities}
    UC = {u.upper() for u in user_cities}

    return len(EC.intersection(UC)) > 0

def is_role_eligible(entity_type, user_ranks, element_cities, user_cities):
    if type(element_cities).__name__ == 'str':
        element_cities = {element_cities}

    if type(user_cities).__name__ == 'str':
        user_cities = {user_cities}


    if type(user_ranks).__name__ == 'str':
        user_ranks = {user_ranks}


    full_access_conditions = [
        (entity_type not in ['actions', 'summary'] and "Centrale" in user_ranks),
        (entity_type in DEFAULT_PERMISSIONS and is_city_eligible(element_cities, user_cities) and user_ranks.intersection(
            {'Assistant DR', 'Directeur régional', 'Centrale'}) != set())
    ]
    readonly_conditions = [
        "Centrale" in user_ranks,
        (entity_type in DEFAULT_PERMISSIONS and is_city_eligible(element_cities, user_cities)),
        (entity_type in ['summary', 'user'] and
                    is_city_eligible(element_cities, user_cities) and 'Directeur régional' in user_ranks),
        (entity_type == 'summary' and is_city_eligible(element_cities, user_cities) and 'Assistant DR' in user_ranks)
    ]


    if any(full_access_conditions):
        return "full_access"
    elif any(readonly_conditions):
        return "readonly"
    else:
        return "no_access"


def set_privileges(element, actor_id, entity_type='default'):
    privilege_list = [x for x in PRIVILEGES]
    user_ranks = fetch_user_rank_roles(actor_id)
    user_cities = fetch_user_city_roles(actor_id)

    #Identifying element's city by the last person editing it
    element_cities = find_editors_history(element['id'])
    if len(element_cities) > 0:
        element_cities = list(fetch_user_city_roles(element_cities[-1]['actor_id']))
        print(f"This element belongs to the following cities: {', '.join(element_cities[:-1])} and {element_cities[-1]}")
    else:
        element_cities = ALL_CITIES

    if is_role_eligible(entity_type, user_ranks, element_cities, user_cities) == 'full_access':
        privilege_list = PRIVILEGES
    elif is_role_eligible(entity_type, user_ranks, element_cities, user_cities) == 'readonly':
        privilege_list = ['list', 'view']
    elif is_role_eligible(entity_type, user_ranks, element_cities, user_cities) == 'no_access':
        privilege_list = []




    element['privileges'] = privilege_list
    return element


def get_entity_history(entity_id, get_last_actions=0):
    results = database['actions'].aggregate([
        {"$match": {'entity_id': entity_id}},
        {"$sort": {'timestamp': -1}},
        {"$project": {
           "id": {"$toString": "$_id"},
            "entity_type": 1,
            "operation_type": 1,
            "actor_id": 1,
            "_id": 0
        }}
    ])
    results = [i for i in results]
    if get_last_actions == 0:
        return results

    return results[:get_last_actions]


def generate_role_grid(entity_type, entity_city):
    cities = {}
    print(f"Droits d'accès aux éléments de type '{entity_type}' à partir du site '{entity_city}':\n")
    for city in sorted(ALL_CITIES):
        roles = {}
        for role in sorted(ALL_ROLES):
            r = is_role_eligible(entity_type, {role}, entity_city, {city})
            roles[role] = r
        cities[city] = roles


    return cities

