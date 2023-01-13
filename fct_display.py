from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import matplotlib as plt
import numpy as np
import os, math, re, time, sys
import datetime as datetime
from osgeo import gdal
from PyQt5 import QtCore



# import numpy as np
# import os as os
# from netCDF4 import Dataset
# from mpl_toolkits import mplot3d
# from mpl_toolkits.mplot3d import axes3d
# from matplotlib import patches
# import matplotlib.pyplot as plt






# def displayTest(self):

#     figure = Figure()
#     axes = figure.gca()
#     axes.set_title("My Plot")
#     x = np.linspace(1, 10)
#     y = np.linspace(1, 10)
#     y1 = np.linspace(11, 20)
#     axes.plot(x, y, "-k", label="first one")
#     axes.plot(x, y1, "-b", label="second one")
#     axes.legend()
#     axes.grid(True)
#     # Canvas creation
#     canvas = FigureCanvas(figure)

#     return canvas

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


    print("X_profile_all = Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx") 
    print("X_profile_all = ",Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx) 
   
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
    self.ax1.set_xlabel('[m] (range dircetion)')
    self.ax1.set_ylabel('[m]')
    self.ax1.text(-250, 2500, "delta X = {}m".format(delta_x))
    self.ax1.text(-250, 2450, "P2 from top = {}m".format(h1))
    self.ax1.text(-250, 2400, "Caldera Radius= {}m".format(Jx))
    self.ax1.text(-250, 2350, "P2 radius = {}m".format(Lx))
    self.ax1.text(-250, 2300, "Crat radius = {}m".format(diameter_crater/2))
    self.ax1.text(-250, 2250, "Bottom from P2 = {}m".format(Cy - Ey))
    self.ax1.text(-250, 2210, "Bottom radius = {}m".format(diameter_bottom/2))

  





    # Create event when mouse clicking on profile
    # self.figure_profile.canvas.mpl_connect('button_press_event', lambda event: onclick_profile(self, event))
    self.figure_profile.canvas.mpl_connect('button_press_event', lambda event: _on_click(event, self))
    self.figure_profile.canvas.mpl_connect('button_release_event', lambda event: _on_release(event, self))
    self.figure_profile.canvas.mpl_connect('motion_notify_event', lambda event: _on_motion(event, self))




    # self.ax1.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

    # Canvas creation
    self.canvas_profile = FigureCanvas(self.figure_profile)
    # self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    # self.canvas.setFocus()




    return self.canvas_profile



#===============================================================================================================
#====================    SIMULATED AMPLITUDE     ===============================================================
#===============================================================================================================




