import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os

ylims = {'ldr':[0, 2300],
         'prs':[98000,106000],
         'tmp':[100,350],
         'acc':[-1300,1300],
         'gyr':[-200,200],
         'mag':[-150,150],
        }
ylabels = {'ldr':'Light',
           'prs':'centiPascals',
           'tmp':'deciCelsius',
           'acc':'Accel (mg)',
           'gyr':'Gyro',
           'mag':'Gauss',
          }
ONEDLI = ['ldr','tmp','prs']
THREEDLI = ['acc','gyr','mag']
MAXDATA = 5000

PATH = "/home/pi/MarkSensorStation"

# Generate csv files in directory
csvFilenames = sorted(list(filter(lambda f: f.endswith('.csv'),os.listdir(PATH))))
print(PATH,csvFilenames)

valsDi = {}
tsDi = {}
for dataname in ONEDLI:
    for filename in csvFilenames:
        if dataname in filename:
            if dataname not in valsDi.keys():
                valsDi[dataname] = np.loadtxt(PATH+"/"+filename,usecols=(1),delimiter=",",max_rows=MAXDATA)
                tsDi[dataname] = np.loadtxt(PATH+"/"+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname]))
            else:
                valsDi[dataname] = np.append(valsDi[dataname],np.loadtxt(PATH+"/"+filename,usecols=(1,),delimiter=",",max_rows=MAXDATA))
                tsDi[dataname] = np.append(tsDi[dataname],np.loadtxt(PATH+"/"+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname])-len(tsDi[dataname])))
            print(dataname,len(tsDi[dataname]),len(valsDi[dataname]))
for dataname in THREEDLI:
    for filename in csvFilenames:
        if dataname in filename:
            if dataname not in valsDi.keys():
                valsDi[dataname] = np.loadtxt(PATH+"/"+filename,usecols=(1,2,3),delimiter=",",max_rows=MAXDATA)
                tsDi[dataname] = np.loadtxt(PATH+"/"+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname]))
            else:
                valsDi[dataname] = np.append(valsDi[dataname],np.loadtxt(PATH+"/"+filename,usecols=(1,2,3),delimiter=",",max_rows=MAXDATA),axis=0)
                tsDi[dataname] = np.append(tsDi[dataname],np.loadtxt(PATH+"/"+filename,usecols=(0),converters={0:lambda s:dt.datetime.strptime(str(s,'UTF-8'),"%Y-%m-%d %H:%M:%S:%f")},dtype='datetime64',delimiter=",",max_rows=len(valsDi[dataname])-len(tsDi[dataname])))
            print(dataname,len(tsDi[dataname]),len(valsDi[dataname]))


# Plot
fig0,ax0 = plt.subplots(3,1,sharex=True,figsize=[10,8])
for i,dataname in enumerate(ONEDLI):
    ax0[i].plot(tsDi[dataname],valsDi[dataname]) #,'o-')
    #ax0[i].set_ylim(ylims[dataname])
    ax0[i].set_ylabel(ylabels[dataname])
    ax0[i].grid()
fig0.tight_layout()
fig0.savefig('/home/pi/MarkSensorStation/websensor/static/oneDdata.png')
fig1,ax1 = plt.subplots(3,1,sharex=True,figsize=[10,12])
for i,dataname in enumerate(THREEDLI):
    ax1[i].plot(tsDi[dataname],valsDi[dataname]) #,'x-')
    #ax1[i].set_ylim(ylims[dataname])
    ax1[i].set_ylabel(ylabels[dataname])
    ax1[i].legend(['x','y','z'])
    ax1[i].grid()
fig1.tight_layout()
fig1.savefig('/home/pi/MarkSensorStation/websensor/static/threeDdata.png')
#plt.show()
