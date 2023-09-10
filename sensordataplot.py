import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import sqlite3
import os
import pickle

oneDLi = ['ldrdata','prsdata','tmpdata']
ylims = {'ldrdata':[0, 2300],
         'prsdata':[98000,106000],
         'tmpdata':[100,350],
         'accdata':[-1300,1300],
         'gyrdata':[-200,200],
         'magdata':[-150,150],
        }
ylabels = {'ldrdata':'Light',
           'prsdata':'centiPascals',
           'tmpdata':'deciCelsius',
           'accdata':'mg',
           'gyrdata':'Gyro',
           'magdata':'Gauss',
          }
threeDLi = ['accdata','gyrdata','magdata']
# get data from picked if it exists otherwise get it from the db
if os.path.isfile('./sensorsData.pickle'):
    print('using pickled data')
    with open('sensorsData.pickle','rb') as f:
        ts,ds = pickle.load(f)
else:
    ts = {}
    ds = {}
    conn = sqlite3.connect('./sensorsData.db')
    curs = conn.cursor()
    for dataname in oneDLi:
        ts[dataname] = []
        ds[dataname] = []
        for row in curs.execute("SELECT * FROM "+dataname+" ORDER BY timestamp DESC LIMIT 900300"):
        #for row in curs.execute("SELECT * FROM "+dataname+" ORDER BY timestamp"):
            ts[dataname].append(dt.datetime.strptime(str(row[0]),"%Y-%m-%d %H:%M:%S:%f"))
            ds[dataname].append(row[1])
        print(dataname,max(ts[dataname]),min(ts[dataname]))
    for dataname in threeDLi:
        ts[dataname] = []
        ds[dataname+'x'] = []
        ds[dataname+'y'] = []
        ds[dataname+'z'] = []
        for row in curs.execute("SELECT * FROM "+dataname+" ORDER BY timestamp DESC LIMIT 900300"):
        #for row in curs.execute("SELECT * FROM "+dataname+" ORDER BY timestamp"):
            ts[dataname].append(dt.datetime.strptime(str(row[0]),"%Y-%m-%d %H:%M:%S:%f"))
            ds[dataname+'x'].append(row[1])
            ds[dataname+'y'].append(row[2])
            ds[dataname+'z'].append(row[3])
        print(dataname,max(ts[dataname]),min(ts[dataname]))
    conn.close()
    with open('./sensorsData.pickle','wb') as f:
        print('creating pickled data')
        pickle.dump([ts,ds],f)


fig0,ax0 = plt.subplots(3,1,sharex=True,figsize=[10,8])
for i,dataname in enumerate(oneDLi):
    ax0[i].plot(ts[dataname],ds[dataname],'o-')
    ax0[i].set_ylim(ylims[dataname])
    ax0[i].set_ylabel(ylabels[dataname])
    ax0[i].grid()
fig0.tight_layout()
fig1,ax1 = plt.subplots(9,1,sharex=True,figsize=[10,12])
for i,dataname in enumerate(threeDLi):
    ax1[i*3].plot(ts[dataname],ds[dataname+'x'],'x-')
    ax1[i*3].set_ylim(ylims[dataname])
    ax1[i*3].set_ylabel('x '+ylabels[dataname])
    ax1[i*3].grid()
    ax1[i*3+1].plot(ts[dataname],ds[dataname+'y'],'x-')
    ax1[i*3+1].set_ylim(ylims[dataname])
    ax1[i*3+1].set_ylabel('y '+ylabels[dataname])
    ax1[i*3+1].grid()
    ax1[i*3+2].plot(ts[dataname],ds[dataname+'z'],'x-')
    ax1[i*3+2].set_ylim(ylims[dataname])
    ax1[i*3+2].set_ylabel('z '+ylabels[dataname])
    ax1[i*3+2].grid()
fig1.tight_layout()
#plt.show()
fig0.savefig('oneDdata.png')
fig1.savefig('threeDdata.png')
