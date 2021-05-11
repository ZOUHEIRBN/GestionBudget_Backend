from bson import ObjectId
from bindings import database

PRIVILEGES = ['view', 'list', 'edit', 'add', 'delete']
CITY_ATTRIBUTE_NAME = {
'market', 'fund', 'charge', 'expense'
}
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

def set_privileges(element, actor_id, entity_type='default'):
    privilege_list = [x for x in PRIVILEGES]
    user_cities = fetch_user_city_roles(actor_id)
    user_ranks = fetch_user_rank_roles(actor_id)

    # print(len(user_ranks.intersection({'Centrale', 'Assistant DR', 'Directeur régional'})))

    if entity_type == 'default' or entity_type in ['market', 'fund', 'charge', 'expense']:
        if len(user_ranks.intersection({'Centrale', 'Assistant DR', 'Directeur régional'})) == 0:
            # print('Default options')
            privilege_list.remove('add')
            privilege_list.remove('edit')
            privilege_list.remove('delete')

    elif entity_type == 'user':
        if 'Centrale' not in user_ranks:
            privilege_list.remove('add')
            privilege_list.remove('edit')
            privilege_list.remove('delete')
            if 'Directeur régional' not in user_ranks:
                privilege_list.remove('view')
                privilege_list.remove('list')

    elif entity_type == "action":
        if 'Centrale' in user_ranks:
            privilege_list = ['view', 'list']
        else:
            privilege_list = []

    elif entity_type == "summary":
        if len(user_ranks.intersection({'Centrale', 'Assistant DR', 'Directeur régional'})) == 0:
            privilege_list = ['view', 'list']
        else:
            privilege_list = []

    element['privileges'] = privilege_list
    return element