import re
import ipaddress

def GenerateSubnets(StartAddress, Size, ReqMatrix):
    #Given a start address, a subnet and a list of requirements, determine the start and end addresses of each of the resulting subnets as well as the address block in reserve.
    #Check that the inputs are correctly formatted
    r = re.compile('/\d*')
    if r.match(Size) is None or int(Size[1:]) > 31:
        print("Check the size of the start subnet: should be format /xx between 1 and 31")
        return
    SubnetCIDR = int(Size[1:])
    r = re.compile('\d*.\d*.\d*.\d*')
    if r.match(StartAddress) is None:
        print("check the format of the starting address: should be xxx.xxx.xxx.xxx")
        return
    #Get octets from start address
    StartAddressOcts = StartAddress.split('.')
    #Check that the address is valid
    if any([int(x)>255 for x in StartAddressOcts]):
        print("Check starting address. No octet can be larger then 255.")
        return
    StartAddressIP = ipaddress.ip_address(StartAddress)
    TotalSize = 2**(32-int(Size[1:]))
    EndAddressIP = StartAddressIP + TotalSize
    #A list of the octets in binary for display
    StartAddressOcts = [bin(int(x))[2:].zfill(8) for x in StartAddressOcts]
    print("Start Address Binary: "+".".join(StartAddressOcts))
    #A list of the octets in binary for display
    BinSubnetMask = ''.zfill(32-SubnetCIDR).rjust(32, '1')
    print("Subnet Mask: "+BinSubnetMask)
    #Loop through the requirements matrix and start generating the output subnet matrix.
    SubnetMatrix = {}
    CurrentAddress = StartAddressIP;
    for SubSize in ReqMatrix:
        #Check if there is a requirement for this size of subnet. If not, move on.
        if ReqMatrix[SubSize] == 0:
            continue
        else:
            counter = 0
            TrueSize = 2**(32-int(SubSize[1:]))
            RecordName = 'Record'+str(counter)
            SubnetMatrix[RecordName] = {'Size':SubSize, 'NetworkAddress':CurrentAddress, 'BroadcastAddress':CurrentAddress+TrueSize}
            counter += 1
    return (SubnetMatrix)

if __name__ == '__main__':
    #Initial inputs. These will be replaced with hooks to web inputs in the future
    StartAddress = '200.120.177.0'
    Size = '/24'
    ReqMatrix = {'S24':0, 'S25':1, 'S26':0, 'S27':0, 'S28':0, 'S29':0, 'S30':0, 'S31':0}
    IPRecord = GenerateSubnets(StartAddress, Size, ReqMatrix)
    print(IPRecord)