def getSimAmpliFig(self):
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
    self.figure_sim_ampli = Figure()
    self.figure_sim_ampli.set_figwidth(100)
    self.figure_sim_ampli.set_figheight(200)

    #===== FIRST PLOT =====#
    # self.ax2 = self.figure_sim_ampli.add_subplot(211) 
    # # Create 1 curve that will react to mouse event to help user modifying the profile
    # # All the other plotwill be superposed on it with color code
    # self._line2 = lines.Line2D(X_profile_all ,Y_profile_all , marker="o", color="grey", markeredgecolor="grey", markerfacecolor="grey")
    # # self.ax2.add_line(self._line2)
    # # # Set fixed data on profile with color related to ellipse on amplitude image
    # # # self.ax2.set_title("Simulated Amplitude")
    # # self.ax2.set_xlim(-2500, 2500)  # self.SAR_width = number of pixels in azimut direction for this image
    # # self.ax2.set_ylim(2200, 4200)
    # # self.ax2.set_xlabel('[m]')
    # # self.ax2.set_ylabel('[m]')
    # # Sampling of profile on 100 points
    # x_values = self._line.get_xdata()
    # y_values = self._line.get_ydata()
    # # create a list of evenly spaced x values
    # num_samples = 200
    # x_samples = np.linspace(min(x_values), max(x_values), num_samples)
    # # interpolate the y values at these x values
    # y_samples = np.interp(x_samples, x_values, y_values)
    # # create a list of points
    # points = [(x, y) for x, y in zip(x_samples, y_samples)]
    # # print(points)
    # # self.ax2.plot(x_samples,y_samples,marker="o", markeredgecolor="orange", markersize=2)
    # # From Delphine
    # self.ax2.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)



    #======================== FIRST PLOT : Ctrater in 3d    ========================#

    if self.pushButton_3d.isChecked():


        print("print 3d view")
        self.ax2 = self.figure_sim_ampli.add_subplot(111, projection='3d') 
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

        print("delta_x in 3D view = ", delta_x)
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

        # print(dir(self.figure_sim_ampli))

        self.ax2.set_ylabel('$Azimuth direction$', fontsize=20, rotation=150)
        self.ax2.set_xlabel('$Range direction$', fontsize=20, rotation=150)


        X_profile_all = [-2500, Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx, 2500]
        Y_profile_all = [2500, Iy, Ky, Cy, Uy, Ey, Fy, Vy, Dy, Ly, Jy, 2500]








    #======================== SECOND PLOT ========================#

    elif self.pushButton_profile.isChecked():

        import matplotlib.path as mpath
        import matplotlib.transforms as transforms

        print("print profile")



    # # Rotate Profile
        print("print profile")
        self.ax2 = self.figure_sim_ampli.add_subplot(211) 
        self.ax2.set_title("Rotate profile: angle = {} deg".format(incidence_angle_deg))

        self._line2 = lines.Line2D(X_profile_all ,Y_profile_all , marker="o", color="grey", markeredgecolor="grey", markerfacecolor="grey", alpha=0.5)
        # self.ax2.add_line(self._line2)
        self.ax2.set_xlim(-2500, 2500)  # self.SAR_width = number of pixels in azimut direction for this image
        self.ax2.set_ylim(2200, 4200)
        self.ax2.set_xlabel('[m]')
        self.ax2.set_ylabel('[m]')   
        # Sampling of profile on 100 points
        x_values = self._line.get_xdata()
        y_values = self._line.get_ydata()    
        # create a list of evenly spaced x values
        num_samples = 200
        x_samples = np.linspace(min(x_values), max(x_values), num_samples)
        # interpolate the y values at these x values
        y_samples = np.interp(x_samples, x_values, y_values)
        # create a list of points
        points = [(x, y) for x, y in zip(x_samples, y_samples)]
        # print(points)
        self.ax2.plot(x_samples,y_samples,marker="o", markeredgecolor="grey", markersize=1)

        # Format as vertices to allow path
        vertices = list(zip(x_samples,y_samples))
        # print("vertices = ", vertices)
        # Create a Path object from the vertices
        path = mpath.Path(vertices)
        # Create a transformation object with center the middle of the crater
        rotation = -incidence_angle_deg
        trans = transforms.Affine2D().rotate_deg_around(0, Iy, rotation)
        # Transform the Path object using the transformation
        transformed_path = trans.transform_path(path)
        # Get the transformed coordinates of the polygon's points
        transformed_vertices = transformed_path.vertices
        # Print the transformed coordinates
        # print(transformed_vertices)
        # Extract x and y array from rotated vertices
        x2, y2 = zip(*transformed_vertices)
        # Plot it
        # self.ax2.plot(x2,y2,marker=".", color="orange", markersize=1)
        self.ax2.scatter(x2,y2, color="red", marker='.', edgecolors="k", linewidths=0.5)


        print("y_samples = ", y_samples)
        print("typeof y_samples = ", type(y_samples))
        print("typeof y_samples = ", type(y_samples[0]))
  

        print("y2 = ", y_samples)
        print("typeof y2 = ", type(y2))
        print("typeof y2 = ", type(y2[0]))        

        # Create Histogram
        self.ax3 = self.figure_sim_ampli.add_subplot(212)
        self.ax3.set_title("Histogram")
        bins = 100 # Number of samples in range
        self.ax3.hist(y_samples, bins=bins, orientation='vertical', color="grey", alpha=0.6)
        # self.ax3.hist(y2, bins=bins, orientation='vertical', color="red", alpha=0.3)

    # #===== THIRD PLOT =====#


    # if self.pushButton_simamp.isChecked():


    #     print("print 3d view")
    #     self.ax2 = self.figure_sim_ampli.add_subplot(111, projection='3d') 
    #     # n1 is number of samples to create circle
    #     # n2, number of sample to link both circle


    #     # Map footprint in meters
    #     xmin, xmax = -3500, 3500
    #     ymin = -3500, 3500
    #     ech = 501     # x and y sampling number
    #     subs = 5     # subsampling intervalle for plots
    #     ech2 = 1000     # range sampling for amplitude computation


    #     # Define grid
    #     x,y = np.linspace(xmin,xmax, ech), np.linspace(ymin,ymax, ech)
    #     X,Y = np.meshgrid(x,y)
    #     Z = np.zeros(len(X))        # initialise elevation at 0m everywhere


    #     n11 = 40
    #     n21 = 20

    #     n12 = 20
    #     n22 = 10

       
    #     # Draw Outside of caldera
    #     X1, Y1, Z1 = get_cone_data(0, 0, -2500, Ix, 2500, Iy, n12, n22)
    #     ind = np.where
    #     self.ax2.plot_wireframe(X, Y, Z, color='grey', alpha=0.2)
    #     # Caldera ring
    #     Xc, Yc, Zc = data_for_cylinder_along_z(0, 0, Ix, Iy)
    #     self.ax2.plot(Xc, Yc, Zc, color='blue', linewidth=3)

    #     # Draw cone from caldera ring to P2 outer ring
    #     X, Y, Z = get_cone_data(0, 0, Ix, Kx, Iy, Ky, n11, n21)
    #     self.ax2.plot_wireframe(X, Y, Z, color='grey', alpha=0.3)
    #     # Draw P2 Outer ring
    #     Xc, Yc, Zc = data_for_cylinder_along_z(0, 0, Kx, Ky)
    #     self.ax2.plot(Xc, Yc, Zc, color='skyblue', linewidth=3)

    #     # Draw P2, need to use another function as both circle are at the same height but not centered the same
    #     rayon_inner = diameter_crater/2
    #     # get_perforated_surface(x1, y1,x2, y2, r1, r2, z, n1, n2)
    #     # print("get_perforated_surface: ",0, 0, delta_x, 0, Kx, rayon_inner, Ky, n11, n21)
    #     X2, Y2, Z2 = get_perforated_surface(0, 0, delta_x, delta_az, Kx, rayon_inner , Ky, n11, n21)
    #     self.ax2.scatter(X2, Y2, Z2, color='grey', linewidth=1, alpha=0.3)

    #     # Draw P2 inner ring (lake limit)
    #     Xc, Yc, Zc = data_for_cylinder_along_z(delta_x, delta_az, rayon_inner, Cy)
    #     self.ax2.plot(Xc, Yc, Zc, color='red', linewidth=3)

    #     print("delta_x in 3D view = ", delta_x)
    #     # Draw cone from P2 level to vertical limit inside the crater
    #     X3, Y3, Z3= get_cone_data(delta_x, delta_az, rayon_inner, rayon_inner, Cy, Uy, n12, n22)
    #     self.ax2.plot_wireframe(X3, Y3, Z3, color='grey', alpha=0.3)
    #     # Draw middle bottom crater ring
    #     Xc, Yc, Zc = data_for_cylinder_along_z(delta_x, delta_az, rayon_inner, Uy)
    #     self.ax2.plot(Xc, Yc, Zc, color='orange', linewidth=3)

    #     # Draw cone from middle of crater to bottom of crater
    #     rayon_inner_bottom = diameter_bottom/2
    #     X2, Y2, Z2= get_cone_data(delta_x, delta_az, rayon_inner, rayon_inner_bottom , Uy, Ey, n12, n22)
    #     self.ax2.plot_wireframe(X2, Y2, Z2, color='grey', alpha=0.3)


    #     # Draw bottom surface
    #     X2, Y2, Z2= get_cone_data(delta_x, delta_az, rayon_inner_bottom, 1, Ey, Ey, n12, n22)
    #     self.ax2.plot_wireframe(X2, Y2, Z2, color='grey', alpha=0.3)
    #     # Draw Bottom ring
    #     Xc, Yc, Zc = data_for_cylinder_along_z(delta_x, delta_az, rayon_inner_bottom, Ey)
    #     self.ax2.plot(Xc, Yc, Zc, color='magenta', linewidth=3)

    #     self.ax2.set_xlim(-1000, 1000)
    #     self.ax2.set_ylim(-1000, 1000)

    #     # print(dir(self.figure_sim_ampli))

    #     self.ax2.set_ylabel('$Azimuth direction$', fontsize=20, rotation=150)
    #     self.ax2.set_xlabel('$Range direction$', fontsize=20, rotation=150)


    #     X_profile_all = [-2500, Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx, 2500]
    #     Y_profile_all = [2500, Iy, Ky, Cy, Uy, Ey, Fy, Vy, Dy, Ly, Jy, 2500]






    self.figure_sim_ampli.tight_layout(pad=100.0)
    # Canvas creation
    self.canvas_sim_ampli = FigureCanvas(self.figure_sim_ampli)


    # self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    # self.canvas.setFocus()

    return self.canvas_sim_ampli







