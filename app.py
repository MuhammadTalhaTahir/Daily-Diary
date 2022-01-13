from logging import DEBUG
from sys import modules
from pymysql import NULL, connections
from ModelClass import *
from flask_cors import CORS
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask import send_file
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'dailykidiary'

with open('config.json') as jsondata:
    config = json.load(jsondata)

@app.route('/login',methods = ["post"])
def login_user():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    email = request.form.get('email')
    password = request.form.get('pass')
    user_data = connection.login(email,password)
    if len(user_data) > 0:
        session["email"] = user_data[0]['email']
        user_data[0]['user_status'] = True
        user_data[0]['profile_picture'] = str(f'http://127.0.0.1:5000/profile_picture/{user_data[0]["email"]}')
        return jsonify(user_data)
    return jsonify(list())

@app.route('/user_pages')
def user_pages():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    page_list = connection.get_pages(session['email'])
    if (bool(page_list)):
        for i in range(len(page_list)):
                if page_list[i]["content_video_pic"] != "NO-PIC":
                    page_list[i]["content_video_pic"] = str(f'http://127.0.0.1:5000/content_pic/{page_list[i]["content_video_pic"]}')
        return jsonify(page_list)
    return jsonify(list())

@app.route('/user_diary',methods = ["post"])
def user_diary():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    new_user = dict()
    now = datetime.now()
    new_user['content_video_pic'] = " "
    new_user['email'] = request.form.get("email")
    new_user['content_text'] = request.form.get('pageContent')
    if request.form.get('isFile')=="true":
        img_vid = request.files['file']
        new_user['content_video_pic'] = f"{img_vid.filename}"
        print(request.form.get("isvideo"))
        if request.form.get("isvideo") == "true":
            new_user['is_content_video'] = True
        elif request.form.get("isvideo") == "false":
            new_user['is_content_video'] = False
    elif request.form.get('isFile')=="false":
        new_user['content_video_pic'] = "NO-PIC"
        new_user['is_content_video'] = False
    new_user['page_date'] = now.strftime('%Y-%m-%d %H:%M:%S')
    new_user['visible_status'] = True
    success = connection.add_page(new_user)
    if success:
        if request.form.get('isFile')=="true":
            img_vid.save(f"user_content\\{img_vid.filename}")
        page_list = connection.get_pages(request.form.get("email"))
        for i in range(len(page_list)):
                if page_list[i]["content_video_pic"] != "NO-PIC":
                    page_list[i]["content_video_pic"] = str(f'http://127.0.0.1:5000/content_pic/{page_list[i]["content_video_pic"]}')
        return jsonify(page_list) if (bool(page_list)) else jsonify(list())
    return jsonify(list())


@app.route('/register', methods=["POST"])
def register_user():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    now = datetime.now()
    new_user = dict()
    new_user["username"] = request.form.get("fname") + " " + request.form.get("lname")
    new_user["email"] = request.form.get('email')
    new_user["user_pass"] = request.form.get('pass')
    new_user["user_status"] = True
    new_user["date_joined"] = now.strftime('%Y-%m-%d %H:%M:%S')
    new_user["dob"] = request.form.get('dob')
    new_user["gender"] = request.form.get('gender')
    new_user["location"] = request.form.get('loc')
    new_user["address"] = request.form.get('add')
    pimg = request.files['img']
    new_user["profile_picture"] = f"userProfilePics\\{pimg.filename}"
    if connection.user_exist(new_user["email"]) is False:
        connection.register(new_user)
        pimg.save(f"userProfilePics\\{pimg.filename}")
        diary = {"email":new_user["email"], "type":"public"}
        connection.add_diary(diary)
        return jsonify(list(1))
    return jsonify(list())

@app.route('/content_pic/<string:path>')
def getContentPic(path):
    path = f'user_content\{path}'
    return send_file(path)

@app.route('/logout')
def logout_user():
    session.clear()
    return jsonify(list())

@app.route('/profile_picture/<string:email>')
def profile_picture(email):
    connection = Model(config["host"], config['user'], config['password'], config['database'])
    path = connection.profile_picture(email)
    if path != "":
        return send_file(path)  #\userProfilePics\name.jpg
    return jsonify(list())

if __name__ == '__main__':
    app.run(debug=True)
    