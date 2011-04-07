#!/usr/bin/env python
#
#   Author: Vincent Perricone <vhp@buffalo.edu>
#   Date: 4/6/2011
#   Title: Best-Block
#   Description: Best-Block is a simple script used to find your systems
#               most efficient blocking factor. Compares speed when data is
#               readily available as well as when it is not.
#   License: Released under "Simplified BSD License" see LICENSE file
#

import os
import decimal
import subprocess
from operator import itemgetter

FILENAME = 'temp.file'
RANDFILE = 'rand.file'

KB = 1024 
MB = 1024 * 1024
GB = 1024 * 1024 * 1024

blocksizes = [512, 1024, 4096, 8192, 262144, 524288, 1048576, 16777216, \
               33554432, 67108864, 268435456,  536870912, 1073741824]

def removefiles():
    ret = subprocess.call(['rm','-f', FILENAME, RANDFILE])
    if ret == 0:
        return 1
    else:
        return 0    

def blockprint(num):
    if num%GB == 0:
        return str(num/GB) + 'G'
    elif num%MB == 0:
        return str(num/MB) + 'M'
    elif num%KB == 0:
        return str(num/KB) + 'K'
    else:
        return num

def tableprint(results, test):
    count = 1
    if results:
        print('\n\t\t'+ test)
        print('----------------------------------------------------------')
        print(' #  Block size\tEasy Unit\tTime\t\tThroughput')
        for (blocksize, time, throughput) in results[0:3]:
            print( str(count).rjust(2)+'  '+ str(blocksize).ljust(14)+' '+\
              str(blockprint(blocksize)).ljust(4)+'\t\t'+str(time).ljust(7)+'s \t'\
                    + str(throughput).rjust(4)+ ' MB/s')
            count = count + 1
    else:
        print('Error: Empty list received upon table printing')

def quick_data_access():
    quickaccess = []
    for element in reversed(blocksizes):
        pipe1 =  subprocess.Popen(['dd', 'if=/dev/zero' , 'of='+FILENAME, \
            'bs='+str(element), 'count='+str(GB/element)], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pipe1.wait()
        for line in pipe1.stderr:
            if 'bytes' in line and 'copied' in line:
                parted = line.partition(', ')[2].partition(', ')
                quickaccess.append([int(element), decimal.Decimal(parted[0].rstrip(' s')),\
                     decimal.Decimal(parted[2].rstrip('\n').rstrip('  MB/s'))])
    removefiles()
    tableprint(sorted(quickaccess, key=itemgetter(1)), 'Quick Access to Data')

def make_rand_file():
    ret = subprocess.call(['dd','if=/dev/urandom','of='+RANDFILE,'bs=4096','count=262144'], stderr=subprocess.PIPE)
    if ret == 0 and os.path.isfile('rand.file'):
        return 1
    else:
        return 0

def same_disk_file_access():
    samediskaccess = []
    if make_rand_file() == 1:
        for element in reversed(blocksizes):
            pipe1 =  subprocess.Popen(['dd', 'if='+RANDFILE , 'of='+FILENAME, \
            'bs='+str(element), 'count='+str(GB/element)], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pipe1.wait()
            for line in pipe1.stderr:
                if 'bytes' in line and 'copied' in line:
                    parted = line.partition(', ')[2].partition(', ')
                    samediskaccess.append([int(element), decimal.Decimal(parted[0].rstrip(' s')),\
                     decimal.Decimal(parted[2].rstrip('\n').rstrip('  MB/s'))])
    else:
        print('Error: Random Test file '+RANDFILE+' does not exist')
    tableprint(sorted(samediskaccess, key=itemgetter(1)), 'Same Disk File Access')

if __name__ == '__main__':
    print('Best-Block is now creating temp files and measuring performance.')
    print('-Please be patient as this may take some time.')
    if removefiles():
        quick_data_access()
        same_disk_file_access()
    else:
        print('Error: Could not properly erase temp files.')
    removefiles()
