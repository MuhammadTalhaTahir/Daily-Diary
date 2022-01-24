from ModelClass import *
from flask_cors import CORS
from datetime import datetime
from flask import Flask, request, jsonify, session, redirect
from flask import send_file
import json
import random
from flask_mail import Mail, Message 

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dailykidiary@gmail.com'
app.config['MAIL_PASSWORD'] = 'dkd12345678'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.secret_key = 'dailykidiary'
mail = Mail(app)

with open('config.json') as jsondata:
    config = json.load(jsondata)

@app.route('/login',methods = ["post"])
def login_user():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    email = request.form.get('email')
    password = request.form.get('pass')
    user_data = connection.login(email,password)
    if len(user_data) > 0:
        user_data[0]['user_status'] = True
        user_data[0]['profile_picture'] = str(f'http://127.0.0.1:5000/profile_picture/{user_data[0]["email"]}')
        return jsonify(user_data)
    return jsonify(list())

@app.route('/user_pages',methods = ["post"])
def user_pages():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    page_list = connection.get_pages(request.form.get('email'))
    if (bool(page_list)):
        for i in range(len(page_list)):
                if page_list[i]["content_video_pic"] != "NO-PIC":
                    page_list[i]["content_video_pic"] = str(f'http://127.0.0.1:5000/content_pic/{page_list[i]["content_video_pic"]}')
        return jsonify(page_list)
    return jsonify(list())

@app.route('/public_pages',methods = ["post"])
def public_pages():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    page_list = connection.get_explore_pages(request.form.get('email'))
    if (page_list):
        for i in page_list:
            if(bool(i)):
                if i["content_video_pic"] != "NO-PIC":
                    i["content_video_pic"] = str(f'http://127.0.0.1:5000/content_pic/{i["content_video_pic"]}')
        random.shuffle(page_list)
        return jsonify(page_list)
    return jsonify(list())

@app.route('/follower_pages',methods = ["post"])
def follower_pages():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    page_list = connection.get_follower_pages(request.form.get('email'))
    if (page_list):
        for i in page_list:
            if(bool(i)):
                if i["content_video_pic"] != "NO-PIC":
                    i["content_video_pic"] = str(f'http://127.0.0.1:5000/content_pic/{i["content_video_pic"]}')
        random.shuffle(page_list)
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
        if request.form.get("isvideo") == "true":
            new_user['is_content_video'] = True
        elif request.form.get("isvideo") == "false":
            new_user['is_content_video'] = False
    elif request.form.get('isFile')=="false":
        new_user['content_video_pic'] = "NO-PIC"
        new_user['is_content_video'] = False
    new_user['page_date'] = now.strftime('%Y-%m-%d %H:%M:%S')
    if request.form.get("isPublic") == "true":
        new_user['visible_status'] = True
    else:
        new_user['visible_status'] = False
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
    new_user["user_status"] = False
    new_user["date_joined"] = now.strftime('%Y-%m-%d %H:%M:%S')
    new_user["dob"] = request.form.get('dob')
    new_user["gender"] = request.form.get('gender')
    new_user["user_key"] = random.randint(1,100)
    new_user["location"] = request.form.get('loc')
    new_user["address"] = request.form.get('add')
    pimg = request.files['img']
    new_user["profile_picture"] = f"userProfilePics\\{pimg.filename}"
    if connection.user_exist(new_user["email"]) is False:
        connection.register(new_user)
        pimg.save(f"userProfilePics\\{pimg.filename}")
        diary = {"email":new_user["email"], "type":"public"}
        connection.add_diary(diary)
        url = "'https://raw.githubusercontent.com/MuhammadTalhaTahir/Daily-Diary/b2a4bcfd064602aae20b58daa8c32f19bd6cefbd/i-like-food.svg'"
        msg = Message('Email Verification', sender = 'dailykidiary@gmail.com', recipients = [new_user["email"]])
        authenticationLink = f'http://127.0.0.1:5000/verify_email/{new_user["user_key"]}/{new_user["email"]}'
        msg.html = f'<div style="background-color: #221e1e; border-radius: 20px; color: wheat; font-family: Tahoma, Verdana, sans-serif; padding: 10px;"><h1 style="text-align: center;"><strong>ٱلسَّلَامُ عَلَيْكُمْ <br /></strong></h1><h2 style="text-align: center;"><span style="color: brown;"> {new_user["username"]} </span></h2><hr/><p>Welcome to Daily کی Diary 📖📕, before being able to use your account you need to verify that this is your email address by clicking here: {authenticationLink}</p><p style="text-align: left;"><span style="color: brown;">If you do not recognize this activity simply ignore this mail.&nbsp;</span></p><p>Kind Regards,<br /><span style="color: brown;"><strong>Daily کی Diary</strong></span></p></div>'
        mail.send(msg)
        return jsonify([1])
    return jsonify(list())

