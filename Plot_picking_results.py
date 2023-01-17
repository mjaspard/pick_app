#!/usr/bin/python3
#
#

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from statistics import mean 
import numpy as np
import math

##########
parser = argparse.ArgumentParser(description='Picker options')
parser.add_argument("csv_file", help="path to csv file", type=str)
args = parser.parse_args()

csv_file = args.csv_file
images_data = pd.read_csv(csv_file, comment='#', na_values=['99999','0'])

images_number = len(images_data['filepath'])
timestr = images_data.iloc[:,1:3].astype(str).apply('T'.join,axis=1)
times = pd.to_datetime(timestr, format='%Y%m%dT%H:%M:%S')

##########
Zvolc = 3460
Zb2002 = 2880
t1=datetime.datetime.strptime('2021-05-13T00:00:00', "%Y-%m-%dT%H:%M:%S");
t2=datetime.datetime.strptime('2021-07-10T00:00:00', "%Y-%m-%dT%H:%M:%S");
Terupt = datetime.datetime.strptime('2021-05-22T16:30:00', "%Y-%m-%dT%H:%M:%S");

#t1=datetime.datetime.strptime('2003-01-01T00:00:00', "%Y-%m-%dT%H:%M:%S");
#t2=datetime.datetime.strptime('2008-01-01T00:00:00', "%Y-%m-%dT%H:%M:%S");
##########

# Pixel size and incidence angle
azimuth_pixel_size = images_data['azimuth_pixel_size']
range_pixel_size = images_data['range_pixel_size']
incidence_angle_deg = images_data['incidence_angle_deg']
incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360
cosincid=np.cos(incidence_angle_rad)
sinincid=abs(np.sin(incidence_angle_rad))

##########


Rcald_m = images_data['Rcald_m']
RP2_m = images_data['RP2_m']
Rcrat_m = images_data['Rcrat_m']
Rbot_m = images_data['Rbot_m']
delta_x = images_data['delta_x_m']
HP2 = images_data['HP2_m']
h = images_data['h']
H = images_data['H']
Alpha = images_data['Alpha']
Beta = images_data['Beta']	

cald_area = math.pi * Rcald_m * Rcald_m
P2_area = math.pi * RP2_m * RP2_m
crat_area = math.pi * Rcrat_m * Rcrat_m
bot_area = math.pi * Rbot_m * Rbot_m

errH = Rbot_m * sinincid / cosincid
indpos=incidence_angle_deg>0
indneg=incidence_angle_deg<0


##########
mks = 10
LW = 2
fig, [ax1, ax2] = plt.subplots(2, 1, sharex=True, figsize=(20,10))
ax1.set_xlim(t1, t2)
ax1.errorbar(times, Rcald_m, yerr=2*azimuth_pixel_size, xerr=None,color='blue',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=5,label='$R_s$')
ax1.errorbar(times, RP2_m, yerr=3*azimuth_pixel_size, xerr=None,color='cyan',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=5,label='$R_{P2}$')
ax1.errorbar(times, Rcrat_m, yerr=4*azimuth_pixel_size, xerr=None,color='red',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=5,label='$R_c$')
ax1.errorbar(times, Rbot_m, yerr=5*azimuth_pixel_size, xerr=None,color='magenta',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=5,label='$R_b$')
ax1.plot([t1, t2],[mean(Rcald_m),mean(Rcald_m)],'--',color='blue')
ax1.plot([t1, t2],[mean(RP2_m),mean(RP2_m)],'--',color='cyan')
ax1.plot([t1, t2],[100,100],'--',color='magenta')
ax1.plot([t1, t2],[350, 350],'--',color='red')

ax1.legend(loc='center left',fontsize=14,bbox_to_anchor=(1, 0.5))
ax1.set_xlabel('Time',fontsize=18)
ax1.set_ylabel('Radius (m)',fontsize=18)


ax2.errorbar(times, Zvolc-HP2, yerr=10*range_pixel_size/cosincid, xerr=None,color='cyan',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=5,label='$Z_{P2}$')
ax2.errorbar(times[indpos],Zvolc-HP2[indpos]-H[indpos], yerr=errH[indpos], xerr=None,color='magenta',ms=mks, fmt='^', ecolor='black', elinewidth=LW, capsize=5,label='$Z_{b; {\\theta}>0}$')
ax2.errorbar(times[indneg],Zvolc-HP2[indneg]-H[indneg], yerr=errH[indneg], xerr=None,color='magenta',ms=mks, fmt='v', ecolor='black', elinewidth=LW, capsize=5,label='$Z_{b;{\\theta}<0}$')
ax2.plot([t1, t2],[Zvolc, Zvolc],color='blue', label='$Z_s$')
ax2.plot([t1, t2],[Zvolc-mean(HP2), Zvolc-mean(HP2)],'--',color='red', label='$Z_{P2}$')
ax2.plot([t1, t2],[Zb2002, Zb2002],':', color='gray', label='$Z_b^{2002}$')

ax1.plot([Terupt, Terupt],[0, 700],'-.',color='black')
ax2.plot([Terupt, Terupt],[2500, 3500],'-.',color='black')


ax2.set_xlabel('Time',fontsize=18)
ax2.set_ylabel('Elevation (m)',fontsize=18)
ax2.legend(loc='center left',fontsize=14,bbox_to_anchor=(1, 0.5))
ax2.tick_params(axis='both',labelsize=16)
ax1.tick_params(axis='y',labelsize=16)

plt.show()

exit()

fig, [ax1, ax2, ax3] = plt.subplots(3, 1, sharex=True, figsize=(20,10))
ax1.set_xlim(t1,t2)

