'''
These are helper functions for network design. min_subnet_size determines the smallest class C network which will support the number of hosts specified as an input.
It will work when passed in a list of host requirements, or a single number.
It uses the equation network_size = rounddown(32-ln(hosts_needed+2)/ln(2))
returns size in CIDR notation. Smallest network is a /30. largest network is unbounded, can return a negative (nonsensical) solution.
'''
import math
import sys
from SubnetGenerator import GenerateSubnets
def min_subnet_size(hosts_needed):
    if type(hosts_needed) is list:
        if not all([type(x) is int for x in hosts_needed]):
            return 'Error:List input must be list of ints'
        return [min_size_fx(x) for x in hosts_needed]
    elif type(hosts_needed) is str or type(hosts_needed) is int:
        try:
            hosts_needed = int(hosts_needed)
        except ValueError:
            return 'passed in string is not a number'
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        min_size = min_size_fx(hosts_needed)
        return min_size
    else:
        return 'Error:Input must be list, str or int'

def min_size_fx(hosts_needed):
    '''
    returns size in CIDR notation
    '''
    if hosts_needed == 0:
        return None
    size = 32-(math.log(hosts_needed+2))/math.log(2)
    size = math.floor(size)
    if size > 30:
        size = 30
    return '/'+str(size)

def build_compatibility_matrix(nets_needed):
    ReqMatrix = {'S24': 0, 'S25': 0, 'S26': 0, 'S27': 0,
                 'S28': 0, 'S29': 0, 'S30': 0, 'S31': 0}
    if type(nets_needed) is list:
        for net in nets_needed:
            ReqMatrix['S'+net[1:]] = ReqMatrix['S'+net[1:]] + 1
        return ReqMatrix
    elif type(nets_needed) is str:
        if int(nets_needed[1:]) < 24:
            return ('net size required exceeds Class C network')
        ReqMatrix['S'+nets_needed[1:]] = 1
    else:
        return 'Error:Input must be list or str in format /xx or Sxx'

if __name__ == '__main__':
    print('Running tests')
    print('string test')
    print(min_subnet_size('3'))
    print('bad string test')
    print(min_subnet_size('a'))
    print('int test')
    print(min_subnet_size(100))
    print('bad list test')
    print(min_subnet_size(['12', '38']))
    print('good list test')
    nets_needed = min_subnet_size([12, 38])
    print(nets_needed)
    ReqMatrix = build_compatibility_matrix(nets_needed)
    print(ReqMatrix)
    #If SubnetGenerator.py is not in the same directory, this test will not work.
    #However, the build_compatibility_matrix function is specifically designed to output a matrix for use with that function.
    StartAddress = '200.200.200.0'
    Size = '/23'
    IPRecord, UserMsg = GenerateSubnets(StartAddress, Size, ReqMatrix)
    print(IPRecord)
