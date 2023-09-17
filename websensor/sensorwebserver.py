#!/usr/bin/python

import flask as fl
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import sqlite3
import os,io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = fl.Flask(__name__)

# Retrieve data from database
def getData():
    datestr = dt.datetime.now().strftime("%Y%m%d")
    with open("../ldr_"+datestr+".csv",'r') as f:
        lines = f.readlines()
        row = lines[-1].strip().split(',')
        timeldr=row[0]
        ldr = int(row[1])
    with open("../tmp_"+datestr+".csv",'r') as f:
        lines = f.readlines()
        row = lines[-1].strip().split(',')
        timetmp=row[0]
        tmp = int(row[1])
    with open("../prs_"+datestr+".csv",'r') as f:
        lines = f.readlines()
        row = lines[-1].strip().split(',')
        timeprs=row[0]
        prs = int(row[1])
    with open("../acc_"+datestr+".csv",'r') as f:
        lines = f.readlines()
        row = lines[-1].strip().split(',')
        timeacc=row[0]
        accx,accy,accz = int(row[1]),int(row[2]),int(row[3])
    with open("../gyr_"+datestr+".csv",'r') as f:
        lines = f.readlines()
        row = lines[-1].strip().split(',')
        timegyr=row[0]
        gyrx,gyry,gyrz = int(row[1]),int(row[2]),int(row[3])
    with open("../mag_"+datestr+".csv",'r') as f:
        lines = f.readlines()
        row = lines[-1].strip().split(',')
        timemag=row[0]
        magx,magy,magz = int(row[1]),int(row[2]),int(row[3])

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

YLABELS = {'ldr':'Light',
           'prs':'centiPascals',
           'tmp':'deciCelsius',
           'acc':'Accel (mg)',
           'gyr':'Gyro',
           'mag':'Gauss',
          }
ONEDLI = ['ldr','tmp','prs']
THREEDLI = ['acc','gyr','mag']
MAXDATA = 5000

@app.route('/plot/oneDdata')
def plot_oneDdata():
   # Generate csv files in directory
    csvFilenames = sorted(list(filter(lambda f: f.endswith('.csv'),os.listdir(".."))))
    valsDi = {}
    tsDi = {}
    for dataname in ONEDLI:
        for filename in csvFilenames:
            if dataname in filename:
                if dataname not in valsDi.keys():
                    valsDi[dataname] = np.loadtxt('../'+filename,usecols=(1),delimiter=",",max_rows=MAXDATA)
                    tsDi[dataname] = np.loadtxt('../'+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname]))
                else:
                    valsDi[dataname] = np.append(valsDi[dataname],np.loadtxt('../'+filename,usecols=(1,),delimiter=",",max_rows=MAXDATA))
                    tsDi[dataname] = np.append(tsDi[dataname],np.loadtxt('../'+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname])-len(tsDi[dataname])))

    # Plot
    fig0,ax0 = plt.subplots(3,1,sharex=True,figsize=[10,12])
    for i,dataname in enumerate(ONEDLI):
        ax0[i].plot(tsDi[dataname],valsDi[dataname]) #,'o-')
        ax0[i].set_ylabel(YLABELS[dataname])
        ax0[i].grid()
    fig0.tight_layout()
    fig0.savefig('oneData.png')

    #canvas = FigureCanvas(fig0)
    #output = io.BytesIO()
    #canvas.print_png(output)
    #response = fl.make_response(output.getvalue())
    #response.mimetype = 'image/png'
    #return response

@app.route('/plot/threeDdata')
def plot_threeDdata():
   # Generate csv files in directory
    csvFilenames = sorted(list(filter(lambda f: f.endswith('.csv'),os.listdir(".."))))
    valsDi = {}
    tsDi = {}
    for dataname in THREEDLI:
        for filename in csvFilenames:
            if dataname in filename:
                if dataname not in valsDi.keys():
                    valsDi[dataname] = np.loadtxt('../'+filename,usecols=(1,2,3),delimiter=",",max_rows=MAXDATA)
                    tsDi[dataname] = np.loadtxt('../'+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname]))
                else:
                    valsDi[dataname] = np.append(valsDi[dataname],np.loadtxt('../'+filename,usecols=(1,2,3),delimiter=",",max_rows=MAXDATA),axis=0)
                    tsDi[dataname] = np.append(tsDi[dataname],np.loadtxt('../'+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname])-len(tsDi[dataname])))
    # Plot
    fig1,ax1 = plt.subplots(3,1,sharex=True,figsize=[10,12])
    for i,dataname in enumerate(THREEDLI):
        ax1[i].plot(tsDi[dataname],valsDi[dataname]) #,'x-')
        ax1[i].set_ylabel(YLABELS[dataname])
        ax1[i].legend(['x','y','z'])
        ax1[i].grid()
    fig1.tight_layout()
    fig1.savefig('threeData.png')

    #canvas = FigureCanvas(fig1)
    #output = io.BytesIO()
    #canvas.print_png(output)
    #response = fl.make_response(output.getvalue())
    #response.mimetype = 'image/png'
    #return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)