ax1.errorbar(times, -HP2, yerr=5*range_pixel_size/cosincid, xerr=None,color='cyan', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$D_{P2}$')
ax1.errorbar(times[indpos],-HP2[indpos]-H[indpos], yerr=errH[indpos], xerr=None,color='magenta', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$D_{b; {\\theta}>0}$')
ax1.errorbar(times[indneg],-HP2[indneg]-H[indneg], yerr=errH[indneg], xerr=None,color='green', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$D_{b;{\\theta}<0}$')
ax1.plot([t1, t2],[0, 0],color='blue')
ax1.plot([t1, t2],[-mean(HP2), -mean(HP2)],'--',color='red')

ax1.set_xlabel('Time',fontsize=18)
ax1.set_ylabel('Depth from crater rim (m)',fontsize=18)
ax1.legend(loc='center left',fontsize=14,bbox_to_anchor=(1, 0.5))


ax2.errorbar(times[indpos],delta_x[indpos], yerr=5*range_pixel_size[indpos]/sinincid[indpos], xerr=None,color='magenta', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$\delta X;{\\theta}>0}$')
ax2.errorbar(times[indneg],-delta_x[indneg], yerr=5*range_pixel_size[indneg]/sinincid[indneg], xerr=None,color='green', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$-\delta X;{\\theta}<0}$')
ax2.set_xlabel('Time',fontsize=18)
ax2.set_ylabel('$\delta X$',fontsize=18)
ax2.legend(loc='center left',fontsize=14,bbox_to_anchor=(1, 0.5))

ax3.plot(times[indpos],Alpha[indpos],'o',color='magenta',label='${\\alpha};{\\theta}>0}$')
ax3.plot(times[indneg],Alpha[indneg],'o',color='green',label='${\\alpha};{\\theta}<0}$')
ax3.set_ylim(0,1)
ax3.plot(times,Beta,'o',color='yellow',label='Beta')

ax3.set_xlabel('Time',fontsize=18)
ax3.set_ylabel('${\\alpha}$',fontsize=18)
ax3.legend(loc='center left',fontsize=14,bbox_to_anchor=(1, 0.5))

ax3.plot([t1, t2],[0.2, 0.2],'--',color='red')

ax1.plot([Terupt, Terupt],[-1000, 0],'-.',color='black')
ax2.plot([Terupt, Terupt],[-50, 250],'-.',color='black')
ax3.plot([Terupt, Terupt],[0, 1],'-.',color='black')
ax3.tick_params(axis='both',labelsize=16)
ax2.tick_params(axis='y',labelsize=16)
ax1.tick_params(axis='y',labelsize=16)

plt.show()

exit()


fig, [ax1, ax2] = plt.subplots(2, 1, sharex=True, figsize=(20,10))

ax1.errorbar(times, cald_area/1e6, yerr=2*2*math.pi*azimuth_pixel_size * Rcald_m/1e6, xerr=None,color='blue', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$A_s$')
ax1.errorbar(times, P2_area/1e6, yerr=3*2*math.pi*azimuth_pixel_size * RP2_m/1e6, xerr=None,color='cyan', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$A_{P2}$')
ax1.errorbar(times, crat_area/1e6, yerr=6*2*math.pi*azimuth_pixel_size * Rcrat_m/1e6, xerr=None,color='red', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$A_c$')
ax1.errorbar(times, bot_area/1e6, yerr=6*2*math.pi*azimuth_pixel_size * Rbot_m/1e6, xerr=None,color='magenta', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$A_b$')

ax1.plot([t1, t2],[mean(cald_area)/1e6,mean(cald_area)/1e6],'--',color='blue')
ax1.plot([t1, t2],[mean(P2_area)/1e6,mean(P2_area)/1e6],'--',color='cyan')
ax1.plot([t1, t2],[100*100*math.pi/1e6,100*100*math.pi/1e6],'--',color='magenta')
ax1.plot([t1, t2],[350*350*math.pi/1e6,350*350*math.pi/1e6],'--',color='red')

ax1.plot([Terupt, Terupt],[0, 1.6],'-.',color='black')
ax2.plot([Terupt, Terupt],[2500, 3500],'-.',color='black')

ax1.set_xlim(t1, t2)
ax1.set_ylabel('Area ($10^6$ m$^2$)',fontsize=18)
ax1.ticklabel_format(style='sci', axis='y', scilimits=(-1,8))

ax1.legend(loc='center left',fontsize=14,bbox_to_anchor=(1, 0.5))
ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1440*3))
ax1.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1440))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))     #optional formatting 
ax2.tick_params(axis='both',labelsize=16)
ax1.tick_params(axis='y',labelsize=16)


ax2.errorbar(times, Zvolc-HP2, yerr=5*range_pixel_size/cosincid, xerr=None,color='cyan', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$Z_{P2}$')
ax2.errorbar(times,Zvolc-HP2-H, yerr=errH, xerr=None,color='magenta', fmt='o', ecolor='black', elinewidth=1, capsize=5,label='$Z_b$')
ax2.plot([t1, t2],[Zvolc, Zvolc],color='blue', label='$Z_s$')
ax2.plot([t1, t2],[Zvolc-mean(HP2), Zvolc-mean(HP2)],'--',color='red')
ax2.plot([t1, t2],[Zb2002, Zb2002],':',color='gray', label='$Z_b2002$')

ax2.set_xlabel('Time',fontsize=18)
ax2.set_ylabel('Elevation (m)',fontsize=18)
ax2.legend(loc='center left',fontsize=14,bbox_to_anchor=(1, 0.5))



