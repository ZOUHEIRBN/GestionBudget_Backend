from flask import request

from bindings import socket_io

ONLINE_USERS = {}
@socket_io.on('disconnected')
def disconnect(user):
    u = user['user']
    try:
        del ONLINE_USERS[u.get('id', '')]
        for c in ONLINE_USERS.keys():
            notify(f"{u['firstname'].title()} {u['lastname'].upper()} has disconnected", c)
    except:
        pass


@socket_io.on('connected')
def connect(user):
    u = user['user']
    ONLINE_USERS[u.get('id', '')] = request.sid
    for c in ONLINE_USERS.keys():
        notify(f"{u['firstname'].title()} {u['lastname'].upper()} has connected", c)


def notify(notification, client):
    print(ONLINE_USERS)
    print("Client SID: ", ONLINE_USERS.get(client, ''))
    socket_io.emit("notification", notification, room=ONLINE_USERS.get(client, ''))
    print()