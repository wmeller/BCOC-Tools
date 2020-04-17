import re
import ipaddress


def GenerateSubnets(StartAddress, Size, ReqMatrix):
    UserMsg = None
    # Given a start address, a subnet and a list of requirements, determine the start and end addresses of each of the resulting subnets as well as the address block in reserve.
    # Check that the inputs are correctly formatted
    StartAddress = StartAddress.strip()
    Size = Size.strip()
    r = re.compile('^/\d*$')
    if r.match(Size) is None:
        print("Check the format of the subnet size: should be format /xx between 23 and 31")
        return "Check the format of the start size: should be format /xx between 23 and 31"
    if int(Size[1:]) > 31:
        print("Check the size of the start subnet: should be format /xx between 23 and 31")
        return "Check the size of the start subnet: should be format /xx between 23 and 31"
    SubnetCIDR = int(Size[1:])
    r = re.compile('^\d*.\d*.\d*.\d*$')
    if r.match(StartAddress) is None:
        print("check the format of the starting address: should be xxx.xxx.xxx.xxx")
        return "check the format of the starting address: should be xxx.xxx.xxx.xxx"
    # Get octets from start address
    StartAddressOcts = StartAddress.split('.')
    # Check that the address is valid
    if any([int(x) > 255 for x in StartAddressOcts]):
        print("Check starting address. No octet can be larger then 255.")
        return "Check starting address. No octet can be larger then 255."
    StartAddressIP = ipaddress.ip_address(StartAddress)
    TotalSize = 2**(32 - int(Size[1:])) - 1
    EndAddressIP = StartAddressIP + TotalSize
    # A list of the octets in binary for display
    StartAddressOcts = [bin(int(x))[2:].zfill(8) for x in StartAddressOcts]
    print("Start Address Binary: " + ".".join(StartAddressOcts))
    # A list of the octets in binary for display
    BinSubnetMask = ''.zfill(32 - SubnetCIDR).rjust(32, '1')
    print("Subnet Mask: " + BinSubnetMask)
    # Loop through the requirements matrix and start generating the output subnet matrix.
    SubnetMatrix = {}
    CurrentAddress = StartAddressIP
    counter = 1
    for SubSize in ReqMatrix:
        # Check if there is a requirement for this size of subnet. If not, move on.
        if ReqMatrix[SubSize] == 0:
            continue
        else:
            # If there is a requirement, loop through the subnetting process until we have met the requirement or run out of space.
            for k in range(ReqMatrix[SubSize]):
                TrueSize = 2**(32 - int(SubSize[1:])) - 1
                RecordName = 'Record' + str(counter)
                BroadcastAddress = CurrentAddress + TrueSize
                # Check if we are exceeding the alotted IP space
                if BroadcastAddress > EndAddressIP:
                    print('Cannot accomodate ' + SubSize +' requested in row ' + str(counter))
                    print('Exceeded IP address Space.')
                    if UserMsg is None:
                        UserMsg = ['Cannot accomodate all requested subnets. Did not include:']
                        UserMsg.append(' /'+SubSize[1:])
                    UserMsg.append(', /'+SubSize[1:])
                    counter += 1
                    continue
                SubnetMatrix[RecordName] = {
                    'Size': SubSize[1:], 'NetworkAddress': CurrentAddress, 'BroadcastAddress': BroadcastAddress}
                counter += 1
                CurrentAddress = BroadcastAddress + 1
        # Determine reserve ip's
        if CurrentAddress < EndAddressIP:
            SubnetMatrix['Reserve'] = {
                'StartAddress': CurrentAddress, 'EndAddress': EndAddressIP}
    return SubnetMatrix, UserMsg


if __name__ == '__main__':
    # Test inputs. Only used when running this script stand alone.
    StartAddress = '200.200.200.2'
    Size = '/23'
    ReqMatrix = {'S24': 6, 'S25': 1, 'S26': 0, 'S27': 0,
                 'S28': 0, 'S29': 0, 'S30': 0, 'S31': 2}
    IPRecord, UserMsg = GenerateSubnets(StartAddress, Size, ReqMatrix)
    print(''.join(UserMsg))
    print(IPRecord)
