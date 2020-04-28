from SubnetGenerator import GenerateSubnets
from min_subnet_size import min_subnet_size, build_compatibility_matrix
from natural_sort import natural_sort
import re
import ipaddress

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
    RequiredNetsList = []
    UserMsg = False
    for VTP_ID in SessionData['VTP_DB'].keys():
        SessionData['VTP_DB'][VTP_ID]['Type']='Distribution'
    #Loop through all the form data and update the corresponding trash
    for FormKey in FormData.keys():
        if "DOMAIN_VTPID" in FormKey:
            ID = FormKey.split(':')[1]
            SessionData['VTP_DB'][ID]['DomainName'] = FormData[FormKey]
        elif 'VTP_TYPE' in FormKey:
            VTP_ID = FormKey.split(':')[1]
            if FormData[FormKey] == 'on':
                SessionData['VTP_DB'][VTP_ID]['Type'] = 'Core'
            else:
                SessionData['VTP_DB'][VTP_ID]['Type'] = 'Distribution'
        elif "HOSTVALUE_VTPID" in FormKey:
            VTP_ID = FormKey.split(':')[1]
            VLAN_ID = FormKey.split(':')[3]
            SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['Hosts'] = FormData[FormKey]
            SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['Size'] = min_subnet_size(FormData[FormKey])
            if SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['Size'] is not None:
                RequiredNetsList.append(SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['Size'])
    #Build the requirements matrix for pulling addresses from the SubnetGenerator function
    RequirementsMatrix = build_compatibility_matrix(RequiredNetsList)
    #Do the function calls to get the addresses I want to show
    StartAddress = SessionData['VTP_Config']['StartAddress']
    Size = SessionData['VTP_Config']['TotalSize']
    IPRecord, UserMsg = GenerateSubnets(StartAddress, Size, RequirementsMatrix)
    print(IPRecord)
    #Populate the tables.
    for VLAN_ID in SessionData['VLANList'].keys():
        for VTP_ID in SessionData['VTP_DB']:
            SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['StartAddress'] = 'Not Assigned'
            Size = SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['Size']
            if Size is None:
                continue
            #Get the next entry in the IPRecord which matches the size we want.
            for record in IPRecord:
                if 'Used' in IPRecord[record].keys() or record == 'Reserve':
                    continue
                if IPRecord[record]['Size'] == Size[1:]:
                    SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['StartAddress'] = str(IPRecord[record]['NetworkAddress'])
                    #MARK the record as used
                    IPRecord[record]['Used']=True
                    print('Assigning '+record+' to VTP '+SessionData['VTP_DB'][VTP_ID]['DomainName']+' VLAN '+SessionData['VTP_DB'][VTP_ID]['VLANData'][VLAN_ID]['Name'])
                    break
    return SessionData['VTP_DB'], UserMsg

def Generate_Diagram_Text(SessionData):
    core_counter = 1
    dist_counter = 1
    for VTP in SessionData:
        SessionData[VTP]['TextTable'] = []
        if SessionData[VTP]['Type'] == 'Core':
            SessionData[VTP]['TextTable'].append('GSCS'+str(core_counter)+' VLAN DATABASE')
            core_counter += 1
        else:
            SessionData[VTP]['TextTable'].append('GSDS'+str(dist_counter)+' VLAN DATABASE')
            dist_counter += 1
        SessionData[VTP]['TextTable'].append('VTP SERVER')
        SessionData[VTP]['TextTable'].append('VTP DOMAIN: '+SessionData[VTP]['DomainName'])
        SessionData[VTP]['TextTable'].append("break")
        for VLAN in SessionData[VTP]['VLANData']:
            if SessionData[VTP]['VLANData'][VLAN]['Size'] is None:
                continue
            else:
                SessionData[VTP]['TextTable'].append('VLAN '+SessionData[VTP]['VLANData'][VLAN]['ID']+':    '+SessionData[VTP]['VLANData'][VLAN]['Name']+"      "+SessionData[VTP]['VLANData'][VLAN]['StartAddress']+" "+SessionData[VTP]['VLANData'][VLAN]['Size'])
        print(SessionData[VTP]['TextTable'])
    return SessionData
