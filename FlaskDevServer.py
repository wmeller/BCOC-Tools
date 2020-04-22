from flask import Flask, redirect, render_template, request, url_for, session
import random
from SubnetGenerator import GenerateSubnets

'''
to run the development server, run these commands in terminal:
export FLASK_ENV=development
export FLASK_APP=FlaskDevServer.py
flask run
'''
UPLOAD_FOLDER = '/home/Weller/mysite/uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

app = Flask(__name__)
app.config["SECRET_KEY"] = '6d5sf4sa65f4as65f'

@app.route('/', methods=["GET"])
def main_page():
    return 'Hello World!'
