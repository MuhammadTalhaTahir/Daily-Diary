from flask import Flask
from flask_socketio import SocketIO,emit,send
from ModelClass import *
import json
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app, cors_allowed_origins="*")

with open('config.json') as jsondata:
    config = json.load(jsondata)


@socket.on("enterWorldChat")
def join_room(data):
    emit('userEnteredChat', data["currentUser"], broadcast=True)

@socket.on("getPrevoiusText")
def getPreviousText():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    messages = connection.get_chat()
    emit('sendPrevious', messages)

@socket.on("sendText")
def getText(data):
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    connection.update_chat(data)
    newData = connection.get_chat()
    send(newData, broadcast=True)


if __name__ == '__main__':
    socket.run(app, debug=True, port=5001)