
Procedure to follow to run pick_app application on a mac/linux machine


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

'folder,img_name,day,hour_UTC,azimuth_pixel_size,range_pixel_size,incidence_angle_deg,expo_greyscale,caldera_edgeN_x,caldera_edgeS_x,crater_outer_edgeN_x,crater_outer_edgeS_x,crater_inner_edgeN_x,crater_inner_edgeS_x,crater_topCone_edgeN_x,crater_topCone_edgeS_x,crater_bottom_edgeN_x,crater_bottom_edgeS_x,caldera_edgeN_y,caldera_edgeS_y,crater_outer_edgeN_y,crater_outer_edgeS_y,crater_inner_edgeN_y,crater_inner_edgeS_y,crater_topCone_edgeN_y,crater_topCone_edgeS_y,crater_bottom_edgeN_y,crater_bottom_edgeS_y'

Each line under the first one above will be linked to the amplitude file "folder/img_name".
If you have a filtered amplitude with the original one, you can rename the filtered as follow example:
	original image: 	amplitude_image_CSK_20200101.r4	
			amplitude_image_CSK_20200101.hdr
	filtered image: 	amplitude_image_CSK_20200101_Filtre.r4
			amplitude_image_CSK_20200101_Filtre.hdr

All your SAR image must be available locally in 'folder,img_name' position.



3. Functionality

-	The application will use all the available datas to draw ellipse, profile, 3d images, simulated amplitude and the plot of picking results.
-	You can also Open/Close each figure with Menubar --> View
-	You can Enable/Disable the automatic update for each figure (excepted SAR amplitude and profile) if you want to focus on specific figure with higher reactivity.
-	The update button turns to blue as soon as a change is available.
-	SAR View image and crater profile can be modified manually to change ellipse/crater shape.
-	3d images, simulated amplitude and the plot of picking results cannot be modified directly and are calculated from ellipse and profile.







4. Picking rules

	
The common usage is to pick ellipse on SAR View image, but you can also change ellipse from crater profile dragging points

Picking ellispe from SAR Image:

-	Activate button Picking Action and Show Ellipse
-	The next Pick point is written, just right clic on the image to pick the point
-	Change greyscale and clip value as desired
-	Zoom is available for better precision. (left clic on image and press escape to return to original zoom)
-	The button save turns to blue as soon as modification has been entered, clic on it to update your csv file.
-	The 'Filtered image' button switch between both amplitude image if present.
-	Some ellipse do not have south points to clic because shape is considered as follow:
-	Crater outer ring is considered centered on caldera ring
-	Top cone is considered centered on inner crater.
		
	
Picking from Profile:

-	Some position are hard coded such as altitude of caldera.
-	The profile on range axis consider that all ellipse are centered on azimut axis (which is not obviously the case on SAR image ellipse view).
-	You can drag and drop only empty-coloured circle, the others are hard coded (caldera altitude) or 	directly derived from other points (inner crater derived from top Cone because crater flanc are considered vertically at that position)
-	The save button to record modifications is the one in the SAR Image view.
	
	
View3d:

-	The view3d will represent the complete shape based on ellipse position and altitude of profile.
	
Simulated amplitude:

-	The simulated amplitude will take into account only the profile, so the shift on azimut axis is lost.
	
Picking results:

-	Evolution of ellipse size and altitude are plotted on two graphics.
-	You can resize the time axis using start/end date.
-	A vertical dotted line will show the current SAR image selected. It will move automatically if check box 'auto' is selected.
	







