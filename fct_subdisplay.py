# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
# import matplotlib as plt
import numpy as np
import os, math, re, time, sys
import datetime as datetime
import pandas as pd
import csv
from input_shape import *
import pandas as pd
# from osgeo import gdal
# from PyQt5 import QtCore




#===============================================================================================================
#====================    GENERAL FUNCTION     ==========================================================================
#===============================================================================================================


# Load csv file into dictionary

def csv_to_dict(csv_file):

    """ Function to open csv file and write into dictionary"""
    print("------->csv_to_dict")
    with open(csv_file, 'r') as f:
        # images_data = pd.read_csv(f, sep=',').to_dict()
        data = pd.read_csv(f, sep=',')
        # data = data.sort_values(by=['folder', 'day'])
        # replace NaN values with 0
        data = data.fillna(0)
        data = data.to_dict()

    return data




# Ellipse stuff
def ellipse_equation_2p(top_x, top_y, bot_x, bot_y, az_pix_size, ra_pix_size, theta,t):
    u = top_x
    v = int((int(bot_y) - int(top_y))/2 + top_y)
    a = int((int(bot_y) - int(top_y))/2)
    theta_rad = (theta * (2*math.pi))/360
    b = a*((az_pix_size*np.sin(theta_rad))/ra_pix_size)
    # print("theta = {}, theta_rad = {}, a = {}, b = {}".format(theta, theta_rad, a, b))
    return np.array([u+b*np.cos(t) , v+a*np.sin(t)])

def ellipse_equation(u, v, a, b, t):
    return np.array([u+a*np.cos(t) , v+b*np.sin(t)])

def ellipse_tilt_equation(u, v, a_x,a_y, b_x,b_y, t,theta):
    a = np.sqrt((a_x-u)**2 + (a_y-v)**2)
    b = np.sqrt((b_x-u)**2 + (b_y-v)**2)
    return np.array([u+a*np.cos(t)*np.cos(theta) - b*np.sin(t)*np.sin(theta) , v+a*np.cos(t)*np.sin(theta)+b*np.sin(t)*np.cos(theta)])

def ellipse_area(a,b):
    return np.pi*a*b

#===============================================================================================================
#================== Picking Amplitude Image (SAR) function ====================================================#
#===============================================================================================================

def pick_point(self, info_str, x, y):
    print("------->pick_point")
    """Function that will write in the dictionary "inages_data" new coordinate of clicked point"""
    x_str = "{}_x".format(info_str)
    y_str = "{}_y".format(info_str)
    # print("{} = [{}:{}]".format(info_str, x, y))
    self.dataset[x_str][self.index_live] = round(x)
    self.dataset[y_str][self.index_live] = round(y)

def pick_point_shad(self, info_str, x, y):
    print("------->pick_point_shad")
    """Function that will write in the dictionary "inages_data" new x position of clicked point for shadow only"""
    x_str = "{}".format(info_str)
    self.shadow_y1 = y
    # print("{} = [{}:{}]".format(info_str, x, y))
    self.dataset[x_str][self.index_live] = round(x)




def getPointNameFromIndex(index):
    print("------->getPointNameFromIndex")
    switcher = {
    0: 'caldera_edgeN',
    1: 'caldera_edgeS',
    2: 'crater_outer_edgeN',
    3: 'crater_inner_edgeN',
    4: 'crater_inner_edgeS',
    5: 'crater_topCone_edgeN',
    6: 'crater_bottom_edgeN',
    7: 'crater_bottom_edgeS',
    }
    return switcher.get(index, "nothing")

def getPointNameFromIndex_shad(index):
    print("------->getPointNameFromIndex_shad")
    switcher = {
    0: 'shadow1_x1',
    1: 'shadow1_x2',
    2: 'shadow2_x1',
    3: 'shadow2_x2',
    }
    return switcher.get(index, "nothing")


# Events
def on_key(event, self):
    """ Function that will call the pickSARManagement function when clicking on the amplitude image"""


     # Re-initialise zoom if escape pressed
    if event.key == 'escape':
        print("Reinitialise zoom")
        self.lim_x = self.lim_x_or
        self.lim_y = self.lim_y_or
        print("roriginal zoom value :", self.lim_x_or, self.lim_y_or)
        print("record zoom value :", self.lim_x, self.lim_y)
        self.updateSARPlot()




