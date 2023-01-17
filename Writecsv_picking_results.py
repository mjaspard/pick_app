#!/usr/bin/python3
#
#	/usr/bin/python3

import csv
import sys
import argparse
import pandas as pd
import os as os
import datetime
import math
import numpy as np

parser = argparse.ArgumentParser(description='Picker options')
parser.add_argument("csv_file", help="path to csv file", type=str)
args = parser.parse_args()

csv_file = args.csv_file

with open(csv_file, 'r') as f:
	# images_data = pd.read_csv(f, sep=',').to_dict()
	images_data = pd.read_csv(f, sep=',')
	# replace NaN values with 0
	images_data = images_data.fillna(0)
	#images_data = images_data.to_dict()
images_number = len(images_data['folder'])
i = 0
Zvolc = 3460
csv_file_out=csv_file + '_out.csv'
with open(csv_file_out, 'w', newline='') as csvfile:
	fieldnames = ['filepath', 'img_date','img_hour','azimuth_pixel_size','range_pixel_size','incidence_angle_deg','Rcald_m','RP2_m','Rcrat_m','Rbot_m','delta_x_m','HP2_m','h','H','Alpha','Beta']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	csvfile.close()

while i < images_number:	
	# File name
	img_dir = images_data['folder'][i]
	print(img_dir)
	img_name = images_data['img_name'][i]
	filepath = os.path.join(img_dir, img_name)

	# Acquisition time
	img_date_string = images_data['day'][i]
	img_hour_string = images_data['hour_UTC'][i]
	# Pixel size and incidence angle
	azimuth_pixel_size = images_data['azimuth_pixel_size'][i]
	range_pixel_size = images_data['range_pixel_size'][i]
	incidence_angle_deg = images_data['incidence_angle_deg'][i]
	incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360

	# Caldera ellipse
	caldera_edgeN_x = images_data['caldera_edgeN_x'][i]
	caldera_edgeN_y = images_data['caldera_edgeN_y'][i]
	caldera_edgeS_x = images_data['caldera_edgeS_x'][i]
	caldera_edgeS_y = images_data['caldera_edgeS_y'][i]

	# Crater outer ellipse
	crater_outer_edgeN_x = images_data['crater_outer_edgeN_x'][i]
	crater_outer_edgeN_y = images_data['crater_outer_edgeN_y'][i]
	crater_outer_edgeS_x = images_data['crater_outer_edgeS_x'][i]
	crater_outer_edgeS_y = images_data['crater_outer_edgeS_y'][i]

	# Crater inner ellipse
	crater_inner_edgeN_x = images_data['crater_inner_edgeN_x'][i]
	crater_inner_edgeN_y = images_data['crater_inner_edgeN_y'][i]
	crater_inner_edgeS_x = images_data['crater_inner_edgeS_x'][i]
	crater_inner_edgeS_y = images_data['crater_inner_edgeS_y'][i]

	# Crater outer ellipse
	crater_topCone_edgeN_x = images_data['crater_topCone_edgeN_x'][i]
	crater_topCone_edgeN_y = images_data['crater_topCone_edgeN_y'][i]
	crater_topCone_edgeS_x = images_data['crater_topCone_edgeS_x'][i]
	crater_topCone_edgeS_y = images_data['crater_topCone_edgeS_y'][i]

	# Crater outer ellipse
	crater_bottom_edgeN_x = images_data['crater_bottom_edgeN_x'][i]
	crater_bottom_edgeN_y = images_data['crater_bottom_edgeN_y'][i]
	crater_bottom_edgeS_x = images_data['crater_bottom_edgeS_x'][i]
	crater_bottom_edgeS_y = images_data['crater_bottom_edgeS_y'][i]

	####### Picked topography ###########
	Rcald_px_Az = abs(caldera_edgeS_y - caldera_edgeN_y)/2
	Rcald_m = Rcald_px_Az*azimuth_pixel_size
	
	RP2_px_Az=abs(crater_outer_edgeS_y - crater_outer_edgeN_y)/2
	RP2_m = RP2_px_Az*azimuth_pixel_size
	
	Rcrat_px_Az=abs(crater_inner_edgeS_y - crater_inner_edgeN_y)/2
	Rcrat_m = Rcrat_px_Az*azimuth_pixel_size
	
	Rbot_px_Az=abs(crater_bottom_edgeS_y - crater_bottom_edgeN_y)/2
	Rbot_m = Rbot_px_Az*azimuth_pixel_size
	
	
	caldcenterx = (caldera_edgeN_x + caldera_edgeS_x)/2
	P2centerx = (crater_outer_edgeN_x + crater_outer_edgeS_x)/2
	cratcenterx = (crater_inner_edgeN_x + crater_inner_edgeS_x)/2
	topconecenterx = (crater_topCone_edgeN_x + crater_topCone_edgeS_x)/2
	botcenterx = (crater_bottom_edgeN_x + crater_bottom_edgeS_x)/2

	delta_x = (P2centerx - cratcenterx)*range_pixel_size/(np.sin(incidence_angle_rad))
	HP2 = (abs(caldcenterx-P2centerx)*range_pixel_size)/np.cos(incidence_angle_rad)
	h = (abs(cratcenterx-topconecenterx)*range_pixel_size)/np.cos(incidence_angle_rad)
	H = (abs(cratcenterx-botcenterx)*range_pixel_size)/np.cos(incidence_angle_rad)
	
	if Rcrat_m != 0:
		Alpha = Rbot_m / Rcrat_m
	else:
		Alpha = 0
	if H != 0:	
		Beta = h / H
	else:
		Beta = 0

    	# Save to text file
	with open(csv_file_out, 'a', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writerow({'filepath':filepath, 'img_date':img_date_string,'img_hour':img_hour_string, 'azimuth_pixel_size':azimuth_pixel_size, 'range_pixel_size':range_pixel_size, 'incidence_angle_deg':incidence_angle_deg, 'Rcald_m':Rcald_m, 'RP2_m':RP2_m, 'Rcrat_m':Rcrat_m, 'Rbot_m':Rbot_m, 'delta_x_m':delta_x,'HP2_m':HP2,'h':h,'H':H,'Alpha':Alpha,'Beta':Beta})
		csvfile.close()
	i += 1

