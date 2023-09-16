#!/usr/bin/python

# Script for repeated getting info

import sys,os
import serial
import datetime as dt
import sqlite3
import numpy as np

## Definitions
RETRIES = 10
# sensor board XplainedA3BU, based on my own definitions
CODEDI = {'ldr':'82',
          'acc':'83',
          'gyr':'85',
          'mag':'87',
          'prs':'88',
          'tmp':'89',
          }
# types of data
FASTLI = ['ldr','acc','gyr','mag']
SLOWLI = ['tmp','prs']
ONEDLI = ['ldr','tmp','prs']
THREEDLI = ['acc','gyr','mag']

## Helper functions
def bytestoint(bytes):
    return int.from_bytes(bytes,byteorder='big',signed=True)

def getsensor1data(serport,dataname):
    if dataname not in ONEDLI:
        return None  # error condition
    for i in range(RETRIES):
        serport.write(bytes.fromhex(CODEDI[dataname]))
        value = bytestoint(serport.read(4))
        if value is not None:
            return value

def getsensor3data(serport,dataname):
    if dataname not in THREEDLI:
        return None, None, None  # error condition
    for i in range(RETRIES):
        serport.write(bytes.fromhex(CODEDI[dataname]))
        xcomp = bytestoint(serport.read(4))
        ycomp = bytestoint(serport.read(4))
        zcomp = bytestoint(serport.read(4))
        if xcomp is not None and ycomp is not None and zcomp is not None:
            return xcomp, ycomp, zcomp

## Parameters
devport = '/dev/ttyACM0'
dbfn = 'sensorsData.db'
numpersec = 10
fastsampTD = dt.timedelta(seconds=1/numpersec)
slowsampTD = dt.timedelta(seconds=10/numpersec)
TIMEWINDOWTD = dt.timedelta(seconds=60)    # seconds
varThresDi = {'ldr':75,
              'acc':49,
              'gyr':4,
              'mag':25,
              }

## Main
# open serial port and flush
ser = serial.Serial(port=devport, baudrate=115200, timeout=1)
print('Port opened:',ser.name)
ser.flushInput()
ser.flushOutput()
    
# open database
con = sqlite3.connect(dbfn)

# Initial data to be written whenever data starts to be collected
# Write to db and csv file for shortterm
entryLi = []
# 1-D data
for dataname in ONEDLI:
    val = getsensor1data(ser, dataname)
    nowDT = dt.datetime.now()
    if val is not None:
        entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % val + ")"
        entryLi.append(entrystr)
        with open("%s_%s.csv" % (dataname,nowDT.strftime("%Y%m%d")),"a") as f:
            f.write("%s,%d\n" % (nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4],val))

# 3-D data
for dataname in THREEDLI:
    valx,valy,valz = getsensor3data(ser, dataname)
    nowDT = dt.datetime.now()
    if valx is not None and valy is not None and valz is not None:
        entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (valx, valy, valz) + ")"
        entryLi.append(entrystr)
        with open("%s_%s.csv" % (dataname,nowDT.strftime("%Y%m%d")),"a") as f:
            f.write("%s,%d,%d,%d\n" % (nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4],valx,valy,valz))

## Add entries into database
with con:
    cur = con.cursor()
    for entry in entryLi:
        print(dt.datetime.now(), "Added",entry)
        cur.execute(entry)

# Final time for this time window
timeWindowEnd = nowDT + TIMEWINDOWTD
# next time to take data
nextTimeFast = nowDT + fastsampTD
nextTimeSlow = nowDT + slowsampTD