def onclick(event, self):
    """ Function that will call the pickSARManagement function when clicking on the amplitude image"""
    # print("Mouse button is clicked: ", event.button)
    # Check if right clic
    if re.search('MouseButton.RIGHT', str(event.button)):
        # Picking options mest be activated
        if self.pushButton_pick_SAR.isChecked():
            # Mouse must be in a place where coordinate are available
            print("------->onclick pick_SAR.isChecked")
            if event.xdata != None and event.ydata != None:

                # record zoom value if anything pressed
                # print("coordinate mouse : ", event.xdata, event.ydata)
                self.lim_x = self.ax.get_xlim()
                self.lim_y = self.ax.get_ylim()
                # print("roriginal zoom value :", self.lim_x_or, self.lim_y_or)
                # print("record zoom value :", self.lim_x, self.lim_y)
                self.SAR_zoom = True
                # Get points to pick fron inex value
                point_str = getPointNameFromIndex(self.pick_SAR_index)
                pick_point(self, point_str, event.xdata, event.ydata)
                # Update figure
                self.updateSARPlot()
                # update index
                self.pick_SAR_index += 1
                self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 9)
                # Display new point to pick in information label
                self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
                # Make Save button + update sim amp checkable 
                self.pushButton_pickSAR_save.setChecked(True)
                self.pushButton_update_simamp.setChecked(True)

        # Picking options mest be activated
        if self.pushButton_pick_SHAD.isChecked():
            # Mouse must be in a place where coordinate are available
            print("------->onclick pick_SHAD.isChecked")
            if event.xdata != None and event.ydata != None:

                # record zoom value if anything pressed
                # print("coordinate mouse : ", event.xdata, event.ydata)
                self.lim_x = self.ax.get_xlim()
                self.lim_y = self.ax.get_ylim()
                # print("roriginal zoom value :", self.lim_x_or, self.lim_y_or)
                # print("record zoom value :", self.lim_x, self.lim_y)
                self.SAR_zoom = True
                # Get points to pick fron inex value
                point_str = getPointNameFromIndex_shad(self.pick_SAR_index)
                print("point_str = {}".format(point_str))
                pick_point_shad(self, point_str, event.xdata, event.ydata)
                # Update figure
                self.updateSARPlot()
                # update index
                self.pick_SAR_index += 1
                self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 5)
                # Display new point to pick in information label
                self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex_shad(self.pick_SAR_index))
                # Make Save button + update sim amp checkable 
                print("set save button blue")
                self.pushButton_pickSAR_save.setChecked(True)

#================================================================================================
#=========================== FUNCTION FOR DRAGGABLE POINTS ON PROFILE ===========================
#================================================================================================



