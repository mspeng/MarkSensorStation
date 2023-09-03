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
    conn = sqlite3.connect('./sensorsData.db')
    curs = conn.cursor()
    ts = {}
    ds = {}
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
        for row in curs.execute("SELECT * FROM "+dataname+" ORDER BY timestamp DESC LIMIT 300"):
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

### apply filters to see if got data correctly
tsamp = 0.1  # seconds
winSizeL = 600
winSizeM = 60
stdThresDi = {'ldrdata':5,
              'accdata':7,
              'gyrdata':2,
              'magdata':5,
              }

# new downsampled data
tdss = {}
ddss = {}

# downsample tmp and prs data regardless
datanameLi = ['prsdata','tmpdata']
for dataname in datanameLi:
    tdss[dataname] = []
    ddss[dataname] = []
    for i in range(0,len(ts[dataname])//winSizeM):
        # take middle timept
        tdss[dataname].append(ts[dataname][i*winSizeM+winSizeM//2])  
        ddss[dataname].append(sum(ds[dataname][i*winSizeM:(i+1)*winSizeM])/winSizeM)

# downsample ldr data 
datanameLi = ['ldrdata']
for dataname in datanameLi:
    tdss[dataname] = []
    ddss[dataname] = []
    # for first data, record it all
    for i in range(winSizeL):
        tdss[dataname].append(ts[dataname][i])  # take first data
        ddss[dataname].append(ds[dataname][i])
    # calculate initial data
    currdata = ds[dataname][0*winSizeL:(0+1)*winSizeL]
    prevavg = np.mean(currdata)
    prevstd = np.std(currdata)
    # run through the rest of the data
    for i in range(1,len(ts[dataname])//winSizeL):
        currdata = ds[dataname][i*winSizeL:(i+1)*winSizeL]
        curravg = np.mean(currdata)
        currstd = np.std(currdata)
        if currstd < stdThresDi[dataname]:
            # take middle timept
            tdss[dataname].append(ts[dataname][i*winSizeL+winSizeL//2]) 
            ddss[dataname].append(curravg)
        else:
            # write all the data
            for j in range(winSizeL):
                tdss[dataname].append(ts[dataname][i*winSizeL+j])
                ddss[dataname].append(ds[dataname][i*winSizeL+j])
# downsample 3-axis data
datanameLi = ['accdata','gyrdata','magdata']
for dataname in datanameLi:
    tdss[dataname] = []
    ddss[dataname+'x'] = []
    ddss[dataname+'y'] = []
    ddss[dataname+'z'] = []
    # for first data, record it all
    for i in range(winSizeL):
        tdss[dataname].append(ts[dataname][i])  # take first data
        ddss[dataname+'x'].append(ds[dataname+'x'][i])
        ddss[dataname+'y'].append(ds[dataname+'y'][i])
        ddss[dataname+'z'].append(ds[dataname+'z'][i])
    # calculate initial data
    currdatax = ds[dataname+'x'][0*winSizeL:(0+1)*winSizeL]
    currdatay = ds[dataname+'y'][0*winSizeL:(0+1)*winSizeL]
    currdataz = ds[dataname+'z'][0*winSizeL:(0+1)*winSizeL]
    prevavgx = np.mean(currdatax)
    prevavgy = np.mean(currdatay)
    prevavgz = np.mean(currdataz)
    prevstdx = np.std(currdatax)
    prevstdy = np.std(currdatay)
    prevstdz = np.std(currdataz)
    # run through the rest of the data
    for i in range(1,len(ts[dataname])//winSizeL):
        currdatax = ds[dataname+'x'][i*winSizeL:(i+1)*winSizeL]
        currdatay = ds[dataname+'y'][i*winSizeL:(i+1)*winSizeL]
        currdataz = ds[dataname+'z'][i*winSizeL:(i+1)*winSizeL]
        curravgx = np.mean(currdatax)
        curravgy = np.mean(currdatay)
        curravgz = np.mean(currdataz)
        currstdx = np.std(currdatax)
        currstdy = np.std(currdatay)
        currstdz = np.std(currdataz)
        if (currstdx**2 + currstdy**2 + currstdz**2)**0.5 < stdThresDi[dataname]:
            # take middle timept
            tdss[dataname].append(ts[dataname][i*winSizeL+winSizeL//2]) 
            ddss[dataname+'x'].append(curravgx)
            ddss[dataname+'y'].append(curravgy)
            ddss[dataname+'z'].append(curravgz)
        else:
            # write all the data
            for j in range(winSizeL):
                tdss[dataname].append(ts[dataname][i*winSizeL+j])
                ddss[dataname+'x'].append(ds[dataname+'x'][i*winSizeL+j])
                ddss[dataname+'y'].append(ds[dataname+'y'][i*winSizeL+j])
                ddss[dataname+'z'].append(ds[dataname+'z'][i*winSizeL+j])


### plot new data
fig0,ax0 = plt.subplots(3,1,sharex=True,figsize=[10,8])
for i,dataname in enumerate(oneDLi):
    ax0[i].plot(ts[dataname],ds[dataname])
    ax0[i].plot(tdss[dataname],ddss[dataname],'r-')
    ax0[i].set_ylim(ylims[dataname])
    ax0[i].set_ylabel(ylabels[dataname])
    ax0[i].grid()
    print(dataname,len(ts[dataname]),len(ds[dataname]),
          len(tdss[dataname]),len(ddss[dataname]))
fig0.tight_layout()
fig1,ax1 = plt.subplots(9,1,sharex=True,figsize=[10,12])
for i,dataname in enumerate(threeDLi):
    ax1[i*3].plot(ts[dataname],ds[dataname+'x'])
    ax1[i*3].plot(tdss[dataname],ddss[dataname+'x'],'r-')
    ax1[i*3].set_ylim(ylims[dataname])
    ax1[i*3].set_ylabel('x '+ylabels[dataname])
    ax1[i*3].grid()
    ax1[i*3+1].plot(ts[dataname],ds[dataname+'y'])
    ax1[i*3+1].plot(tdss[dataname],ddss[dataname+'y'],'r-')
    ax1[i*3+1].set_ylim(ylims[dataname])
    ax1[i*3+1].set_ylabel('y '+ylabels[dataname])
    ax1[i*3+1].grid()
    ax1[i*3+2].plot(ts[dataname],ds[dataname+'z'])
    ax1[i*3+2].plot(tdss[dataname],ddss[dataname+'z'],'r-')
    ax1[i*3+2].set_ylim(ylims[dataname])
    ax1[i*3+2].set_ylabel('z '+ylabels[dataname])
    ax1[i*3+2].grid()
    print(dataname,len(ts[dataname]),len(ds[dataname+'x']),
          len(ds[dataname+'y']),len(ds[dataname+'z']),
          len(tdss[dataname]),len(ddss[dataname+'x']),
          len(ddss[dataname+'y']),len(ddss[dataname+'z']))
fig1.tight_layout()
plt.show()
#fig0.savefig('oneDdata.png')
#fig1.savefig('threeDdata.png')
