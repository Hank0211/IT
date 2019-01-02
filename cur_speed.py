#!/usr/bin/env python3

import threading
import time
import sys
import re


def cur_speed(ethx):
    global timer
    global last_triffic
    speed = 0
    with open('/proc/net/dev','r') as f :
        file_line=list(f)
        if ethx == 1:
            eth_line=re.split(r'\W+',file_line[2])
        else :
            eth_line=re.split(r'\W+',file_line[6])
        cur_triffic=int(eth_line[1])
        if last_triffic !=0 :
            speed=(cur_triffic-last_triffic)/1048576
        last_triffic=cur_triffic

    timer = threading.Timer(1,cur_speed,args=[ethx])
    timer.start()
    print("Eth{1} Current speed is : {0}Mb\n".format(speed,ethx))

if __name__=='__main__' :
    last_triffic = 0

    if len(sys.argv) < 2 :
        print("usage: cur_speed {1|2}")
    else :
        cur_speed(int(sys.argv[1]))
        time.sleep(15)
        timer.cancel()
