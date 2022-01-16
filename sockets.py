from flask import Flask
from flask_socketio import SocketIO,emit
from ModelClass import *
import json
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app, cors_allowed_origins="*")

with open('config.json') as jsondata:
    config = json.load(jsondata)


@socket.on("enterWorldChat")
def join_room(data):
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    messages = connection.get_chat()
    emit('userEnteredChat', list(data["currentUser"],messages), broadcast=True)

@socket.on("sendText")
def getText(data):
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    connection.update_chat(data)
    emit("recieveText", data, broadcast=True)


if __name__ == '__main__':
    socket.run(app, debug=True, port=5001)