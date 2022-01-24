from flask import Flask
from flask_socketio import SocketIO,emit,send, join_room, leave_room
from ModelClass import *
import json
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app, cors_allowed_origins="*")

with open('config.json') as jsondata:
    config = json.load(jsondata)


@socket.on("enterWorldChat")
def enteredWorldChat(data):
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
    
#connect people  
@socket.on("updateText")
def updateText(data):
    send(data, broadcast=True, to=data["room"])

@socket.on("joinRoom")
def joinRoom(data):
    join_room(data["roomID"])

@socket.on("leaveRoom")
def leaveRoom(data):
    leave_room(data["roomID"])

if __name__ == '__main__':
    socket.run(app, debug=True, port=5001)