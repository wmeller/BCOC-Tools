from flask import Flask, redirect, render_template, request, url_for, session
from collections import OrderedDict
from SubnetGenerator import GenerateSubnets
from natural_sort import natural_sort
import re
import ipaddress
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
            #Hard set a bunch of defaults. These are helpful for demo and debugging, and ensuring I don't start off with blanks I don't want.
            print('Setting Defaults...')
            session['UserMsg'] = False
            session['ErrorMsg'] = False
            session['VLANList'] = {'1':{'ID':1, 'Name':'Servers'}, '2':{'ID':2, 'Name':'Users'}}
            session[''] = {'StartAddress':'192.168.0.0', 'TotalSize':'/24'}
            session['VTP_DB'] = {'1':{'ID':1, 'DomainName':'Tech1', 'VLANData':{}}, '2':{'ID':2, 'DomainName':'COC', 'VLANData':{}}}
            for VTPID in session['VTP_DB'].keys():
                for VLAN in session['VLANList'].keys():
                    session['VTP_DB'][VTPID]['VLANData'][VLAN] = {'ID':session['VLANList'][VLAN]['ID'], 'Name':session['VLANList'][VLAN]['Name'], 'Hosts':0, 'StartAddress':'', 'Size':''}
            session.modified = True
        return render_template('VTPBuilder.html', SessionData=session)
    print('POST!!!')
    #Set messages to False so that old messages don't pop up.
    session['UserMsg'] = False
    session['ErrorMsg'] = False
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
        session['VTP_DB'][NextID]={'ID':int(NextID), 'DomainName':'New', 'VLANData':{}}
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
        session['VTP_DB'] = Update_VTP_DB_Config(session['VTP_Config'], request.form)
        return redirect(url_for('vtp_build'))
    elif any(['gen_vtp_db' in x for x in request.form.keys()]):
        #Generate the text blocks for direct copy and pasting into a LAN network diagram
        return redirect(url_for('vtp_build'))
    else:
        print('Whatever you just clicked, it doesnt do anything.')
        return redirect(url_for('vtp_build'))


######################################################################
#################          Functions                ##################
######################################################################
def Save_VLAN_DB(SessionData, VLANDB):
    #This function saves modifications to the vlan table. Right now it is called by clicking save, but it could really also be called asynchronously on typing in the text boxes too.
    for key in SessionData.keys():
        if 'ID_NUM' in key:
            RelID = key.split(':')[1]
            VLANDB[RelID]['ID'] = SessionData[key]
        elif 'NAME' in key:
            RelID = key.split(':')[1]
            VLANDB[RelID]['Name'] = SessionData[key]

    return VLANDB

def Save_VTP_Config(SessionData, FormData):
    #Get the set IP address and size, then error check them to make sure they are the expected type.
    UserMsg = False
    StartAddress = FormData['StartAddress']
    StartAddress = StartAddress.strip()
    Size = FormData['TotalSize']
    Size = Size.strip()
    SessionData['StartAddress']=StartAddress
    SessionData['TotalSize']=Size
    r = re.compile('^/\d*$')
    if r.match(Size) is None:
        print("Check the format of the subnet size: should be format /xx between 23 and 31")
        return  SessionData, "Check the format of the start size: should be format /xx between 23 and 31"
    if int(Size[1:]) > 31:
        print("Check the size of the start subnet: should be format /xx between 23 and 31")
        return SessionData, "Check the size of the start subnet: should be format /xx between 23 and 31"
    try:
        ipaddress.ip_address(StartAddress)
    except:
        print("check the format of the starting address: should be xxx.xxx.xxx.xxx")
        return SessionData, "Check the format of the starting address: should be xxx.xxx.xxx.xxx Every octet should be between 0-255"
    try:
        ipaddress.ip_network(StartAddress+Size)
    except:
        print("For the network size "+Size+", the starting address "+StartAddress+" is not valid")
        return SessionData,"For the network size "+Size+", the starting address "+StartAddress+" is not valid"
    #Ok, everything is good to go. Save the configuration.
    return  SessionData, UserMsg

def Update_VTP_DB_VLAN_data(SessionData, FormData):
    #Update the VTP database with new vlan information
    for VTPID in SessionData['VTP_DB'].keys():
        for VLAN in SessionData['VLANList'].keys():
            if not VLAN in SessionData['VTP_DB'][VTPID]['VLANData'].keys():
                #If this is a new VLAN, just set a bunch of defaults
                SessionData['VTP_DB'][VTPID]['VLANData'][VLAN] = {'ID':SessionData['VLANList'][VLAN]['ID'], 'Name':SessionData['VLANList'][VLAN]['Name'], 'Hosts':0, 'StartAddress':'', 'Size':''}
            else:
                #IF this is a previously known VLAN, just update the parts that might have changed.
                SessionData['VTP_DB'][VTPID]['VLANData'][VLAN]['ID'] = SessionData['VLANList'][VLAN]['ID']
                SessionData['VTP_DB'][VTPID]['VLANData'][VLAN]['Name'] = SessionData['VLANList'][VLAN]['Name']
    return SessionData['VTP_DB']

def Update_VTP_DB_Config(SessionData, FormData):
    #Gather all the updates to the VTP databases.
    #Inputs are Domain names and hosts
    #Knowns are the VLAN data for each VTP database
    #Output is updating the VTP configuration panels with the domain names, start addresses and subnet sizes
    #TODO: only check databases which are showing unedited changes?

    #Loop through all the form data and update the corresponding trash
    for key in FormData:
        if "DOMAIN_VTPID" in key:
            ID = key.split(':')[1]
            SessionData[ID]['DomainName'] = FormData[key]
        elif "HOSTVALUE_VTPID" in key:
            VTP_ID = key.split(':')[1]
            VLAN_ID = key.split(':')[3]
            SessionData[VTP_ID]['VLANData'][VLAN_ID]['Hosts']=FormData[key]
    #Create the requirements table for the Hosts

    #Do the function calls to get the addresses I want to show

    #Populate the tables.
    return SessionData['VTP_DB']
