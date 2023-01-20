from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import matplotlib as plt
import matplotlib.pyplot as pyplt
import numpy as np
import matplotlib.dates as mdates
import os, math, re, time, sys
import datetime as datetime
from osgeo import gdal
from PyQt5 import QtCore
from statistics import mean 
from fct_subdisplay import *



#===============================================================================================================
#====================    AMPLITUDE IMAGE     ===================================================================
#===============================================================================================================


def getSARFig(self):
    """ Function to draw SAR image in canvas """

    # File name
    i = self.index_live
    dataset = self.dataset

    img_dir = dataset['folder'][i]
    img_name = dataset['img_name'][i]
    filepath = os.path.join(img_dir, img_name)
    filepath_filter = filepath.replace(".r4", "_Filtre.r4")
    satname = img_dir.split('/')[-2]

    # Acquisition time
    img_date_string = dataset['day'][i]
    img_date = datetime.datetime.strptime(str(img_date_string), "%Y%m%d")

    # Pixel size and incidence angle
    azimuth_pixel_size = dataset['azimuth_pixel_size'][i]
    range_pixel_size = dataset['range_pixel_size'][i]
    incidence_angle_deg = dataset['incidence_angle_deg'][i]
    incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360

    # Caldera ellipse
    caldera_edgeN_x = dataset['caldera_edgeN_x'][i]
    caldera_edgeN_y = dataset['caldera_edgeN_y'][i]
    caldera_edgeS_x = dataset['caldera_edgeS_x'][i]
    caldera_edgeS_y = dataset['caldera_edgeS_y'][i]

    # Crater outer ellipse
    crater_outer_edgeN_x = dataset['crater_outer_edgeN_x'][i]
    crater_outer_edgeN_y = dataset['crater_outer_edgeN_y'][i]
    crater_outer_edgeS_x = dataset['crater_outer_edgeS_x'][i]
    crater_outer_edgeS_y = dataset['crater_outer_edgeS_y'][i]

    # Crater inner ellipse
    crater_inner_edgeN_x = dataset['crater_inner_edgeN_x'][i]
    crater_inner_edgeN_y = dataset['crater_inner_edgeN_y'][i]
    crater_inner_edgeS_x = dataset['crater_inner_edgeS_x'][i]
    crater_inner_edgeS_y = dataset['crater_inner_edgeS_y'][i]

    # Crater outer ellipse
    crater_topCone_edgeN_x = dataset['crater_topCone_edgeN_x'][i]
    crater_topCone_edgeN_y = dataset['crater_inner_edgeN_y'][i]
    crater_topCone_edgeS_x = dataset['crater_topCone_edgeS_x'][i]
    crater_topCone_edgeS_y = dataset['crater_inner_edgeS_y'][i]

    # Crater outer ellipse
    crater_bottom_edgeN_x = dataset['crater_bottom_edgeN_x'][i]
    crater_bottom_edgeN_y = dataset['crater_bottom_edgeN_y'][i]
    crater_bottom_edgeS_x = dataset['crater_bottom_edgeS_x'][i]
    crater_bottom_edgeS_y = dataset['crater_bottom_edgeS_y'][i]


    expo_greyscale = dataset['expo_greyscale'][i] 

   


    # print("!!! Coordinate caldera_N = ", dataset['crater_outer_edgeN_x'][i])
    # print("index i = ", i)


    # Open the file:
    if self.pushButton_filtered_SAR.isChecked():
        file_to_open = filepath_filter
    else:
        file_to_open = filepath
    Raster = gdal.Open(file_to_open)

    # print("file_to_open = ",file_to_open)
    # Extract data from envi file
    Band   = Raster.GetRasterBand(1) # 1 based, for this example only the first
    NoData = Band.GetNoDataValue()  # this might be important later
    nBands = Raster.RasterCount      # how many bands, to help you loop
    nRows  = Raster.RasterYSize      # how many rows
    nCols  = Raster.RasterXSize      # how many columns
    dType  = Band.DataType          # the datatype for this band

    # print("nBands, nRows, nCols, dType = ", nBands, nRows, nCols, dType)
    self.SAR_width = nRows
    self.SAR_height = nCols
    # Extract band
    inputArray = (np.array(Band.ReadAsArray()**expo_greyscale))


    # Cleanup
    del Raster, Band


   
    #--------------------- Calculate ellipse + profile ccordinate -----------------#

    if self.pushButton_ellipse.isChecked():
        # Parameter for curvilinear coordinates of ellipse
        t = np.linspace(0, 2*np.pi, 100)

        # Calculate South point for some ellipse as several ellipse are centered together
        dataset['crater_outer_edgeS_x'][i] = crater_outer_edgeN_x
        center_caldera_y = (((caldera_edgeS_y - caldera_edgeN_y)/2) + caldera_edgeN_y)
        dataset['crater_outer_edgeS_y'][i] = ((center_caldera_y - crater_outer_edgeN_y) * 2) + crater_outer_edgeN_y


        dataset['crater_topCone_edgeS_x'][i] = crater_topCone_edgeN_x
        dataset['crater_topCone_edgeS_y'][i] = crater_inner_edgeS_y

        dataset['crater_bottom_edgeS_x'][i] = crater_bottom_edgeN_x
        center_crater_y = (((crater_inner_edgeS_y - crater_inner_edgeN_y)/2) + crater_inner_edgeN_y)
        # dataset['crater_bottom_edgeS_y'][i] = ((center_crater_y  - crater_bottom_edgeN_y) * 2) + crater_bottom_edgeN_y

        # Rewrite in local variable
        crater_outer_edgeS_x = dataset['crater_outer_edgeS_x'][i]
        crater_outer_edgeS_y = dataset['crater_outer_edgeS_y'][i]
        crater_topCone_edgeS_x = dataset['crater_topCone_edgeS_x'][i]
        crater_topCone_edgeS_y = dataset['crater_topCone_edgeS_y'][i]
        crater_bottom_edgeS_x = dataset['crater_bottom_edgeS_x'][i]
        # crater_bottom_edgeS_y = dataset['crater_bottom_edgeS_y'][i]


        # Ellipses
        [caldera_ellipse_x, caldera_ellipse_y] = ellipse_equation_2p(caldera_edgeN_x, caldera_edgeN_y, caldera_edgeS_x, caldera_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_outer_ellipse_x, crater_outer_ellipse_y] = ellipse_equation_2p(crater_outer_edgeN_x, crater_outer_edgeN_y, crater_outer_edgeS_x, crater_outer_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_inner_ellipse_x, crater_inner_ellipse_y] = ellipse_equation_2p(crater_inner_edgeN_x, crater_inner_edgeN_y, crater_inner_edgeS_x, crater_inner_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_topCone_ellipse_x, crater_topCone_ellipse_y] = ellipse_equation_2p(crater_topCone_edgeN_x, crater_topCone_edgeN_y, crater_topCone_edgeS_x, crater_topCone_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_bottom_ellipse_x, crater_bottom_ellipse_y] = ellipse_equation_2p(crater_bottom_edgeN_x, crater_bottom_edgeN_y, crater_bottom_edgeS_x, crater_bottom_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)




    #========================== DRAW FIGURE ================================#


    # matplotlib.style.use('seaborn-talk')

    self.figure = Figure()
    self.ax = self.figure.gca()
    self.ax.set_title("{}:{}".format(satname, img_date_string))

    if self.pushButton_filtered_SAR.isChecked():    # Need to rescale mi/max between 0 and 1
        vmin = float((self.SAR_clip_min.value()/255))
        vmax = float((self.SAR_clip_max.value()/255))
    else:
        vmin = int(self.SAR_clip_min.value())
        vmax = int(self.SAR_clip_max.value())
    # print("greyscale, vmin, vmax =", expo_greyscale, vmin, vmax)
    if vmin < vmax:
        self.ax.imshow(inputArray, cmap='Greys_r', vmin=vmin, vmax=vmax)
    else:
        print("Value not coherent to display this image : please check clip value!")


    if self.pushButton_ellipse.isChecked():
        self.ax.plot(caldera_ellipse_x, caldera_ellipse_y, color='blue', alpha=0.8)
        self.ax.plot(crater_outer_ellipse_x, crater_outer_ellipse_y, color='skyblue', alpha=0.8)
        self.ax.plot(crater_inner_ellipse_x, crater_inner_ellipse_y, color='red', alpha=0.8)
        self.ax.plot(crater_topCone_ellipse_x, crater_topCone_ellipse_y, color='orange', alpha=0.8)
        self.ax.plot(crater_bottom_ellipse_x, crater_bottom_ellipse_y, color='magenta', alpha=0.8)
        self.ax.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

        self.ax.plot(caldera_edgeN_x,caldera_edgeN_y,marker="o", markeredgecolor="blue", markerfacecolor="blue")
        self.ax.plot(caldera_edgeS_x,caldera_edgeS_y,marker="o", markeredgecolor="blue", markerfacecolor="blue")
        self.ax.plot(crater_outer_edgeN_x,crater_outer_edgeN_y,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
        # self.ax.plot(crater_outer_edgeS_x,crater_outer_edgeS_y,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
        self.ax.plot(crater_inner_edgeN_x,crater_inner_edgeN_y,marker="o", markeredgecolor="red", markerfacecolor="red")
        self.ax.plot(crater_inner_edgeS_x,crater_inner_edgeS_y,marker="o", markeredgecolor="red", markerfacecolor="red")
        self.ax.plot(crater_topCone_edgeN_x,crater_topCone_edgeN_y,marker="o", markeredgecolor="orange", markerfacecolor="orange")
        # self.ax.plot(crater_topCone_edgeN_x,crater_topCone_edgeS_y,marker="o", markeredgecolor="orange", markerfacecolor="orange")
        self.ax.plot(crater_bottom_edgeN_x,crater_bottom_edgeN_y,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
        self.ax.plot(crater_bottom_edgeS_x,crater_bottom_edgeS_y,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
    
    # restore previous zoom value
    # print("self.SAR_zoom = ", self.SAR_zoom)
    if self.SAR_zoom:
        # print("set zoom value :", self.lim_x, self.lim_y)
        self.ax.set_xlim(self.lim_x)
        self.ax.set_ylim(self.lim_y)




    # self.canvas.mpl_connect('key_press_event', lambda event: on_key(event, self)) 
    self.figure.canvas.mpl_connect('button_press_event', lambda event: onclick(event, self))
    self.figure.canvas.mpl_connect('key_press_event', lambda event: on_key(event, self))   # Do not work !!! Why ???


    self.ax.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

    # Canvas creation
    self.canvas = FigureCanvas(self.figure)
    self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    self.canvas.setFocus()




    return self.canvas



#===============================================================================================================
#====================    PROFILE      ==========================================================================
#===============================================================================================================

from input_shape import *
from matplotlib.backend_bases import MouseEvent
import matplotlib.lines as lines

def getProfileFig(self):
    """ Function to draw SAR image in canvas """

    # File name
    i = self.index_live
    dataset = self.dataset



    # Pixel size and incidence angle
    azimuth_pixel_size = dataset['azimuth_pixel_size'][i]
    range_pixel_size = dataset['range_pixel_size'][i]
    incidence_angle_deg = dataset['incidence_angle_deg'][i]
    incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360

    # Caldera ellipse
    caldera_edgeN_x = dataset['caldera_edgeN_x'][i]
    caldera_edgeN_y = dataset['caldera_edgeN_y'][i]
    caldera_edgeS_x = dataset['caldera_edgeS_x'][i]
    caldera_edgeS_y = dataset['caldera_edgeS_y'][i]

    # Crater outer ellipse
    crater_outer_edgeN_x = dataset['crater_outer_edgeN_x'][i]
    crater_outer_edgeN_y = dataset['crater_outer_edgeN_y'][i]
    crater_outer_edgeS_x = dataset['crater_outer_edgeS_x'][i]
    crater_outer_edgeS_y = dataset['crater_outer_edgeS_y'][i]

    # Crater inner ellipse
    crater_inner_edgeN_x = dataset['crater_inner_edgeN_x'][i]
    crater_inner_edgeN_y = dataset['crater_inner_edgeN_y'][i]
    crater_inner_edgeS_x = dataset['crater_inner_edgeS_x'][i]
    crater_inner_edgeS_y = dataset['crater_inner_edgeS_y'][i]

    # Crater outer ellipse
    crater_topCone_edgeN_x = dataset['crater_topCone_edgeN_x'][i]
    crater_topCone_edgeN_y = dataset['crater_topCone_edgeN_y'][i]
    crater_topCone_edgeS_x = dataset['crater_topCone_edgeS_x'][i]
    crater_topCone_edgeS_y = dataset['crater_topCone_edgeS_y'][i]

    # Crater outer ellipse
    crater_bottom_edgeN_x = dataset['crater_bottom_edgeN_x'][i]
    crater_bottom_edgeN_y = dataset['crater_bottom_edgeN_y'][i]
    crater_bottom_edgeS_x = dataset['crater_bottom_edgeS_x'][i]
    crater_bottom_edgeS_y = dataset['crater_bottom_edgeS_y'][i]


    ####### Draw picked topography ###########


    # Manage to know if we are in an ascebding or descenfing SAR image
    if (float(incidence_angle_deg) < 0):
        self.current_orbit_asc = True
        self.current_orbit_desc = False
    else:
        self.current_orbit_asc = False
        self.current_orbit_desc = True

    # >=P2
    Ix = int(caldera_edgeN_y*azimuth_pixel_size)
    Iy = Zvolc

    Jx = int(caldera_edgeS_y*azimuth_pixel_size)
    Jy = Zvolc


    delta_ref_x = Ix + ((Jx - Ix)/2)


    Kx = int(crater_outer_edgeN_y*azimuth_pixel_size)
    a1 = abs(crater_outer_edgeN_x - caldera_edgeN_x)*range_pixel_size
    h1 = int(a1 / np.cos(incidence_angle_rad))
    Ky = Iy - h1

    Lx = int(crater_outer_edgeS_y*azimuth_pixel_size)
    Ly = Ky



    # P2
    a2 = (crater_outer_edgeN_x - crater_inner_edgeN_x)*range_pixel_size
    delta_x = (a2)/(np.sin(incidence_angle_rad))
    if self.current_orbit_desc:
        delta_x = -delta_x
    diameter_crater = (int(crater_inner_edgeS_y) - int(crater_inner_edgeN_y)) * azimuth_pixel_size


    Cx = (delta_ref_x + delta_x) - (diameter_crater/2)
    Cy = Ky

    Dx = (delta_ref_x + delta_x) + (diameter_crater/2)
    Dy = Ky

    # <P2
    Ux = Cx
    a3 = abs(crater_topCone_edgeN_x - crater_inner_edgeN_x)*range_pixel_size
    h2 = int(a3/np.cos(incidence_angle_rad))
    Uy = Cy - h2

    Vx = Dx
    Vy = Uy

    # Cone

    a4 = abs(crater_bottom_edgeN_x - crater_topCone_edgeN_x)*range_pixel_size
    h3 = int(a4/np.cos(incidence_angle_rad))
    Ey = Uy - h3
    diameter_bottom = (int(crater_bottom_edgeS_y) - int(crater_bottom_edgeN_y)) * azimuth_pixel_size
    Ex = (delta_ref_x + delta_x) - (diameter_bottom/2)
    Fx = (delta_ref_x + delta_x) + (diameter_bottom/2)
    Fy = Ey


    # print("Ix = ", Ix)

    # Centering all X axis points with the middle of the caldera as reference.
    Ix -= delta_ref_x 
    Jx -= delta_ref_x
    Kx -= delta_ref_x
    Lx -= delta_ref_x
    Cx -= delta_ref_x
    Dx -= delta_ref_x
    Ux -= delta_ref_x
    Vx -= delta_ref_x
    Ex -= delta_ref_x
    Fx -= delta_ref_x

    # save caldera point because we don't want them to be moved manually by profile
    self.Ix = Ix
    self.Iy = Iy
    self.Jx = Jx
    self.Jy = Jy




    # Need to make global this value to use to scale back data in function _update_plot()
    self.delta_ref_x = delta_ref_x



    # Create array to draw profile
    X_profile_1 = [-2500, Ix, Kx]   # flanc caldera
    Y_profile_1 = [2500, Iy, Ky]

    X_profile_2 = [Kx, Cx]  # P2
    Y_profile_2 = [Ky, Cy]

    X_profile_3 = [Cx, Dx]  # crater top
    Y_profile_3 = [Cy, Dy]

    X_profile_4 = [Cx, Ux]  # flanc cratere vertical
    Y_profile_4 = [Cy, Uy]  

    X_profile_5 = [Ux, Vx]  # middle 
    Y_profile_5 = [Uy, Vy]  

    X_profile_6 = [Ux, Ex]  # flanc crater conique
    Y_profile_6 = [Uy, Ey]  

    X_profile_7 = [Fx, Ex]  # bottom
    Y_profile_7 = [Fy, Ey]  

    X_profile_66 = [Fx, Vx]
    Y_profile_66 = [Fy, Vy] 

    X_profile_44 = [Dx, Vx]
    Y_profile_44 = [Dy, Vy]

    X_profile_22 = [Dx, Lx]
    Y_profile_22 = [Dy, Ly]

    X_profile_11 = [Lx, Jx, 2500]
    Y_profile_11 = [Ly, Jy, 2500]


    X_profile_all = [-2500, Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx, 2500]
    Y_profile_all = [2500, Iy, Ky, Cy, Uy, Ey, Fy, Vy, Dy, Ly, Jy, 2500]
  
    X_profile_clickable = [Ix, Kx, Ux, Ex, Fx, Vx, Lx, Jx]
    Y_profile_clickable = [Iy, Ky, Uy, Ey, Fy, Vy, Ly, Jy]


    # print("X_profile_all = Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx") 
    # print("X_profile_all = ",Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx) 
   
    #========================== DRAW FIGURE ================================#


    # matplotlib.style.use('seaborn-talk')

    self.figure_profile = Figure()
    self.ax1 = self.figure_profile.gca()
    # self.ax1.set_title("{}:{}".format(satname, img_date_string))

  
    # Create 1 curve that will react to mouse event to help user modifying the profile
    # All the other plotwill be superposed on it with color code
    self._dragging_point = None
    self._points = {}
    self._line= lines.Line2D(X_profile_all ,Y_profile_all , marker="o", color="grey", markeredgecolor="grey", markerfacecolor="grey")
    self.ax1.add_line(self._line)
    # self._line, = self.ax1.plot(X_profile_all ,Y_profile_all ,marker="o", markeredgecolor="green", markerfacecolor="green")
    # Fill variable _points to manage draggable points
    for idx in range(len(X_profile_clickable)):
        self._points[idx] = {}
        self._points[idx][X_profile_clickable[idx]] = Y_profile_clickable[idx]

    # Set fixed data on profile with color related to ellipse on amplitude image
    self.ax1.set_title("profile from picking points")
    # Caldera
    self.ax1.plot(Ix,Iy,marker="o", markeredgecolor="blue", markerfacecolor="blue")
    self.ax1.plot(X_profile_1, Y_profile_1, color='black')
    self.ax1.plot(Jx,Jy,marker="o", markeredgecolor="blue", markerfacecolor="blue")
    self.ax1.plot(X_profile_11, Y_profile_11, color='black')

    # Crater outer = P2
    self.ax1.plot(Lx,Ly,marker="o", markeredgecolor="skyblue", markerfacecolor="white")
    self.ax1.plot(X_profile_2, Y_profile_2, color='skyblue')
    self.ax1.plot(Kx,Ky,marker="o", markeredgecolor="skyblue", markerfacecolor="white")
    self.ax1.plot(X_profile_22, Y_profile_22, color='skyblue')

    # Crater at top position (level P2)
    self.ax1.plot(Cx,Cy,marker="o", markeredgecolor="red", markerfacecolor="red")
    self.ax1.plot(Dx,Dy,marker="o", markeredgecolor="red", markerfacecolor="red")
    self.ax1.plot(X_profile_3, Y_profile_3, color='red',linestyle='dashed', linewidth=1)


    self.ax1.plot(X_profile_4, Y_profile_4, color='black')
    self.ax1.plot(X_profile_44, Y_profile_44, color='black')

    # Crater at middle position (Between bottom and top)
    self.ax1.plot(Ux,Uy,marker="o", markeredgecolor="orange", markerfacecolor="white")
    self.ax1.plot(Vx,Vy,marker="o", markeredgecolor="orange", markerfacecolor="white")
    self.ax1.plot(X_profile_5, Y_profile_5, color='orange',linestyle='dashed', linewidth=1)


    self.ax1.plot(X_profile_6, Y_profile_6, color='black')
    self.ax1.plot(X_profile_66, Y_profile_66, color='black')

    # Crater at bottom
    self.ax1.plot(Ex,Ey,marker="o", markeredgecolor="magenta", markerfacecolor="white")
    self.ax1.plot(Fx,Fy,marker="o", markeredgecolor="magenta", markerfacecolor="white")
    self.ax1.plot(X_profile_7, Y_profile_7, color='magenta',linestyle='dashed', linewidth=1)

    # self.ax1.axis('equal')
    self.ax1.set_xlim(-1000, 1000)  # self.SAR_width = number of pixels in azimut direction for this image
    self.ax1.set_ylim(2200, 3600)
    self.ax1.set_xlabel('[m] (range direction)')
    self.ax1.set_ylabel('[m]')
    self.ax1.text(-250, 2500, "delta X = {}m".format(round(delta_x, 2)))
    self.ax1.text(-250, 2450, "P2 from top = {}m".format(round(h1, 2)))
    self.ax1.text(-250, 2400, "Caldera Radius= {}m".format(round(Jx, 2)))
    self.ax1.text(-250, 2350, "P2 radius = {}m".format(round(Lx, 2)))
    self.ax1.text(-250, 2300, "Crat radius = {}m".format(round((diameter_crater/2), 2)))
    self.ax1.text(-250, 2250, "Bottom from P2 = {}m".format(round((Cy - Ey), 2)))
    self.ax1.text(-250, 2210, "Bottom radius = {}m".format(round((diameter_bottom/2), 2)))

  

    # Draw line to represent satellite direction
    sat_incid = (math.pi/2) - incidence_angle_rad
    m = np.tan(sat_incid)
    x_incid = np.linspace(delta_x - 1000, delta_x + 1000, 3)
    y_incid = m*(x_incid - delta_x) + Cy
    self.ax1.plot(x_incid, y_incid, linestyle='dashed', linewidth=1, color="grey")
    self.ax1.text(0, 3500, "incid = {}°".format(incidence_angle_deg), color='grey')

    # Create event when mouse clicking on profile
    # self.figure_profile.canvas.mpl_connect('button_press_event', lambda event: onclick_profile(self, event))
    self.figure_profile.canvas.mpl_connect('button_press_event', lambda event: on_click(event, self))
    self.figure_profile.canvas.mpl_connect('button_release_event', lambda event: on_release(event, self))
    self.figure_profile.canvas.mpl_connect('motion_notify_event', lambda event: on_motion(event, self))




    # self.ax1.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

    # Canvas creation
    self.canvas_profile = FigureCanvas(self.figure_profile)
    # self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    # self.canvas.setFocus()




    return self.canvas_profile



#===============================================================================================================
#====================   3D VIEW    ===============================================================
#===============================================================================================================



def getView3dFig(self):
    """ Function to draw Simulated amplitude based on profile"""

  # File name
    i = self.index_live
    dataset = self.dataset



    # Pixel size and incidence angle
    azimuth_pixel_size = dataset['azimuth_pixel_size'][i]
    range_pixel_size = dataset['range_pixel_size'][i]
    incidence_angle_deg = dataset['incidence_angle_deg'][i]
    incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360

    # Caldera ellipse
    caldera_edgeN_x = dataset['caldera_edgeN_x'][i]
    caldera_edgeN_y = dataset['caldera_edgeN_y'][i]
    caldera_edgeS_x = dataset['caldera_edgeS_x'][i]
    caldera_edgeS_y = dataset['caldera_edgeS_y'][i]

    # Crater outer ellipse
    crater_outer_edgeN_x = dataset['crater_outer_edgeN_x'][i]
    crater_outer_edgeN_y = dataset['crater_outer_edgeN_y'][i]
    crater_outer_edgeS_x = dataset['crater_outer_edgeS_x'][i]
    crater_outer_edgeS_y = dataset['crater_outer_edgeS_y'][i]

    # Crater inner ellipse
    crater_inner_edgeN_x = dataset['crater_inner_edgeN_x'][i]
    crater_inner_edgeN_y = dataset['crater_inner_edgeN_y'][i]
    crater_inner_edgeS_x = dataset['crater_inner_edgeS_x'][i]
    crater_inner_edgeS_y = dataset['crater_inner_edgeS_y'][i]

    # Crater outer ellipse
    crater_topCone_edgeN_x = dataset['crater_topCone_edgeN_x'][i]
    crater_topCone_edgeN_y = dataset['crater_topCone_edgeN_y'][i]
    crater_topCone_edgeS_x = dataset['crater_topCone_edgeS_x'][i]
    crater_topCone_edgeS_y = dataset['crater_topCone_edgeS_y'][i]

    # Crater outer ellipse
    crater_bottom_edgeN_x = dataset['crater_bottom_edgeN_x'][i]
    crater_bottom_edgeN_y = dataset['crater_bottom_edgeN_y'][i]
    crater_bottom_edgeS_x = dataset['crater_bottom_edgeS_x'][i]
    crater_bottom_edgeS_y = dataset['crater_bottom_edgeS_y'][i]





 ####### Draw picked topography ###########




    # >=P2
    Ix = int(caldera_edgeN_y*azimuth_pixel_size)
    Iy = Zvolc

    Jx = int(caldera_edgeS_y*azimuth_pixel_size)
    Jy = Zvolc


    delta_ref_x = Ix + ((Jx - Ix)/2)


    Kx = int(crater_outer_edgeN_y*azimuth_pixel_size)
    a1 = abs(crater_outer_edgeN_x - caldera_edgeN_x)*range_pixel_size
    h1 = int(a1 / np.cos(incidence_angle_rad))
    Ky = Iy - h1

    Lx = int(crater_outer_edgeS_y*azimuth_pixel_size)
    Ly = Ky



    # P2
    a2 = (crater_outer_edgeN_x - crater_inner_edgeN_x)*range_pixel_size
    delta_x = (a2)/(np.sin(incidence_angle_rad))
    if self.current_orbit_desc:
        delta_x = -delta_x
    diameter_crater = (int(crater_inner_edgeS_y) - int(crater_inner_edgeN_y)) * azimuth_pixel_size


    Cx = (delta_ref_x + delta_x) - (diameter_crater/2)
    Cy = Ky

    Dx = (delta_ref_x + delta_x) + (diameter_crater/2)
    Dy = Ky

    # <P2
    Ux = Cx
    a3 = abs(crater_topCone_edgeN_x - crater_inner_edgeN_x)*range_pixel_size
    h2 = int(a3/np.cos(incidence_angle_rad))
    Uy = Cy - h2

    Vx = Dx
    Vy = Uy

    # Cone

    a4 = abs(crater_bottom_edgeN_x - crater_topCone_edgeN_x)*range_pixel_size
    h3 = int(a4/np.cos(incidence_angle_rad))
    Ey = Uy - h3
    diameter_bottom = (int(crater_bottom_edgeS_y) - int(crater_bottom_edgeN_y)) * azimuth_pixel_size
    Ex = (delta_ref_x + delta_x) - (diameter_bottom/2)
    Fx = (delta_ref_x + delta_x) + (diameter_bottom/2)
    Fy = Ey

# Add informations about azimut position, which is not needed in profile !

    Caz = int(crater_inner_edgeN_y*azimuth_pixel_size)
    Daz = int(crater_inner_edgeS_y*azimuth_pixel_size)
    center_az = (Daz - Caz)/2 + Caz 
    delta_az = delta_ref_x - center_az



    # Centering all X axis points with the middle of the caldera as reference.
    Ix -= delta_ref_x 
    Jx -= delta_ref_x
    Kx -= delta_ref_x
    Lx -= delta_ref_x
    Cx -= delta_ref_x
    Dx -= delta_ref_x
    Ux -= delta_ref_x
    Vx -= delta_ref_x
    Ex -= delta_ref_x
    Fx -= delta_ref_x





    # Create array to draw profile

    X_profile_all = [-2500, Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx, 2500]
    Y_profile_all = [2500, Iy, Ky, Cy, Uy, Ey, Fy, Vy, Dy, Ly, Jy, 2500]
    
   
    #========================== DRAW FIGURE ================================#


    # Create figure that will be return to the mainwindow
    self.figure_view_3d = Figure()
    # self.figure_view_3d.set_figwidth(100)
    # self.figure_view_3d.set_figheight(200)



    # print("print 3d view")
    self.ax2 = self.figure_view_3d.add_subplot(111, projection='3d') 
    # n1 is number of samples to create circle
    # n2, number of sample to link both circle

    n11 = 40
    n21 = 20

    n12 = 20
    n22 = 10

   
    # Draw Outside of caldera
    X, Y, Z = get_cone_data(0, 0, -2500, Ix, 2500, Iy, n12, n22)
    self.ax2.plot_wireframe(X, Y, Z, color='grey', alpha=0.2)
    # Caldera ring
    Xc, Yc, Zc = data_for_cylinder_along_z(0, 0, Ix, Iy)
    self.ax2.plot(Xc, Yc, Zc, color='blue', linewidth=3)

    # Draw cone from caldera ring to P2 outer ring
    X, Y, Z = get_cone_data(0, 0, Ix, Kx, Iy, Ky, n11, n21)
    self.ax2.plot_wireframe(X, Y, Z, color='grey', alpha=0.3)
    # Draw P2 Outer ring
    Xc, Yc, Zc = data_for_cylinder_along_z(0, 0, Kx, Ky)
    self.ax2.plot(Xc, Yc, Zc, color='skyblue', linewidth=3)

    # Draw P2, need to use another function as both circle are at the same height but not centered the same
    rayon_inner = diameter_crater/2
    # get_perforated_surface(x1, y1,x2, y2, r1, r2, z, n1, n2)
    # print("get_perforated_surface: ",0, 0, delta_x, 0, Kx, rayon_inner, Ky, n11, n21)
    X2, Y2, Z2 = get_perforated_surface(0, 0, delta_x, delta_az, Kx, rayon_inner , Ky, n11, n21)
    self.ax2.scatter(X2, Y2, Z2, color='grey', linewidth=1, alpha=0.3)

    # Draw P2 inner ring (lake limit)
    Xc, Yc, Zc = data_for_cylinder_along_z(delta_x, delta_az, rayon_inner, Cy)
    self.ax2.plot(Xc, Yc, Zc, color='red', linewidth=3)

    # Draw cone from P2 level to vertical limit inside the crater
    X3, Y3, Z3= get_cone_data(delta_x, delta_az, rayon_inner, rayon_inner, Cy, Uy, n12, n22)
    self.ax2.plot_wireframe(X3, Y3, Z3, color='grey', alpha=0.3)
    # Draw middle bottom crater ring
    Xc, Yc, Zc = data_for_cylinder_along_z(delta_x, delta_az, rayon_inner, Uy)
    self.ax2.plot(Xc, Yc, Zc, color='orange', linewidth=3)

    # Draw cone from middle of crater to bottom of crater
    rayon_inner_bottom = diameter_bottom/2
    X2, Y2, Z2= get_cone_data(delta_x, delta_az, rayon_inner, rayon_inner_bottom , Uy, Ey, n12, n22)
    self.ax2.plot_wireframe(X2, Y2, Z2, color='grey', alpha=0.3)


    # Draw bottom surface
    X2, Y2, Z2= get_cone_data(delta_x, delta_az, rayon_inner_bottom, 1, Ey, Ey, n12, n22)
    self.ax2.plot_wireframe(X2, Y2, Z2, color='grey', alpha=0.3)
    # Draw Bottom ring
    Xc, Yc, Zc = data_for_cylinder_along_z(delta_x, delta_az, rayon_inner_bottom, Ey)
    self.ax2.plot(Xc, Yc, Zc, color='magenta', linewidth=3)



    self.ax2.set_xlim(-1000, 1000)
    self.ax2.set_ylim(-1000, 1000)

    # print(dir(self.figure_view_3d))

    self.ax2.set_ylabel('$Azimuth$', fontsize=15, rotation=150)
    self.ax2.set_xlabel('$Range$', fontsize=15, rotation=150)


    X_profile_all = [-2500, Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx, 2500]
    Y_profile_all = [2500, Iy, Ky, Cy, Uy, Ey, Fy, Vy, Dy, Ly, Jy, 2500]




    self.figure_view_3d.tight_layout(pad=100.0)
    # Canvas creation
    self.canvas_view_3d = FigureCanvas(self.figure_view_3d)


    # self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    # self.canvas.setFocus()

    return self.canvas_view_3d



#===============================================================================================================
#====================    SIMULATED AMPLITUDE     ===============================================================
#===============================================================================================================


def getSimAmpliFig(self, init):
    """ Function that will return the canvas of simulated amplitude
    1. Load data locally from csv file (no need somewhere else so do not use self)
    2. Call function that will calculate the final matrice
    3. Plot the matrice and return the canvas"""

    # Load data for simulated amplitude

    csv_file_out = self.csv_file + '_pick_tmp.csv'

    dataset = csv_to_dict(csv_file_out)

    # find line corresponding to current image 
      # File name
    i = self.index_live

    # Map footprint in meters
    xmin, xmax = -3500, 3500
    ymin, ymax = -3500, 3500
    ech = 501     # x and y sampling number
    subs = 5     # subsampling intervalle for plots
    ech2 = 1000     # range sampling for amplitude computation


    # Define grid
    x,y = np.linspace(xmin,xmax, ech), np.linspace(ymin,ymax, ech)
    Y,X = np.meshgrid(x,y)
    Z = np.zeros(X.shape)        # initialise elevation at 0m everywhere


    #------ Define 3D Volcano -----#

    # Cone edifice
    Rcald = dataset['Rcald_m'][i]
    Rbase = 2500
    Zbase = 2500
    Zvolc = 3460
    R_P2 = dataset['RP2_m'][i]
    ZP2 = Zvolc - dataset['HP2_m'][i]
    ZBotcrat = ZP2 - dataset['H'][i]
    Rcrat = dataset['Rcrat_m'][i]
    Beta = dataset['Beta'][i]  # 0 conic, 1 cylinder
    Alpha = dataset['Alpha'][i] # 0 conic, 1 cylinder
    decalX = dataset['delta_x_m'][i]
    # 
    incid_deg = dataset['incidence_angle_deg'][i]
    azim = dataset['azimuth_pixel_size'][i]
    slra = dataset['range_pixel_size'][i]
    MODE = "Descending Right"

    filepath = dataset['filepath'][i]
    satname = filepath.split('/')[-2]
    img_date_string = dataset['img_date'][i]


    incid = math.radians(incid_deg)
    incidir = [math.sin(incid), 0, math.cos(incid)]
    M = [0,0,Zvolc]

    #----- Define ellipse ----#

    t = np.linspace(0, 2*np.pi, 1000)
    caldera = [Rcald*np.cos(t), Rcald*np.sin(t), t*0+Zvolc ]
    P2 = [R_P2*np.cos(t), R_P2*np.sin(t), t*0+ZP2 ]
    crat = [Rcrat*np.cos(t)+decalX, Rcrat*np.sin(t), t*0+ZP2 ]
    interm = [Rcrat*np.cos(t)+decalX, Rcrat*np.sin(t), t*0+ZP2-(ZP2-ZBotcrat)*Beta]
    bot = [Alpha*Rcrat*np.cos(t)+decalX,Alpha*Rcrat*np.sin(t),t*0+ZBotcrat]
    base = [Rbase*np.cos(t),Rbase*np.sin(t),t*0+Zbase]


    # project ellipse
    caldera_proj = proj_ortho(np.array(caldera), M[2], incid) 
    P2_proj = proj_ortho(np.array(P2), M[2], incid) 
    crat_proj = proj_ortho(np.array(crat), M[2], incid) 
    interm_proj = proj_ortho(np.array(interm), M[2], incid) 
    bot_proj = proj_ortho(np.array(bot), M[2], incid) 
    base_proj = proj_ortho(np.array(base), M[2], incid) 



    if init:
        # print("test calculate sim ampli")
        #----- create 3d shape, project matrice along plane, compute space between points to calculate final matrice ---#

        theta_edifice = math.atan((Rcald - Rbase)/(Zbase - Zvolc))
        ind =  np.where((X**2 + Y**2) <= Rbase**2)
        Z[ind] = (Rbase / math.tan(theta_edifice)) - np.sqrt((X[ind]**2 + Y[ind]**2)/(math.tan(theta_edifice))**2)

        # inverted cone calderaZ
        theta_cald = math.atan((R_P2 - Rcald)/(Zvolc - ZP2))
        ind =  np.where((X**2 + Y**2) <= Rcald**2)
        Z[ind] = Zvolc - Zbase + (Rcald/math.tan(theta_cald)) + np.sqrt((X[ind]**2 + Y[ind]**2)/(math.tan(theta_cald))**2)
        Z = Z + Zbase

        # platform P2
        ind =  np.where((X**2 + Y**2) <= R_P2**2)
        Z[ind] = ZP2

        # crater cylinder
        ind =  np.where((((X - decalX)**2) + Y**2) <= Rcrat**2)
        Z[ind] = Z[ind] - (Beta * (ZP2 - ZBotcrat))

        # # crater inverted cone
        theta_crat = math.atan(np.float64(Rcrat * (Alpha - 1))/(ZP2 - ZBotcrat)*(1 - Beta))
        Z[ind] = Z[ind] + (np.float64(Rcrat)/math.tan(theta_crat)) + np.sqrt((np.float64((X[ind] - decalX)**2 + Y[ind]**2))/(math.tan(theta_crat)**2))
        # # crater flat bottom
        ind =  np.where(((X - decalX)**2 + Y**2) <= (Alpha * Rcrat)**2)
        Z[ind] = ZBotcrat


        #------ Projection -----#



        # projection line of interest
        ind = np.where(abs(X - decalX) == min(abs(x - decalX)))
        proj = proj_ortho(np.array([X[ind], Y[ind], Z[ind]]), M[2], incid)         # !!! not same indice as in matlab
        ind2 = np.where(abs(X) == min(abs(x)))
        proj2 = proj_ortho(np.array([X[ind2], Y[ind2], Z[ind2]]), M[2], incid)         # !!! not same indice as in matlab

        # projection of all points (X,Y,Z)
        n, p = Z.shape

        fullsize = n * p
        Xr = X.reshape(fullsize, 1)
        Yr = Y.reshape(fullsize, 1)
        Zr = Z.reshape(fullsize, 1)

        points2proj = np.array([Xr, Yr, Zr])
        pointsproj = proj_ortho(points2proj, M[2], incid)

        Xp = pointsproj[0]
        Yp = pointsproj[1]
        Zp = pointsproj[2]

        Xproj = Xp.reshape(n, p)
        Yproj = Yp.reshape(n, p)
        Zproj = Zp.reshape(n, p)


        #------ Compute distance for simulated amplitude -----#


        # initialisation
        Dist = np.zeros(Z.shape)
        Distcum = np.zeros(Z.shape)
        Distnorm = np.zeros(Z.shape)

        for k in range(1, p):
            # compute distance topo between two consecutive points for all raws
            Dist[:,k] = np.sqrt(((Z[k,:] - Z[k-1, :])**2 + (X[k,:] - X[k-1, :])**2))
            # compute cumulative distance since the beginning of the profiles
            Distcum[:,k] = Distcum[:, k-1] + Dist[:,k]

        maxdistcum = np.max(Distcum,1) # compute distance max of each profile   # !!! not same indice as in matla


        for k in range(0, n):
            # normalize Dist with distance max of each profile
            Distnorm[k,:] = np.divide(Dist[k,:], maxdistcum[k])



        # # compute vector between each projected point and fixed point M

        pointsproj_f = pointsproj.transpose()
        pointsproj_f = pointsproj_f.reshape(fullsize, 3)
        M_np = np.array(M)
        M_np = M_np.reshape(1, 3)
        rep_M = np.tile(M_np, (fullsize, 1))
        Vec = np.subtract(pointsproj_f, rep_M)


        # # compute scalar product of Vec with direction of incidence (distance along range)
        distproj = np.zeros((fullsize, 1))
        for k in range(0, fullsize):
            distproj[k,:] = np.dot(Vec[k,:], incidir)

        Distproj = distproj.reshape(n, p)
        Distproj = Distproj.transpose()

        mindistproj = np.min(np.min(Distproj))
        maxdistproj = np.max(np.max(Distproj))


        self.distotprojforinterp = np.linspace(mindistproj, maxdistproj, ech2) # interpole range regular sampling
        Matdist = np.zeros((n, p, ech2))

        for k in range(0, n):
            distprojk = Distproj[k,:]
            mindistprojk = np.min(distprojk)
            maxdistprojk = np.max(distprojk)
            distotproj = np.linspace(mindistproj, maxdistproj, ech2)
            for l in range(1, p):
                dist1 = distprojk[l-1]
                dist2 = distprojk[l]
                if (dist1 < dist2):
                    ind = np.where((distotproj > dist1) & (distotproj <= dist2))
                else:
                    ind = np.where((distotproj <= dist1) & (distotproj > dist2))

                Matdist[k,l,ind] = Distnorm[k,l]/abs(dist1 - dist2) * abs(maxdistprojk - mindistprojk)



        # # Compute simulated amplitude
        MATDIST = np.zeros((n, ech2))
        MATDIST[:,:] = np.sum(Matdist, 1)


        if incid_deg < 0:
            self.MATDIST = np.fliplr(MATDIST)
            self.sign= -1
        else:      
            self.sign = 1
            self.MATDIST = MATDIST


    #------ Plot stuff -----#

    # Create figure that will be return to the mainwindow
    # fig = Figure(projection='3d')
    fig = Figure(figsize = (7,7))
    # self.figure_view_3d.set_figwidth(100)
    # self.figure_view_3d.set_figheight(200)

    ax = fig.add_subplot(111) 
    # ax = fig.add_subplot(111, projection='3d') 
    ax.set_title("{}:{}".format(satname, img_date_string))


    # Get the coordinate of center of caldera in original image
    center_x = self.dataset['caldera_edgeN_x'][i]
    center_y = self.dataset['caldera_edgeN_y'][i] + ((self.dataset['caldera_edgeS_y'][i] - self.dataset['caldera_edgeN_y'][i])/2)
    xmin = -center_x
    xmax = self.SAR_height - center_x
    ymin = -center_y
    ymax = self.SAR_width - center_y

    # Manage pixel ticks with command extend and the brightness with vmin - vmax
    range_ra = self.sign*self.distotprojforinterp/slra
    range_az = y/azim
    mean_val = np.mean(self.MATDIST)
    vmin = mean_val - (80/100 * mean_val)
    vmax = mean_val + (150/100 * mean_val)
    ax.imshow(self.MATDIST, cmap='Greys_r', vmin=vmin, vmax=vmax, extent=[np.min(range_ra),np.max(range_ra), range_az[0] ,range_az[-1]], aspect='auto')
    # ax.plot_surface(X, Y, Z, alpha=0.5, color='b')
    # ax.plot_surface(Xproj, Yproj, Zproj, alpha=0.5, color='r')

    if self.pushButton_ellipse_simamp.isChecked():
        ax.plot(caldera_proj[0,:]/abs(math.sin(incid))/slra , caldera_proj[1,:]/azim, color='blue')
        ax.plot(P2_proj[0,:]/abs(math.sin(incid))/slra , P2_proj[1,:]/azim, color='skyblue')
        ax.plot(crat_proj[0,:]/abs(math.sin(incid))/slra , crat_proj[1,:]/azim, color='red')
        ax.plot(interm_proj[0,:]/abs(math.sin(incid))/slra , interm_proj[1,:]/azim, color='orange')
        ax.plot(bot_proj[0,:]/abs(math.sin(incid))/slra , bot_proj[1,:]/azim, color='magenta')
        ax.plot(base_proj[0,:]/abs(math.sin(incid))/slra , base_proj[1,:]/azim, color='k')


    # Crop the image to calcluted coordinate from original SAR image
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_ylabel("azimut")
    ax.set_xlabel("range")
    fig.tight_layout()


    # Canvas creation
    canvas = FigureCanvas(fig)


    # self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    # self.canvas.setFocus()

    return canvas




#===============================================================================================================
#====================    SIMULATED AMPLITUDE     ===============================================================
#===============================================================================================================


def getPickingResultsFig(self, date_only):
    """ Function that will return the canvas of picking results plot
    1. Load data locally from csv file (no need somewhere else so do not use self)
    2. Plot the results and return the canvas"""

    # Load data for simulated amplitude
    csv_file_out = self.csv_file + '_pick_tmp.csv'
    images_data = pd.read_csv(csv_file_out, comment='#', na_values=['99999','0'])


    images_number = len(images_data['filepath'])
    timestr = images_data.iloc[:,1:3].astype(str).apply('T'.join,axis=1)
    times = pd.to_datetime(timestr, format='%Y%m%dT%H:%M:%S')
    

    # find line corresponding to current image 
      # File name
    i = self.index_live
    current_date_str = images_data['img_date'][i]
    current_date = datetime.datetime.strptime(str(current_date_str), "%Y%m%d")
    current_time_str = images_data['img_hour'][i]
    current_time = datetime.datetime.strptime(str(current_time_str), "%H:%M:%S")
    current_datetime_str = "{}_{}".format(current_date_str, current_time_str)
    current_datetime = datetime.datetime.strptime(str(current_datetime_str), "%Y%m%d_%H:%M:%S")


    start_date_str = np.sort(images_data['img_date'])[0]
    start_date = datetime.datetime.strptime(str(start_date_str), "%Y%m%d")
    end_date_str = np.sort(images_data['img_date'])[-1]
    end_date = datetime.datetime.strptime(str(end_date_str), "%Y%m%d")
    print("start_date = ", start_date)
    print("end_date = ", end_date)

    # Set the date to dateEdit object by default (value coming from csv file)
    if not self.mem_date_pickplt:
        self.dateEdit_plotpicks_start.setDate(start_date)
        self.dateEdit_plotpicks_end.setDate(end_date)
        self.mem_date_pickplt = True

     # getting the date from the dateEdit object
    t1 = self.dateEdit_plotpicks_start.date().toPyDate()
    t2 = self.dateEdit_plotpicks_end.date().toPyDate()

    # display time of last eruption
    Terupt = datetime.datetime.strptime('2021-05-22T16:30:00', "%Y-%m-%dT%H:%M:%S")


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
    mks = 4
    LW = 0.7
    fig, [ax1, ax2] = pyplt.subplots(2, 1, sharex=True, figsize=(7,7))
    ax1.set_xlim(t1, t2)
    ax1.errorbar(times, Rcald_m, yerr=2*azimuth_pixel_size, xerr=None,color='blue',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=2,label='$R_s$')
    ax1.errorbar(times, RP2_m, yerr=3*azimuth_pixel_size, xerr=None,color='cyan',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=2,label='$R_{P2}$')
    ax1.errorbar(times, Rcrat_m, yerr=4*azimuth_pixel_size, xerr=None,color='red',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=2,label='$R_c$')
    ax1.errorbar(times, Rbot_m, yerr=5*azimuth_pixel_size, xerr=None,color='magenta',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=2,label='$R_b$')
    ax1.plot([t1, t2],[mean(Rcald_m),mean(Rcald_m)],'--',color='blue')
    ax1.plot([t1, t2],[mean(RP2_m),mean(RP2_m)],'--',color='cyan')
    ax1.plot([t1, t2],[100,100],'--',color='magenta')
    ax1.plot([t1, t2],[350, 350],'--',color='red')

    ax1.legend(loc='center left',fontsize=10,bbox_to_anchor=(1, 0.5))
    ax1.set_xlabel('Time',fontsize=10)
    ax1.set_ylabel('Radius (m)',fontsize=10)


    ax2.errorbar(times, Zvolc-HP2, yerr=10*range_pixel_size/cosincid, xerr=None,color='cyan',ms=mks, fmt='o', ecolor='black', elinewidth=LW, capsize=2,label='$Z_{P2}$')
    ax2.errorbar(times[indpos],Zvolc-HP2[indpos]-H[indpos], yerr=errH[indpos], xerr=None,color='magenta',ms=mks, fmt='^', ecolor='black', elinewidth=LW, capsize=2,label='$Z_{b; {\\theta}>0}$')
    ax2.errorbar(times[indneg],Zvolc-HP2[indneg]-H[indneg], yerr=errH[indneg], xerr=None,color='magenta',ms=mks, fmt='v', ecolor='black', elinewidth=LW, capsize=2,label='$Z_{b;{\\theta}<0}$')
    ax2.plot([t1, t2],[Zvolc, Zvolc],color='blue', label='$Z_s$')
    ax2.plot([t1, t2],[Zvolc-mean(HP2), Zvolc-mean(HP2)],'--',color='red', label='$Z_{P2}$')
    # ax2.plot([t1, t2],[Zb2002, Zb2002],':', color='gray', label='$Z_b^{2002}$')

    ax1.plot([Terupt, Terupt],[0, 700],'-.',color='black')
    ax2.plot([Terupt, Terupt],[2500, 3500],'-.',color='black')


    ax2.set_xlabel('Time',fontsize=10)
    ax2.set_ylabel('Elevation (m)',fontsize=10)
    ax2.legend(loc='center left',fontsize=10,bbox_to_anchor=(1, 0.5))
    ax2.tick_params(axis='both',labelsize=9)
    ax1.tick_params(axis='y',labelsize=9)

    # draw vertical line on current displayed SAR image
    ax1.axvline(current_datetime, color='grey', linestyle='--', linewidth=1)
    ax2.axvline(current_datetime, color='grey', linestyle='--', linewidth=1)

    # Set the x-axis format to "day/month/year"
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))



    canvas = FigureCanvas(fig)

    return canvas










#===============================================================================================================
#====================    Connected functions    ===============================================================
#===============================================================================================================


def _add_point(self, x, y=None):
    if isinstance(x, MouseEvent):
        x, y = int(x.xdata), int(x.ydata)
        self._points[self._dragging_key] = {}
        self._points[self._dragging_key][x] = y
    return x, y

def _remove_point(self, x, _):
    if x in self._points:
        self._points[self._dragging_key].pop(x)

def _find_neighbor_point(self, event):
    u""" Find point around mouse position
    :rtype: ((int, int)|None)
    :return: (x, y) if there are any point around mouse else None
    """
    distance_threshold = 20.0
    nearest_point = None
    min_distance = math.sqrt(2 * (100 ** 2))
    for key in self._points.keys():
        for x, y in self._points[key].items():
            distance = math.hypot(event.xdata - x, event.ydata - y)
            if distance < min_distance:
                min_distance = distance
                nearest_point = (x, y)
                if min_distance < distance_threshold:
                    return key, nearest_point
    return None

def on_click(event, self):
    u""" callback method for mouse click event
    :type event: MouseEvent
    """
    # left click
    if event.button == 1 and event.inaxes in [self.ax1]:
        key, point = _find_neighbor_point(self, event)
        # print("on_click, point = ", key, point)
        if point:
            self._dragging_point = point
            self._dragging_key = key
        # else:
        #     self._add_point(event)
        update_plot(self)



def on_release(event, self):
    u""" callback method for mouse release event
    :type event: MouseEvent
    """
    if event.button == 1 and event.inaxes in [self.ax1] and self._dragging_point:
        self._dragging_point = None
        update_plot(self)

        # Update profile with color code
        # self.updateProfilePlt()
        # Update ellipse position from profile change
        self.updateSARPlot()
        # Set checked save button to tell user modification has been done
        self.pushButton_pickSAR_save.setChecked(True)



def on_motion(event, self):
    """ callback method for mouse motion event
    :type event: MouseEvent
    """
    if not self._dragging_point:
        return
    if event.xdata is None or event.ydata is None:
        return
    _remove_point(self, *self._dragging_point)
    self._dragging_point = _add_point(self, event)
    update_plot(self)




# end