#===============================================================================================================
#====================    FUNCTION     ==========================================================================
#===============================================================================================================



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


#================== Picking Amplitude Image (SAR) function =========================#

def pick_point(self, info_str, x, y):
    """Function that will write in the dictionary "inages_data" new coordinate of clicked point"""
    x_str = "{}_x".format(info_str)
    y_str = "{}_y".format(info_str)
    # print("{} = [{}:{}]".format(info_str, x, y))
    self.dataset[x_str][self.index_live] = round(x)
    self.dataset[y_str][self.index_live] = round(y)


def getPointNameFromIndex(index):
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



#=========================== FUNCTION FOR DRAGGABLE POINTS ON PROFILE ===========================


def _update_plot(self):
    """ Write in dataset new value when points move on profile"""



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



    X_profile_all = [-2500, Ix, Kx, Cx, Ux, Ex, Fx, Vx, Dx, Lx, Jx, 2500]
    Y_profile_all = [2500, Iy, Ky, Cy, Uy, Ey, Fy, Vy, Dy, Ly, Jy, 2500]
    

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

def _on_click(event, self):
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
        _update_plot(self)



def _on_release(event, self):
    u""" callback method for mouse release event
    :type event: MouseEvent
    """
    if event.button == 1 and event.inaxes in [self.ax1] and self._dragging_point:
        self._dragging_point = None
        _update_plot(self)

        # Update profile with color code
        # self.updateProfilePlt()
        # Update ellipse position from profile change
        self.updateSARPlot()
        # Set checked save button to tell user modification has been done
        self.pushButton_pickSAR_save.setChecked(True)
        # Update 3dView if mode auto
        if self.checkBox_auto_update.isChecked():
            self.initiateSimAmpliPlot()
        else:
            self.pushButton_update_simamp.setChecked(True)


def _on_motion(event, self):
    """ callback method for mouse motion event
    :type event: MouseEvent
    """
    if not self._dragging_point:
        return
    if event.xdata is None or event.ydata is None:
        return
    _remove_point(self, *self._dragging_point)
    self._dragging_point = _add_point(self, event)
    _update_plot(self)



            


#=========================== FUNCTION FOR SIMULATED AMPLITUDE CREARTION ===========================

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










# end