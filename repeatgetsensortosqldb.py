#!/usr/bin/python

# Script for repeated getting info

import serial
import datetime
import sqlite3

## Definitions
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

## Parameters
devport = '/dev/ttyACM0'
dbfn = 'sensorsData.db'
numpersec = 10

## Main
# open serial port and flush
ser = serial.Serial(port=devport, baudrate=115200, timeout=1)
print('Port opened:',ser.name)
ser.flushInput()
ser.flushOutput()
    
# open database
con = sqlite3.connect(dbfn)

nexttime = datetime.datetime.now() + datetime.timedelta(seconds=1/numpersec)

while True:
    entry1Li = []
    for i in range(numpersec):
        while datetime.datetime.now() < nexttime: pass
        entrystr = "INSERT INTO SENSOR1data VALUES(" + "'%s', " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

        # LDR
        ldrdata = getsensor1data(ser, CODE_LDR)
        if ldrdata is not None:
            entrystr += "%d, " % ldrdata
        else:
            entrystr += "NA, "

        # Accel
        accx, accy, accz = getsensor3data(ser, CODE_ACC)
        if accx is not None and accy is not None and accz is not None:
            entrystr += "%d, %d, %d, " % (accx, accy, accz)
        else:
            entrystr += "NA, NA, NA, "

        # Gyro
        gyrx, gyry, gyrz = getsensor3data(ser, CODE_GYR)
        if gyrx is not None and gyry is not None and gyrz is not None:
            entrystr += "%d, %d, %d, " % (gyrx, gyry, gyrz)
        else:
            entrystr += "NA, NA, NA, "

        # Magnetometer
        magx, magy, magz = getsensor3data(ser, CODE_MAG)
        if magx is not None and magy is not None and magz is not None:
            entrystr += "%d, %d, %d " % (magx, magy, magz)
        else:
            entrystr += "NA, NA, NA "

        # End the entry
        entrystr += ")"
        entry1Li.append(entrystr)
        nexttime = nexttime + datetime.timedelta(seconds=1/numpersec)

    entry2 = "INSERT INTO SENSOR2data VALUES(" + "'%s', " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Barometer
    barodata = getsensor1data(ser, CODE_PRS)
    if barodata is not None:
        entry2 += "%.2f, " % (barodata/100)
    else:
        entry2 += "NA, "
    # Temp
    tempdata = getsensor1data(ser, CODE_TMP)
    if tempdata is not None:
        entry2 += "%.1f " % (tempdata/10)
    else:
        entry2 += "NA "

    # End the entry
    entry2 += ")"
 
    ## Add entry into database
    print(datetime.datetime.now(), dbfn, "Added entry")
    with con:
        cur = con.cursor()
        for entry in entry1Li:
            cur.execute(entry)
        cur.execute(entry2)

## Cleanup
ser.close()
