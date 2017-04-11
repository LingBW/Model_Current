# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 11:33:53 2016

@author: Bingwei Ling
"""

import sys
import netCDF4
#import calendar
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
from dateutil.parser import parse
#import pytz
from matplotlib.path import Path
import math
from mpl_toolkits.basemap import Basemap
import colorsys
from sympy import *
from sympy.geometry import *
from fractions import Fraction


def get_nc_data(url, *args):
    '''
    get specific dataset from url

    *args: dataset name, composed by strings
    ----------------------------------------
    example:
        url = 'http://www.nefsc.noaa.gov/drifter/drift_tcs_2013_1.dat'
        data = get_url_data(url, 'u', 'v')
    '''
    nc = netCDF4.Dataset(url)
    data = {}
    for arg in args:
        try:
            data[arg] = nc.variables[arg]
        except (IndexError, NameError, KeyError):
            print 'Dataset {0} is not found'.format(arg)
    return data
    
class get_fvcom():
    
    def __init__(self, mod):
        self.modelname = mod
    def points_square(self,point, hside_length):
        '''point = (lat,lon); length: units is decimal degrees.
           return a squre points(lats,lons) on center point,without center point'''
        ps = []
        (lat,lon) = point; 
        length =float(hside_length)
        #lats=[lat]; lons=[lon]
        #lats=[]; lons=[]
        bbox = [lon-length, lon+length, lat-length, lat+length]
        bbox = np.array(bbox)
        self.points = np.array([bbox[[0,1,1,0]],bbox[[2,2,3,3]]])
        #print points
        pointt = self.points.T
        for i in pointt:
            ps.append((i[1],i[0]))
        ps.append((pointt[0][1],pointt[0][0]))# add first point one more time for Path.
        #lats.extend(points[1]); lons.extend(points[0])
        #bps = np.vstack((lon,lat)).T
        #return lats,lons
        return ps
        
    def nearest_point(self, lon, lat, lons, lats, length):  #0.3/5==0.06
        '''Find the nearest point to (lon,lat) from (lons,lats),
           return the nearest-point (lon,lat)
           author: Bingwei'''
        p = Path.circle((lon,lat),radius=length)
        #numpy.vstack(tup):Stack arrays in sequence vertically
        points = np.vstack((lons.flatten(),lats.flatten())).T  
        
        insidep = []
        #collect the points included in Path.
        for i in xrange(len(points)):
            if p.contains_point(points[i]):# .contains_point return 0 or 1
                insidep.append(points[i])  
        # if insidep is null, there is no point in the path.
        if not insidep:
            print 'There is no model-point near the given-point.'
            raise Exception()
        #calculate the distance of every points in insidep to (lon,lat)
        distancelist = []
        for i in insidep:
            ss=math.sqrt((lon-i[0])**2+(lat-i[1])**2)
            distancelist.append(ss)
        # find index of the min-distance
        mindex = np.argmin(distancelist)
        # location the point
        lonp = insidep[mindex][0]; latp = insidep[mindex][1]
        
        return lonp,latp
        
    def get_data(self, starttime, endtime,point,leh):
        '''
        get different url according to starttime and endtime.
        urls are monthly.
        '''
        self.hours = int(round((endtime-starttime).total_seconds()/60/60))
        #print self.hours
                
        if self.modelname == "GOM3":
            turl = '''http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'''
            
            try:
                tdata = netCDF4.Dataset(turl).variables
                #MTime = tdata['time'] 
                MTime = tdata['Times']
            except:
                print '"GOM3" database is unavailable!'
                raise Exception()
            #Times = netCDF4.num2date(MTime[:],MTime.units)
            Times = []
            for i in MTime:
                strt = '201'+i[3]+'-'+i[5]+i[6]+'-'+i[8]+i[9]+' '+i[11]+i[12]+':'+i[14]+i[15]
                Times.append(datetime.strptime(strt,'%Y-%m-%d %H:%M'))#'''
            fmodtime = Times[0]; emodtime = Times[-1]         
            if starttime<fmodtime or starttime>emodtime or endtime<fmodtime or endtime>emodtime:
                print 'Time: Error! Model(GOM3) only works between %s with %s(UTC).'%(fmodtime,emodtime)
                raise Exception()
            npTimes = np.array(Times)
            tm1 = npTimes-starttime; #tm2 = mtime-t2
            index1 = np.argmin(abs(tm1))#'''
            #index1 = netCDF4.date2index(starttime,MTime,select='nearest')
            index2 = index1 + self.hours#'''
            #print 'index1,index2',index1,index2
            #url = url.format(index1, index2)
            self.mTime = Times[index1:index2+1]
            
            self.url = turl
            
        elif self.modelname == "massbay":
            timeurl = '''http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc?Times[0:1:144]'''
            url = """http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc?
            lon[0:1:98431],lat[0:1:98431],lonc[0:1:165094],latc[0:1:165094],siglay[0:1:9][0:1:98431],h[0:1:98431],
            nbe[0:1:2][0:1:165094],u[{0}:1:{1}][0:1:9][0:1:165094],v[{0}:1:{1}][0:1:9][0:1:165094],zeta[{0}:1:{1}][0:1:98431]"""
            
            try:
                mTime = netCDF4.Dataset(timeurl).variables['Times'][:]              
            except:
                print '"massbay" database is unavailable!'
                raise Exception()
            Times = []
            for i in mTime:
                strt = '201'+i[3]+'-'+i[5]+i[6]+'-'+i[8]+i[9]+' '+i[11]+i[12]+':'+i[14]+i[15]
                Times.append(datetime.strptime(strt,'%Y-%m-%d %H:%M'))
            fmodtime = Times[0]; emodtime = Times[-1]         
            if starttime<fmodtime or starttime>emodtime or endtime<fmodtime or endtime>emodtime:
                print 'Time: Error! Model(massbay) only works between %s with %s(UTC).'%(fmodtime,emodtime)
                raise Exception()
            npTimes = np.array(Times)
            tm1 = npTimes-starttime; #tm2 = mtime-t2
            index1 = np.argmin(abs(tm1))
            index2 = index1 + self.hours#'''
            url = url.format(index1, index2)
            self.mTime = Times[index1:index2+1]
            
            self.url = url

        elif self.modelname == "30yr": #start at 1977/12/31 23:00, end at 2014/1/1 0:0, time units:hours
            timeurl = """http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3?time[0:1:316008]"""
            url = '''http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3?h[0:1:48450],
            lat[0:1:48450],latc[0:1:90414],lon[0:1:48450],lonc[0:1:90414],nbe[0:1:2][0:1:90414],siglay[0:1:44][0:1:48450],
            u[{0}:1:{1}][0:1:44][0:1:90414],v[{0}:1:{1}][0:1:44][0:1:90414],zeta[{0}:1:{1}][0:1:48450]'''
            
            try:
                mtime = netCDF4.Dataset(timeurl).variables['time'][:]
            except:
                print '"30yr" database is unavailable!'
                raise Exception
            # get model's time horizon(UTC).
            '''fmodtime = datetime(1858,11,17) + timedelta(float(mtime[0]))
            emodtime = datetime(1858,11,17) + timedelta(float(mtime[-1]))
            mstt = fmodtime.strftime('%m/%d/%Y %H:%M')
            mett = emodtime.strftime('%m/%d/%Y %H:%M') #'''
            # get number of days from 11/17/1858
            t1 = (starttime - datetime(1858,11,17)).total_seconds()/86400 
            t2 = (endtime - datetime(1858,11,17)).total_seconds()/86400
            if not mtime[0]<t1<mtime[-1] or not mtime[0]<t2<mtime[-1]:
                #print 'Time: Error! Model(massbay) only works between %s with %s(UTC).'%(mstt,mett)
                print 'Time: Error! Model(massbay) only works between 1978-1-1 with 2014-1-1(UTC).'
                raise Exception()
            
            tm1 = mtime-t1; #tm2 = mtime-t2
            index1 = np.argmin(abs(tm1)); #index2 = np.argmin(abs(tm2)); print index1,index2
            index2 = index1 + self.hours
            url = url.format(index1, index2)
            Times = []
            for i in range(self.hours+1):
                Times.append(starttime+timedelta(hours=i))
            self.mTime = Times
            self.url = url
        #print url
        self.lonc, self.latc = tdata['lonc'][:], tdata['latc'][:]  #quantity:165095
        #self.lons, self.lats = self.data['lon'][:], self.data['lat'][:]
        #self.h = self.data['h'][:]; self.siglay = self.data['siglay'][:]; #
        #self.nv = self.data['nv'][:].T - 1 #nv = nc['nv'][:].T - 1
        #print 'tdata['u'][index1:index2+1]',len(tdata['u'][index1:index2+1])
        self.u = tdata['u'][index1:index2+1,0,:][:]; self.v = tdata['v'][index1:index2+1,0,:][:]#; self.zeta = self.data['zeta']
        
        nbe1=tdata['nbe'][0];nbe2=tdata['nbe'][1];
        nbe3=tdata['nbe'][2]
        pointt = np.vstack((nbe1,nbe2,nbe3)).T; self.pointt = pointt
        wl=[]
        for i in pointt:
            if 0 in i: 
                wl.append(1)
            else:
                wl.append(0)
        self.wl = wl
        tf = np.array(wl)
        self.inde = np.where(tf==True)
        #print len(self.u)
        #self.nbe = tdata['nbe'][:].T - 1
        # Get plot boundary
        (lat,lon) = point
        self.lonlp,self.latlp = self.shrink_data(lon,lat,self.lonc,self.latc,leh)
        #self.lonk,self.latk = self.shrink_data(lon,lat,self.lons,self.lats,leh)
        self.epoints = np.vstack((self.lonlp[::3],self.latlp[::3])).T
        
        return self.mTime,self.points#,nv lons,lats,lonc,latc,,h,siglay
        
    def shrink_data(self,lon,lat,lons,lats,le):
        lont = []; latt = []
        #p = Path.circle((lon,lat),radius=rad)
        self.psqus = self.points_square((lon,lat),le) # Got four point of rectangle with center point (lon,lat)
        codes = [Path.MOVETO,Path.LINETO,Path.LINETO,Path.LINETO,Path.CLOSEPOLY,]
        #print psqus
        self.sp = Path(self.psqus,codes)
        pints = np.vstack((lons,lats)).T
        for i in range(len(pints)):
            if self.sp.contains_point(pints[i]):
                lont.append(pints[i][0])
                latt.append(pints[i][1])
        lonl=np.array(lont); latl=np.array(latt)#'''
        if not lont:
            print 'Given point out of model area.'
            sys.exit()
        return lonl,latl
        
    def current_track(self,jn):
        cts = []
        
        numep = len(self.epoints)
        for i in range(numep):
            print '%d of %d, %d' % (i+1,numep,jn+1)
            getk = self.get_track(jn,self.epoints[i][0],self.epoints[i][1])
            #print type(getk['lon']),type(getk['lat']),type(getk['layer']),type(getk['spd'])
            #ld = min(len(getk['lon']),len(getk['lat']),len(getk['spd']))
            '''for j in getk:
                if len(getk[j])>ld:
                    getk[j] = getk[j][:ld]
            #print getk
            pgetk = pd.DataFrame(getk)#'''
            
            #print pgetk
            cts.append(getk)
        return cts#,self.points
        
    def get_track(self,jnu,lon,lat): #,b_index,nvdepth,,bcon 
        '''
        Get forecast points start at lon,lat
        '''
        #modpts = dict(lon=[lon], lat=[lat], time=[], spd=[]) #model forecast points, layer=[]
        modpts = {}
        #self.lonl,self.latl = self.shrink_data(lon,lat,self.lonc,self.latc,0.2)
            
        t = abs(self.hours) 
        #fps = [];a = 0 
        for i in xrange(t):
                                  
            if i<jnu: continue
            if i >= jnu+4: # break
                return modpts
            #fpst = []
            #for j in fps:
            fp = self.f_point(i,lon,lat)
            print len(fp)
            #if a < 1 : # Setting the length of the currents line.
                #fpst.insert(0,(lon,lat))
            #fps = fpst ; print len(fps)
            modpts[self.mTime[i]] = fp
            if len(fp)<2:#change -1 to 1 at 4/11/2017 09:28, start-point is second point from last track, not the last point.
                break
            (lon,lat) = fp[1] 
        return modpts
                  
    def f_point(self,a,lon,lat):
        '''
        forecast one elementpoint , if it out of the boundary, return None.
        '''
        pls = [(lon,lat)]
        for i in range(5):                
            try:
                if self.modelname == "GOM3" or self.modelname == "30yr":
                    lonp,latp = self.nearest_point(lon, lat, self.lonlp, self.latlp,0.1)
                    #lonn,latn = self.nearest_point(lon,lat,self.lonk,self.latk,0.3)
                if self.modelname == "massbay":
                    lonp,latp = self.nearest_point(lon, lat, self.lonlp, self.latlp,0.03)
                    #lonn,latn = self.nearest_point(lon,lat,self.lonk,self.latk,0.05)        
                index1 = np.where(self.lonc==lonp)
                index2 = np.where(self.latc==latp)
                elementindex = np.intersect1d(index1,index2); #print 'elementindex',elementindex
                if elementindex in self.inde[0]:
                    print 'boundary elementindex',elementindex,type(elementindex)
                    return pls  # hits the boundary.
            except:
                #raise
                return pls 
            #modpts['time'].append(self.mTime[i])
            u_t1 = self.u[a,elementindex][0]; v_t1 = self.v[a,elementindex][0]
                #u_t2 = self.u[i+1,layer,elementindex][0]; v_t2 = self.v[i+1,layer,elementindex][0]
            #u_t,v_t = self.uvt(u_t1,v_t1,u_t2,v_t2)
            #u_t = (u_t1+u_t2)/2; v_t = (v_t1+v_t2)/2
            
            dx = 60*60*u_t1; dy = 60*60*v_t1
            #pspeed = math.sqrt(u_t1**2+v_t1**2)
            #modpts['spd'].append(pspeed)
            #if i == t-1:# stop when got the last point speed.
                #return modpts,2
            #if i >= jnu+5:# break
                #return modpts,2
            #x,y = mapx(lon,lat)
            #temlon,temlat = mapx(x+dx,y+dy,inverse=True)            
            temlon = lon + (dx/(111111*np.cos(lat*np.pi/180)))
            temlat = lat + dy/111111 #''' 
            #print '%d,Lat,Lon,Speed'%(i+1),temlat,temlon,pspeed
            pls.append((temlon,temlat))
            lon = temlon; lat = temlat
        return pls
    
def draw_basemap(ax, points, interval_lon=0.1, interval_lat=0.1):
    '''
    draw the basemap?
    '''
    
    lons = points['lons']
    lats = points['lats']
    #size = max((max(lons)-min(lons)),(max(lats)-min(lats)))/2
    size = 0
    map_lon = [min(lons)-size,max(lons)+size]
    map_lat = [min(lats)-size,max(lats)+size]
    
    #ax = fig.sca(ax)
    dmap = Basemap(projection='cyl',
                   llcrnrlat=map_lat[0], llcrnrlon=map_lon[0],
                   urcrnrlat=map_lat[1], urcrnrlon=map_lon[1],
                   resolution='h',ax=ax)# resolution: c,l,i,h,f.
    dmap.drawparallels(np.arange(int(map_lat[0])-1,
                                 int(map_lat[1])+1,interval_lat),
                       labels=[1,0,0,0])
    dmap.drawmeridians(np.arange(int(map_lon[0])-1,
                                 int(map_lon[1])+1,interval_lon),
                       labels=[0,0,0,1])
    #dmap.drawcoastlines()
    dmap.fillcontinents(color='grey')
    dmap.drawmapboundary()
    #dmap.etopo()
    
def totdis(lons,lats):
    "return path length of list points" 
    ts = 0
    lp = len(lons)-1
    for i in xrange(lp):
        dx = lons[i+1]-lons[i]
        dy = lats[i+1]-lats[i]
        ds = math.sqrt(dx**2+dy**2)
        ts += ds
    return ts