@app.route('/edit_profile', methods=["POST"])
def edit():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    edit_user = dict()
    edit_user["username"] = request.form.get("fname") + " " + request.form.get("lname")
    edit_user["email"] = request.form.get('email')
    edit_user["user_pass"] = request.form.get('pass')
    if request.files.get("img") is None:
        pimg = "NO-PIC"
    else:
        pimg = request.files['img']
    if pimg != "NO-PIC":
        edit_user["profile_picture"] = f"userProfilePics\\{pimg.filename}"
    else:
        edit_user["profile_picture"] = pimg
    if connection.user_exist(edit_user['email']):
        if connection.editProfile(edit_user):
            if pimg != "NO-PIC":
                pimg.save(f"userProfilePics\\{pimg.filename}")
            user_data = connection.login(edit_user['email'],edit_user['user_pass'])
            if len(user_data) > 0:
                user_data[0]['user_status'] = True
                user_data[0]['profile_picture'] = str(f'http://127.0.0.1:5000/profile_picture/{user_data[0]["email"]}')
                return jsonify(user_data)
            return jsonify(list())

@app.route('/verify_email/<int:key>/<string:email>')
def verify(key,email):
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    success = connection.confirmation(key,email)
    print("Verified: ", success)
    return redirect("http://localhost:3000/")

@app.route('/search', methods=["POST"])
def search_user():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    name = request.form.get("name")
    email = request.form.get("email")
    users = connection.search_user(name,email)
    return jsonify(users) if (bool(users)) else jsonify(list())

@app.route('/follow', methods=["POST"])
def follow_user():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    user = request.form.get("email")
    followed_user = request.form.get("femail")
    flag = connection.add_follower(user,followed_user)
    return jsonify([flag]) if (flag!=None) else jsonify(["Failed"])

@app.route('/get_followers', methods=["POST"])
def get_followers():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    user = request.form.get("email")
    followers_data = connection.get_followers(user)
    return jsonify(followers_data) if (followers_data) else jsonify(list())

@app.route('/liked', methods=["POST"])
def liked_page():
    connection = Model(config['host'], config['user'], config['password'], config['database'])
    now = datetime.now()
    interaction = dict()
    interaction["email"] = request.form.get("email")
    interaction["page_id"] = request.form.get("page_id")
    interaction["date"] = now.strftime('%Y-%m-%d %H:%M:%S')
    followers = connection.set_like(interaction)
    return jsonify([1]) if (followers) else jsonify(list())

@app.route('/profile_picture/<string:email>')
def profile_picture(email):
    connection = Model(config["host"], config['user'], config['password'], config['database'])
    path = connection.profile_picture(email)
    if path != "":
        return send_file(path)  
    return jsonify(list())

@app.route('/content_pic/<string:path>')
def getContentPic(path):
    path = f'user_content\{path}'
    return send_file(path)

if __name__ == '__main__':
    app.run(debug=True)
    