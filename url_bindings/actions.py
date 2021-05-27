from datetime import datetime

from bson import ObjectId

from url_bindings.socket import notify
from url_bindings.users import get_roles, get_full_name
from bindings import database

actions = database['actions']
OPERATIONS = {
    "GET": "Consultation",
    "POST": "Ajout",
    "PUT": "Modification",
    "DELETE": "Suppression"
}
class LogAction:
    def __init__(self, actor_id, action="", timestamp=datetime.now(), operation_type=None, entity_type=None, entity_id=None):
        self.actor_id = actor_id
        self.action = action
        self.timestamp = timestamp

        self.operation_type = operation_type
        self.entity_type = entity_type
        self.entity_id = entity_id

    def insert(self):
        new_action = actions.insert_one({
            'actor_id': self.actor_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'operation_type': self.operation_type,
            'timestamp': self.timestamp,
            'entity_id': self.entity_id
        })
        self.id = new_action.inserted_id

        #Notify clients
        clients = get_roles(self.actor_id)
        for client in clients:
            notify(f"{get_full_name(self.actor_id)} has {self.action.lower()}", client)

        return self

    def make_statement(self, entity_type, operation_type, single_element=True, entity_id=None, additional_text=None):
        if operation_type == 'POST':
            self.action = f"Created a new {entity_type}"
            if entity_id is not None:
                self.action = self.action + f" with id {entity_id}"

        elif operation_type == 'PUT':
            self.action = f"Modified {entity_type} having the ID: {entity_id}"

        elif operation_type == 'DELETE':
            self.action = f"Deleted {entity_type} having the ID: {entity_id}"

        elif operation_type == 'GET' and single_element:
            self.action = f"Fetched {entity_type} having the ID: {entity_id}"

        else:
            self.action = f"Fetched list of {entity_type}s"

        if additional_text is not None:
            self.action = self.action + " " + str(additional_text)

        if operation_type == 'GET' and not single_element:
            self.operation_type = "Liste"
        else:
            self.operation_type = OPERATIONS[operation_type]

        self.entity_type = entity_type

        if entity_id is not None:
            self.entity_id = entity_id

        return self

# class ConnectionAction(LogAction):
    def make_connection_statement(self, operation_type, actor_ip=None):
        if operation_type.upper() == "CONNECTED":
            self.action = f"Connected on {self.timestamp}"
            if actor_ip is not None:
                self.action = self.action + f" from ip {actor_ip}"

        elif operation_type.upper() == "DISCONNECTED":
            self.action = f"Disconnected on {self.timestamp}"
            if actor_ip is not None:
                self.action = self.action + f" from ip {actor_ip}"






def serialize(a):
    try:
        actor = database['users'].find_one({'_id': ObjectId(a['actor_id'])})

        a['firstname'] = actor['firstname']
        a['lastname'] = actor['lastname']
        a['roles'] = actor['roles']
    except:
        a['firstname'] = ''
        a['lastname'] = ''
        a['roles'] = []

    a['id'] = str(a['_id'])
    del a['_id']

    a['timestamp'] = a['timestamp'].strftime('%a %b %d %Y')
    return a
