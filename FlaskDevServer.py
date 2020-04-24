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

@app.route('/', methods=["GET",  "POST"])
def main_page():
    print('Running main page')
    if 'VLANList' not in session:
        session['VLANList'] = OrderedDict({'1':{'ID':1, 'Name':'Servers'}, '2':{'ID':2, 'Name':'Users'}})
        session.modified = True
    return render_template('VTPBuilder.html', SessionData=session)

@app.route('/add_vlan', methods=["GET", "POST"])
def add_vlan():
    #This is getting called a whole bunch of times for every click right now.
    print('Running add vlan script')
    LastID = list(session['VLANList'].keys())[-1]
    NextID = str(int(LastID)+1)
    session['VLANList'][NextID]={'ID':int(NextID), 'Name':""}
    session.modified = True
    print('Printing VLAN list...')
    print(session['VLANList'])
    return redirect(url_for('add_vlan', _anchor="end_VLAN_table"))
