from flask import Flask, redirect, render_template, request, url_for, session
import random
from collections import OrderedDict
from SubnetGenerator import GenerateSubnets
from natural_sort import natural_sort
import pdb
'''
to run on the local OSX development server, run these commands in terminal:
cd /Users/wesleyeller/github/BCOC-Tools
export FLASK_ENV=development
export FLASK_APP=FlaskDevServer.py
flask run

to run on the local Windows development server, run these commands in terminal:
cd C:\\Users\\wmell_000\\Desktop\\BCOC-Tools
set FLASK_ENV=development
set FLASK_DEBUG = 1
set FLASK_APP=FlaskDevServer.py
flask run
'''

UPLOAD_FOLDER = '/home/Weller/mysite/uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

app = Flask(__name__)
app.config["SECRET_KEY"] = '6d5sf4sa65f4as65f'

@app.route('/', methods=["GET"])
def main_page():
    return 'You bounced to the index page'

@app.route('/vtp_builder', methods=["GET",  "POST"])
def vtp_build():
    if request.method=='GET':
        print('Running main page')
        if 'VLANList' not in session:
            session['VLANList'] = OrderedDict({'1':{'ID':1, 'Name':'Servers'}, '2':{'ID':2, 'Name':'Users'}})
            session.modified = True
        return render_template('VTPBuilder.html', SessionData=session)
    print('POST!!!')
    #pdb.set_trace()
    if 'add_vlan' in request.form:
        LastID = natural_sort(list(session['VLANList'].keys()))[-1]
        NextID = str(int(LastID)+1)
        session['VLANList'][NextID]={'ID':int(NextID), 'Name':""}
        session.modified = True
        print(session['VLANList'])
        return redirect(url_for('vtp_build'))
    else:
        return redirect(url_for('vtp_build'))