def update_plot(self):
    """ Write in dataset new value when points move on profile"""

    print("------->update_plot")
    dataset = self.dataset
    i = self.index_live

    # Pixel size and incidence angle
    azimuth_pixel_size = dataset['azimuth_pixel_size'][i]
    range_pixel_size = dataset['range_pixel_size'][i]
    incidence_angle_deg = dataset['incidence_angle_deg'][i]
    incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360

        # Caldera ellipse

    # Get coordinate of draggable profile
    Kx, Ky = list(self._points[1].items())[0]
    Ux, Uy = list(self._points[2].items())[0]
    Ex, Ey = list(self._points[3].items())[0]
    Fx, Fy = list(self._points[4].items())[0]
    Vx, Vy = list(self._points[5].items())[0]
    Lx, Ly = list(self._points[6].items())[0]



    # rewrite original caldera point because we don't want them to be moved manually by profile (only moved by picking amplitude image)
    Ix = self.Ix
    Iy = self.Iy
    Jx = self.Jx
    Jy = self.Jy

    Cx = Ux           # if both point are together, Ux is on top of Cx, so we decide to play with Dx (They must be the same in the end)
    Dx = Vx

    Cy = Ky
    Dy = Ly



   # De-centering all X axis points from middle of the caldera to original amplitude image
    delta_ref_x = self.delta_ref_x
    Ix += delta_ref_x 
    Jx += delta_ref_x
    Kx += delta_ref_x
    Lx += delta_ref_x
    Cx += delta_ref_x
    Dx += delta_ref_x
    Ux += delta_ref_x
    Vx += delta_ref_x
    Ex += delta_ref_x
    Fx += delta_ref_x



    # dataset['caldera_edgeN_y'][i] = Ix/azimuth_pixel_size
    # dataset['caldera_edgeS_y'][i] = Jx/azimuth_pixel_size
    Iy = Zvolc # cconstante and reference point for th rest
    Jy = Zvolc


    # Crater outer ellipse

    h1 = Iy - Ky
    a1 = h1*np.cos(incidence_angle_rad)
    if self.current_orbit_desc:
        a1 = -abs(a1)
    diameter_P2 = (Lx - Kx)/azimuth_pixel_size
    center_y_mem = ((dataset['crater_outer_edgeS_y'][i] - dataset['crater_outer_edgeN_y'][i])/2) + dataset['crater_outer_edgeN_y'][i]
    # print("diameter_P2 = ", diameter_P2)
    # print("center_y_mem = ", center_y_mem)
    dataset['crater_outer_edgeN_x'][i] = (a1/range_pixel_size) + dataset['caldera_edgeN_x'][i] 
    dataset['crater_outer_edgeN_y'][i] = center_y_mem - (diameter_P2/2)
    # dataset['crater_outer_edgeS_x'][i] = dataset['crater_outer_edgeN_x'][i]
    # dataset['crater_outer_edgeS_y'][i] = center_y_mem - (diameter_P2/2)

    # Crater inner ellipse (need to record previous center position for crater)
    caldera_center = ((Jx - Ix)/2) + Ix
    crater_center = ((Dx - Cx)/2) + Cx
    if self.current_orbit_desc:
        delta_x = caldera_center - crater_center
    else:
        delta_x = crater_center - caldera_center
    a2 = delta_x*np.sin(incidence_angle_rad)
    # if self.current_orbit_desc:
    #     a2 = -abs(a2)
    diameter_crater = (Dx - Cx)/azimuth_pixel_size
    center_y_mem = ((dataset['crater_inner_edgeS_y'][i] - dataset['crater_inner_edgeN_y'][i])/2) + dataset['crater_inner_edgeN_y'][i]
    # print("diameter_crater = ", diameter_crater)
    # print("center_y_mem = ", center_y_mem)
    dataset['crater_inner_edgeN_x'][i] = dataset['crater_outer_edgeN_x'][i] - (a2/range_pixel_size)
    dataset['crater_inner_edgeN_y'][i] = center_y_mem - (diameter_crater/2)
    dataset['crater_inner_edgeS_x'][i] = dataset['crater_inner_edgeN_x'][i] 
    dataset['crater_inner_edgeS_y'][i] = center_y_mem + (diameter_crater/2)

    # Middle crater
    h2 = Cy - Uy
    a3 = h2 * np.cos(incidence_angle_rad)
    if self.current_orbit_desc:
        a3 = -abs(a3) 
    dataset['crater_topCone_edgeN_x'][i] = (a3 / range_pixel_size) + dataset['crater_inner_edgeN_x'][i]
    dataset['crater_topCone_edgeN_y'][i] =dataset['crater_inner_edgeN_y'][i]
    dataset['crater_topCone_edgeS_x'][i] = dataset['crater_topCone_edgeN_x'][i] 
    dataset['crater_topCone_edgeS_y'][i] = dataset['crater_inner_edgeS_y'][i]

    # Bottom crater
    h3 = Uy -Ey
    a4 = h3 * np.cos(incidence_angle_rad)
    if self.current_orbit_desc:
        a4 = -abs(a4)
    diameter_crater_bottom = (Fx - Ex)/azimuth_pixel_size
    dataset['crater_bottom_edgeN_x'][i] = (a4 / range_pixel_size) + dataset['crater_topCone_edgeN_x'][i]
    dataset['crater_bottom_edgeN_y'][i] = center_y_mem - (diameter_crater_bottom/2)
    dataset['crater_bottom_edgeS_x'][i] = dataset['crater_bottom_edgeN_x'][i] 
    dataset['crater_bottom_edgeS_y'][i] = center_y_mem + (diameter_crater_bottom/2)




    # Manage grey shape (TO BE REMOVED)
    x = []
    y = []
    for key in sorted(self._points.keys()):
        # print("--> key =", key)
        # print("--> self._points[key] =", self._points[key])
        x_, y_ = zip(*self._points[key].items())
        x.append(x_)
        y.append(y_)
    # print(x, y)
    self._line.set_data(x, y)
    self.figure_profile.canvas.draw()

    #---------------------------------------



    # X_profile_all = [-Rbase, Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx, Rbase]
    # Y_profile_all = [Zbase, Iy, Ky, Cy, Uy, Ey, Fy, Vy, Dy, Ly, Jy, Zbase]
    


    


