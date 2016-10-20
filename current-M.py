# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 09:30:19 2016

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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from Currents_M_functions import get_fvcom,draw_basemap
from matplotlib import animation

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
depth = 1    # depth below ocean surface, positive
track_hours = 36    #MODEL track time(days)
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
colors = ['#99ffff','#b3ffff','#ccffff','#e6ffff','#ffffff','#ffebe6','#ffc2b3','#ff9980','#ff704d','#ff471a','#e62e00','#b32400'] #16
utcti = datetime.utcnow(); utct = utcti.strftime('%H')
locti = datetime.now(); loct = locti.strftime('%H')
ditnu = int(utct)-int(loct) # the deference between UTC and local time .
if ditnu < 0:
    ditnu = int(utct)+24-int(loct)
locstart_time = start_time - timedelta(hours=ditnu)

################################## Option ####################################
centerpoint = (41.9,-70.26)
bordersidele = 0.15
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
url_fvcom,toltime = get_obj.get_url(start_time,end_time)
b_points = get_obj.get_data(url_fvcom)# b_points is model boundary points.
# Core codes
currents_points = {}
for j in range(track_hours):#len(toltime)
    cpoints,psqus = get_obj.current_track(j,centerpoint,depth,track_way,bordersidele,bcon)
    currents_points[toltime[j]] = cpoints
points['lons'].extend(psqus[1]);points['lats'].extend(psqus[0]) 
   
try:
    pd.DataFrame(currents_points).to_csv(st_run_time.strftime("%d-%b-%Y_%H:%M")+'currents_points.csv')
    #np.save('currents_points',np.array(currents_points))
except:
    print 'Failed to save the data to a file.'
    pass
#lcp = len(currents_points)
spds = []
for a in currents_points:
    lb = currents_points[a]
    for i in range(len(lb)):
        spds.extend(lb[i]['spd'])#;points['lats'].extend(cpoints[i]['lat']);   
        '''if len(cpoints[i]['time']) > len(maxtime):
            maxtime = cpoints[i]['time']#'''
crang = np.linspace(min(spds),max(spds), num=12) #color range
#minspd = np.argmin(crang-speed)
#ax.plot(points['lons'],points['lats'])
#ax.plot(psqus[1],psqus[0])
draw_basemap(ax, points)  # points is using here

def animate(n): #del ax.collections[:]; del ax.lines[:]; ax.cla(); ax.lines.remove(line)        
    '''if track_way=='backward':
        Time = (locstart_time-timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")
    else:
        Time = (locstart_time+timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")#'''
    #plt.suptitle('%.f%% simulated drifters ashore\n%d days, %d m, %s'%(int(round(p)),track_days,depth,Time))
    plt.suptitle('Current model %d' % n)
    del ax.lines[:]   
    #for k in range(len(maxtime)):  
        #print k
    #for j in xrange(lcp):
    for k in currents_points:
        kl = currents_points[k]
        for j in xrange(len(kl)):
            if any(kl[j]['time']==toltime[n]):
                nu = kl[j]['time'][kl[j]['time']==toltime[n]].index[0]
                
                if nu<1:    
                    speed = kl[j]['spd'][nu]
                    #if n<len(lon_set[j]):
                    #,label='Depth=10m' ,markersize=4
                    ax.plot(kl[j]['lon'][:nu+1],kl[j]['lat'][:nu+1],'-',color=colors[np.argmin(abs(crang-speed))])
                if nu>=1:
                    speed = kl[j]['spd'][nu-1]
                    #if n<len(lon_set[j]):
                    ax.plot(kl[j]['lon'][nu-1:nu+1],kl[j]['lat'][nu-1:nu+1],'-',color=colors[np.argmin(abs(crang-speed))])
anim = animation.FuncAnimation(fig, animate, frames=len(toltime),interval=500) #,
en_run_time = datetime.now()
print 'Take '+str(en_run_time-st_run_time)+' running the code. End at '+str(en_run_time)
anim.save(save_dir+'%s-%s_%s.gif'%(MODEL,track_way,en_run_time.strftime("%d-%b-%Y_%H:%M")),writer='imagemagick',dpi=250) #,,,fps=1
print 'Min-spd,max-spd',crang[0],crang[-1]
plt.show()
