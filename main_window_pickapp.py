
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QSlider, QCheckBox
from Ui_main_window_pickapp import Ui_MainWindow
from PyQt5.QtCore import pyqtSlot, QSize
from Loader import Loader
import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import numpy as np
from osgeo import gdal
import pandas as pd
from fct_display import *


#------------------------------------ DECORATEUR ----------------------------------------------#



# def data_loaded(fonction):
#     def autre_fonction():
#         self.label_SAR.setText("Please open a csv file before playing")
#     if not self.dataset:
#         return autre_fonction
#     return fonction 


#-----------------------------------------------------------------------------------------------#


class MainWindowPickApp(QMainWindow,Ui_MainWindow):
	def __init__(self,parent=None): 
		super(MainWindowPickApp,self).__init__(parent) 
		self.setupUi(self)
		self.dataset = {}
		self.rm_canvas = False
		self.rm_canvas_simampli = False
		self.index_live = 0
		self.pick_SAR_index = 0
		self.pickSAR_activated = False
		self.SAR_zoom = False
		self.SAR_change.valueChanged.connect(lambda:  self.updateSAR_info())	# use a lambda to consume the unwanted argument
		self.SAR_change.sliderReleased.connect(lambda:  self.loadSAR())			# It is to manage decorator inside a class
		self.SAR_greyscale.sliderReleased.connect(lambda:  self.updateSAR())
		self.SAR_clip_max.sliderReleased.connect(lambda:  self.updateSAR())
		self.SAR_clip_min.sliderReleased.connect(lambda:  self.updateSAR())
		self.pushButton_SAR_left.clicked.connect(lambda:  self.decrementSAR())
		self.pushButton_SAR_right.clicked.connect(lambda:  self.incrementSAR())
		self.pushButton_ellipse.clicked.connect(lambda:  self.updateSAR())
		self.pushButton_filtered_SAR.clicked.connect(lambda:  self.updateSAR())
		self.pushButton_pick_SAR.clicked.connect(lambda:  self.pickSAR())
		self.frame_pickSAR.hide()
		self.pushButton_pickSAR_next.clicked.connect(self.pickSARNext)
		self.pushButton_pickSAR_previous.clicked.connect(self.pickSARPrev)
		self.pushButton_pickSAR_save.clicked.connect(self.pickSARSave)
		self.pushButton_update_simamp.clicked.connect(self.initiateSimAmpliPlot)
		self.pushButton_simamp.clicked.connect(lambda: self.updateView(1))
		self.pushButton_3d.clicked.connect(lambda: self.updateView(2))
		self.pushButton_profile.clicked.connect(lambda: self.updateView(3))

		# Initialise view option between amplitude and 3d 
		self.pushButton_simamp.setChecked(False)
		self.pushButton_3d.setChecked(True)
		self.pushButton_profile.setChecked(False)



		# rewrite the size here to work in DT designer easier
		# self.SARImage.setMaximumSize(QSize(2000, 2000))
		# self.dockWidget_SimAmp.resize(QSize(700, 700))

		# self.ProfilePlt.setMinimumSize(QSize(100, 100))
		# self.ProfilePlt.resize(1000, 500)


	# Decorator to bypass function if data not loaded
	def data_loaded(fonction):
		print("start deco")
		def check_dataset(self):
			if self.dataset:
				return fonction(self)
			else:
				self.label_SAR.setText("Please open a csv file before playing")
		return check_dataset



	@pyqtSlot()
	def on_action_Open_csv_triggered(self):
		""" Function that open csv file and write data into a dictionary
			Then, display the first image of the file
			"""
		(self.csv_file,filtre) = QFileDialog.getOpenFileName(self,"Open CSV File", filter="(*.csv)")

		# if csv_file:
		# 	QMessageBox.information(self,"TRACE", "Fichier à ouvrir:\n\n%s"%csv_file)

		# Load data into a dict
		self.dataset = Loader(self.csv_file).images_data
		self.image_number = len(self.dataset['folder'])
		# Manage horizontal slider directly dependant of number of datas
		self.SAR_change.setMaximum(self.image_number - 1)
		self.SAR_change.setTickPosition(QSlider.TicksBelow)
		self.SAR_change.setTickInterval(1)
		# Activate pushButton Ellipse
		self.pushButton_ellipse.setEnabled(True)
		self.pushButton_filtered_SAR.setEnabled(True)
		self.pushButton_pick_SAR.setEnabled(True)

		self.initiateSARPlot()


	# def closeEvent(self,event):
	# 	messageConfirmation = "Êtes-vous sûr de vouloir quitter Pick App ?"
	# 	reponse = QMessageBox.question(self,"Confirmation",messageConfirmation,QMessageBox.Yes,QMessageBox.No) 
	# 	if reponse == QMessageBox.Yes:
	# 		event.accept() 
	# 	else:
	# 		event.ignore()