#================================================================================================
#=========================== FUNCTION FOR 3D ====================================================
#================================================================================================




from mpl_toolkits.mplot3d import axes3d
def get_cone_data(x, y, r1, r2, z1, z2, n1, n2):
    """ Get 3 2d array to plot cone
        x, y are coordinate of center of both circle 
        r1, r2 are rayon of circle 1 and 2
        z1, z2 are height of circle 1 and 2
        n1 is number of samples to create circle
        n2, number of sample to link both circle

        """

    theta = np.linspace(0,2*np.pi,n1)
    z = np.linspace(z1,z2,n2)
    r = np.linspace(r1,r2,n2)

    # Create 2d matrice with Z limit value in order to create all intermediate points in between
    T, Z = np.meshgrid(theta, z)
    # Create 2d matrice with both circle rayon limit value in order to create all intermediate points in between
    T, R = np.meshgrid(theta, r)


    # Then calculate X, Y, using cos and sin to variate points between both circle value in x and y axis
    X = (R * np.cos(T))
    Y = (R * np.sin(T))

    # Move to reference
    X = X + x
    Y = Y + y

    return X, Y, Z


def get_perforated_surface(x1, y1,x2, y2, r1, r2, z, n1, n2):
    """ Get 3 2d array to plot cone
        x1, y1 are coordinate of center of first circle
        x2, y2 are coordinate of center of secondary circle
        r1, r2 are rayon of circle 1 and 2
        z is height of surface to draw
        n1 is number of samples to create circle
        n2, number of sample to link both circle

        """

    theta = np.linspace(0,2*np.pi,n1)
    z1 = np.linspace(z,z,n2)
    r1 = np.linspace(0,r1,n2)

    # Create 2d matrice with Z limit value in order to create all intermediate points in between

    T, Z1 = np.meshgrid(theta, z1)

    # Create 2d matrice with both circle rayon limit value in order to create all intermediate points in between
    T1, R1 = np.meshgrid(theta, r1)

    # Then calculate X, Y, using cos and sin to variate points between both circle value in x and y axis
    X1 = (R1* np.cos(T1))
    Y1 = (R1* np.sin(T1))
    # Move to reference
    X1 = X1 + x1
    Y1 = Y1 + y1


    # Loop throug index of X1 and extract X and Y value
    for iy, ix in np.ndindex(X1.shape):
        x_val = (X1[iy, ix])
        y_val = (Y1[iy, ix])
        if is_inside_circle(x_val, y_val, x2, y2, r2):
            # print("remove this coordinate:", x_val, y_val)
            Z1[iy, ix] = np.nan


    return X1, Y1, Z1



def data_for_cylinder_along_z(center_x,center_y,radius,height_z):

    theta = np.linspace(0, 2*np.pi, 100)
    x = radius*np.cos(theta) + center_x
    y = radius*np.sin(theta) + center_y
    z = np.zeros(len(x))
    z.fill(height_z)
    return x, y, z

def is_inside_circle(x, y, x_center, y_center, r):
    distance = math.sqrt((x - x_center)**2 + (y - y_center)**2)
    return distance < r




#================================================================================================
#=========================== FUNCTION FOR SIMULATED AMPLITUDE CREARTION =========================
#================================================================================================



