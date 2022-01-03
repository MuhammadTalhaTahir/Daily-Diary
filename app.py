from logging import DEBUG

from pymysql import connections
import json
from ModelClass import *
from flask import Flask, request, jsonify,make_response

app = Flask(__name__)
@app.route('/users')
def user_access():
    connection = Model("localhost", "root", "1234", "dailydiary")
    email = request.args.get('email')
    password = request.args.get('pass')
    user_data = connection.login(email,password)
    print(user_data)
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(debug=True)
