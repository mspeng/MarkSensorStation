#!/usr/bin/python

#from flask import Flask, render_template, request
import flask as fl
import sqlite3

app = fl.Flask(__name__)

# Retrieve data from database
def getData():
    conn=sqlite3.connect('../sensorsData.db')
    curs=conn.cursor()
    for row in curs.execute("SELECT * FROM ldrdata WHERE timestamp=(SELECT MAX(timestamp) FROM ldrdata)"):
        timeldr = str(row[0])
        ldr = row[1]
    for row in curs.execute("SELECT * FROM accdata WHERE timestamp=(SELECT MAX(timestamp) FROM accdata)"):
        timeacc = str(row[0])
        accx,accy,accz = row[1],row[2],row[3]
    for row in curs.execute("SELECT * FROM gyrdata WHERE timestamp=(SELECT MAX(timestamp) FROM gyrdata)"):
        timegyr = str(row[0])
        gyrx,gyry,gyrz = row[1],row[2],row[3]
    for row in curs.execute("SELECT * FROM magdata WHERE timestamp=(SELECT MAX(timestamp) FROM magdata)"):
        timemag = str(row[0])
        magx,magy,magz = row[1],row[2],row[3]
    for row in curs.execute("SELECT * FROM prsdata WHERE timestamp=(SELECT MAX(timestamp) FROM prsdata)"):
        timeprs = str(row[0])
        prs = row[1]
    for row in curs.execute("SELECT * FROM tmpdata WHERE timestamp=(SELECT MAX(timestamp) FROM tmpdata)"):
        timetmp = str(row[0])
        tmp = row[1]
    conn.close()

    return timeldr,ldr,timeacc,accx,accy,accz,timegyr,gyrx,gyry,gyrz,timemag,magx,magy,magz,timeprs,prs,timetmp,tmp

# main route
@app.route("/")
def index():
    timeldr,ldr,timeacc,accx,accy,accz,timegyr,gyrx,gyry,gyrz,timemag,magx,magy,magz,timeprs,prs,timetmp,tmp = getData()
    templateData = {
            'timeldr' : timeldr,
            'ldr' : ldr,
            'timeacc' : timeacc,
            'accx' : accx/1000,
            'accy' : accy/1000,
            'accz' : accz/1000,
            'timegyr' : timegyr,
            'gyrx' : gyrx,
            'gyry' : gyry,
            'gyrz' : gyrz,
            'timemag' : timemag,
            'magx' : magx,
            'magy' : magy,
            'magz' : magz,
            'timeprs' : timeprs,
            'prs'  : prs/100,
            'timetmp' : timetmp,
            'tmp' : tmp/10
    }
    return fl.render_template('index.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)

