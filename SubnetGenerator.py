import re
import ipaddress

class Subnet:
    Name = ''
    Size = ''
    StartAddress = ipaddress.IpV4Address('0.0.0.0')
    NetworkAddress = '0.0.0.0'
    BroadcastAddress = '0.0.0.0'

    def CalcCharacteristics(self):
        #Check that the size and start address have been set correctly
        r = re.compile('/\d*')
        if re.match(self.Size) is none or int(self.Size[1:]) > 31: return "Check the size of the start subnet: should be format /xx between 1 and 31"
        SubnetCIDR = int(self.Size[1:])
        r = re.compile('\d*.\d*.\d*.\d*')
        if re.match(self.StartAddress) is none: return "check the format of the starting address: should be xxx.xxx.xxx.xxx"
        #Get octets from start address
        StartAddressOcts = self.StartAddress.split('.')
        #Check that the address is valid
        if any([int(x)>255 for x in StartAddressOcts]): return "Check starting address. No octet can be larger then 255."
        StartAddressOcts = [bin(int(x))[2:].zfill(8) for x in StartAddressOcts]
        BinSubnetMask = ''.zfill(32-SubnetCIDR).rjust(32, '1')
        self.NetworkAddress = self.StartAddress
        self.BroadcastAddress =
