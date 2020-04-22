from flask import Flask, redirect, render_template, request, url_for, session
import random
from collections import OrderedDict
from SubnetGenerator import GenerateSubnets

'''
to run on the local development server, run these commands in terminal:
cd /Users/wesleyeller/github/BCOC-Tools
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
    if 'VLANList' not in session:
        session['VLANList'] = OrderedDict({'1':{'ID':1, 'Name':'Servers'}, '2':{'ID':2, 'Name':'Users'}})
        session.modified = True
    return render_template('VTPBuilder.html', SessionData=session)

@app.route('/add_vlan', methods=["GET"])
def add_vlan():
    session['VLANList'].append
