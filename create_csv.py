#!/usr/bin/env python
import subprocess, os, re
import sys
import os
import shutil
import fnmatch
import pandas as pd

# Run the other script

print("This script will generate an an empty csv file:\n")

csv_out = input("Please enter the name of the csv file to generate in the current folder:")
csv_out = "{}.csv".format(csv_out)
# initialise dataset
# Define the column names
column_names = ['folder','img_name','day','hour_UTC','azimuth_pixel_size','range_pixel_size','incidence_angle_deg','expo_greyscale','caldera_edgeN_x','caldera_edgeS_x','crater_outer_edgeN_x','crater_outer_edgeS_x','crater_inner_edgeN_x','crater_inner_edgeS_x','crater_topCone_edgeN_x','crater_topCone_edgeS_x','crater_bottom_edgeN_x','crater_bottom_edgeS_x','caldera_edgeN_y','caldera_edgeS_y','crater_outer_edgeN_y','crater_outer_edgeS_y','crater_inner_edgeN_y','crater_inner_edgeS_y','crater_topCone_edgeN_y','crater_topCone_edgeS_y','crater_bottom_edgeN_y','crater_bottom_edgeS_y','shadow1_x1','shadow1_x2','shadow2_x1','shadow2_x2']
# Initialize an empty dictionary for each column
dataset = {column: [] for column in column_names}
df = pd.DataFrame(dataset)
var_q = False

while(var_q != 'q'):
	# Ask user for folders to search for hdr files
	path_folder = input("Please enter the path to folder where to find envi files:")
	path_folder = path_folder.replace(" ", "") # remove extra spaces
	az_pix = input("Please enter azimuth pixels size for image in this folder:")
	sl_pix = input("Please enter slant range pixels size for image in this folder:")
	incid = input("Please enter incidence angle for image in this folder:")

	print("path folder = ", path_folder)
	img_list = [file for file in os.listdir(path_folder) if fnmatch.fnmatch(file, "*" + 'Crop.r4')]
	# img_list = [file for file in os.listdir(path_folder) if (not file.endswith('hdr') and not fnmatch.fnmatch(file, "*" + 'Filtre' + "*"))]
	img_path = [os.path.join(path_folder, filename) for filename in img_list]


	try:
		for img_name in img_list:
			# with open(hdr_file, 'r') as f:

			print("add file {}".format(img_name))
			try:
				day = re.search(r"[0-9]{8}", img_name)[0]
			except:
				try:
					day = re.search(r"[0-9]{6}", img_name)[0]
					day = "20{}".format(day)
				except:
					print("No date found in the file {}".format(img_name))
					day = "00000000"

			data = {'folder':[path_folder],'img_name':[img_name],'day':[day],'azimuth_pixel_size':[az_pix],'range_pixel_size':[sl_pix],'incidence_angle_deg':[incid],'expo_greyscale':["1.0"]}
			df2 = pd.DataFrame(data)

			df = pd.concat([df, df2], axis=0, ignore_index=True)
	except:
		print("Error occured")

	var_q = input("Press 'q' to stop adding files and create the csv file, or press enter to add image...")



print("\n Create csv file")
sort_date = input("By default, image will be sorted by folder name (satellite), and then by date. Would you like to sort by date only ? [Y/N]")
print(dataset)
if re.search(r"[yY]", sort_date):
	df = df.sort_values(by=['day'])
else:
	df = df.sort_values(by=['folder','day'])

df.to_csv(csv_out, index=False, header=True)


"""
'ALOS2A' :		AzPx=13.06;             SlRaPx=8.58;             	incid=-40.18;             	expo=1;
'ALOS2D' :		AzPx=13;             	SlRaPx=8.6;             	incid=41;             		expo=1;
'CSKA' :		AzPx=2.260303042116516; SlRaPx=1.249135241666667;   incid=-34.94558650375905;   expo=1;
'CSKD' :		AzPx=2.212050692338113; SlRaPx=0.9295890170542636;  incid=26.08606526943014;    expo=1;
'ENVISAT_A314' :AzPx = 3.24; 			SlRaPx=7.80 ;				incid = -43.14; 			expo=1;
'ENVISAT_D450' :AzPx = 3.24; 			SlRaPx=7.80 ; 				incid = 43.04; 				expo=1;
'ERS_A' :		AzPx=3.999;             SlRaPx=7.904;             incid=-24.2;             		expo=1;
'ERS_D' :		AzPx=3.999;             SlRaPx=7.905;             incid=-24.1;             		expo=1;
'RSAT1_D' :		AzPx=5.117;             SlRaPx=4.638;             incid=75.0;             		expo=1;
'RSAT1_A' :		AzPx=4.953;             SlRaPx=11.596;            incid=-44.27;             	expo=1;
'SAOCOM' :		AzPx=8.98;             	SlRaPx=4.51;              incid=30;             		expo=1;
'Sentinel1A' :	AzPx=14.04931;          SlRaPx=2.329562;          incid=-34.02086764440035;     expo=1;
'Sentinel1D' :	AzPx=14.04875;          SlRaPx=2.329562;          incid=39.3612049337785;       expo=1;
'TSXA' :		AzPx=3.00;             	SlRaPx=1.32;              incid=-26;             		expo=1;
'TSXD' :		AzPx=3.25;             	SlRaPx=1.099;             incid=21.5;             		expo=1;
"""