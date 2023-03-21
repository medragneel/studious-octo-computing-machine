#!/usr/bin/env python

#a script can help u to convert the lyrics file to .srt
#created by wOOL, iamwool@gmail.com
#edited by eadmaster  http://eadmaster.tk

import sys, re, os
from datetime import datetime
from datetime import timedelta

#args checking
if(len(sys.argv)==1 or sys.argv[1]=='-h' or sys.argv[1]=='--help' or not os.path.isfile(sys.argv[1])):
	print("usage: lrc2srt FILE.SRT")
	exit(0)

p = re.compile("[0-9]+")
filename = sys.argv[1]
#interval = str(sys.argv[2])

lrc = open(filename)

listtime =  []
listlyrics = []

for line in lrc.readlines():
    if p.match(line.split(":")[0].replace("[","")):
        listtime.append("00:" + line.split("]")[0].replace("[","")+"0")
        listlyrics.append(line.split("]")[1])

#read file and delete empty&useless lines

o=""
i=0
#listtime[i].replace(".",",")+\
while i <= listtime.__len__()-2:
    start_time = (datetime.strptime(listtime[i],"%H:%M:%S.%f")-datetime.strptime("1","%S"))
    if (start_time.days < 0 ):
        start_time = (datetime.strptime(listtime[i],"%H:%M:%S.%f")-datetime.strptime("0","%S"))
    if (start_time.microseconds == 0 ):
        start_time = start_time+timedelta(microseconds=1) # add 1 msec to avoid empty msec field

    o = o+\
    str(i+1)+\
    "\n"+\
    "0" + str(start_time).replace("000","").replace(".",",") +\
    " --> " +\
    listtime[i+1].replace(".",",")+\
    "\n"+listlyrics[i]+\
    "\n"
    i=i+1

o = o + str(i+1) + "\n" + listtime[-1].replace(".",",")+ " --> " + "\n" + listlyrics[-1] + "\n"
srt = open(filename.replace("lrc","srt"),"w")
srt.write(o)
