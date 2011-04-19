#!/usr/bin/env python
#
#   Author: Vincent Perricone <vhp@lavabit.com>
#   Date: 4/6/2011
#   Title: Best Block - bestblock.py
#   Description: Best Block is a simple script used to find your systems
#               most efficient blocking factor. Compares speed when data is
#               readily available as well as when it is not.
#   License: Released under "Simplified BSD License" see LICENSE file
#

import os
import subprocess
from operator import itemgetter
from decimal import Decimal

TEMPFILE = 'temp.file'
RANDFILE = 'rand.file'

KB = 1024
MB = 1024 * 1024
GB = 1024 * 1024 * 1024

blocksizes = [512, 1024, 4096, 8192, 262144, 524288, 1048576, 16777216,
               33554432, 67108864, 268435456,  536870912, 1073741824]

def sync():
    """ Flush filesystem buffers. """
    subprocess.call(['sync'])

def remove_files():
    """ remove all temporary files """
    try:
        for delible in [TEMPFILE, RANDFILE]:
            os.unlink(delible)
    except OSError:
        pass
    sync()

def pretty_blocks(blocksize):
    """ Return formatted string of human readable block size unit like 1G """
    if blocksize % GB == 0:
        return '{0}G'.format(str(blocksize / GB))
    elif blocksize % MB == 0:
        return '{0}M'.format(str(blocksize / MB))
    elif blocksize % KB == 0:
        return '{0}K'.format(str(blocksize / KB))
    else:
        return blocksize

def print_table(results, table_title):
    """ Print tabulated results to user """
    if results:
        print('\n\t\t'+ table_title)
        print('----------------------------------------------------------')
        print(' #  Block size\tEasy Unit\tTime\t\tThroughput')
        for index, (bsize, time, throughput) in enumerate(results[0:3],start=1):
            print('{0} {1} {2}\t\t{3}s \t {4} MB/s'.format(
                                        str(index).rjust(2),
                                        str(bsize).ljust(14),
                                        str(pretty_blocks(bsize)).ljust(4),
                                        str(time).ljust(7),
                                        str(throughput).rjust(4)))
    else:
        print('Error: Empty list of results received upon table printing')

def quick_data_access():
    """ Evaluate block size when information is readily available """
    results_list = []
    for blocksize in reversed(blocksizes):
        dd_subprocess = (subprocess.Popen(['dd', 'if=/dev/zero',
                        'of=' + TEMPFILE,
                        'bs=' + str(blocksize),
                        'count=' + str(GB / blocksize), 'conv=fsync'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        dd_subprocess.wait()
        for line in dd_subprocess.stderr:
            if 'bytes' in line and 'copied' in line:
                dd_data = line.partition(', ')[2].partition(', ')
                (results_list.append([int(blocksize),
                    Decimal(dd_data[0].rstrip(' s')),
                    Decimal(dd_data[2].rstrip('\n').rstrip('  MB/s'))]))
    remove_files()
    print_table(sorted(results_list, key=itemgetter(1)), 'Quick Access to Data')

def create_random_file():
    """ Create file of size 1GB consistent of pseudo random data """
    ret = (subprocess.call(['dd', 'if=/dev/urandom', 'of=' + RANDFILE,
                            'bs=4096', 'count=262144'], stderr=subprocess.PIPE))
    if ret == 0 and os.path.isfile(RANDFILE):
        return 1
    else:
        return 0

def same_disk_file_access():
    """ Evaluate block size when data is I/O dependent """
    results_list = []
    if create_random_file() == 1:
        for blocksize in reversed(blocksizes):
            dd_subprocess = (subprocess.Popen(['dd', 'if=' + "/dev/urandom" ,
                            'of=' + TEMPFILE, 'bs=' + str(blocksize),
                            'count=' + str(GB / blocksize), 'conv=fsync'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE))
            dd_subprocess.wait()
            for line in dd_subprocess.stderr:
                if 'bytes' in line and 'copied' in line:
                    dd_data = line.partition(', ')[2].partition(', ')
                    (results_list.append([int(blocksize),
                        Decimal(dd_data[0].rstrip(' s')),
                        Decimal(dd_data[2].rstrip('\n').rstrip('  MB/s'))]))
    else:
        print('Error: Random Test file {0} does not exist'.format(RANDFILE))
    print_table(sorted(results_list,key=itemgetter(1)), 'Same Disk File Access')

if __name__ == '__main__':
    print('Best Block is now measuring your systems performance.')
    print('Please be patient as this may take some time.')
    remove_files()
    quick_data_access()
    same_disk_file_access()
    remove_files()
