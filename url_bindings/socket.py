from datetime import datetime

from flask import request

from bindings import socket_io

from url_bindings import actions

ONLINE_USERS = {}
@socket_io.on('disconnected')
def disconnect(user):
    u = user['user']
    try:
        connection_action = actions.LogAction(u.get('id', ''), operation_type='Déconnexion', actor_ip=u.get('ip', None))
        connection_action.make_connection_statement('Disconnected')
        connection_action.insert()

        del ONLINE_USERS[u.get('id', '')]

        for c in ONLINE_USERS.keys():
            notify(f"{u['firstname'].title()} {u['lastname'].upper()} has disconnected", c)
    except:
        pass


@socket_io.on('connected')
def connect(user):
    u = user['user']
    print(u.keys())
    ONLINE_USERS[u.get('id', '')] = {"sid": request.sid}

    connection_action = actions.LogAction(u.get('id', ''), operation_type='Connexion', actor_ip=u.get('ip', None))
    connection_action.make_connection_statement('Connected')
    connection_action.insert()

    # print(connection_action)

    for c in ONLINE_USERS.keys():
        n = {
            "sender": u.get('id', 0),
            "title": "User connected",
            "timestamp": datetime.now().strftime("%a, %b %d %Y"),
            "text": f"{u['firstname'].title()} {u['lastname'].upper()} has connected"
        }
        notify(n, c)


def notify(notification, client):
    # print(ONLINE_USERS)
    # print("Client SID: ", ONLINE_USERS.get(client, ''))
    client_sid = ONLINE_USERS.get(client, '')
    if type(client_sid).__name__ == "dict":
        client_sid = client_sid.get('sid', '')

    socket_io.emit("notification", notification, room=client_sid)
    # print()