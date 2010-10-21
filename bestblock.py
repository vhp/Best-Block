#!/usr/bin/env python
import sys
import subprocess
import decimal
from operator import itemgetter


FILENAME = "temp.file"
RANDFILE = "rand.file"
KB = 1024 
MB = 1024 * 1024
GB = 1024 * 1024 * 1024

blocksizes = [512, 1024, 4096, 8192, 262144, 524288, 1048576, 16777216, \
               33554432, 67108864, 268435456,  536870912, 1073741824]

quickaccess = []
slowdataaccess = []
samediskaccess = []

def removefile():
     pipe1 =  subprocess.Popen(["rm","-f", FILENAME, RANDFILE])

def blockprint(num):
    if num%GB == 0:
        return str(num/GB) + "G"
    elif num%MB == 0:
        return str(num/MB) + "M"
    elif num%KB == 0:
        return str(num/KB) + "K"
    else:
        return num

def tableprint(results, test):
    count = 1
    print("\n\t\t"+ test)
    print("----------------------------------------------------------")
    print(" #  Blocksize\tEasy Unit\tTime\t\tThroughput")
    for (blocksize, time, throughput) in results[0:3]:
        print( str(count).rjust(2)+"  "+ str(blocksize).ljust(14)+" "+\
            str(blockprint(blocksize)).ljust(4)+"\t\t"+str(time).ljust(7)+"s \t"\
                + str(throughput).rjust(4)+ " MB/s")
        count = count + 1

def quick_data_access():
    for element in reversed(blocksizes):
        pipe1 =  subprocess.Popen(["dd", "if=/dev/zero" , "of="+FILENAME, \
            "bs="+str(element), "count="+str(GB/element)], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pipe1.wait()
        for line in pipe1.stderr:
            if "bytes" in line and "copied" in line:
                parted = line.partition(", ")[2].partition(", ")
                quickaccess.append([int(element), decimal.Decimal(parted[0].rstrip(" s")),\
                     decimal.Decimal(parted[2].rstrip("\n").rstrip("  MB/s"))])
    removefile()
    tableprint(sorted(quickaccess, key=itemgetter(1)), "Quick Access to Data")


def same_disk_file_access():
    pipe2 = subprocess.Popen(["dd", "if=/dev/urandom" , "of="+RANDFILE, \
            "bs=4096", "count=262144"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pipe2.wait()
    for element in reversed(blocksizes):
        pipe1 =  subprocess.Popen(["dd", "if="+RANDFILE , "of="+FILENAME, \
            "bs="+str(element), "count="+str(GB/element)], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pipe1.wait()
        for line in pipe1.stderr:
            if "bytes" in line and "copied" in line:
                parted = line.partition(", ")[2].partition(", ")
                samediskaccess.append([int(element), decimal.Decimal(parted[0].rstrip(" s")),\
                     decimal.Decimal(parted[2].rstrip("\n").rstrip("  MB/s"))])
    removefile()
    tableprint(sorted(samediskaccess, key=itemgetter(1)), "Same Disk File Access")

if __name__ == '__main__':
    quick_data_access()
    same_disk_file_access()
    
