from datetime import datetime

from bindings import database

actions = database['actions']

class LogAction:
    def __init__(self, actor_id, action, timestamp=datetime.now()):
        self.actor_id = actor_id
        self.action = action
        self.timestamp = timestamp

    def insert(self):
        new_action = actions.insert_one({
            'actor_id': self.actor_id,
            'action': self.action,
            'timestamp': self.timestamp
        })
        self.id = new_action.inserted_id
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
        return self