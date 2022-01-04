from logging import DEBUG
from pymysql import connections
from ModelClass import *
from flask_cors import CORS
from flask import Flask, request, jsonify, session

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'dailykidiary'

@app.route('/users',methods = ["post"])
def user_access():
    connection = Model("localhost", "root", "1234", "dailykidiary")
    email = request.form.get('email')
    password = request.form.get('pass')
    user_data = connection.login(email,password)
    if len(user_data) > 0:
        session["email"] = user_data[0]['email']
        print(session['email'])
    return jsonify(user_data)


if __name__ == '__main__':
    app.run(debug=True)
