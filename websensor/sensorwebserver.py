#!/usr/bin/python

#from flask import Flask, render_template, request
import flask as fl
import sqlite3

app = fl.Flask(__name__)

# Retrieve data from database
def getData():
    conn=sqlite3.connect('../sensorsData.db')
    curs=conn.cursor()
    #for row in curs.execute("SELECT * FROM SENSOR1DATA ORDER BY timestamp DESC LIMIT 1"):
    for row in curs.execute("SELECT * FROM SENSOR1DATA WHERE timestamp=(SELECT MAX(timestamp) FROM SENSOR1DATA)"):
        time = str(row[0])
        ldrdata = row[1]
        accx,accy,accz = row[2],row[3],row[4]
        gyrx,gyry,gyrz = row[5],row[6],row[7]
        magx,magy,magz = row[8],row[9],row[10]
    #for row in curs.execute("SELECT * FROM SENSOR2DATA ORDER BY timestamp DESC LIMIT 1"):
    for row in curs.execute("SELECT * FROM SENSOR2DATA WHERE timestamp=(SELECT MAX(timestamp) FROM SENSOR2DATA)"):
        time2 = str(row[0])
        barodata = row[1]
        tempdata = row[2]
    conn.close()

    return time,ldrdata,accx,accy,accz,gyrx,gyry,gyrz,magx,magy,magz,time2,barodata,tempdata
#    return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

# main route
@app.route("/")
def index():
    time,ldrdata,accx,accy,accz,gyrx,gyry,gyrz,magx,magy,magz,time2,barodata,tempdata = getData()
    templateData = {
            'time' : time,
            'ldrdata' : ldrdata,
            'accx' : accx,
            'accy' : accy,
            'accz' : accz,
            'gyrx' : gyrx,
            'gyry' : gyry,
            'gyrz' : gyrz,
            'magx' : magx,
            'magy' : magy,
            'magz' : magz,
            'time2' : time2,
            'barodata' : barodata,
            'tempdata' : tempdata
    }
    return fl.render_template('index.html', **templateData)
    #return fl.render_template('index2.html')

if __name__ == "__main__":
    #print(getData())
    app.run(host='0.0.0.0', port=80, debug=False)

