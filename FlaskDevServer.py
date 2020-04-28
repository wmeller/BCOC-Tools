from flask import Flask, redirect, render_template, request, url_for, session
from collections import OrderedDict
from SubnetGenerator import GenerateSubnets
from min_subnet_size import min_subnet_size, build_compatibility_matrix
from natural_sort import natural_sort
import re
import ipaddress
from VTP_Builder_functions import *
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
            #Hard set a bunch of defaults. These are helpful for demo and debugging, and ensuring I don't start off with blanks I don't want.
            print('Setting Defaults...')
            session['UserMsg'] = False
            session['VTP_Printout_Flag'] = False
            session['VLANList'] = {'1':{'ID':1, 'Name':'Servers'}, '2':{'ID':2, 'Name':'Users'}}
            session[''] = {'StartAddress':'192.168.0.0', 'TotalSize':'/24'}
            session['VTP_DB'] = {'1':{'ID':1, 'DomainName':'Tech1', 'Type':'Core', 'VLANData':{}}, '2':{'ID':2, 'DomainName':'COC', 'Type':'Core', 'VLANData':{}}}
            for VTPID in session['VTP_DB'].keys():
                for VLAN in session['VLANList'].keys():
                    session['VTP_DB'][VTPID]['VLANData'][VLAN] = {'ID':session['VLANList'][VLAN]['ID'], 'Name':session['VLANList'][VLAN]['Name'], 'Hosts':0, 'StartAddress':'', 'Size':''}
            session.modified = True
        return render_template('VTPBuilder.html', SessionData=session)
    print('POST!!!')
    #Set messages to False so that old messages don't pop up.
    session['UserMsg'] = False
    if any(['add_vlan' in x for x in request.form.keys()]):
        #Right now, for some reason, the session is getting ASCII sorted when it is handed off to the html. I'll have to figure that out later.
        print('add VLAN function')
        #Save the VLAN table first
        session['VLANList']=Save_VLAN_DB(request.form, session['VLANList'])
        #Now modify the table to add a new line.
        LastID = natural_sort(list(session['VLANList'].keys()))[-1]
        NextID = str(int(LastID)+1)
        session['VLANList'][NextID]={'ID':int(NextID), 'Name':""}
        session['VTP_DB'] = Update_VTP_DB_VLAN_data(session, request.form)
        session.modified = True
        return redirect(url_for('vtp_build'))
    elif any(['save_vlan' in x for x in request.form.keys()]):
        #Save the vlan database
        print('Save VLAN DB function')
        session['VLANList']=Save_VLAN_DB(request.form, session['VLANList'])
        session['VTP_DB'] = Update_VTP_DB_VLAN_data(session, request.form)
        session.modified = True
        return redirect(url_for('vtp_build'))
    elif any(['DEL_ID' in x for x in request.form.keys()]):
        #Delete the requested VLAN
        ## TODO:  a popup confirmation that the deletion is desired.
        ## TODO: add 'unsaved changes' checkmark or reminder or something
        print('Delete function')
        #Save the VLAN table first
        session['VLANList']=Save_VLAN_DB(request.form, session['VLANList'])
        #Find the ID of the VLAN we want to delete
        for key in request.form.keys():
            if 'DEL_ID' in key:
                DeletionIndex = key.split(':')[1]
                print('DeletionIndex: '+DeletionIndex)
                break
        del session['VLANList'][DeletionIndex]
        session.modified = True
        return redirect(url_for('vtp_build'))
    elif any(['save_vtp' in x for x in request.form.keys()]):
        #Save VTP Configuration
        print('Save VTP Config function')
        [session['VTP_Config'], session['UserMsg']] = Save_VTP_Config(session['VTP_Config'], request.form)
        session.modified = True
        print(session['VTP_Config'])
        print(session['UserMsg'])
        return redirect(url_for('vtp_build'))
    elif any(['add_vtp' in x for x in request.form.keys()]):
        #Add VTP to Table
        #Save the VTP table first
        session['VTP_DB'] = Update_VTP_DB_VLAN_data(session, request.form)
        #Now modify the table to add a new line.
        LastID = natural_sort(list(session['VTP_DB'].keys()))[-1]
        NextID = str(int(LastID)+1)
        session['VTP_DB'][NextID]={'ID':int(NextID), 'DomainName':'New', 'Type':'Core', 'VLANData':{}}
        session['VTP_DB'] = Update_VTP_DB_VLAN_data(session, request.form)
        session.modified = True
        return redirect(url_for('vtp_build', _anchor="vtp_config_anchor"))
    elif any(['DEL_VTP' in x for x in request.form.keys()]):
        #Delete the requested VLAN
        ## TODO:  a popup confirmation that the deletion is desired.
        ## TODO: add 'unsaved changes' checkmark or reminder or something
        print('Delete VTP function')
        #Save the VTP table first
        session['VTP_DB'] = Update_VTP_DB_VLAN_data(session, request.form)
        #Find the ID of the VTP we want to delete
        for key in request.form.keys():
            if 'DEL_VTP' in key:
                DeletionIndex = key.split(':')[1]
                print('DeletionIndex: '+DeletionIndex)
                break
        del session['VTP_DB'][DeletionIndex]
        session.modified = True
        return redirect(url_for('vtp_build', _anchor="vtp_config_anchor"))
    elif any(['save_and_update_vtp' in x for x in request.form.keys()]):
        #Save all the data from the VTP forms and update all the addresses and sizes. Clear the generated text blocks
        [session['VTP_Config'], session['UserMsg']] = Save_VTP_Config(session['VTP_Config'], request.form)
        session['VTP_DB'], session['UserMsg'] = Update_VTP_DB_Config(session, request.form)
        if session['UserMsg'] is not False:
            session['UserMsg'] = ' '.join(session['UserMsg'])
        print(session['UserMsg'])
        session.modified=True
        return redirect(url_for('vtp_build', _anchor="vtp_config_anchor"))
    elif any(['gen_vtp_db' in x for x in request.form.keys()]):
        #Generate the text blocks for direct copy and pasting into a LAN network diagram
        [session['VTP_Config'], UserMsg] = Save_VTP_Config(session['VTP_Config'], request.form)
        if UserMsg is not False:
            session['UserMsg'] = ' '.join(UserMsg)
        session['VTP_DB'], UserMsg = Update_VTP_DB_Config(session, request.form)
        if UserMsg is not False:
            session['UserMsg'] = ' '.join(UserMsg)
        session['VTP_DB'], UserMsg = Update_VTP_DB_Config(session, request.form)
        if UserMsg is not False:
            session['UserMsg'] = ' '.join(UserMsg)
        session['VTP_DB'] = Generate_Diagram_Text(session['VTP_DB'])
        session['VTP_Printout_Flag']=True
        session.modified=True
        return redirect(url_for('vtp_build', _anchor="vtp_printout"))
    else:
        print('Whatever you just clicked, it doesnt do anything.')
        return redirect(url_for('vtp_build'))
