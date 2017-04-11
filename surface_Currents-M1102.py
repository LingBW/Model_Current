# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 09:30:19 2016
Surface currents : with the long streamline as I expect.
Tha last improve at 4/11/2017, The best streamline I have ever made.
@author: Bingwei Ling
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 15:54:43 2014
This routine can plot both the observed and modeled drifter tracks.
It has various options including how to specify start positions, how long to track, 
whether to generate animation output, etc. See Readme.
@author: Bingwei Ling
Derived from previous particle tracking work by Manning, Muse, Cui, Warren.
"""

import sys
#import pytz
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from surface_Currents_M_functions1102 import get_fvcom,draw_basemap,totdis
from matplotlib import animation
import matplotlib as mpl
from pydap.client import open_url

st_run_time = datetime.now() # Caculate execution time with en_run_time
############################### Options #######################################
'''
Option 1: Drifter track.
Option 2: Specify the start point.
Option 3: Specify the start point with simulated map.
Option 4: Area(box) track.          
'''
######## Hard codes ##########
MODEL = 'GOM3'     # 'ROMS', 'GOM3','massbay','30yr'
GRIDS = ['GOM3','massbay','30yr']    # All belong to FVCOM. '30yr' works from 1977/12/31 22:58 to 2014/1/1 0:0
#depth = 1    # depth below ocean surface, positive
track_hours = 24    #MODEL track time(days)
track_way = 'forward'    # Three options: backward, forward and both. 'both' only apply to Option 2 and 3.
image_style = 'plot'      # Two option: 'plot', animation
# You can track form now by specify start_time = datetime.now(pytz.UTC) 
#start_time = datetime(2013,10,19,12,0,0,0)#datetime.now(pytz.UTC) 
start_time = datetime.utcnow()
end_time = start_time + timedelta(hours=track_hours)

model_boundary_switch = 'ON' # OFF or ON. Only apply to FVCOM
streamline = 'OFF'
wind = 'OFF'
bcon = 'stop' #boundary-condition: stop,reflection

save_dir = './Results/'
#colors = ['magenta','cyan','olive','blue','orange','green','red','yellow','black','purple']
#'#0039b3','#0049e6','#1a62ff','#4d85ff','#80a8ff',,'#b3cbff','#e6eeff'
#colors = ['#99ffff','#b3ffff','#ccffff','#e6ffff','#ffffff','#ffebe6','#ffc2b3','#ff9980','#ff704d','#ff471a','#e62e00','#b32400'] #16
colors = ['#00bfff','#00ffff','#00ffbf','#00ff80','#80ff00','#bfff00','#ffff00','#ffbf00','#ff8000','#ff4000']
cmap = mpl.colors.ListedColormap(colors)

utcti = datetime.utcnow(); utct = utcti.strftime('%H')
locti = datetime.now(); loct = locti.strftime('%H')
ditnu = int(utct)-int(loct) # the deference between UTC and local time .
if ditnu < 0:
    ditnu = int(utct)+24-int(loct)
locstart_time = start_time - timedelta(hours=ditnu)

################################## Option ####################################
#centerpoint = (41.91,-70.233)
centerpoint = (41.578,-69.326)
bordersidele = 0.6
#lats = get_obj.points_square(centerpoint,0.1)

############################## Common codes ###################################

#loop_length = []
fig = plt.figure() #figsize=(16,9)
ax = fig.add_subplot(111)
points = {'lats':[],'lons':[]}  # collect all points we've gained
#points['lons'].extend(lons);points['lats'].extend(lats)
#ax.plot(lats,lons,'bo',markersize=3)
#draw_basemap(ax, points)  # points is using here  
#plt.show()    

get_obj = get_fvcom(MODEL)
toltime,pby = get_obj.get_data(start_time,end_time,centerpoint,bordersidele)
points['lons'].extend(pby[1]);points['lats'].extend(pby[0]) 
#b_points = get_obj.get_data(url_fvcom)# b_points is model boundary points.
# Core codes
currents_points = {}
for j in range(track_hours):#len(toltime)
    #if j==0 or (j+1)%24==0 :
    # Make change at 4/11/2017 09:31, to
    if j%4==0 :
        cpoints = get_obj.current_track(j)
        currents_points[toltime[j]] = cpoints

   
try:
    pd.DataFrame(currents_points).to_csv(st_run_time.strftime("%d-%b-%Y_%H:%M")+'currents_points.csv')
    #np.save('currents_points',np.array(currents_points))
except:
    print 'Failed to save the data to a file.'
    pass
#lcp = len(currents_points)
'''spds = []
for a in currents_points:
    lb = currents_points[a]
    for i in range(len(lb)):
        spds.extend(lb[i]['spd'])#;points['lats'].extend(cpoints[i]['lat']);   
        if len(cpoints[i]['time']) > len(maxtime):
            maxtime = cpoints[i]['time']#'''

#minspd = np.argmin(crang-speed)
#ax.plot(points['lons'],points['lats'])
#ax.plot(psqus[1],psqus[0])
draw_basemap(ax, points)  # points is using here
'''
levels=np.arange(-80,0,10)
ss=1
cont_range = [-3,0]
draw_parallels = 'ON'
url='http://geoport.whoi.edu/thredds/dodsC/bathy/gom03_v1_0'
dataset=open_url(url)
basemap_lat=dataset['lat']
basemap_lon=dataset['lon']
basemap_topo=dataset['topo']
minlat=min(points['lats'])
maxlat=max(points['lats'])
minlon=min(points['lons'])
maxlon=max(points['lons'])
index_minlat=int(round(np.interp(minlat,basemap_lat,range(0,basemap_lat.shape[0]))))-2
index_maxlat=int(round(np.interp(maxlat,basemap_lat,range(0,basemap_lat.shape[0]))))+2
index_minlon=int(round(np.interp(minlon,basemap_lon,range(0,basemap_lon.shape[0]))))-2
index_maxlon=int(round(np.interp(maxlon,basemap_lon,range(0,basemap_lon.shape[0]))))+2
min_index_lat=min(index_minlat,index_maxlat)
max_index_lat=max(index_minlat,index_maxlat)
min_index_lon=min(index_minlon,index_maxlon)
max_index_lon=max(index_minlon,index_maxlon)
X,Y=np.meshgrid(basemap_lon[min_index_lon:max_index_lon:ss],basemap_lat[min_index_lat:max_index_lat:ss])
'''


lminlat0 = min(points['lats'])+0.01;lmaxlon0 = max(points['lons'])-0.07
lminlat1 = lminlat0; lmaxlon1 = lmaxlon0+3600*0.44704/(111111*np.cos(lminlat0*np.pi/180))
dx = lmaxlon1-lmaxlon0; dy = lminlat1-lminlat0
unil = math.sqrt(dx**2+dy**2); print 'unit length', unil
crang = np.linspace(0,10*unil, num=10) #color range
norm = mpl.colors.Normalize(vmin=0, vmax=10*unil)

cax = fig.add_axes([0.85, 0.2, 0.02, 0.6])                    
cb1 = mpl.colorbar.ColorbarBase(cax, cmap=cmap,norm=norm,spacing='proportional',orientation='vertical')#,orientation='horizontal')
cb1.set_label('MPH')#'''

def animate(n): #del ax.collections[:]; del ax.lines[:]; ax.cla(); ax.lines.remove(line)        
    '''if track_way=='backward':
        Time = (locstart_time-timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")
    else:
        Time = (locstart_time+timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")#'''
    #plt.suptitle('%.f%% simulated drifters ashore\n%d days, %d m, %s'%(int(round(p)),track_days,depth,Time))
    #plt.suptitle('Current model %d' % n)
    plt.suptitle('FVCOM Surface Currents \n' + toltime[n].strftime("%d-%b-%Y %H:%M"))
    del ax.lines[:] 
    #ax.cla()
    #CS=ax.contour(X,Y,basemap_topo.topo[min_index_lat:max_index_lat:ss,index_minlon:index_maxlon:ss],levels,cmap=plt.cm.gist_earth,linewidths=0.5)
    #ax.clabel(CS,fmt='%5.0f')#, np.arange(-80,0,20), inline=1)fontsize=3,
    #ax.contourf(X,Y,basemap_topo.topo[min_index_lat:max_index_lat:ss,min_index_lon:max_index_lon:ss],[0,1000],colors='gray')
    for k in currents_points:
        if k <= toltime[n]:
            kl = currents_points[k]
            for j in kl:
                #if any(j.keys()==toltime[n]):
                if toltime[n] in j.keys():
                    
                    ps = j[toltime[n]]
                    pst = np.array(ps).T
                    speed = totdis(pst[0],pst[1])
                    cl = colors[np.argmin(abs(crang-speed))]
                    ax.plot(pst[0],pst[1],'-',color=cl)
    ax.plot([lmaxlon0,lmaxlon1],[lminlat0,lminlat1],'-|',color='k',linewidth=3)
    ax.text(lmaxlon1,lminlat1+0.004,'1 mph')
anim = animation.FuncAnimation(fig, animate, frames=track_hours,interval=1000) #,
en_run_time = datetime.now()
print 'Take '+str(en_run_time-st_run_time)+' running the code.\nStart at '+str(st_run_time)+'\nEnd at   '+str(en_run_time)
#print 'Min-spd,max-spd',crang[0],crang[-1]
anim.save(save_dir+'%s-%s_%s.gif'%(MODEL,track_way,en_run_time.strftime("%d-%b-%Y_%H:%M")),writer='imagemagick',dpi=250) #,,,fps=1
plt.show()
