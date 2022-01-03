from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/talhas')
def talha():
    return "this is talhas rout"
    
@app.route('/about')
def intro():
    return "This is us"

@app.route('/contact')
def intro():
    return "Contact Us"

@app.route('/contact2')
def intro():
    return "Contact Us2"
@app.route('/conatact2')
def intrao():
    return "Contact Us2"