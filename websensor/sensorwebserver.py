#!/usr/bin/python

import flask as fl
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import sqlite3
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

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

@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples
    numSamples = int (fl.request.form['numSamples'])
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

@app.route('/plot/oneDdata')
def plot_oneDdata():
    conn = sqlite3.connect('../sensorsData.db')
    curs = conn.cursor()
    ts = {}
    ds = {}

    oneDLi = ['ldrdata','prsdata','tmpdata']
    ylims = {'ldrdata':[0, 500],
             'prsdata':[100000,110000],
             'tmpdata':[100,350],
             'accdata':[-1300,1300],
             'gyrdata':[-200,200],
             'magdata':[-100,100],
            }
    ylabels = {'ldrdata':'Light',
               'prsdata':'centiPascals',
               'tmpdata':'deciCelsius',
               'accdata':'mg',
               'gyrdata':'Gyro',
               'magdata':'Gauss',
              }
    threeDLi = ['accdata','gyrdata','magdata']
    for dataname in oneDLi:
        ts[dataname] = []
        ds[dataname] = []
        for row in curs.execute("SELECT * FROM "+dataname+" DESC LIMIT 300"):
            ts[dataname].append(dt.datetime.strptime(str(row[0]),"%Y-%m-%d %H:%M:%S:%f"))
            ds[dataname].append(row[1])
#    for dataname in threeDLi:
#        ts[dataname] = []
#        ds[dataname+'x'] = []
#        ds[dataname+'y'] = []
#        ds[dataname+'z'] = []
#        for row in curs.execute("SELECT * FROM "+dataname+" DESC LIMIT 300"):
#            ts[dataname].append(dt.datetime.strptime(str(row[0]),"%Y-%m-%d %H:%M:%S:%f"))
#            ds[dataname+'x'].append(row[1])
#            ds[dataname+'y'].append(row[2])
#            ds[dataname+'z'].append(row[3])
    conn.close()

    fig0,ax0 = plt.subplots(3,1,sharex=True,figsize=[10,8])
    for i,dataname in enumerate(oneDLi):
        ax0[i].plot(ts[dataname],ds[dataname])
        ax0[i].set_ylim(ylims[dataname])
        ax0[i].set_ylabel(ylabels[dataname])
        ax0[i].grid()
    fig0.tight_layout()
    canvas = FigureCanvas(fig0)
    output = io.BytesIO()
    canvas.print_png(output)
    response = fl.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/threeDdata')
def plot_threeDdata():
    conn = sqlite3.connect('../sensorsData.db')
    curs = conn.cursor()
    ts = {}
    ds = {}

    oneDLi = ['ldrdata','prsdata','tmpdata']
    ylims = {'ldrdata':[0, 500],
             'prsdata':[90000,110000],
             'tmpdata':[100,350],
             'accdata':[-1300,1300],
             'gyrdata':[-200,200],
             'magdata':[-100,100],
            }
    ylabels = {'ldrdata':'Light',
               'prsdata':'centiPascals',
               'tmpdata':'deciCelsius',
               'accdata':'mg',
               'gyrdata':'Gyro',
               'magdata':'Gauss',
              }
    threeDLi = ['accdata','gyrdata','magdata']
    for dataname in threeDLi:
        ts[dataname] = []
        ds[dataname+'x'] = []
        ds[dataname+'y'] = []
        ds[dataname+'z'] = []
        for row in curs.execute("SELECT * FROM "+dataname+" DESC LIMIT 300"):
            ts[dataname].append(dt.datetime.strptime(str(row[0]),"%Y-%m-%d %H:%M:%S:%f"))
            ds[dataname+'x'].append(row[1])
            ds[dataname+'y'].append(row[2])
            ds[dataname+'z'].append(row[3])
    conn.close()

    fig1,ax1 = plt.subplots(9,1,sharex=True,figsize=[10,12])
    for i,dataname in enumerate(threeDLi):
        ax1[i*3].plot(ts[dataname],ds[dataname+'x'])
        ax1[i*3].set_ylim(ylims[dataname])
        ax1[i*3].set_ylabel('x '+ylabels[dataname])
        ax1[i*3].grid()
        ax1[i*3+1].plot(ts[dataname],ds[dataname+'y'])
        ax1[i*3+1].set_ylim(ylims[dataname])
        ax1[i*3+1].set_ylabel('y '+ylabels[dataname])
        ax1[i*3+1].grid()
        ax1[i*3+2].plot(ts[dataname],ds[dataname+'z'])
        ax1[i*3+2].set_ylim(ylims[dataname])
        ax1[i*3+2].set_ylabel('z '+ylabels[dataname])
        ax1[i*3+2].grid()
    fig1.tight_layout()
    canvas = FigureCanvas(fig1)
    output = io.BytesIO()
    canvas.print_png(output)
    response = fl.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)

