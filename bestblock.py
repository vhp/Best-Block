#!/usr/bin/env python
import sys
import subprocess
import decimal
from operator import itemgetter


FILENAME = "temp.file"
KB = 1024 
MB = 1024 * 1024
GB = 1024 * 1024 * 1024

blocksizes = [512, 1024, 4096, 8192, 262144, 524288, 1048576, 16777216, \
               33554432, 67108864, 268435456,  536870912, 1073741824]

resultlist = []

def removefile():
     pipe1 =  subprocess.Popen(["rm", FILENAME])

def tableprint(results):
    count = 1
    print "\n #  Blocksize(b)\tTime\tThroughput"
    for (blocksize, time, throughput) in results:
        print( str(count).rjust(2)+"  " + str(blocksize).ljust(10)+"\t" + str(time).ljust(7)+"s  " + str(throughput).rjust(4)+ " MB/s")
        count = count + 1

def main():
    print blocksizes
    for element in reversed(blocksizes):
        print( "Working on - "+"Block Size: "+ str(element).ljust(10) + "\tCount: "+str(GB/element))
        pipe1 =  subprocess.Popen(["dd", "if=/dev/zero" , "of="+FILENAME, \
            "bs="+str(element), "count="+str(GB/element)], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pipe1.wait()
        for line in pipe1.stderr:
            if "bytes" in line and "copied" in line:
#                print line
                parted = line.partition(", ")[2].partition(", ")
#                print parted
                resultlist.append([int(element), decimal.Decimal(parted[0].rstrip(" s")),\
                     decimal.Decimal(parted[2].rstrip("\n").rstrip("  MB/s"))])
    removefile()

if __name__ == '__main__':
    main()
    tableprint(sorted(resultlist, key=itemgetter(1)))
