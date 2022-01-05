from logging import DEBUG
from sys import modules
from pymysql import NULL, connections
from ModelClass import *
from flask_cors import CORS
from datetime import datetime
from flask import Flask, request, jsonify, session

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'dailykidiary'

@app.route('/login',methods = ["post"])
def login_user():
    connection = Model("localhost", "root", "1234", "dailykidiary")
    email = request.form.get('email')
    password = request.form.get('pass')
    user_data = connection.login(email,password)
    if len(user_data) > 0:
        session["email"] = user_data[0]['email']
        user_data[0]['user_status'] = True
    return jsonify(user_data)

@app.route('/register', methods=["POST"])
def register_user():
    connection = Model("localhost", "root", "1234", "dailykidiary")
    now = datetime.now()
    new_user = dict()
    new_list = list()
    new_user["username"] = request.form.get("fname") + " " + request.form.get("lname")
    new_user["email"] = request.form.get('email')
    new_user["user_pass"] = request.form.get('pass')
    new_user["user_status"] = True
    new_user["date_joined"] = now.strftime('%Y-%m-%d %H:%M:%S')
    new_user["dob"] = request.form.get('dob')
    new_user["gender"] = request.form.get('gen')
    new_user["location"] = request.form.get('loc')
    new_user["address"] = request.form.get('add')
    pimg = request.files['img']
    new_user["profile_picture"] = f"userProfilePics\\{pimg.filename}"
    if connection.user_exist(new_user["email"]) is False:
        connection.register(new_user)
        pimg.save(f"userProfilePics\\{pimg.filename}")
        session["email"] = new_user['email']
        new_list.append(new_user)
        return jsonify(new_list)
    return jsonify(list())

if __name__ == '__main__':
    app.run(debug=True)
    