while True:
    # Gather raw data at fastest sampling rate
    oneDDataDi = {x:[] for x in ONEDLI}
    threeDDataDi = {x+"x":[] for x in THREEDLI} | {y+"y":[] for y in THREEDLI} | {z+"z":[] for z in THREEDLI}
    timeDi = {x:[] for x in ONEDLI+THREEDLI}
    while dt.datetime.now() < timeWindowEnd: 
        while dt.datetime.now() < nextTimeFast: pass
        for dataname in FASTLI:
            if dataname in ONEDLI:
                val = getsensor1data(ser, dataname)
                nowDT = dt.datetime.now()
                timeDi[dataname].append(nowDT)
                oneDDataDi[dataname].append(val)
            else:
                valx,valy,valz = getsensor3data(ser, dataname)
                nowDT = dt.datetime.now()
                timeDi[dataname].append(nowDT)
                threeDDataDi[dataname+'x'].append(valx)
                threeDDataDi[dataname+'y'].append(valy)
                threeDDataDi[dataname+'z'].append(valz)
        nextTimeFast += fastsampTD
        if dt.datetime.now() > nextTimeSlow:
            for dataname in SLOWLI:
                # Condition is redundant since SLOWLI is subset of ONEDLI, 
                # but keep for consistency
                if dataname in ONEDLI: 
                    val = getsensor1data(ser, dataname)
                    nowDT = dt.datetime.now()
                    timeDi[dataname].append(nowDT)
                    oneDDataDi[dataname].append(val)
            nextTimeSlow += slowsampTD

    # Final time for this time window
    timeWindowEnd += TIMEWINDOWTD
    entryLi = []
    # Time window has passed; now check the data to wether it should be 
    # averaged or not or not
    for dataname in ONEDLI:
        varval = np.var(oneDDataDi[dataname])
        # check if little energy in data (variance) then average
        if dataname in SLOWLI or varval < varThresDi[dataname]:
            # take middle time point and average value and overwrite the values
            timeDi[dataname] = [timeDi[dataname][len(timeDi[dataname])//2]]
            oneDDataDi[dataname] = [np.mean(oneDDataDi[dataname])]
        # Write the data
        for i in range(len(timeDi[dataname])):
            entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % timeDi[dataname][i].strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % oneDDataDi[dataname][i] + ")"
            entryLi.append(entrystr)
            with open("%s_%s.csv" % (dataname,nowDT.strftime("%Y%m%d")),"a") as f:
                f.write("%s,%d\n" % (timeDi[dataname][i].strftime("%Y-%m-%d %H:%M:%S:%f")[:-4],oneDDataDi[dataname][i]))
    for dataname in THREEDLI:
        varvalx = np.var(threeDDataDi[dataname+'x'])
        varvaly = np.var(threeDDataDi[dataname+'y'])
        varvalz = np.var(threeDDataDi[dataname+'z'])
        # check if little energy in data (variance) then average
        if varvalx+varvaly+varvalz < varThresDi[dataname]:
            # take middle time point and average value and overwrite the values
            timeDi[dataname] = [timeDi[dataname][len(timeDi[dataname])//2]]
            threeDDataDi[dataname+'x'] = [np.mean(threeDDataDi[dataname+'x'])]
            threeDDataDi[dataname+'y'] = [np.mean(threeDDataDi[dataname+'y'])]
            threeDDataDi[dataname+'z'] = [np.mean(threeDDataDi[dataname+'z'])]
        # Write the data
        for i in range(len(timeDi[dataname])):
            entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % timeDi[dataname][i].strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (threeDDataDi[dataname+'x'][i],threeDDataDi[dataname+'y'][i],threeDDataDi[dataname+'z'][i]) + ")"
            entryLi.append(entrystr)
            with open("%s_%s.csv" % (dataname,nowDT.strftime("%Y%m%d")),"a") as f:
                f.write("%s,%d,%d,%d\n" % (timeDi[dataname][i].strftime("%Y-%m-%d %H:%M:%S:%f")[:-4],threeDDataDi[dataname+'x'][i],threeDDataDi[dataname+'y'][i],threeDDataDi[dataname+'z'][i])) 
    
    ## Add entries into database, hope this can finish fast so that it
    # doesn't mess up the next sampling time
    with con:
        cur = con.cursor()
        for entry in entryLi:
            print(dt.datetime.now(),"Added",entry)
            cur.execute(entry)

    ## Delete short term data files that are older than one day
    oldDT = nowDT - dt.timedelta(days=2)
    for filename in os.listdir('.'):
        if filename.endswith('.csv') and dt.datetime.strptime(filename.split('_')[-1].split('.')[0],"%Y%m%d") < oldDT:
            os.remove(filename)
    
## Cleanup
con.close()
ser.close()