#===============================================================================================================
#====================     SAR AMPLITUDE IMAGE  IMAGE ===========================================================
#===============================================================================================================


	def initiateSARPlot(self):
		""" Function that display the image from the dataset at the index
			1: Reterive the figure object from "getSARFig function"
			2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
			"""

		# Close current figure if it exists:
		print(" initiate sar plot")
		if self.rm_canvas:
			print("-- remove canvas")
			self.canvas.close()
			self.toolbar.close()


		# Get matplotlib figure objetct and min/max value of amplitude image
		self.SAR_clip_min.setValue(int(self.SAR_clip_min.minimum()))
		self.SAR_clip_max.setValue(int(self.SAR_clip_max.maximum()))
		self.canvas = getSARFig(self)
		self.SAR_greyscale.setValue(int((self.dataset['expo_greyscale'][self.index_live])*100))
		# Add figure to layout properties of SARImage Widget
		self.SARLayout.addWidget(self.canvas)
		# Draw the figure
		self.canvas.draw()
		# Create a tool bar
		self.toolbar = NavigationToolbar(self.canvas, self.SARImage, coordinates=True)
		self.SARLayout.addWidget(self.toolbar)
		# Display crater profile
		self.initiateProfilePlot()
		# Display simulated amplitude plot
		if self.checkBox_auto_update.isChecked():
			self.initiateSimAmpliPlot()
		else:
			self.pushButton_update_simamp.setChecked(True)
		# Set variable tp allow removing canvas after first creation
		self.rm_canvas = True
		# Re-initialise picking ellipse counter
		self.pick_SAR_index = 0
		# Reinitialise zoom memorisation and memorise original one
		self.SAR_zoom = False
		self.lim_x_or = self.ax.get_xlim()
		self.lim_y_or = self.ax.get_ylim()
		# Display name of first point to pick
		self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))


	def updateSARPlot(self):
		""" Function that display the image from the dataset at the index
			1: Reterive the figure object from "getSARFig function"
			2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
			3: we do not set clip min/max  
			"""
		# print("update sar plot")
		self.canvas.close()
		self.toolbar.close()
		self.dataset['expo_greyscale'][self.index_live] = self.SAR_greyscale.value()/100
		self.canvas = getSARFig(self)
		
		# Add figure to layout properties of SARImage Widget
		self.SARLayout.addWidget(self.canvas)
		# Draw the figure
		self.canvas.draw()
		# Create a tool bar
		self.toolbar = NavigationToolbar(self.canvas, self.SARImage, coordinates=True)
		self.SARLayout.addWidget(self.toolbar)

		# Update Profile 
		self.updateProfilePlt()


	@data_loaded
	def loadSAR(self):
		# print("on_SAR_change_changed")
		self.index_live = self.SAR_change.value()
		self.SAR_greyscale.setValue(int((self.dataset['expo_greyscale'][self.index_live])*100))
		self.initiateSARPlot()

	@data_loaded
	def updateSAR(self):
		print("updateSAR request")
		self.updateSARPlot()

	@data_loaded
	def updateSAR_info(self):
		""" Write SAR image info that will be displayed on the current slider position"""
		self.index_hold = self.SAR_change.value()
		img_dir = self.dataset['folder'][self.index_hold]
		satname = img_dir.split('/')[-2]
		img_date_string = self.dataset['day'][self.index_hold]
		text = "{} : {}".format(img_date_string, satname)
		self.label_SAR.setText(text)


	@data_loaded
	def decrementSAR(self):
		self.index_live += -1
		self.index_live = np.clip(self.index_live, 0 , (self.image_number -1))
		self.label_SAR_index.setText(str(self.index_live))
		self.SAR_change.setValue(int(self.index_live))
		self.initiateSARPlot()


	@data_loaded
	def incrementSAR(self):
		# print("on_pushButton_SAR_right_clicked")
		self.index_live += 1
		self.index_live = np.clip(self.index_live, 0 , (self.image_number - 1))
		self.label_SAR_index.setText(str(self.index_live))
		self.SAR_change.setValue(int(self.index_live))
		self.initiateSARPlot()

	@data_loaded
	def pickSAR(self):
		# print("pickSAR")
		if self.pushButton_pick_SAR.isChecked():
			self.frame_pickSAR.show()
			self.pushButton_ellipse.setChecked(True)
			self.updateSARPlot()
			# Activate variable to use in the pickingManagement function
			self.pickSAR_activated = True
			# Display the next points to pick in the label of picking frame panel
			self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
		else:
			self.frame_pickSAR.hide()
			self.pickSAR_activated = False


	def pickSARNext(self):
		self.pick_SAR_index += 1
		self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 9)
		self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
		# pickSARManagement(self)

	def pickSARPrev(self):
		self.pick_SAR_index += -1
		self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 9)
		self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
		# pickSARManagement(self)

	def pickSARSave(self):
		print("save to csv file last modification")
		df = pd.DataFrame.from_dict(self.dataset)
		df.to_csv(self.csv_file, index=False)
		print("		New values has been saved to csv")
		self.pushButton_pickSAR_save.setChecked(False)
		self.pickSARNext()