def proj_ortho(points, z0, incid):
    """compute orthogonal projection of point [x,y,z] along plane defined by
    inciddir, ey and M[0,0,z0]
    incidence angle in rad
    """
    X = points[0,:]
    Y = points[1,:]
    Z = points[2,:]
    u = math.sin(incid)
    w = math.cos(incid)
    proj = np.array([(X+((Z - z0) * (w/u)))/(1 + (w/u)**2), Y, (X + (z0 * u / w) + (Z*w/u))/((u/w)+(w/u))])
    return proj



def convert_csv(csv_file):
    """ This function is used to convert initial csv file with ellipse data to geodetic data for creating simulated 
    amplitude file"""

    print("------->convert_csv")
    with open(csv_file, 'r') as f:
        # images_data = pd.read_csv(f, sep=',').to_dict()
        images_data = pd.read_csv(f, sep=',')
        # replace NaN values with 0
        images_data = images_data.fillna(0)
        #images_data = images_data.to_dict()
        images_number = len(images_data['folder'])
        i = 0
        Zvolc = 3460
        csv_file_out=csv_file + '_pick.csv'
    with open(csv_file_out, 'w', newline='') as csvfile:
        fieldnames = ['filepath', 'img_date','img_hour','azimuth_pixel_size','range_pixel_size','incidence_angle_deg','Rcald_m','RP2_m','Rcrat_m','Rbot_m','delta_x_m','HP2_m','h','H','Alpha','Beta']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        csvfile.close()

    while i < images_number:    
        # File name
        img_dir = images_data['folder'][i]
        # print(img_dir)
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



def create_csv_tmp(self):
    """ This function is used to convert images_data dictionary (ellipse data ) to geodetic data for creating simulated 
    amplitude file"""

    print("------->create_csv_tmp")

    images_data = self.dataset
    #images_data = images_data.to_dict()
    images_number = len(images_data['folder'])
    i = 0
    Zvolc = 3460
    csv_file_out = self.csv_file + '_pick_tmp.csv'


    with open(csv_file_out, 'w', newline='') as csvfile:
        fieldnames = ['filepath', 'img_date','img_hour','azimuth_pixel_size','range_pixel_size','incidence_angle_deg','Rcald_m','RP2_m','Rcrat_m','Rbot_m','delta_x_m','HP2_m','h','H','Alpha','Beta']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        csvfile.close()

    while i < images_number:    
        # File name
        img_dir = images_data['folder'][i]
        # print(img_dir)
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


def updateParametersFile(filename, param, new_value):
    """ This function is used to replace in a file the value of a parameters.
    The parameters must be written before a #, and the value just after the dash """
    print("------->updateParametersFile")
    # Open the file in 'read' mode and read all the lines into a list
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the line you want to replace
    for i, line in enumerate(lines):
        if re.search(param, line) and re.search(r'^[^#].', line):
            # create pattern to extract current parameter value
            pattern = r"=\s+[0-9]+"
            value = re.search(pattern, line)[0]
            value = re.search("\d+", value)[0]
            new_line = line.replace(value, new_value)
            lines[i] = new_line
                
    # Open the file in 'write' mode and write the updated lines to the file
    with open(filename, 'w') as file:
        file.writelines(lines)




def LooadParametersFile(filename):
    """ This function is load in a dictionarry all paramaters from input shape file
    each line with equal in it and not starting with # will be recorded in the dico """
    print("------->LooadParametersFile")
    dict_param = {}
    # Open the file in 'read' mode and read all the lines into a list
    # Open the file in 'read' mode and read all the lines into a list
    with open(filename, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if re.search("=", line) and re.search(r'^[^#].', line):

            try:
                pattern = r"^\s*.+="
                param = re.search(pattern, line)[0]
                param = re.search("\w+", param)[0]
                pattern = r"=\s+.+\s*#*"
                value = re.search(pattern, line)[0]
                value = re.search("\w+", value)[0]
            except:
                print("issue no param or value found: File input shape does not match <param = value>  ")
                break
                # print(value)

            dict_param[param] = value

    return dict_param



def convert_dictionary_to_table(dictionary):
    df = pd.DataFrame.from_dict(dictionary, orient='columns')
    return df


def extract_values_with_condition(data_frame, condition_column, condition_value, target_column):
    filtered_values = data_frame.loc[data_frame[condition_column] == condition_value, target_column]
    return filtered_values
# end