
Procedure to follow to run PickCraterSAR application on a mac/linux machine


1. Create a python environment and install required package

git clone https://github.com/mjaspard/pick_app.git	# clone rep
cd pick_app					# go in repo folder
python -m venv env				# create python env (env is arbitrary)
source env/bin/activate				# activate env
python -m pip install -r requirements.txt	# Install required package (this list works fine with python3.8.1)
python start_app.py				# Run application

note: 	GDAL maybe tricky to install depending on dependencies already installed.(https://gdal.org/api/python_bindings.html)
		


2. Prepare data to load on application (csv file)


Once the application opened, you can open your csv file in the menubar 'File --> Open'
This csv file must be conform to the following structure starting with the following line:

'folder,img_name,day,hour_UTC,azimuth_pixel_size,range_pixel_size,incidence_angle_deg,expo_greyscale,caldera_edgeN_x,caldera_edgeS_x,crater_outer_edgeN_x,crater_outer_edgeS_x,crater_inner_edgeN_x,crater_inner_edgeS_x,crater_topCone_edgeN_x,crater_topCone_edgeS_x,crater_bottom_edgeN_x,crater_bottom_edgeS_x,caldera_edgeN_y,caldera_edgeS_y,crater_outer_edgeN_y,crater_outer_edgeS_y,crater_inner_edgeN_y,crater_inner_edgeS_y,crater_topCone_edgeN_y,crater_topCone_edgeS_y,crater_bottom_edgeN_y,crater_bottom_edgeS_y',shadow1_x1,shadow1_x2,shadow2_x1,shadow2_x2

This file can be generated with the script "create.csv"

On line 32, you can adapt the filter to select only the desired files (if not envi the appication will not be happy)
We need for each image at least following parameters:

'folder' = folder where file is located
'img_name' = name of the file
'azimuth_pixel_size', 'range_pixel_size'and 'incidence_angle_deg' = value specific to a satellite and orbit (can be different for each image depending on satellite)

With the script "create_csv", the user must select a folder and give for all images from this folder the pixels size and incidence angle. (considering we have sorted images coming from the same satellite - orbit in one folder). 
We can do this for several folder and script will create unique csv file sorted by date or by satellite.
Pixels size and incidence angle are written in comments in the scripts for several satellites.


The date is extracted from the filename of the SAR image. Script will search for successive 8 digit in the name in format %Y%m%d and consider this as the day. 


3. Picking the shadow

	
The specific usage of picking shadow is quite basic. We pick on the image 2 points (shadow distance) and we calculate the corresponding depth based on the "range" legth and incidence angle. We can record 2 different shadow on the same image. The results are written in a additional csv file.


-	Launch application with "start_app.py"
- 	Open the csv file in menubar "File - Open"
-	Activate "Picking Shadow"
- 	4 click will be recorded: 'x1 and x2' positions by shadow (green = shadow1 | red = shadow2)
-   Click on 'Save' to record the position in csv file and move to next image.
- 	The resluts are written in new csv, the name of this file is the same as csv input file with "_shadow_data_" added. 

Additional info

-	Zoom is available for better precision. (left clic on image and press escape to return to original zoom)
-	The 'Filtered image' button switch between both amplitude image if present. 
				If you have a filtered amplitude with the original one, you can rename the filtered as follow example:
				original image: 	amplitude_image_CSK_20200101.r4	
				amplitude_image_CSK_20200101.hdr
				filtered image: 	amplitude_image_CSK_20200101_Filtre.r4
				amplitude_image_CSK_20200101_Filtre.hdr

- 	A pink dot-dashed vertical can appears. It correspond to the x1 poistion (left) of the previous pick (based on time) for the same satellite (based on incidence angle)


4. Plot the results

A very basic script is written to plot both results: 
You just have to run the following script and put results csv file as argument.

"plot_shadow.py csv_file_shadow_data.csv"



5. Example.

As an example, there is a set of data in "test_data" folder.
The corresponding csv file create with the scripts is "test_data_folder.csv" or "test_data_date.csv" (The sorting option is different and may be easier to pick if image are sorted by folder to avoid working with zoom too much)
The results file after picking only the shadow is "test_data_folder_shadow_data.csv"