#===============================================================================================================
#====================     PROFILE OF CRATER          ===========================================================
#===============================================================================================================


	def initiateProfilePlot(self):
			""" Function that display the image from the dataset at the index
				1: Reterive the figure object from "getSARFig function"
				2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
				"""

			# Close current figure if it exists:
			print(" initiate sar plot")
			if self.rm_canvas:
				self.canvas_profile.close()
				print("-- remove canvas profile")
				# self.canvas_profile.close()


			# Get matplotlib figure objetct and min/max value of amplitude image
			self.canvas_profile = getProfileFig(self)
			# Add figure to layout properties of ProfilePlt Widget
			self.Profile_Layout.addWidget(self.canvas_profile)
			# Draw the figure
			self.canvas_profile.draw()


	def updateProfilePlt(self):
			""" Function that display the image from the dataset at the index
				1: Reterive the figure object from "getSARFig function"
				2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
				3: we do not set clip min/max  
				"""
			print("update sar plot")
			self.canvas_profile.close()
			# Get matplotlib figure objetct and min/max value of amplitude image
			self.canvas_profile = getProfileFig(self)
			# Add figure to layout properties of ProfilePlt Widget
			self.Profile_Layout.addWidget(self.canvas_profile)
			# Draw the figure
			self.canvas_profile.draw()


#===============================================================================================================
#===========================    SIMULATED AMPLITUDE IMAGE  ===================================================
#===============================================================================================================


	def initiateSimAmpliPlot(self):
			""" Function that display the image from the dataset at the index
				1: Reterive the figure object from "getSARFig function"
				2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
				"""

			# Close current figure if it exists:
			# print(" initiate amplitude simulation plot")
			if self.rm_canvas_simampli:
				self.canvas_sim_ampli.close()
				# print("-- remove canvas profile")
				# self.canvas_profile.close()


			self.rm_canvas_simampli = True
			# Get matplotlib figure objetct and min/max value of amplitude image
			self.canvas_sim_ampli = getSimAmpliFig(self)

			# Create a tool bar
			# self.toolbar_3 = NavigationToolbar(self.canvas_sim_ampli, self.SimAmpPlt, coordinates=True)
			# self.SimAmp_Layout.addWidget(self.toolbar_3)
			# Add figure to layout properties of ProfilePlt Widget
			self.SimAmp_Layout.addWidget(self.canvas_sim_ampli)
			# Draw the figure
			self.canvas_sim_ampli.draw()

	def updateView(self, num):
		""" This function will switch between different view (3d, simulated amplitude ...)
		It will change the status of button and the reload the graph"""

		if (num == 1):
			print("Clicked 1")
			self.pushButton_simamp.setChecked(True)
			self.pushButton_3d.setChecked(False)
			self.pushButton_profile.setChecked(False)
		elif (num == 2):
			print("Clicked 2")
			self.pushButton_simamp.setChecked(False)
			self.pushButton_3d.setChecked(True)
			self.pushButton_profile.setChecked(False)
		elif (num == 3):
			self.pushButton_simamp.setChecked(False)
			self.pushButton_3d.setChecked(False)
			self.pushButton_profile.setChecked(True)

		self.initiateSimAmpliPlot()
