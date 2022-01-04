from logging import DEBUG
from pymysql import connections
from ModelClass import *
from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/users',methods = ["post"])
def user_access():
    connection = Model("localhost", "root", "1234", "dailykidiary")
    email = request.form.get('email')
    password = request.form.get('pass')
    user_data = connection.login(email,password)
    return jsonify(user_data)


if __name__ == '__main__':
    app.run(debug=True)
