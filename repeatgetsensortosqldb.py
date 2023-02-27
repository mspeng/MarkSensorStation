#!/usr/bin/python

# Script for repeated getting info

import sys
import serial
import datetime
import sqlite3

## Definitions
RETRIES = 10
# sensor board XplainedA3BU, based on my own definitions
CODE_LDR = '82'
CODE_ACC = '83'
CODE_GYR = '85'
CODE_MAG = '87'
CODE_PRS = '88'
CODE_TMP = '89'

## Helper functions
def bytestoint(bytes):
    return int.from_bytes(bytes,byteorder='big',signed=True)

def getsensor1data(serport,code):
    if code not in [CODE_LDR, CODE_PRS, CODE_TMP]:
        value = None  # error condition
    else:
        serport.write(bytes.fromhex(code))
        value = bytestoint(serport.read(4))
    return value

def getsensor3data(serport,code):
    if code not in [CODE_ACC, CODE_GYR, CODE_MAG]:
        xcomp, ycomp, zcomp = None, None, None  # error condition
    else:
        serport.write(bytes.fromhex(code))
        xcomp = bytestoint(serport.read(4))
        ycomp = bytestoint(serport.read(4))
        zcomp = bytestoint(serport.read(4))
    return xcomp, ycomp, zcomp

def outtol1(val1, val2, tol):
    return (abs(val1-val2) > tol)

def outtol3(val1x, val1y, val1z, val2x, val2y, val2z, tol):
    return ((val1x-val2x)**2 + (val1y-val2y)**2 + (val1z-val2z)**2)**0.5 > tol

## Parameters
devport = '/dev/ttyACM0'
dbfn = 'sensorsData.db'
numpersec = 10
timetol =  datetime.timedelta(seconds=2/numpersec)
ldrtol = 15  #
acctol = 50 # 1/100 g
gyrtol = 10
magtol = 7
prstol = 100 # 1 Pascal
tmptol = 2 # 1/10 degrees Celsius

## Main
# open serial port and flush
ser = serial.Serial(port=devport, baudrate=115200, timeout=1)
print('Port opened:',ser.name)
ser.flushInput()
ser.flushOutput()
    
# open database
con = sqlite3.connect(dbfn)

# Initial data set, for comparison to determine if new values should
# be written to database or not
entryLi = []
# LDR
for i in range(RETRIES):
    ldr = getsensor1data(ser, CODE_LDR)
    nowDT = datetime.datetime.now()
    if ldr is not None:
        entrystr = "INSERT INTO ldrdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % ldr + ")"
        entryLi.append(entrystr)
        oldldr = ldr
        oldldrDT = nowDT
        break
else:
    # could not get data something is wrong
    sys.exit()
# Accelerometer
for i in range(RETRIES):
    accx, accy, accz = getsensor3data(ser, CODE_ACC)
    nowDT = datetime.datetime.now()
    if accx is not None and accy is not None and accz is not None:
        entrystr = "INSERT INTO accdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (accx, accy, accz) + ")"
        entryLi.append(entrystr)
        oldaccx,oldaccy,oldaccz = accx,accy,accz
        oldaccDT = nowDT
        break
else:
    # could not get data something is wrong
    sys.exit()
# Gyroscope
for i in range(RETRIES):
    gyrx, gyry, gyrz = getsensor3data(ser, CODE_GYR)
    nowDT = datetime.datetime.now()
    if gyrx is not None and gyry is not None and gyrz is not None:
        entrystr = "INSERT INTO gyrdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (gyrx, gyry, gyrz) + ")"
        entryLi.append(entrystr)
        oldgyrx,oldgyry,oldgyrz = gyrx,gyry,gyrz
        oldgyrDT = nowDT
        break
else:
    # could not get data something is wrong
    sys.exit()
# Magnetometer
for i in range(RETRIES):
    magx, magy, magz = getsensor3data(ser, CODE_MAG)
    nowDT = datetime.datetime.now()
    if magx is not None and magy is not None and magz is not None:
        entrystr = "INSERT INTO magdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (magx, magy, magz) + ")"
        entryLi.append(entrystr)
        oldmagx,oldmagy,oldmagz = magx,magy,magz
        oldmagDT = nowDT
        break
else:
    # could not get data something is wrong
    sys.exit()
# Pressure
for i in range(RETRIES):
    prs = getsensor1data(ser, CODE_PRS)
    nowDT = datetime.datetime.now()
    if prs is not None:
        entrystr = "INSERT INTO prsdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % prs + ")"
        entryLi.append(entrystr)
        oldprs = prs
        oldprsDT = nowDT
        break
else:
    # could not get data something is wrong
    sys.exit()
# Temperature
for i in range(RETRIES):
    tmp = getsensor1data(ser, CODE_TMP)
    nowDT = datetime.datetime.now()
    if tmp is not None:
        entrystr = "INSERT INTO tmpdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % tmp + ")"
        entryLi.append(entrystr)
        oldtmp = tmp
        oldtmpDT = nowDT
        break
else:
    # could not get data something is wrong
    sys.exit()

## Add entries into database
with con:
    cur = con.cursor()
    for entry in entryLi:
        print(datetime.datetime.now(), "Added",entry)
        cur.execute(entry)

# next time to take data
nexttime = datetime.datetime.now() + datetime.timedelta(seconds=1/numpersec)
nexttime10 = nexttime + datetime.timedelta(seconds=10/numpersec)

while True:
    entryLi = []
    while datetime.datetime.now() < nexttime: pass

    # LDR - insert value only if it changed outside tolerance
    ldr = getsensor1data(ser, CODE_LDR)
    if ldr is not None:
        entrystr = "INSERT INTO ldrdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % ldr + ")"
        entryLi.append(entrystr)

    # Accel
    accx, accy, accz = getsensor3data(ser, CODE_ACC)
    if accx is not None and accy is not None and accz is not None:
        entrystr = "INSERT INTO accdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (accx, accy, accz) + ")"
        entryLi.append(entrystr)

    # Gyro
    gyrx, gyry, gyrz = getsensor3data(ser, CODE_GYR)
    if gyrx is not None and gyry is not None and gyrz is not None:
        entrystr = "INSERT INTO gyrdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (gyrx, gyry, gyrz) + ")"
        entryLi.append(entrystr)

    # Magnetometer
    magx, magy, magz = getsensor3data(ser, CODE_MAG)
    if magx is not None and magy is not None and magz is not None:
        entrystr = "INSERT INTO magdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d, %d, %d" % (magx, magy, magz) + ")"
        entryLi.append(entrystr)
    
    # slower sampled by 10
    if datetime.datetime.now() > nexttime10:
        # Barometer
        prs = getsensor1data(ser, CODE_PRS)
        if prs is not None:
            entrystr = "INSERT INTO prsdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % prs + ")"
            entryLi.append(entrystr)
            oldprs = prs
            
        # Temp
        tmp = getsensor1data(ser, CODE_TMP)
        if tmp is not None:
            entrystr = "INSERT INTO tmpdata VALUES(" + "'%s', " % nowDT.strftime("%Y-%m-%d %H:%M:%S:%f")[:-4] + "%d" % tmp + ")"
            entryLi.append(entrystr)

        nexttime10 = datetime.datetime.now() + datetime.timedelta(seconds=10/numpersec)

    ## Add entries into database
    with con:
        cur = con.cursor()
        for entry in entryLi:
            print(datetime.datetime.now(),"Added",entry)
            cur.execute(entry)

    # next time to take data
    nexttime = nexttime + datetime.timedelta(seconds=1/numpersec)

## Cleanup
ser.close()
