#!/usr/bin/python

# Script for repeated getting info

import sys
import serial
import datetime as dt
import sqlite3
import numpy as py

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
        return = None, None, None  # error condition
    else:
    for i in range(RETRIES):
        serport.write(bytes.fromhex(CODEDI[dataname]))
        xcomp = bytestoint(serport.read(4))
        ycomp = bytestoint(serport.read(4))
        zcomp = bytestoint(serport.read(4))
        if xcomp is not None and ycomp is not None and zcomp is not None:
            return xcomp, ycomp, zcomp

def outtol1(val1, val2, tol):
    return (abs(val1-val2) > tol)

def outtol3(val1x, val1y, val1z, val2x, val2y, val2z, tol):
    return ((val1x-val2x)**2 + (val1y-val2y)**2 + (val1z-val2z)**2)**0.5 > tol

## Parameters
devport = '/dev/ttyACM0'
dbfn = 'sensorsData.db'
numpersec = 10
TIMEWINDOW = 60    # seconds
#timetol =  dt.timedelta(seconds=2/numpersec)
#ldrtol = 15  #
#acctol = 50 # 1/100 g
#gyrtol = 10
#magtol = 7
#prstol = 100 # 1 Pascal
#tmptol = 2 # 1/10 degrees Celsius
varThresDi = {'ldr':25,
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
entryLi = []
# 1-D data
for dataname in ONEDLI:
    val = getsensor1data(ser, dataname)
    nowDT = dt.datetime.now()
    if val is not None:
        entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % val + ")"
        entryLi.append(entrystr)

# 3-D data
for dataname in THREEDLI:
    valx,valy,valz = getsensor3data(ser, dataname)
    nowDT = dt.datetime.now()
    if valx is not None and valy is not None and valz is not None:
        entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (valx, valy, valz) + ")"
        entryLi.append(entrystr)

## Add entries into database
with con:
    cur = con.cursor()
    for entry in entryLi:
        print(dt.datetime.now(), "Added",entry)
        cur.execute(entry)

# Final time for this time window
timeWindowEnd = nowDT + dt.timedelta(seconds=TIMEWINDOW)
# next time to take data
nextTimeFast = nowDT + dt.timedelta(seconds=1/numpersec)
nextTimeSlow = nowDT + dt.timedelta(seconds=10/numpersec)

while True:
    # Gather raw data at fastest sampling rate
    oneDDataDi = {x:[] for x in ONEDLI}
    threeDDataDi = {x+"x":[] for x in THREEDLI,
                    y+"y":[] for y in THREEDLI,
                    z+"z":[] for z in THREEDLI,
                    }
    timeDi = {x:[] for x in ONEDLI+THREEDLI}
    while dt.datetime.now() < timeWindowEnd: pass
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
        nextTimeFast = nextTimeFast + dt.timedelta(seconds=10/numpersec)
        if dt.datetime.now() > nextTimeSlow:
            for dataname in SLOWLI:
                # Condition is redundant since SLOWLI is subset of ONEDLI, 
                # but keep for consistency
                if dataname in ONEDLI: 
                    val = getsensor1data(ser, dataname)
                    nowDT = dt.datetime.now()
                    timeDi[dataname].append(nowDT)
                    oneDDataDi[dataname].append(val)
            nextTimeSlow = nextTimeSlow + dt.timedelta(seconds=1/numpersec)

    # Final time for this time window
    timeWindowEnd = timeWindowEnd + dt.timedelta(seconds=TIMEWINDOW)
    entryLi = []
    # Time window has passed; now check the data to wether it should be 
    # averaged or not or not
    for dataname in ONEDLI:
        varval = np.var(oneDDataDi[dataname])
        # check if little energy in data (variance) then average
        if varval < varThresDi[dataname]:
            # take middle time point and average value and overwrite the values
            timeDi[dataname] = [timeDi[dataname][len(timeDi[dataname])//2]]
            oneDDataDi[dataname] = [np.avg(oneDDataDi[dataname])]
        # Write the data
        for i in range(len(timeDi[dataname])):
            entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % timeDi[dataname][i].strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % oneDDataDi[dataname][i] + ")"
            entryLi.append(entrystr)
    for dataname in THREEDLI:
        varvalx = np.var(threeDDataDi[dataname+'x'])
        varvaly = np.var(threeDDataDi[dataname+'y'])
        varvalz = np.var(threeDDataDi[dataname+'z'])
        # check if little energy in data (variance) then average
        if varvalx+varvaly+varvalz < varThresDi[dataname]:
            # take middle time point and average value and overwrite the values
            timeDi[dataname] = [timeDi[dataname][len(timeDi[dataname])//2]]
            threeDDataDi[dataname+'x'] = [np.avg(threeDDataDi[dataname+'x'])]
            threeDDataDi[dataname+'y'] = [np.avg(threeDDataDi[dataname+'y'])]
            threeDDataDi[dataname+'z'] = [np.avg(threeDDataDi[dataname+'z'])]
        # Write the data
        for i in range(len(timeDi[dataname])):
            entrystr = "INSERT INTO " + "%s" % (dataname+"data") + " VALUES(" + "'%s', " % timeDi[dataname][i].strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (threeDDataDi[dataname+'x'][i],threeDDataDi[dataname+'y'][i],threeDDataDi[dataname+'z'][i] + ")"
            entryLi.append(entrystr)
    
    ## Add entries into database, hope this can finish fast so that it
    # doesn't mess up the next sampling time
    with con:
        cur = con.cursor()
        for entry in entryLi:
            print(dt.datetime.now(),"Added",entry)
            cur.execute(entry)

'''
    # LDR - insert value only if it changed outside tolerance
    ldr = getsensor1data(ser, CODE_LDR)
    nowDT = dt.datetime.now()
    if ldr is not None:
        entrystr = "INSERT INTO ldrdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % ldr + ")"
        entryLi.append(entrystr)

    # Accel
    accx, accy, accz = getsensor3data(ser, CODE_ACC)
    nowDT = dt.datetime.now()
    if accx is not None and accy is not None and accz is not None:
        entrystr = "INSERT INTO accdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (accx, accy, accz) + ")"
        entryLi.append(entrystr)

    # Gyro
    gyrx, gyry, gyrz = getsensor3data(ser, CODE_GYR)
    nowDT = dt.datetime.now()
    if gyrx is not None and gyry is not None and gyrz is not None:
        entrystr = "INSERT INTO gyrdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (gyrx, gyry, gyrz) + ")"
        entryLi.append(entrystr)

    # Magnetometer
    magx, magy, magz = getsensor3data(ser, CODE_MAG)
    nowDT = dt.datetime.now()
    if magx is not None and magy is not None and magz is not None:
        entrystr = "INSERT INTO magdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (magx, magy, magz) + ")"
        entryLi.append(entrystr)
    
    # slower sampled by 10
    if dt.datetime.now() > nexttime10:
        # Barometer
        prs = getsensor1data(ser, CODE_PRS)
        nowDT = dt.datetime.now()
        if prs is not None:
            entrystr = "INSERT INTO prsdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % prs + ")"
            entryLi.append(entrystr)
            oldprs = prs
            
        # Temp
        tmp = getsensor1data(ser, CODE_TMP)
        nowDT = dt.datetime.now()
        if tmp is not None:
            entrystr = "INSERT INTO tmpdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % tmp + ")"
            entryLi.append(entrystr)

        nexttime10 = dt.datetime.now() + dt.timedelta(seconds=10/numpersec)
'''

## Cleanup
con.close()
ser.close()
